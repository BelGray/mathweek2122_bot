import warnings
import aiogram.types
from aiogram.dispatcher import FSMContext

from mathweek.admin import BotMode
from mathweek.logger import log
from modules.message_design import MessageDrawer
from modules.server.data.enums import HandlerType


class ExecutionControllerWarning(UserWarning):
    pass


class ExecutionController:
    """Класс для предупреждения пользователя о возникшей ошибке. В режиме разработки отображение ошибок происходит корректно"""

    @staticmethod
    def catch_exception(bot_mode: BotMode, handler_type: HandlerType = HandlerType.MESSAGE):
        """Перехват исключения и его отображение пользователю"""
        def wrap(call):
            async def wrapper(message: aiogram.types.Message, state: FSMContext = None):
                if bot_mode == BotMode.PRODUCTION or bot_mode == BotMode.TESTING:
                    try:
                        await call(message)
                    except Exception as e:
                        await MessageDrawer(message, handler_type).error(str(e))
                        log.e(call.__name__, "Вызов исключения: " + str(e))
                        warnings.warn(str(e), ExecutionControllerWarning)
                else:
                    (await call(message)) if state is None else (await call(message, state))

            return wrapper
        return wrap
