# -*- coding: utf-8 -*-
import enum

from aiogram import types

from mathweek.loader import bot


class Statuses(enum.Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1
    TESTING = 2


class Support(enum.Enum):
    BOT = "https://t.me/+Gr-kjdpbtZVkMmVi"
    TASKS = "https://t.me/+xRHfD2XzKBk5NDgy"

class Admin:
    __admins = (1066757578, 995631274, 1498070696, 5255516914)

    @staticmethod
    def is_admin(user_id: int):
        '''Есть ли ID пользователя в списке админов'''
        return True if user_id in Admin.__admins else False

    @staticmethod
    def status(status: Statuses):
        '''Декоратор статуса бота. Команда становится доступной только админам в режиме тестирования и разработки'''

        def wrapper(call):
            async def inner(message: types.Message):
                if status == Statuses.TESTING:
                    if Admin.is_admin(message.from_user.id):
                        await call(message)
                    else:
                        await bot.send_message(chat_id=message.chat.id,
                                               text='🔧 Ведутся технические работы. Функционал бота временно недоступен.', )
                elif status == Statuses.DEVELOPMENT:
                    if Admin.is_admin(message.from_user.id):
                        await call(message)
                    else:
                        await bot.send_message(chat_id=message.chat.id,
                                               text='💻 Ведется разработка функционала бота. Бот временно недоступен.', )

                elif status == Statuses.PRODUCTION:
                    await call(message)

            return inner

        return wrapper
