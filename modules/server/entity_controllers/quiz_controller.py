import aiohttp

from modules.server.data.dataclasses import ServerResponse
from modules.server.data.enums import HTTPMethods, Subjects
from modules.server.entity_controllers.main_controller import ServerRequests


class QuizController(ServerRequests):

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_quiz_by_subject(self, subject: Subjects) -> ServerResponse:
        """Получить викторину по предмету"""
        endpoint = f"quiz.getBySubject?subject={subject.value}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_quiz_by_subject_and_class_and_day(self, subject: Subjects, class_number: int,
                                                    day: int) -> ServerResponse:
        """Получить викторину по предмету, параллели классов и дню разблокировки"""
        endpoint = f"quiz.getBySubjectAndClassNumberAndDay?subject={subject.value}&classNumber={class_number}&day={day}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_quiz_by_day(self, day: int) -> ServerResponse:
        """Получить викторину по дню разблокировки"""
        endpoint = f"quiz.getByDay?day={day}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_quiz_by_class(self, class_number: int) -> ServerResponse:
        """Получить викторину по параллели классов"""
        endpoint = f"quiz.getByClassNumber?classNumber={class_number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))
