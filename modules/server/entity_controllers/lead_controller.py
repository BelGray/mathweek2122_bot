import aiohttp

from modules.server.data.dataclasses import ServerResponse
from modules.server.data.enums import HTTPMethods
from modules.server.entity_controllers.main_controller import ServerRequests
from modules.server.data.enums import Subjects


class LeadBoardController(ServerRequests):
    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_leaderboard_by_subject_and_class_number(self, subject: Subjects,
                                                          class_number: int) -> ServerResponse:
        """Получить таблицу лидеров учеников по предмету и параллели классов"""
        endpoint = f"leadBoard.getBySubjectAndClassNumber?classNumber={class_number}&subject={subject.value}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_leaderboard_by_subject_and_class_number_and_class_letter(self, subject: Subjects,
                                                                           class_number: int, class_letter: str) -> ServerResponse:
        """Получить таблицу лидеров учеников определенного класса по предмету"""
        endpoint = f"leadBoard.getBySubjectAndClassNumberAndClassLetter?classNumber={class_number}&classLetter={class_letter}&subject={subject.value}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_leaderboard_by_class_number(self, class_number: int) -> ServerResponse:
        """Получить таблицу лидеров по баллам параллели классов"""
        endpoint = f"leadBoard.getByClassNumber?classNumber={class_number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_leaderboard_by_class_number_and_class_letter(self, class_number: int, class_letter: str) -> ServerResponse:
        """Получить таблицу лидеров по баллам определенного класса"""
        endpoint = f"leadBoard.getByClassNumberAndClassLetter?classNumber={class_number}&classLetter={class_letter}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))
