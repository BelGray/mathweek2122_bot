# -*- coding: utf-8 -*-
from mathweek.bot_commands import set_default_commands
from mathweek.loader import dp
from mathweek.logger import log
from modules.content_manager import ContentManager


async def on_startup(dispatcher):
    ContentManager.init_content_path()
    log.s('on_startup', 'Successfully connected to: Telegram API')
    await set_default_commands(dispatcher)


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, on_startup=on_startup)
