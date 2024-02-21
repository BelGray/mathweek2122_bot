import aiogram.types
from mathweek.admin import Support
from mathweek.buttons import RegButtonClient, TechSupportButtonClient
from mathweek.loader import bot
from modules.server.entity_controllers.student_controller import *
from mathweek.logger import log


def check_user_registered(call):
    """Декоратор проверки наличия пользователя в базе данных"""

    async def wrapper(message: aiogram.types.Message):
        controller = StudentController()
        result: aiohttp.ClientResponse = await controller.get_student(telegram_id=message.from_user.id)
        if result.status == 404:
            log.w(check_user_registered.__name__,
                  f"Пользователя с Telegram ID {message.from_user.id} нет в базе данных (404)")
            await bot.send_message(chat_id=message.chat.id,
                                   text='❌ Чтобы пользоваться функционалом бота, тебе нужно зарегистрироваться как ученик школы № 2122.\n\n(Разработчики имеют право отстранить ученика от участия в событии, если будут указаны фальшивые данные при регистрации)',
                                   reply_markup=RegButtonClient)
        elif result.status == 200:
            log.s(check_user_registered.__name__,
                  f'Пользователь с Telegram ID {message.from_user.id} присутствует в базе данных (200)')
            await call(message)
        else:
            log.e(check_user_registered.__name__,
                  f"При получении данных пользователя с Telegram ID {message.from_user.id} сервер выдал ошибку {result.status}")
            await bot.send_message(chat_id=message.chat.id,
                                   text=f'❌ При попытке найти данные об ученике на сервере, произошла ошибка: HTTP {result.status}.',
                                   reply_markup=TechSupportButtonClient)

    return wrapper


async def register_new_student(message: aiogram.types.Message, student: Student) -> aiohttp.ClientResponse:
    """Зарегистрировать нового ученика"""
    result: aiohttp.ClientResponse = await StudentController.create_student(student)
    if result.status == 201:
        log.s(register_new_student.__name__,
              f"Успешно зарегистрирован новый ученик с Telegram ID {student.telegram_id}")
        await bot.send_message(chat_id=message.chat.id,
                               text=f'🗝️ Ты успешно зарегистрирован(-а) как <b>{student.name} {student.lastname} {student.class_number}{student.class_letter}</b>',
                               parse_mode='HTML')
    if result.status == 400:
        log.e(register_new_student.__name__,
              f'Ученик {student.name} {student.lastname} {student.class_number}{student.class_letter} уже существует в базе данных.')
        await bot.send_message(chat_id=message.chat.id,
                               text=f'❌ Ученик <b>{student.name} {student.lastname} {student.class_number}{student.class_letter} уже является пользователем данного бота.</b>',
                               parse_mode='HTML',
                               reply_markup=TechSupportButtonClient)
    else:
        log.e(register_new_student.__name__,
              f"Что-то пошло не так при регистрации пользователя с Telegram ID {student.telegram_id}. HTTP статус: {result.status}")
        await bot.send_message(chat_id=message.chat.id,
                               text=f'❌ Что-то пошло не так при регистрации нового ученика. HTTP {result.status}',
                               reply_markup=TechSupportButtonClient)

    return result