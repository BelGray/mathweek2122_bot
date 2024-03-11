import aiogram.types
from aiogram.types import InputFile
import aiogram.utils.markdown as fmt
import state_instance
from mathweek.bot_commands import BotCommandsEnum
from mathweek.buttons import RegButtonClient, TechSupportButtonClient
from mathweek.loader import bot
from modules.content_manager import ContentManager
from modules.date_manager import DateManager
from modules.server.data.enums import HandlerType, DayAvailability, TaskStatus
from modules.server.entity_controllers.student_controller import *
from mathweek.logger import log
from modules.server.requests_instance import student_con, task_con, student_answer_con


async def get_leaderboard_place(leaders: list, telegram_id: int) -> int:
    """Определить место в таблице лидеров"""
    leaders = sorted(leaders, key=lambda user: user['points'], reverse=True)
    for student in leaders:
        if student['student']['telegramId'] == telegram_id:
            return leaders.index(student) + 1


async def check_calendar_day(day: int) -> DayAvailability:
    status = DayAvailability.UNAVAILABLE
    if DateManager.day() < day:
        status = DayAvailability.UNAVAILABLE
    elif DateManager.day() == day:
        status = DayAvailability.AVAILABLE
    elif DateManager.day() > day:
        status = DayAvailability.PASSED

    return status


def xor(operand_1: bool, operand_2: bool):
    return bool(operand_1) != bool(operand_2)


async def check_task_status(telegram_id: int, day: int, task_id: int) -> tuple[TaskStatus, str]:
    check_day = await check_calendar_day(day)

    answer = " - "
    status = TaskStatus.UNTOUCHED
    is_answered = (await student_answer_con.is_student_answer_to_task(telegram_id, task_id)).json
    if check_day == DayAvailability.AVAILABLE:
        if is_answered['isAnswered']:
            answer = is_answered['object']['studentAnswerText']
            status = TaskStatus.WAIT
        else:
            status = TaskStatus.UNTOUCHED
    if check_day == DayAvailability.PASSED:
        if is_answered['isAnswered']:
            answer = is_answered['object']['studentAnswerText']
            if is_answered['object']['correct']:
                status = TaskStatus.SOLVED
            else:
                status = TaskStatus.MISSED

    return status, answer


def commands_detector(command: BotCommandsEnum):
    def wrapper(call):
        async def inner(*args):
            message: aiogram.types.Message = args[0]
            log.i(commands_detector.__name__, f"Пользователь с ID {message.from_user.id} ({message.from_user.username}) вызвал команду {command.value}")
            await state_instance.state_manager.detect_command_call()
            await call(*args)
        return inner
    return wrapper

def check_user_registered(handler_type: HandlerType = HandlerType.MESSAGE):
    """Декоратор проверки наличия пользователя в базе данных"""

    def wrap(call):
        async def wrapper(*args):
            mes: aiogram.types.Message = args[0]
            controller = student_con
            chat_id = handler_type(mes)
            result: ServerResponse = await controller.get_student(telegram_id=mes.from_user.id)
            ban = (await controller.get_student(mes.from_user.id)).json.get('ban', False)
            if ban:
                await bot.send_message(chat_id=chat_id,
                                       text="⛔ Тебя отстранили от использования бота! Обратись в поддержку, если считаешь, что это ошибка")
            elif result.result.status == 404:
                log.w(check_user_registered.__name__,
                      f"Пользователя с Telegram ID {mes.from_user.id} нет в базе данных (404)")
                with open('system_images/auth_required.png', 'rb') as image:
                    await bot.send_photo(chat_id=chat_id,
                                         caption='❌ Чтобы пользоваться функционалом бота, тебе нужно зарегистрироваться как ученик школы № 2122.\n\n⚠️ Разработчики имеют право отстранить ученика от участия в событии, если будут указаны фальшивые данные при регистрации!',
                                         photo=image,
                                         reply_markup=RegButtonClient
                                         )
            elif result.result.status == 200:
                log.s(check_user_registered.__name__,
                      f'Пользователь с Telegram ID {mes.from_user.id} присутствует в базе данных (200)')
                await call(*args)
            else:
                log.e(check_user_registered.__name__,
                      f"При получении данных пользователя с Telegram ID {mes.from_user.id} сервер выдал ошибку {result.result.status}")
                await bot.send_photo(chat_id=chat_id,
                                     caption=f'❌ При попытке найти данные об ученике на сервере, произошла ошибка: HTTP {result.result.status}.',
                                     photo=InputFile(ContentManager.make_server_error_image(result.result.status)),
                                     reply_markup=TechSupportButtonClient
                                     )

        return wrapper

    return wrap


async def register_new_student(message: aiogram.types.Message, student: Student) -> ServerResponse:
    """Зарегистрировать нового ученика"""
    result: ServerResponse = await student_con.create_student(student)
    if result.result.status == 201:
        log.s(register_new_student.__name__,
              f"Успешно зарегистрирован новый ученик с Telegram ID {student.telegram_id}")
        await bot.send_message(chat_id=message.chat.id,
                               text=f'🗝️ Ты успешно зарегистрирован(-а) как <b>{fmt.quote_html(student.name)} {fmt.quote_html(student.lastname)} {student.class_number}{student.class_letter}</b>',
                               parse_mode='HTML')
    elif result.result.status == 400:
        log.e(register_new_student.__name__,
              f'Ученик {fmt.quote_html(student.name)} {fmt.quote_html(student.lastname)} {student.class_number}{student.class_letter} уже существует в базе данных.')
        with open('system_images/user_exists.png', 'rb') as image:
            await bot.send_photo(chat_id=message.chat.id,
                                 caption=f'❌ Ученик <b>{fmt.quote_html(student.name)} {fmt.quote_html(student.lastname)} {student.class_number}{student.class_letter} уже является пользователем данного бота.</b>',
                                 photo=image,
                                 parse_mode='HTML',
                                 reply_markup=TechSupportButtonClient
                                 )
    else:
        log.e(register_new_student.__name__,
              f"Что-то пошло не так при регистрации пользователя с Telegram ID {student.telegram_id}. HTTP статус: {result.result.status}")
        await bot.send_photo(chat_id=message.chat.id,
                             caption=f'❌ Что-то пошло не так при регистрации нового ученика. HTTP {result.result.status}',
                             photo=InputFile(ContentManager.make_server_error_image(result.result.status)),
                             reply_markup=TechSupportButtonClient
                             )

    return result
