import aiohttp
import json
from modules.server.data.dataclasses import Student
from modules.server.data.enums import HTTPMethods
from modules.server.entity_controllers.main_controller import ServerRequests


class StudentController(ServerRequests):
    @ServerRequests.request_log(HTTPMethods.POST)
    async def create_student(self, student: Student) -> aiohttp.ClientResponse:
        """Создать ученика"""

        endpoint = "student.create"

        data = {
            "id": 0,
            "name": student.name,
            "lastName": student.lastname,
            "telegramId": student.telegram_id,
            "classNumber": student.class_number,
            "classLetter": student.class_letter
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint, json=data) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_student(self, telegram_id: int) -> aiohttp.ClientResponse:
        """Получить ученика"""
        endpoint = f"student.get?telegramId={telegram_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_all_students_by_class(self, class_number: int) -> aiohttp.ClientResponse:
        """Получить всех учеников параллели классов"""
        endpoint = f"student.getAllByClassNumber?classNumber={class_number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.DELETE)
    async def delete_student(self, telegram_id: int) -> aiohttp.ClientResponse:
        """Удалить ученика"""
        endpoint = f"student.deleteByTelegramId?telegramId={telegram_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response
