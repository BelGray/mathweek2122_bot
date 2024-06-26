import random

import aiogram.types
import aiohttp
import aiogram.utils.markdown as fmt
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
import mathweek.buttons as btn
from mathweek.loader import bot
from mathweek.logger import log
from mathweek.message_text import points_system_text
from modules import tools
from modules.content_manager import ContentManager
from modules.current_user_answer import LastUserAnswer
from modules.date_manager import DateManager
from modules.server.data.dataclasses import student_class_subjects, ServerResponse, tasks_levels, subject_symbols, \
    subject_labels
from modules.server.data.enums import HandlerType, TaskTypes, TaskStatus
from modules.server.requests_instance import student_con, student_answer_con, lead_con
import modules.tools as tools


class MessageDrawer:
    """Класс с методами отправки различных сообщений для конкретных целей. Не выводит ошибки в режиме разработки, тестирования"""

    def __init__(self, message: aiogram.types.Message, handler_type: HandlerType = HandlerType.MESSAGE):
        self.__message = message
        self.__chat_id = handler_type(self.__message)

    @property
    def message(self):
        return self.__message

    async def error(self, error_text: str):
        mes = f"❌ <b>Ой, что-то пошло не так!</b>\n<code>{fmt.quote_html(error_text)}</code>"
        await bot.send_message(chat_id=self.__chat_id, text=mes, reply_markup=btn.TechSupportButtonClient)

    async def server_error(self, http_status: int, error_text: str = '❌ Произошла ошибка: HTTP {0}.'):
        await bot.send_photo(chat_id=self.__chat_id,
                             caption=fmt.quote_html(error_text.format(http_status)),
                             photo=InputFile(ContentManager.make_server_error_image(http_status)),
                             reply_markup=btn.TechSupportButtonClient
                             )

    async def pic_error(self, path: str, error_text: str):
        await bot.send_photo(chat_id=self.__chat_id,
                             caption=fmt.quote_html(error_text),
                             photo=open(path, 'rb'),
                             reply_markup=btn.TechSupportButtonClient
                             )

    async def event_calendar(self):

        last_answer = f"{subject_labels[LastUserAnswer.subject]} {LastUserAnswer.class_number} класс. {fmt.quote_html(LastUserAnswer.name)} {fmt.quote_html(LastUserAnswer.lastname)} {LastUserAnswer.class_number}{LastUserAnswer.class_letter}" if not LastUserAnswer.is_none() else "Нет данных"

        text = f'📆 <b>Календарь события</b>\n\n<blockquote>📆 <b>Неделя математики 2024</b>: {DateManager.days_text[DateManager.day()]}</blockquote>\n<blockquote>🕘 <b>Последний ответ</b>:\n{last_answer}</blockquote>\n\n<i>Выполняй ежедневно задания и получай баллы за правильные ответы</i>\n\n{points_system_text}\n<blockquote>❗ Ежедневный материал: статья, викторина по статье, два задания на тему статьи</blockquote>\n<blockquote>❗ Задания дня можно решить только в данный день. На ввод ответа дается <u>1 попытка</u></blockquote>'
        markup = InlineKeyboardMarkup(row_width=3)
        for day in DateManager.event_days:
            markup.insert(InlineKeyboardButton(text=f'️{(await tools.check_calendar_day(day)).value} {day} марта',
                                               callback_data=f"taskday_{day}"))

        await bot.send_message(chat_id=self.__chat_id, text=text, reply_markup=markup)

    @classmethod
    async def make_article(cls, day: int, label: str, text: str) -> str:
        title = f'<b>{day} марта. Статья на тему "{label}"</b>' if day != DateManager.event_days[
            -1] else f'<b>{day} марта. Завершающая статья (просто интересный факт без темы)</b>'
        text = f'📰 {title}\n\n<blockquote>{fmt.quote_html(text)}</blockquote>'
        return text

    async def quiz(self, variants_list: list, label: str):
        text = f'🧩 Викторина. \n"{label}"'
        true_var = 0
        random.shuffle(variants_list)
        variants = []
        for i in range(len(variants_list)):
            variants.append(variants_list[i]['text'])
            if variants_list[i]['isCorrect']:
                true_var = i

        await bot.send_poll(self.__chat_id, text, variants, type='quiz', is_anonymous=False,
                            correct_option_id=true_var, reply_markup=btn.ShadowButtonClient)

    @classmethod
    async def make_task(cls, topic: str, task_type: str, level: int, text: str, status: TaskStatus,
                        answer: str = None) -> str:
        status_str = "Неизвестный статус (ошибка)"
        if status == TaskStatus.MISSED:
            status_str = "Неверный ответ"
        elif status == TaskStatus.SOLVED:
            status_str = "Верный ответ"
        elif status == TaskStatus.UNTOUCHED:
            status_str = "Задание не решено"
        elif status == TaskStatus.WAIT:
            status_str = 'Ответ дан. Результаты будут уже завтра.'

        text = (text
                .replace('#n', "\n")
                .replace('^2', '²')
                .replace('^3', '³')
                )

        task_text = (
            f'📌 <b>Задание на тему "{topic}"</b>\n<i>{"Текстовая задача" if task_type == TaskTypes.WORD_TASK.value else "Выражение"}.'
            f' {tasks_levels[level]["label"]}</i>\n\n<blockquote>{fmt.quote_html(text)}</blockquote>\n\n🎯 <b>Вес задания: {tasks_levels[level]["points"]}</b>'
            f'\n\n{status.value} <b>{status_str}</b>\n💬 <b>Ответ: {answer if answer is not None else " - "}</b>')

        return task_text

    @classmethod
    async def make_leaderboard(cls, leaders_list: list, students_count: int) -> str:
        leaders_list = sorted(leaders_list, key=lambda user: user['points'], reverse=True)
        leaders_str = ""
        for i in range(students_count if len(leaders_list) >= students_count else len(leaders_list)):
            student = leaders_list[i]

            name = student['student']['name']
            lastname = student['student']['lastName']
            telegram_id = student['student']['telegramId']
            class_number = student['student']['classNumber']
            class_letter = student['student']['classLetter']
            is_banned = student['student']['ban']

            points = student['points']

            username = f'<a href="tg://user?id={telegram_id}">{fmt.quote_html(lastname)} {fmt.quote_html(name)} {"🚫" if is_banned else ""}</a>'

            leaders_str += f"<b># {i + 1}</b> | {username} | {class_number}{class_letter} | <code>{points} {'балл' if points % 10 == 1 else ('балла' if 1 < points % 10 < 5 else 'баллов')}</code>\n"

        return leaders_str

    async def profile(self, telegram_id: int):
        student: ServerResponse = await student_con.get_student(telegram_id)
        student_data = student.json

        name = student_data['name']
        lastname = student_data['lastName']
        class_number = student_data['classNumber']
        class_letter = student_data['classLetter']

        answers_count = len(list(filter(lambda task: task["customStudentAnswer"] is not None, (
            await student_answer_con.get_student_answers_by_telegram_id(telegram_id)).json)))

        points_sum = (await student_con.get_student_points(telegram_id)).json['object']

        points_str = "🎯 Количество баллов:<blockquote>"
        for sub in student_class_subjects[class_number]:
            points_str += f"\n <i>{sub[1]}</i>: <code>{(await student_con.get_student_points_by_subject(telegram_id, sub[0])).json['object']}/38</code>"

        letter_leader_places_str = f"🔝 Место по предметам среди учеников <b>{class_number}{class_letter}</b> класса:<blockquote>"
        for sub in student_class_subjects[class_number]:
            letter_leader_places_str += f"\n <i>{sub[1]}</i>: <code>{await tools.get_leaderboard_place((await lead_con.get_leaderboard_by_subject_and_class_number_and_class_letter(sub[0], class_number, class_letter)).json, telegram_id)} место</code>"

        number_leader_places_str = f"🔝 Место по предметам среди параллели <b>{class_number}</b> классов:<blockquote>"
        for sub in student_class_subjects[class_number]:
            number_leader_places_str += f"\n <i>{sub[1]}</i>: <code>{await tools.get_leaderboard_place((await lead_con.get_leaderboard_by_subject_and_class_number(sub[0], class_number)).json, telegram_id)} место</code>"

        text = f"👤 <b>{fmt.quote_html(lastname)} {fmt.quote_html(name)} {class_number}{class_letter}</b>\n<blockquote>📆 <b>Неделя математики 2024</b>: {DateManager.days_text[DateManager.day()]}</blockquote>\n\n{points_str}</blockquote>\n\n💬 Ответов на задания: <code>{answers_count}</code>\n📌 Баллов по всем предметам: <code>{points_sum}</code>\n\n{letter_leader_places_str}</blockquote>\n\n{number_leader_places_str}</blockquote>"
        await bot.send_message(chat_id=self.__chat_id, text=text, parse_mode='HTML', reply_markup=btn.ShadowButtonClient)
