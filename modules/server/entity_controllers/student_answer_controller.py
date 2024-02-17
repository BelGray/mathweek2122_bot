import aiohttp

from modules.server.data.enums import HTTPMethods
from modules.server.entity_controllers.main_controller import ServerRequests


class StudentAnswerController(ServerRequests):

    # todo: Дописать метод для указания задания всем ученикам класса. POST (taskID, classNumber)

    @ServerRequests.request_log(HTTPMethods.POST)
    async def set_student_answer(self, answer_id: int, points: int, student_telegram_id: int, task_id: int) -> aiohttp.ClientResponse:
        """Присвоить ответ ученика заданию"""

        endpoint = f"answer.setStudentAnswer?answerId={answer_id}&points={points}&studentTelegramId={student_telegram_id}&taskId={task_id}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.POST)
    async def assign_task_to_student(self, student_telegram_id: int,
                                 task_id: int) -> aiohttp.ClientResponse:
        """Присвоить задание ученику"""

        endpoint = f"answer.assignToStudent?studentTelegramId={student_telegram_id}&taskId={task_id}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_student_answers_by_telegram_id(self, student_telegram_id: int) -> aiohttp.ClientResponse:
        """Получить ответы ученика по ID в Telegram"""
        endpoint = f"answer.getStudentAnswersByTelegramId?studentTelegramId={student_telegram_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_count_task_or_quiz(self, student_telegram_id: int, is_quiz: bool) -> aiohttp.ClientResponse:
        """Получить количество заданий или викторин"""
        endpoint = f"answer.getCountTaskOrQuiz?studentTelegramId={student_telegram_id}&isQuiz={is_quiz}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response