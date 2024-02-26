# -*- coding: utf-8 -*-
import asyncio
import atexit

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from mathweek.buttons import (RegButtonClient, TechSupportButtonClient, TasksSupportButtonClient,
                              StopRegLastnameButtonClient, StopRegNameButtonClient)
from modules.server.requests_instance import student_con
from mathweek.admin import Statuses, Admin
from mathweek.bot_commands import set_default_commands, BotCommandsEnum
from mathweek.loader import dp, state_manager, bot
from mathweek.logger import log
from modules.content_manager import ContentManager
from modules.tools import check_user_registered
from aiogram import types

from modules.user_dict import UserRegData, User
from modules.user_list import UserList

mode = Statuses.DEVELOPMENT

reg_users = UserList()
reg_users_data = UserRegData()


class RegName(StatesGroup):
    name = State()


class RegLastname(StatesGroup):
    lastname = State()


async def on_startup(dispatcher):
    log.s('on_startup', 'Успешное подключение к Telegram API')
    await state_manager.state_control_loop()
    ContentManager.init_directory('content')
    await set_default_commands(dispatcher)


@dp.message_handler(commands=[BotCommandsEnum.START.value])
@Admin.bot_mode(mode, BotCommandsEnum.START)
@check_user_registered
async def start(message: types.Message):
    text = f"""📐 Привет, ученик! Добро пожаловать в бота по событию <b>«Неделя математики»</b> в <i>ГБОУ школе №2122 имени О. А. Юрасова</i>.

🤔 <b>Неделя математики</b> - это неделя, на протяжении которой ученики <i>5-11</i> классов проходят различные викторины и задания в боте, изучают интересные факты о предметах технического направления: <b>математика, физика, информатика</b>.
<blockquote>Для подробной информации введи /start</blockquote>

📅 <b>Неделя математики</b> 2024: <code>04.03.2024 - 13.03.2024</code>
"""


@dp.callback_query_handler(text='reg')
async def reg_button_callback(message: types.Message):
    if reg_users.is_involved(message.from_user.id):
        return
    student = await student_con.get_student(message.from_user.id)
    if student.status == 200:
        with open('system_images/user_exists.png', 'rb') as image:
            await bot.send_photo(chat_id=message['message']['chat']['id'], caption="✅ Ты уже и так зарегистрирован(-а)",
                                 photo=image)
        return

    await reg_users_data.set(message.from_user.id, User('', '', 0, ''))
    await reg_users.add(message.from_user.id)
    await bot.send_message(chat_id=message['message']['chat']['id'], text="👤 Введи свое настоящее имя: ",
                           reply_markup=StopRegNameButtonClient)
    await RegName.name.set()


@dp.message_handler(state=RegName.name)
async def process_reg_name(message: types.Message, state: FSMContext):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await state.finish()
        name = message.text
        user: User = reg_users_data.get(message.from_user.id)
        user.name = name
        await bot.send_message(chat_id=message['chat']['id'], text="👤 Введи свою настоящую фамилию: ",
                               reply_markup=StopRegLastnameButtonClient)
        await RegLastname.lastname.set()


@dp.message_handler(state=RegLastname.lastname)
async def process_reg_lastname(message: types.Message, state: FSMContext):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await state.finish()
        lastname = message.text
        user: User = reg_users_data.get(message.from_user.id)
        user.lastname = lastname
        markup = InlineKeyboardMarkup(row_width=1)
        for klass in range(5, 12):
            markup.insert(InlineKeyboardButton(text=f'{klass} класс', callback_data="class_number"))
        await bot.send_message(chat_id=message['chat']['id'], text="📚 Выбери свой класс: ",
                               reply_markup=markup)

        # todo: Дописать регистрацию


@dp.callback_query_handler(text='stop_reg_name', state=RegName.name)
async def stop_reg_name_button_callback(message: types.Message, state: FSMContext):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await state.reset_state()
        await reg_users_data.remove(message.from_user.id)
        await reg_users.remove(message.from_user.id)
        cancel_message = await bot.send_message(chat_id=message['message']['chat']['id'],
                                                text="❌ Регистрация ученика отменена")
        await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])
        await asyncio.sleep(5)
        await cancel_message.delete()


@dp.callback_query_handler(text='stop_reg_lastname', state=RegLastname.lastname)
async def stop_reg_lastname_button_callback(message: types.Message, state: FSMContext):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await state.reset_state()
        await reg_users_data.remove(message.from_user.id)
        await reg_users.remove(message.from_user.id)
        cancel_message = await bot.send_message(chat_id=message['message']['chat']['id'],
                                                text="❌ Регистрация ученика отменена")
        await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])
        await asyncio.sleep(5)
        await cancel_message.delete()


if __name__ == "__main__":
    from aiogram import executor, types

    executor.start_polling(dp, on_startup=on_startup)
