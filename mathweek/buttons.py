from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from mathweek.admin import Support

RegButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='🗝️ Зарегистрироваться', callback_data="reg")))
TechSupportButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='⚙️ Обратиться в техническую поддержку', url=Support.BOT.value)))
TasksSupportButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='📚 Обратиться в поддержку по заданиям', url=Support.TASKS.value)))