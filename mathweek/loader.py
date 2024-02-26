from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from modules.state_manager import StateManager

bot = Bot(input("Send the token here: "), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Первичный дамп состояния бота и инициализация менеджера состояний
StateManager.primary_state_dump()
state_manager = StateManager()