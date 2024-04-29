# -*- coding: utf-8 -*-
import enum
import types
import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.types import ChatActions

from mathweek.bot_commands import BotCommandsEnum
from mathweek.loader import bot
from mathweek.logger import log
from modules import bot_config
from modules.server.data.enums import HandlerType


class Support(enum.Enum):
    BOT = "https://t.me/+Gr-kjdpbtZVkMmVi"
    TASKS = "https://t.me/+xRHfD2XzKBk5NDgy"


class Admin:
    __admins = (1066757578, 995631274, 5255516914, 638377681, 1498070696)

    @staticmethod
    def is_admin(user_id: int):
        '''Есть ли ID пользователя в списке админов'''
        return True if user_id in Admin.__admins else False

    @staticmethod
    def bot_mode(status: bot_config.BotMode, command: BotCommandsEnum, handler_type: HandlerType = HandlerType.MESSAGE):
        '''Декоратор статуса бота. Команда становится доступной только админам в режиме тестирования и разработки'''

        def wrapper(call: types.FunctionType):
            async def inner(*args):
                message: aiogram.types.Message = args[0]
                chat_id = handler_type(message)
                log.i('bot_mode', f'Пользователь {message.from_user.username} вызвал команду /{command.value}')
                await bot.send_chat_action(chat_id, ChatActions.TYPING)
                if status == bot_config.BotMode.TESTING:
                    if Admin.is_admin(message.from_user.id):
                        await call(*args)
                    else:
                        with open('system_images/development_mode.png', 'rb') as image:
                            await bot.send_photo(chat_id=chat_id,
                                                 caption='🔧 Ведутся технические работы. Функционал бота временно недоступен.',
                                                 photo=image)
                elif status == bot_config.BotMode.DEVELOPMENT:
                    if Admin.is_admin(message.from_user.id):
                        await call(*args)
                    else:
                        with open('system_images/development_mode.png', 'rb') as image:
                            await bot.send_photo(chat_id=chat_id,
                                                 caption='💻 Ведется разработка функционала. Бот временно недоступен.',
                                                 photo=image)

                elif status == bot_config.BotMode.PRODUCTION:
                    await call(*args)

            return inner

        return wrapper
