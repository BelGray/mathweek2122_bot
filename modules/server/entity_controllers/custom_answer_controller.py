import aiohttp

from modules.server.data.enums import HTTPMethods
from modules.server.entity_controllers.main_controller import ServerRequests


class CustomAnswerController(ServerRequests):

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_custom_answers_by_task_id(self, task_id: int) -> aiohttp.ClientResponse:
        """Получить свои ответы учеников на задание"""
        endpoint = f"customAnswers.getByTaskId?taskId={task_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_custom_answers_by_student_telegram_id(self, student_telegram_id: int) -> aiohttp.ClientResponse:
        """Получить свои ответы ученика на задания"""
        endpoint = f"customAnswers.getByStudentTelegramId?telegramId={student_telegram_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response