import aiohttp

from modules.server.data.dataclasses import ServerResponse
from modules.server.data.enums import HTTPMethods
from modules.server.entity_controllers.main_controller import ServerRequests


class StudentAnswerController(ServerRequests):

    @ServerRequests.request_log(HTTPMethods.POST)
    async def set_student_easy_answer(self, student_answer_id: int, student_telegram_id: int,
                                      task_id: int) -> ServerResponse:
        """Присвоить вариант ответа ученика заданию"""

        endpoint = f"answer.setStudentEasyAnswer?studentTelegramId={student_telegram_id}&taskId={task_id}&studentAnswerId={student_answer_id}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.POST)
    async def set_student_custom_answer(self, custom_student_answer: str, student_telegram_id: int,
                                        task_id: int) -> ServerResponse:
        """Присвоить свой ответ ученика заданию"""

        endpoint = f"answer.setStudentCustomAnswer?studentTelegramId={student_telegram_id}&taskId={task_id}&CustomStudentAnswer={custom_student_answer}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.POST)
    async def assign_task_to_student(self, student_telegram_id: int,
                                     task_id: int) -> ServerResponse:
        """Присвоить задание ученику"""

        endpoint = f"answer.assignToStudent?studentTelegramId={student_telegram_id}&taskId={task_id}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.POST)
    async def assign_task_to_students_by_class(self, class_number: int,
                                               task_id: int) -> ServerResponse:
        """Присвоить задание ученикам параллели классов"""

        endpoint = f"answer.assignToStudentsByClassNumber?taskId={task_id}&classNumber={class_number}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_student_answers_by_telegram_id(self, student_telegram_id: int) -> ServerResponse:
        """Получить ответы ученика по ID в Telegram"""
        endpoint = f"answer.getStudentAnswersByTelegramId?studentTelegramId={student_telegram_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_count_task_or_quiz(self, student_telegram_id: int, is_quiz: bool) -> ServerResponse:
        """Получить количество заданий или викторин"""
        endpoint = f"answer.getCountTaskOrQuiz?studentTelegramId={student_telegram_id}&isQuiz={is_quiz}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def is_task_assigned(self, student_telegram_id: int, task_id: int) -> ServerResponse:
        """Выдано ли ученику задание"""
        endpoint = f"answer.isTaskAssigned?studentTelegramId={student_telegram_id}&taskId={task_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def is_student_answer_to_task(self, student_telegram_id: int, task_id: int) -> ServerResponse:
        """Ответил ли ученик на задание"""
        endpoint = f"answer.isStudentAnswerToTask?studentTelegramId={student_telegram_id}&taskId={task_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))