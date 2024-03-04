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

StartButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️ℹ️ О проекте', callback_data="bot_about"))
                   .insert(InlineKeyboardButton(text='️📆 Календарь события', callback_data="event_calendar"))
                   .insert(InlineKeyboardButton(text='⚙️ Обратиться в техническую поддержку', url=Support.BOT.value))
                   .insert(InlineKeyboardButton(text='📚 Обратиться в поддержку по заданиям', url=Support.TASKS.value))
)

StartGoBackButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️⬅️ Вернуться назад', callback_data="go_back_start")))

EventCalendarGoBackButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️⬅️ Назад', callback_data="go_back_calendar")))

LeadersGoBackButtonClient = (InlineKeyboardMarkup(row_width=1).insert(InlineKeyboardButton(text="⬅️ Вернуться назад", callback_data=f"go_back_leaders")))

DeleteAccountButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️🗑️ Удалить профиль', callback_data="delete_account")))

CancelDeleteAccountButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️❌ Отменить удаление', callback_data="cancel_delete_account")))

LeaderboardTypesButtonClient = (InlineKeyboardMarkup(row_width=1)
                    .insert(InlineKeyboardButton(text='️📚 Таблица параллели классов', callback_data="leaders_classes"))
                    .insert(InlineKeyboardButton(text='️📗 Таблица класса', callback_data="leaders_letter"))

)

ClearButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='️Ясно', callback_data="clear")))

ShadowButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='👁️‍ Скрыть', callback_data="clear")))

StopAnswerButtonClient = (InlineKeyboardMarkup(row_width=1)
                   .insert(InlineKeyboardButton(text='❌ Отменить ввод ответа', callback_data="stop_answer")))