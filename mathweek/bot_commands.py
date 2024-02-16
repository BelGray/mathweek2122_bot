# -*- coding: utf-8 -*-
from aiogram import types
async def set_default_commands(dp):
    """Команды бота"""
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "ℹ️ Информация о боте"),
            types.BotCommand("leaders", "🔥 Таблицы лидеров"),
            types.BotCommand('event_calendar', "📅 Календарь события"),
            types.BotCommand("profile", "👤 Профиль ученика")
        ]
    )