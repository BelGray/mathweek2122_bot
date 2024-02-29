# -*- coding: utf-8 -*-
import asyncio
import atexit

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from mathweek.buttons import *
from mathweek.message_text import *
from modules.execution_controller import ExecutionController
from modules.server.data.dataclasses import student_class_letters, Student
from modules.server.requests_instance import student_con
from mathweek.admin import BotMode, Admin, HandlerType
from mathweek.bot_commands import set_default_commands, BotCommandsEnum
from mathweek.loader import dp, state_manager, bot
from mathweek.logger import log
from modules.content_manager import ContentManager
from modules.tools import check_user_registered, register_new_student
from aiogram import types

from modules.user_dict import UserRegData, User
from modules.user_list import UserList

# todo: Написать основные команды. Написать класс с методами основного оформления сообщений бота.

mode = BotMode.DEVELOPMENT  # <- Режим, в котором сейчас находится бот

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
@ExecutionController.catch_exception(mode, HandlerType.MESSAGE)
@check_user_registered(HandlerType.MESSAGE)
async def start(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=start_text, reply_markup=StartButtonClient, parse_mode='HTML')


@dp.callback_query_handler(text='bot_about')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def bot_about_button_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(text=bot_about_text, parse_mode='HTML', reply_markup=StartGoBackButtonClient)


@dp.callback_query_handler(text='go_back_start')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def bot_about_button_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(text=start_text, parse_mode='HTML', reply_markup=StartButtonClient)


@dp.callback_query_handler(text='reg')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def reg_button_callback(message: types.Message):
    if reg_users.is_involved(message.from_user.id):
        return
    student = await student_con.get_student(message.from_user.id)
    if student.status == 200:
        with open('system_images/user_exists.png', 'rb') as image:
            await bot.send_photo(chat_id=message['message']['chat']['id'], caption="✅ Ты уже и так зарегистрирован(-а)",
                                 photo=image)
        return

    await reg_users_data.set(message.from_user.id)
    await reg_users.add(message.from_user.id)
    await bot.send_message(chat_id=message['message']['chat']['id'],
                           text="👤 Введи свое настоящее имя:\n\n⚠️ Убедись в правильности написания имени. Указанное имя уже нельзя будет изменить самостоятельно!",
                           reply_markup=StopRegNameButtonClient)
    await RegName.name.set()


@dp.message_handler(state=RegName.name)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def process_reg_name(message: types.Message, state: FSMContext):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await state.finish()
        name = message.text.replace(' ', '').capitalize()
        user: User = reg_users_data.get(message.from_user.id)
        user.name = name
        await bot.send_message(chat_id=message['chat']['id'],
                               text="👤 Введи свою настоящую фамилию\n\n⚠️ Убедись в правильности написания фамилии. Указанную фамилию уже нельзя будет изменить самостоятельно!",
                               reply_markup=StopRegLastnameButtonClient)
        await RegLastname.lastname.set()


@dp.message_handler(state=RegLastname.lastname)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def process_reg_lastname(message: types.Message, state: FSMContext):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await state.finish()
        lastname = message.text.replace(' ', '').capitalize()
        user: User = reg_users_data.get(message.from_user.id)
        user.lastname = lastname
        markup = InlineKeyboardMarkup(row_width=6)
        for klass in range(5, 12):
            markup.insert(InlineKeyboardButton(text=f'{klass}', callback_data=f"class_{klass}"))
        await bot.send_message(chat_id=message['chat']['id'], text="📚 Выбери свой класс: ",
                               reply_markup=markup)


@dp.callback_query_handler(Text(startswith='letter_'))
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def class_letter_choice_button_callback(callback: types.CallbackQuery):
    user: User = reg_users_data.get(callback.from_user.id)
    if reg_users.is_involved(callback.from_user.id) and reg_users_data.is_involved(callback.from_user.id) and user.class_letter is None:
        student_letter = callback.data.split('_')[1]
        user.class_letter = student_letter
        await register_new_student(callback.message, Student(
            telegram_id=callback.from_user.id,
            name=user.name,
            lastname=user.lastname,
            class_letter=user.class_letter,
            class_number=user.class_number
        ))
        await reg_users_data.remove(callback.message.from_user.id)
        await reg_users.remove(callback.message.from_user.id)
        return
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

@dp.callback_query_handler(Text(startswith='class_'))
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def class_number_choice_button_callback(callback: types.CallbackQuery):
    user: User = reg_users_data.get(callback.from_user.id)
    if reg_users.is_involved(callback.from_user.id) and reg_users_data.is_involved(callback.from_user.id) and user.class_number is None:
        student_class = callback.data.split('_')[1]
        user.class_number = int(student_class)
        await bot.send_message(chat_id=callback.message.chat.id, text="🤔 Ты точно выбрал свой настоящий класс?",
                               reply_markup=ConfirmClassNumberButtonClient)
        return
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

@dp.callback_query_handler(text='confirm_class')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def confirm_class_button_callback(message: types.Message):
    user: User = reg_users_data.get(message.from_user.id)
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id) and user.class_number is not None:
        markup = InlineKeyboardMarkup(row_width=6)
        for letter in student_class_letters[user.class_number]:
            markup.insert(InlineKeyboardButton(text=f'{letter}', callback_data=f"letter_{letter}"))
        await bot.send_message(chat_id=message['message']['chat']['id'], text=f"📚 <b>{user.class_number} класс</b>\n\n🅰️ Выбери букву класса:  ",
                               reply_markup=markup, parse_mode='HTML')
        return
    await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])


@dp.callback_query_handler(text='stop_class_reg')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def stop_class_reg_button_callback(message: types.Message):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await reg_users_data.remove(message.from_user.id)
        await reg_users.remove(message.from_user.id)
        cancel_message = await bot.send_message(chat_id=message['message']['chat']['id'],
                                                text="❌ Регистрация ученика отменена")
        await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])
        await asyncio.sleep(5)
        await cancel_message.delete()
        return
    await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])


@dp.callback_query_handler(text='stop_reg_name', state=RegName.name)
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def stop_reg_name_button_callback(message: types.Message, state: FSMContext):
    await state.reset_state()
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await reg_users_data.remove(message.from_user.id)
        await reg_users.remove(message.from_user.id)
        cancel_message = await bot.send_message(chat_id=message['message']['chat']['id'],
                                                text="❌ Регистрация ученика отменена")
        await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])
        await asyncio.sleep(5)
        await cancel_message.delete()
        return
    await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])


@dp.callback_query_handler(text='stop_reg_lastname', state=RegLastname.lastname)
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def stop_reg_lastname_button_callback(message: types.Message, state: FSMContext):
    await state.reset_state()
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await reg_users_data.remove(message.from_user.id)
        await reg_users.remove(message.from_user.id)
        cancel_message = await bot.send_message(chat_id=message['message']['chat']['id'],
                                                text="❌ Регистрация ученика отменена")
        await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])
        await asyncio.sleep(5)
        await cancel_message.delete()
        return
    await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])


if __name__ == "__main__":
    from aiogram import executor, types

    executor.start_polling(dp, on_startup=on_startup)
