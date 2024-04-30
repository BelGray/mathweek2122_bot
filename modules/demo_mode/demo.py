import enum

import aiogram
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mathweek.loader import bot
import modules.message_design as ms_design
from modules.server.data.dataclasses import subject_labels
from modules.server.data.enums import Subjects, HandlerType, TaskStatus
from modules.server.requests_instance import task_con


class DemoCallbackData(enum.Enum):
    demo_calendar = "demo_calendar"
    demo_taskday = "demo_taskday"
    demo_subtaskday_math = "demo_subtaskday_math"
    demo_subtaskday_phys = "demo_subtaskday_phys"
    demo_subtaskday_it = "demo_subtaskday_it"


class DemoCalendar:
    demo_button = InlineKeyboardButton(text="📅 (ДЕМО) Календарь события",
                                       callback_data=DemoCallbackData.demo_calendar.value)

    @staticmethod
    async def _event_calendar(chat_id: int):

        last_answer = f"Нет данных"

        text = f'📆 <b>Демоверсия календаря события</b>\n\n<blockquote>📆 <b>Неделя математики 2024</b>: ДЕМО</blockquote>\n<blockquote>🕘 <b>Последний ответ</b>:\n{last_answer}</blockquote>\n\n<i>Демоверсия календаря предлагает пользователю ознакомиться с тем, в каком виде ученики получают учебный материал во время события.</i>\n\n<blockquote>❗ Ежедневный материал: статья, викторина по статье, два задания на тему статьи. Демо календарь выдает материал случайного класса.</blockquote>\n<blockquote>❗ За верные ответы на задания из демо календаря баллы не зачисляются. Статус ответа отображается сразу</blockquote>'
        markup = InlineKeyboardMarkup(row_width=3)
        for day in range(1, 8):
            markup.insert(InlineKeyboardButton(text=f'️День {day}',
                                               callback_data=DemoCallbackData.demo_taskday.value))

        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

    @staticmethod
    async def on_button_click(data: DemoCallbackData, callback: aiogram.types.CallbackQuery, chat_id: int):
        if data == DemoCallbackData.demo_calendar:
            await callback.message.delete()
            await DemoCalendar._event_calendar(chat_id)
        elif data == DemoCallbackData.demo_taskday:
            markup = InlineKeyboardMarkup(row_width=3)
            markup.insert(InlineKeyboardButton(text='️⬅️ Назад',
                                               callback_data=DemoCallbackData.demo_calendar.value))
            markup.insert(InlineKeyboardButton(text=f'️{subject_labels["math"]}',
                                               callback_data=DemoCallbackData.demo_subtaskday_math.value))
            markup.insert(InlineKeyboardButton(text=f'️{subject_labels["phys"]}',
                                               callback_data=DemoCallbackData.demo_subtaskday_phys.value))
            markup.insert(InlineKeyboardButton(text=f'️{subject_labels["it"]}',
                                               callback_data=DemoCallbackData.demo_subtaskday_it.value))

            text = f"<b>🆕 Материал (ДЕМО). Случайный уровень сложности</b>\n<i>Случайный класс</i>"
            await callback.message.edit_text(text=text, reply_markup=markup)
        elif data == DemoCallbackData.demo_subtaskday_math:
            sub = Subjects.MATH
            await callback.message.delete()
            material = await task_con.get_random_task(sub)
            md = ms_design.MessageDrawer(callback, HandlerType.CALLBACK)
            if material.result.status == 500:
                await md.server_error(material.result.status, "❌ Произошла ошибка при получении материала.")
                return
            article = material.json['article']
            quiz = material.json['quiz']
            tasks = material.json['task']
            day = article['day']
            if tasks[0]['text'].lower() == 'none' or tasks[1]['text'].lower() == 'none' or quiz[0][
                'text'].lower() == 'none' or article[
                'text'].lower() == 'none':
                await md.pic_error('system_images/not_found.png', "❌ Не удалось получить материал")
                return
            article_pattern = await ms_design.MessageDrawer.make_article(day, tasks[0]['topic'], article['text'])
            await bot.send_message(chat_id=callback.message.chat.id, text=article_pattern,
                                   reply_markup=(InlineKeyboardMarkup(row_width=1)
                                   .insert(
                                       InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))))

            await md.quiz(quiz[0]['answers'], quiz[0]['text'])
            for task in tasks:
                topic = task['topic']
                task_type = task['type']
                level = task['difficultyLevel']
                task_text = task['text']
                content = task['content']

                task_str = await ms_design.MessageDrawer.make_task(topic, task_type, level, task_text,
                                                                   TaskStatus.UNTOUCHED, None)

                markup = InlineKeyboardMarkup(row_width=1)
                markup.insert(InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))
                markup.insert(InlineKeyboardButton(text="💬 Ответить", callback_data=f"taskdemoanswer_{task['id']}"))
                if content != "" and content is not None:
                    image = str(content).replace(" ", "")
                    try:
                        await bot.send_photo(callback.message.chat.id, photo=image, caption=task_str,
                                             reply_markup=markup)
                    except aiogram.utils.exceptions.BadRequest as e:
                        await md.error(str(e))
                else:
                    await bot.send_message(chat_id=callback.message.chat.id, text=task_str, reply_markup=markup)

        elif data == DemoCallbackData.demo_subtaskday_phys:
            sub = Subjects.PHYS
            await callback.message.delete()
            material = await task_con.get_random_task(sub)
            md = ms_design.MessageDrawer(callback, HandlerType.CALLBACK)
            if material.result.status == 500:
                await md.server_error(material.result.status, "❌ Произошла ошибка при получении материала.")
                return
            article = material.json['article']
            quiz = material.json['quiz']
            tasks = material.json['task']
            day = article['day']
            if tasks[0]['text'].lower() == 'none' or tasks[1]['text'].lower() == 'none' or quiz[0][
                'text'].lower() == 'none' or article[
                'text'].lower() == 'none':
                await md.pic_error('system_images/not_found.png', "❌ Не удалось получить материал")
                return
            article_pattern = await ms_design.MessageDrawer.make_article(day, tasks[0]['topic'], article['text'])
            await bot.send_message(chat_id=callback.message.chat.id, text=article_pattern,
                                   reply_markup=(InlineKeyboardMarkup(row_width=1)
                                   .insert(
                                       InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))))

            await md.quiz(quiz[0]['answers'], quiz[0]['text'])
            for task in tasks:
                topic = task['topic']
                task_type = task['type']
                level = task['difficultyLevel']
                task_text = task['text']
                content = task['content']

                task_str = await ms_design.MessageDrawer.make_task(topic, task_type, level, task_text,
                                                                   TaskStatus.UNTOUCHED, None)

                markup = InlineKeyboardMarkup(row_width=1)
                markup.insert(InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))
                markup.insert(InlineKeyboardButton(text="💬 Ответить", callback_data=f"taskdemoanswer_{task['id']}"))
                if content != "" and content is not None:
                    image = str(content).replace(" ", "")
                    try:
                        await bot.send_photo(callback.message.chat.id, photo=image, caption=task_str,
                                             reply_markup=markup)
                    except aiogram.utils.exceptions.BadRequest as e:
                        await md.error(str(e))
                else:
                    await bot.send_message(chat_id=callback.message.chat.id, text=task_str, reply_markup=markup)
        elif data == DemoCallbackData.demo_subtaskday_it:
            sub = Subjects.IT
            await callback.message.delete()
            material = await task_con.get_random_task(sub)
            md = ms_design.MessageDrawer(callback, HandlerType.CALLBACK)
            if material.result.status == 500:
                await md.server_error(material.result.status, "❌ Произошла ошибка при получении материала.")
                return
            article = material.json['article']
            quiz = material.json['quiz']
            tasks = material.json['task']
            day = article['day']
            if tasks[0]['text'].lower() == 'none' or tasks[1]['text'].lower() == 'none' or quiz[0]['text'].lower() == 'none' or article[
                'text'].lower() == 'none':
                await md.pic_error('system_images/not_found.png', "❌ Не удалось получить материал")
                return
            article_pattern = await ms_design.MessageDrawer.make_article(day, tasks[0]['topic'], article['text'])
            await bot.send_message(chat_id=callback.message.chat.id, text=article_pattern,
                                   reply_markup=(InlineKeyboardMarkup(row_width=1)
                                   .insert(
                                       InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))))

            await md.quiz(quiz[0]['answers'], quiz[0]['text'])
            for task in tasks:
                topic = task['topic']
                task_type = task['type']
                level = task['difficultyLevel']
                task_text = task['text']
                content = task['content']

                task_str = await ms_design.MessageDrawer.make_task(topic, task_type, level, task_text,
                                                                   TaskStatus.UNTOUCHED, None)

                markup = InlineKeyboardMarkup(row_width=1)
                markup.insert(InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear"))
                markup.insert(InlineKeyboardButton(text="💬 Ответить", callback_data=f"taskdemoanswer_{task['id']}"))
                if content != "" and content is not None:
                    image = str(content).replace(" ", "")
                    try:
                        await bot.send_photo(callback.message.chat.id, photo=image, caption=task_str,
                                             reply_markup=markup)
                    except aiogram.utils.exceptions.BadRequest as e:
                        await md.error(str(e))
                else:
                    await bot.send_message(chat_id=callback.message.chat.id, text=task_str, reply_markup=markup)
