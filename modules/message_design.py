import aiogram.types

from mathweek.buttons import TechSupportButtonClient
from mathweek.loader import bot
from mathweek.logger import log
from modules.server.data.enums import HandlerType


class MessageDrawer:
    """Класс с методами отправки различных сообщений для конкретных целей. Не выводит ошибки в режиме разработки, тестирования"""

    def __init__(self, message: aiogram.types.Message, handler_type: HandlerType = HandlerType.MESSAGE):
        self.__message = message
        self.__chat_id = handler_type(self.__message)

    @property
    def message(self):
        return self.__message

    async def error(self, error_text: str):
        mes = f"❌ <b>Ой, что-то пошло не так!</b>\n<code>{error_text}</code>"
        await bot.send_message(chat_id=self.__chat_id, text=mes, reply_markup=TechSupportButtonClient)

