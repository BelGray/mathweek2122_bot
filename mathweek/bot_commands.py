# -*- coding: utf-8 -*-
import enum

from aiogram import types

class BotCommandsEnum(enum.Enum):
    START = 'start'
    LEADERS = 'leaders'
    EVENT_CALENDAR = 'event_calendar'
    PROFILE = 'profile'

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