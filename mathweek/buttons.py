from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from mathweek.admin import Support

RegButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='🗝️ Зарегистрироваться', callback_data="reg")))
TechSupportButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='⚙️ Обратиться в техническую поддержку', url=Support.BOT.value)))
TasksSupportButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='📚 Обратиться в поддержку по заданиям', url=Support.TASKS.value)))

StopRegNameButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️🛑 Завершить регистрацию', callback_data="stop_reg_name")))

StopRegLastnameButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️🛑 Завершить регистрацию', callback_data="stop_reg_lastname")))

ConfirmClassNumberButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️🛑 Завершить регистрацию', callback_data="stop_class_reg"))
                   .insert(InlineKeyboardButton(text='️✅ Подтвердить', callback_data="confirm_class"))
                    )
