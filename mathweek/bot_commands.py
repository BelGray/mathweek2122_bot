# -*- coding: utf-8 -*-
import enum

from aiogram import types


class BotCommandsEnum(enum.Enum):
    START = 'start'
    LEADERS = 'leaders'
    EVENT_CALENDAR = 'event_calendar'
    PROFILE = 'profile'

    handler = '[обработка промежуточного события]'


str_commands_list = [f"/{BotCommandsEnum.START.value}", f"/{BotCommandsEnum.LEADERS.value}", f"/{BotCommandsEnum.EVENT_CALENDAR.value}", f"/{BotCommandsEnum.PROFILE.value}"]


async def set_default_commands(dp):
    """Команды бота"""
    await dp.bot.set_my_commands(
        [
            types.BotCommand(BotCommandsEnum.START.value, "ℹ️ Информация о боте"),
            types.BotCommand(BotCommandsEnum.LEADERS.value, "🔥 Таблицы лидеров"),
            types.BotCommand(BotCommandsEnum.EVENT_CALENDAR.value, "📅 Календарь события"),
            types.BotCommand(BotCommandsEnum.PROFILE.value, "👤 Профиль ученика")
        ]
    )
