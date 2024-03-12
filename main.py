# -*- coding: utf-8 -*-
import asyncio
import atexit
import datetime
import random
import re

import aiogram.utils.markdown as fmt
import aiogram.utils.exceptions
import configuration_instance
import requests
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMedia, InputFile
from modules import tools
from modules.current_user_answer import LastUserAnswer
from state_instance import state_manager
from mathweek.buttons import *
from mathweek.message_text import *
from modules.date_manager import DateManager
from modules.execution_controller import ExecutionController
from modules.message_design import MessageDrawer
from modules.server.data.dataclasses import student_class_letters, Student, ServerResponse, student_class_subjects, \
    subject_symbols, days_difficulty_levels, tasks_levels, subject_labels
from modules.server.data.enums import Subjects, DayAvailability, TaskStatus
from modules.server.requests_instance import student_con, lead_con, task_con, article_con, quiz_con, student_answer_con
from mathweek.admin import Admin, HandlerType
from mathweek.bot_commands import set_default_commands, BotCommandsEnum, str_commands_list
from mathweek.loader import dp, bot
from mathweek.logger import log
from modules.content_manager import ContentManager
from modules.tools import check_user_registered, register_new_student, check_task_status, check_calendar_day, \
    commands_detector
from aiogram import types

from modules.user_dict import UserRegData, User, UserData
from modules.user_list import UserList

mode = configuration_instance.bot_mode

reg_users = UserList()
reg_users_data = UserRegData()

task_id_input = UserData()

user_input = UserData()


class AnswerInput(StatesGroup):
    answer = State()


class ConfirmDelete(StatesGroup):
    code = State()


class RegName(StatesGroup):
    name = State()


class RegLastname(StatesGroup):
    lastname = State()


async def on_startup(dispatcher):
    log.s('on_startup', 'Успешное подключение к Telegram API')
    await state_manager.state_control_loop()
    # await DateManager.set_event_time_control_loop()
    ContentManager.init_directory('content')
    await set_default_commands(dispatcher)


@dp.message_handler(commands=[BotCommandsEnum.PROFILE.value])
@Admin.bot_mode(mode, BotCommandsEnum.PROFILE)
@ExecutionController.catch_exception(mode, HandlerType.MESSAGE)
@check_user_registered(HandlerType.MESSAGE)
@commands_detector(BotCommandsEnum.PROFILE)
async def profile(message: types.Message):
    await MessageDrawer(message, HandlerType.MESSAGE).profile(telegram_id=message.from_user.id)


@dp.message_handler(commands=[BotCommandsEnum.EVENT_CALENDAR.value])
@Admin.bot_mode(mode, BotCommandsEnum.EVENT_CALENDAR)
@ExecutionController.catch_exception(mode, HandlerType.MESSAGE)
@check_user_registered(HandlerType.MESSAGE)
@commands_detector(BotCommandsEnum.EVENT_CALENDAR)
async def event_calendar(message: types.Message):
    await MessageDrawer(message, HandlerType.MESSAGE).event_calendar()


@dp.callback_query_handler(text='event_calendar')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def event_calendar_button_callback(callback: types.CallbackQuery):
    await MessageDrawer(callback.message, HandlerType.MESSAGE).event_calendar()


@dp.callback_query_handler(Text(startswith="taskday_"))
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def task_day_button_callback(callback: types.CallbackQuery):
    data = callback.data.split('_')
    day = int(data[1])
    day_check = await check_calendar_day(day)
    student = (await student_con.get_student(callback.from_user.id)).json
    class_number = student['classNumber']
    markup = InlineKeyboardMarkup(row_width=3)
    markup.insert(InlineKeyboardButton(text='️⬅️ Назад', callback_data="go_back_calendar"))

    text = f"<b>{day_check.value} Задания {day} марта. {tasks_levels[days_difficulty_levels[day]]['label']}</b>\n<i>{class_number} класс</i>"

    if day_check == DayAvailability.AVAILABLE or day_check == DayAvailability.PASSED:

        for sub in student_class_subjects[class_number]:
            markup.insert(
                InlineKeyboardButton(text=f'{sub[1]}',
                                     callback_data=f"subtaskday_{day}_{sub[0].value}"))
        await callback.message.edit_text(text=text, reply_markup=markup)
    elif day_check == DayAvailability.UNAVAILABLE:
        await bot.send_photo(chat_id=callback.message.chat.id, caption=text,
                             photo=open("system_images/no_tasks.png", 'rb'), reply_markup=ClearButtonClient)


@dp.callback_query_handler(Text(startswith="subtaskday_"))
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def sub_task_day_button_callback(callback: types.CallbackQuery):
    await callback.message.delete()
    data = callback.data.split('_')
    day = int(data[1])
    sub = data[2]
    day_check = await check_calendar_day(day)
    student = (await student_con.get_student(callback.from_user.id)).json
    class_number = student['classNumber']
    md = MessageDrawer(callback, HandlerType.CALLBACK)

    if sub == Subjects.IT.value:
        subject = Subjects.IT

        tasks = list(filter(lambda current_task: current_task['quiz'] is False,
                            (await task_con.get_task_by_class_and_date_and_difficulty_and_subject(class_number, day,
                                                                                                  days_difficulty_levels[
                                                                                                      day],
                                                                                                  subject)).json))
        article = (await article_con.get_article_by_subject_and_day_and_class(subject, day, class_number)).json
        quiz = (await quiz_con.get_quiz_by_subject_and_class_and_day(subject, class_number, day)).json
        if len(tasks) == 0 or len(article) == 0 or len(quiz) == 0:
            await md.pic_error('system_images/not_found.png', "❌ Не удалось получить материал на этот день")
            return

        article_pattern = await MessageDrawer.make_article(day, tasks[0]['topic'], article[0]['text'])
        await bot.send_message(chat_id=callback.message.chat.id, text=article_pattern, reply_markup=ShadowButtonClient)

        await md.quiz(quiz[0]['answerList'], quiz[0]['text'])

        for task in tasks:
            topic = task['topic']
            task_type = task['type']
            level = task['difficultyLevel']
            task_text = task['text']
            content = task['content']
            status, answer = await check_task_status(callback.from_user.id, day, task['id'])

            task_str = await MessageDrawer.make_task(topic, task_type, level, task_text, status, answer)

            markup = InlineKeyboardMarkup(row_width=1)
            markup.insert(InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))

            if day_check == DayAvailability.AVAILABLE:
                if status == TaskStatus.UNTOUCHED:
                    markup.insert(InlineKeyboardButton(text="💬 Ответить", callback_data=f"taskanswer_{task['id']}"))
                is_assigned = await student_answer_con.is_task_assigned(callback.from_user.id, task['id'])
                if not is_assigned.json['isAssigned']:
                    await state_manager.detect_task_assignation(1)
                    await student_answer_con.assign_task_to_student(callback.from_user.id, task['id'])

            if content != "" and content is not None:
                image = str(content).replace(" ", "")
                try:
                    await bot.send_photo(callback.message.chat.id, photo=image, caption=task_str,
                                         reply_markup=markup)
                except aiogram.utils.exceptions.BadRequest as e:
                    await md.error(str(e))
            else:
                await bot.send_message(chat_id=callback.message.chat.id, text=task_str, reply_markup=markup)

    if sub == Subjects.PHYS.value:
        subject = Subjects.PHYS

        tasks = list(filter(lambda current_task: current_task['quiz'] is False,
                            (await task_con.get_task_by_class_and_date_and_difficulty_and_subject(class_number, day,
                                                                                                  days_difficulty_levels[
                                                                                                      day],
                                                                                                  subject)).json))
        article = (await article_con.get_article_by_subject_and_day_and_class(subject, day, class_number)).json
        quiz = (await quiz_con.get_quiz_by_subject_and_class_and_day(subject, class_number, day)).json
        if len(tasks) == 0 or len(article) == 0 or len(quiz) == 0:
            await md.pic_error('system_images/not_found.png', "❌ Не удалось получить материал на этот день")
            return

        article_pattern = await MessageDrawer.make_article(day, tasks[0]['topic'], article[0]['text'])
        await bot.send_message(chat_id=callback.message.chat.id, text=article_pattern, reply_markup=ShadowButtonClient)

        await md.quiz(quiz[0]['answerList'], quiz[0]['text'])

        for task in tasks:
            topic = task['topic']
            task_type = task['type']
            level = task['difficultyLevel']
            task_text = task['text']
            content = task['content']
            status, answer = await check_task_status(callback.from_user.id, day, task['id'])

            task_str = await MessageDrawer.make_task(topic, task_type, level, task_text, status, answer)

            markup = InlineKeyboardMarkup(row_width=1)
            markup.insert(InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))

            if day_check == DayAvailability.AVAILABLE:
                if status == TaskStatus.UNTOUCHED:
                    markup.insert(InlineKeyboardButton(text="💬 Ответить", callback_data=f"taskanswer_{task['id']}"))
                is_assigned = await student_answer_con.is_task_assigned(callback.from_user.id, task['id'])
                if not is_assigned.json['isAssigned']:
                    await state_manager.detect_task_assignation(1)
                    await student_answer_con.assign_task_to_student(callback.from_user.id, task['id'])

            if content != "" and content is not None:
                image = str(content).replace(" ", "")
                try:
                    await bot.send_photo(callback.message.chat.id, photo=image, caption=task_str,
                                         reply_markup=markup)
                except aiogram.utils.exceptions.BadRequest as e:
                    await md.error(str(e))
            else:
                await bot.send_message(chat_id=callback.message.chat.id, text=task_str, reply_markup=markup)

    if sub == Subjects.MATH.value:
        subject = Subjects.MATH

        tasks = list(filter(lambda current_task: current_task['quiz'] is False,
                            (await task_con.get_task_by_class_and_date_and_difficulty_and_subject(class_number, day,
                                                                                                  days_difficulty_levels[
                                                                                                      day],
                                                                                                  subject)).json))
        article = (await article_con.get_article_by_subject_and_day_and_class(subject, day, class_number)).json
        quiz = (await quiz_con.get_quiz_by_subject_and_class_and_day(subject, class_number, day)).json
        if len(tasks) == 0 or len(article) == 0 or len(quiz) == 0:
            await md.pic_error('system_images/not_found.png', "❌ Не удалось получить материал на этот день")
            return

        article_pattern = await MessageDrawer.make_article(day, tasks[0]['topic'], article[0]['text'])
        await bot.send_message(chat_id=callback.message.chat.id, text=article_pattern, reply_markup=ShadowButtonClient)

        await md.quiz(quiz[0]['answerList'], quiz[0]['text'])

        for task in tasks:
            topic = task['topic']
            task_type = task['type']
            level = task['difficultyLevel']
            task_text = task['text']
            content = task['content']
            status, answer = await check_task_status(callback.from_user.id, day, task['id'])

            task_str = await MessageDrawer.make_task(topic, task_type, level, task_text, status, answer)

            markup = InlineKeyboardMarkup(row_width=1)
            markup.insert(InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))

            if day_check == DayAvailability.AVAILABLE:
                if status == TaskStatus.UNTOUCHED:
                    markup.insert(InlineKeyboardButton(text="💬 Ответить", callback_data=f"taskanswer_{task['id']}"))
                is_assigned = await student_answer_con.is_task_assigned(callback.from_user.id, task['id'])
                if not is_assigned.json['isAssigned']:
                    await state_manager.detect_task_assignation(1)
                    await student_answer_con.assign_task_to_student(callback.from_user.id, task['id'])

            if content != "" and content is not None:
                image = str(content).replace(" ", "")
                try:
                    await bot.send_photo(callback.message.chat.id, photo=image, caption=task_str,
                                         reply_markup=markup)
                except aiogram.utils.exceptions.BadRequest as e:
                    await md.error(str(e))
            else:
                await bot.send_message(chat_id=callback.message.chat.id, text=task_str, reply_markup=markup)


@dp.callback_query_handler(Text(startswith="taskanswer_"))
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def taskanswer_button_callback(callback: types.CallbackQuery):
    if not task_id_input.is_involved(callback.from_user.id):
        data = callback.data.split("_")
        task_id = int(data[1])
        await task_id_input.set(callback.from_user.id, task_id)
        task = (await task_con.get_task(task_id)).json
        day_checker = await check_calendar_day(task['day'])
        if day_checker == DayAvailability.AVAILABLE:
            await bot.send_message(chat_id=callback.message.chat.id, text="💬 Введи ответ на задание: ",
                                   reply_markup=StopAnswerButtonClient)
            await AnswerInput.answer.set()
        else:
            await callback.answer("⛔ На это задание нельзя ответить!", show_alert=True)
    else:
        await callback.answer('✏️ Ты уже отвечаешь на это задание!', show_alert=True)


@dp.callback_query_handler(text='stop_answer', state=AnswerInput.answer)
async def stop_answer_button_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    if task_id_input.is_involved(callback.from_user.id):
        await state.reset_state()
        await task_id_input.remove(callback.from_user.id)
        await callback.answer("⛔ Ввод ответа отменен", show_alert=True)


@dp.message_handler(state=AnswerInput.answer, content_types=types.ContentTypes.TEXT)
async def process_task_answer(message: types.Message, state: FSMContext):
    await state.reset_state()
    if task_id_input.is_involved(message.from_user.id):
        task_id = int(task_id_input.get(message.from_user.id))
        task = (await task_con.get_task(task_id)).json
        student = (await student_con.get_student(message.from_user.id)).json
        answer = message.text.lower().replace(',', '.').strip()[:200]
        answer_req = await student_answer_con.set_student_custom_answer(answer, message.from_user.id, task_id)
        current_time = datetime.datetime.now()
        if answer_req.result.status == 409:
            alert = await bot.send_message(chat_id=message.chat.id, text="❌ Ты уже ранее отвечал на это задание")
            await asyncio.sleep(5)
            await alert.delete()
        elif answer_req.result.status // 100 == 2:
            await state_manager.detect_answer()
            await LastUserAnswer.set(name=student['name'], lastname=student['lastName'],
                                     class_number=student['classNumber'], class_letter=student['classLetter'],
                                     subject=str(task['subject']).lower())
            alert = await bot.send_message(chat_id=message.chat.id, text="✅ Ответ сохранен!")
            await asyncio.sleep(5)
            await alert.delete()
        else:
            await MessageDrawer(message).server_error(answer_req.result.status,
                                                      f"❌ Что-то пошло не так при сохранении ответа!\nСтатус: <code>{answer_req.result.status}</code>\nВремя: <code>{current_time}</code>\n\nПожалуйста, обратитесь в поддержку.")
        await task_id_input.remove(message.from_user.id)
    else:
        await message.answer('❌ Ты не можешь отвечать на этот вопрос!')


@dp.callback_query_handler(text='clear')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def clear_button_callback(callback: types.CallbackQuery):
    await callback.message.delete()


@dp.callback_query_handler(text='go_back_calendar')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def go_back_calendar_button_callback(callback: types.CallbackQuery):
    last_answer = f"{subject_labels[LastUserAnswer.subject]} {LastUserAnswer.class_number} класс. {fmt.quote_html(LastUserAnswer.name)} {fmt.quote_html(LastUserAnswer.lastname)} {LastUserAnswer.class_number}{LastUserAnswer.class_letter}" if not LastUserAnswer.is_none() else "Нет данных"

    text = f'📆 <b>Календарь события</b>\n\n<blockquote>📆 <b>Неделя математики 2024</b>: {DateManager.days_text[DateManager.day()]}</blockquote>\n<blockquote>🕘 <b>Последний ответ</b>:\n{last_answer}</blockquote>\n\n<i>Выполняй ежедневно задания и получай баллы за правильные ответы</i>\n\n{points_system_text}\n<blockquote>❗ Ежедневный материал: статья, викторина по статье, два задания на тему статьи</blockquote>\n<blockquote>❗ Задания дня можно решить только в данный день. На ввод ответа дается <u>1 попытка</u></blockquote>'

    markup = InlineKeyboardMarkup(row_width=3)
    for day in DateManager.event_days:
        markup.insert(InlineKeyboardButton(text=f'️{(await tools.check_calendar_day(day)).value} {day} марта',
                                           callback_data=f"taskday_{day}"))
    await callback.message.edit_text(text=text, reply_markup=markup)


@dp.callback_query_handler(text='delete_account')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def delete_account_button_callback(callback: types.CallbackQuery):
    confirmation_code = random.randint(100000, 999999)
    await user_input.set(telegram_id=callback.from_user.id, value=confirmation_code)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f"⚠️ Внимание! Твой профиль будет удалён. Введи следующий код для подтверждения действия:\n\n<code>{confirmation_code}</code>",
                           reply_markup=CancelDeleteAccountButtonClient, parse_mode='HTML'
                           )
    await ConfirmDelete.code.set()


@dp.callback_query_handler(text='cancel_delete_account', state=ConfirmDelete.code)
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def cancel_delete_account_button_callback(callback: types.CallbackQuery, state: FSMContext):
    if user_input.is_involved(callback.from_user.id):
        await state.reset_state()
        await user_input.remove(telegram_id=callback.from_user.id)
        await bot.send_message(chat_id=callback.message.chat.id, text="✖️ Процесс удаления профиля отменён!")
    await callback.message.delete()


@dp.message_handler(state=ConfirmDelete.code, content_types=types.ContentTypes.TEXT)
async def process_confirm_delete(message: types.Message, state: FSMContext):
    if user_input.is_involved(message.from_user.id):
        code = str(user_input.get(message.from_user.id))
        input_code = message.text
        await user_input.remove(telegram_id=message.from_user.id)
        if input_code == code:
            await state.reset_state()
            result: ServerResponse = await student_con.delete_student(message.from_user.id)
            if result.result.status // 100 == 2:
                await bot.send_message(chat_id=message.chat.id, text="🚮 Профиль удалён успешно!")
            else:
                await MessageDrawer(message, HandlerType.MESSAGE).server_error(http_status=result.result.status)
        else:
            await state.reset_state()
            await bot.send_message(chat_id=message.chat.id, text="✖️ Процесс удаления профиля отменён!")
    await message.delete()


@dp.message_handler(commands=[BotCommandsEnum.START.value])
@Admin.bot_mode(mode, BotCommandsEnum.START)
@ExecutionController.catch_exception(mode, HandlerType.MESSAGE)
@check_user_registered(HandlerType.MESSAGE)
@commands_detector(BotCommandsEnum.START)
async def start(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=start_text, reply_markup=StartButtonClient, parse_mode='HTML')


@dp.message_handler(commands=[BotCommandsEnum.LEADERS.value])
@Admin.bot_mode(mode, BotCommandsEnum.LEADERS)
@ExecutionController.catch_exception(mode, HandlerType.MESSAGE)
@check_user_registered(HandlerType.MESSAGE)
@commands_detector(BotCommandsEnum.LEADERS)
async def leaders(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text="🔝 <b>Таблицы лидеров</b>\n\n<i>Выбери тип таблицы лидеров</i>",
                           reply_markup=LeaderboardTypesButtonClient)


@dp.callback_query_handler(text='leaders_classes')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def leaders_classes_button_callback(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="📖 Все предметы", callback_data=f"classes_leaderboard_subjects"))
    student = await student_con.get_student(callback.from_user.id)
    class_number = student.json['classNumber']
    for sub in student_class_subjects[class_number]:
        markup.insert(InlineKeyboardButton(text=sub[1], callback_data=f"classes_leaderboard_{sub[0].value}"))
    await callback.message.edit_text(text="🔝 <b>Таблицы лидеров параллели классов</b>\n\n<i>Выбери таблицу лидеров</i>",
                                     reply_markup=markup)


@dp.callback_query_handler(text='leaders_letter')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def leaders_letter_button_callback(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="📖 Все предметы", callback_data=f"letter_leaderboard_subjects"))
    student = await student_con.get_student(callback.from_user.id)
    class_number = student.json['classNumber']
    for sub in student_class_subjects[class_number]:
        markup.insert(InlineKeyboardButton(text=sub[1], callback_data=f"letter_leaderboard_{sub[0].value}"))
    await callback.message.edit_text(text="🔝 <b>Таблицы лидеров класса</b>\n\n<i>Выбери таблицу лидеров</i>",
                                     reply_markup=markup)


@dp.callback_query_handler(Text(contains="_leaderboard_"))
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def leaderboard_button_callback(callback: types.CallbackQuery):
    data = callback.data.split("_")
    leaders_list = []
    leaders_str = "<blockquote>Пустая таблица :(</blockquote>"
    table_label = ""
    students_count = 25

    student = await student_con.get_student(callback.from_user.id)
    if data[0] == "letter":
        class_number = student.json['classNumber']
        class_letter = student.json['classLetter']
        if data[2] == Subjects.MATH.value:
            leaders_list = (
                await lead_con.get_leaderboard_by_subject_and_class_number_and_class_letter(Subjects.MATH, class_number,
                                                                                            class_letter)).json
            leaders_done_str = await MessageDrawer.make_leaderboard(leaders_list, students_count)
            if leaders_done_str != "":
                leaders_str = leaders_done_str
            table_label = f"<b>{subject_symbols['math']} Математика {class_number}{class_letter} класс. ТОП <code>{students_count}</code> по баллам</b>\n"

        elif data[2] == Subjects.IT.value:
            leaders_list = (
                await lead_con.get_leaderboard_by_subject_and_class_number_and_class_letter(Subjects.IT, class_number,
                                                                                            class_letter)).json
            leaders_done_str = await MessageDrawer.make_leaderboard(leaders_list, students_count)
            if leaders_done_str != "":
                leaders_str = leaders_done_str
            table_label = f"<b>{subject_symbols['it']} Информатика {class_number}{class_letter} класс. ТОП <code>{students_count}</code> по баллам</b>\n"

        elif data[2] == Subjects.PHYS.value:
            leaders_list = (
                await lead_con.get_leaderboard_by_subject_and_class_number_and_class_letter(Subjects.PHYS, class_number,
                                                                                            class_letter)).json
            leaders_done_str = await MessageDrawer.make_leaderboard(leaders_list, students_count)
            if leaders_done_str != "":
                leaders_str = leaders_done_str
            table_label = f"<b>{subject_symbols['phys']} Физика {class_number}{class_letter} класс. ТОП <code>{students_count}</code> по баллам</b>\n"

        elif data[2] == "subjects":
            leaders_list = (
                await lead_con.get_leaderboard_by_class_number_and_class_letter(class_number, class_letter)).json
            leaders_done_str = await MessageDrawer.make_leaderboard(leaders_list, students_count)
            if leaders_done_str != "":
                leaders_str = leaders_done_str
            table_label = f"<b>📖 Все предметы {class_number}{class_letter} класс. ТОП <code>{students_count}</code> по общим баллам</b>\n"

    elif data[0] == "classes":
        class_number = student.json['classNumber']
        if data[2] == Subjects.MATH.value:
            leaders_list = (
                await lead_con.get_leaderboard_by_subject_and_class_number(Subjects.MATH, class_number)).json
            leaders_done_str = await MessageDrawer.make_leaderboard(leaders_list, students_count)
            if leaders_done_str != "":
                leaders_str = leaders_done_str
            table_label = f"<b>{subject_symbols['math']} Математика {class_number} классы. ТОП <code>{students_count}</code> по баллам</b>\n"

        elif data[2] == Subjects.IT.value:
            leaders_list = (
                await lead_con.get_leaderboard_by_subject_and_class_number(Subjects.IT, class_number)).json
            leaders_done_str = await MessageDrawer.make_leaderboard(leaders_list, students_count)
            if leaders_done_str != "":
                leaders_str = leaders_done_str
            table_label = f"<b>{subject_symbols['it']} Информатика {class_number} классы. ТОП <code>{students_count}</code> по баллам</b>\n"

        elif data[2] == Subjects.PHYS.value:
            leaders_list = (
                await lead_con.get_leaderboard_by_subject_and_class_number(Subjects.PHYS, class_number)).json
            leaders_done_str = await MessageDrawer.make_leaderboard(leaders_list, students_count)
            if leaders_done_str != "":
                leaders_str = leaders_done_str
            table_label = f"<b>{subject_symbols['phys']} Физика {class_number} классы. ТОП <code>{students_count}</code> по баллам</b>\n"

        elif data[2] == "subjects":
            leaders_list = (
                await lead_con.get_leaderboard_by_class_number(class_number)).json
            leaders_done_str = await MessageDrawer.make_leaderboard(leaders_list, students_count)
            if leaders_done_str != "":
                leaders_str = leaders_done_str
            table_label = f"<b>📖 Все предметы {class_number} классы. ТОП <code>{students_count}</code> по общим баллам</b>\n"

    await callback.message.edit_text(text=f"{table_label}\n{leaders_str}", reply_markup=LeadersGoBackButtonClient)


@dp.callback_query_handler(text='go_back_leaders')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
@check_user_registered(HandlerType.CALLBACK)
async def go_back_leaders_button_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(text="🔝 <b>Таблицы лидеров</b>\n\n<i>Выбери тип таблицы лидеров</i>",
                                     reply_markup=LeaderboardTypesButtonClient)


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
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        return
    student: ServerResponse = await student_con.get_student(message.from_user.id)
    if student.result.status == 200:
        with open('system_images/user_exists.png', 'rb') as image:
            await bot.send_photo(chat_id=message['message']['chat']['id'], caption="✅ Ты уже и так зарегистрирован(-а)",
                                 photo=image)
        return
    await reg_users_data.set(message.from_user.id)
    await reg_users.add(message.from_user.id)
    await bot.send_message(chat_id=message['message']['chat']['id'],
                           text="👤 Введи свое настоящее <b><u>ИМЯ</u></b>:\n\n⚠️ Убедись в правильности написания имени. Указанное имя уже нельзя будет изменить самостоятельно!",
                           reply_markup=StopRegNameButtonClient)
    await RegName.name.set()


@dp.message_handler(state=RegName.name, content_types=types.ContentTypes.TEXT)
async def process_reg_name(message: types.Message, state: FSMContext):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await state.reset_state()
        name = message.text.replace(' ', '').capitalize()[:20]
        if not re.match("^[а-яА-Я]{3,}$", name):
            await reg_users_data.remove(message.from_user.id)
            await reg_users.remove(message.from_user.id)
            await bot.send_message(chat_id=message.chat.id,
                                   text="❌ Регистрация ученика отменена. Введи имя корректно!")
            return
        user: User = reg_users_data.get(message.from_user.id)
        user.name = name
        await bot.send_message(chat_id=message['chat']['id'],
                               text="👤 Введи свою настоящую <b><u>ФАМИЛИЮ</u></b>\n\n⚠️ Убедись в правильности написания фамилии. Указанную фамилию уже нельзя будет изменить самостоятельно!",
                               reply_markup=StopRegLastnameButtonClient)
        await RegLastname.lastname.set()


@dp.message_handler(state=RegLastname.lastname, content_types=types.ContentTypes.TEXT)
async def process_reg_lastname(message: types.Message, state: FSMContext):
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await state.reset_state()
        lastname = message.text.replace(' ', '').capitalize()[:25]
        if not re.match("^[а-яА-Я]{3,}$", lastname):
            await reg_users_data.remove(message.from_user.id)
            await reg_users.remove(message.from_user.id)
            await bot.send_message(chat_id=message.chat.id,
                                   text="❌ Регистрация ученика отменена. Введи фамилию корректно!")
            return
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
    if reg_users.is_involved(callback.from_user.id) and reg_users_data.is_involved(
            callback.from_user.id) and user.class_letter is None:
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
    if reg_users.is_involved(callback.from_user.id) and reg_users_data.is_involved(
            callback.from_user.id):
        user: User = reg_users_data.get(callback.from_user.id)
        if user.class_number is None:
            student_class = callback.data.split('_')[1]
            user.class_number = int(student_class)
            await bot.send_message(chat_id=callback.message.chat.id,
                                   text=f"<b>{student_class} класс</b>\n🤔 Ты точно выбрал(-а) свой настоящий класс?",
                                   reply_markup=ConfirmClassNumberButtonClient)
            return
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@dp.callback_query_handler(text='confirm_class')
@Admin.bot_mode(mode, BotCommandsEnum.handler, HandlerType.CALLBACK)
@ExecutionController.catch_exception(mode, HandlerType.CALLBACK)
async def confirm_class_button_callback(message: types.Message):
    user: User = reg_users_data.get(message.from_user.id)
    await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(
            message.from_user.id) and user.class_number is not None:
        markup = InlineKeyboardMarkup(row_width=6)
        for letter in student_class_letters[user.class_number]:
            markup.insert(InlineKeyboardButton(text=f'{letter}', callback_data=f"letter_{letter}"))
        await bot.send_message(chat_id=message['message']['chat']['id'],
                               text=f"📚 <b>{user.class_number} класс</b>\n\n🅰️ Выбери букву класса:  ",
                               reply_markup=markup, parse_mode='HTML')
        return


@dp.callback_query_handler(text='stop_class_reg')
async def stop_class_reg_button_callback(message: types.Message):
    await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])
    if reg_users.is_involved(message.from_user.id) and reg_users_data.is_involved(message.from_user.id):
        await reg_users_data.remove(message.from_user.id)
        await reg_users.remove(message.from_user.id)
        cancel_message = await bot.send_message(chat_id=message['message']['chat']['id'],
                                                text="❌ Регистрация ученика отменена")
        await bot.delete_message(chat_id=message['message']['chat']['id'], message_id=message['message']['message_id'])
        await asyncio.sleep(5)
        await cancel_message.delete()
        return


@dp.callback_query_handler(text='stop_reg_name', state=RegName.name)
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
