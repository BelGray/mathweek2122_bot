from typing import Union

import aiohttp

from modules.server.data.dataclasses import Task
from modules.server.data.enums import HTTPMethods, DifficultyLevels, Subjects
from modules.server.entity_controllers.main_controller import ServerRequests


class TaskController(ServerRequests):

    @ServerRequests.request_log(HTTPMethods.POST)
    async def create_task(self, task: Task) -> aiohttp.ClientResponse:
        """Создать задание"""
        endpoint = "task.create"

        task_answers = [{"id": answer.id, "text": answer.text, "isCorrect": answer.is_correct} for answer in
                        task.answers]

        data = {
            "id": 0,
            "classNumber": task.class_number,
            "day": task.day,
            "subject": task.subject.value,
            "difficultyLevel": task.difficulty_level,
            "type": task.type.value,
            "text": task.text,
            "content": task.content,
            "answers": task_answers,
            "quiz": task.quiz
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint, data=data) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_task(self, task_id: int) -> aiohttp.ClientResponse:
        """Получить задание"""
        endpoint = f"task.get?taskId={task_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_task_by_class_and_date(self, class_number: int, day: int) -> aiohttp.ClientResponse:
        """Получить задание по номеру класса и дню разблокировки"""
        endpoint = f"task.getByClassAndDate?classNumber={class_number}&day={day}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_task_by_class_and_date_and_difficulty_and_subject(self, class_number: int, day: int,
                                                                    difficulty_level: Union[DifficultyLevels, int],
                                                                    subject: Subjects) -> aiohttp.ClientResponse:
        """Получить задание по номеру класса, дню разблокировки, уровню сложности, предмету"""
        endpoint = f"task.getByClassAndDateAndDifficultyAndSubject?classNumber={class_number}&day={day}&difficultyLevel={difficulty_level.value if isinstance(difficulty_level, DifficultyLevels) else difficulty_level}&subject={subject.value}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response