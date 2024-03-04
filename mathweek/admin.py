# -*- coding: utf-8 -*-
import enum
import types
import aiogram
from aiogram.dispatcher import FSMContext

from mathweek.bot_commands import BotCommandsEnum
from mathweek.loader import bot
from mathweek.logger import log
from modules.server.data.enums import HandlerType


class BotMode(enum.Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1
    TESTING = 2


class Support(enum.Enum):
    BOT = "https://t.me/+Gr-kjdpbtZVkMmVi"
    TASKS = "https://t.me/+xRHfD2XzKBk5NDgy"


class Admin:
    __admins = (1066757578, 995631274, 5255516914, 638377681)

    @staticmethod
    def is_admin(user_id: int):
        '''Есть ли ID пользователя в списке админов'''
        return True if user_id in Admin.__admins else False

    @staticmethod
    def bot_mode(status: BotMode, command: BotCommandsEnum, handler_type: HandlerType = HandlerType.MESSAGE):
        '''Декоратор статуса бота. Команда становится доступной только админам в режиме тестирования и разработки'''

        def wrapper(call: types.FunctionType):
            async def inner(message: aiogram.types.Message, state: FSMContext = None):
                chat_id = handler_type(message)
                log.i('bot_mode', f'Пользователь {message.from_user.username} вызвал команду /{command.value}')
                if status == BotMode.TESTING:
                    if Admin.is_admin(message.from_user.id):
                        await call(message)
                    else:
                        with open('system_images/development_mode.png', 'rb') as image:
                            await bot.send_photo(chat_id=chat_id,
                                                 caption='🔧 Ведутся технические работы. Функционал бота временно недоступен.',
                                                 photo=image)
                elif status == BotMode.DEVELOPMENT:
                    if Admin.is_admin(message.from_user.id):
                        await call(message)
                    else:
                        with open('system_images/development_mode.png', 'rb') as image:
                            await bot.send_photo(chat_id=chat_id,
                                                 caption='💻 Ведется разработка функционала. Бот временно недоступен.',
                                                 photo=image)

                elif status == BotMode.PRODUCTION:
                    await call(message)

            return inner

        return wrapper
