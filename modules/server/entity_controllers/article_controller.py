import aiohttp

from modules.server.data.dataclasses import Article
from modules.server.data.enums import HTTPMethods, Subjects
from modules.server.entity_controllers.main_controller import ServerRequests


class ArticleController(ServerRequests):
    @ServerRequests.request_log(HTTPMethods.POST)
    async def create_article(self, article: Article) -> aiohttp.ClientResponse:
        """Создать статью"""

        endpoint = "article.create"

        data = {
            "id": 0,
            "classNumber": article.class_number,
            "day": article.day,
            "subject": article.subject.value,
            "text": article.text
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=super().url + endpoint, json=data) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_article_by_subject(self, subject: Subjects) -> aiohttp.ClientResponse:
        """Получить статью по предмету"""
        endpoint = f"article.getBySubject?subject={subject.value}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_article_by_subject_and_day(self, subject: Subjects, day: int) -> aiohttp.ClientResponse:
        """Получить статью по предмету и дню разблокировки"""
        endpoint = f"article.getBySubjectAndDay?subject={subject.value}&day={day}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_article_by_subject_and_day_and_class(self, subject: Subjects, day: int, class_number: int) -> aiohttp.ClientResponse:
        """Получить статью по предмету, дню разблокировки и парарллели классов"""
        endpoint = f"article.getBySubjectAndDayAndClass?subject={subject.value}&day={day}&classNumber={class_number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_article_by_subject_and_class(self, subject: Subjects, class_number: int) -> aiohttp.ClientResponse:
        """Получить статью по предмету и параллели классов"""
        endpoint = f"article.getBySubjectAndClass?subject={subject.value}&classNumber={class_number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_article_by_day(self, day: int) -> aiohttp.ClientResponse:
        """Получить статью по дню разблокировки"""
        endpoint = f"article.getByDay?day={day}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response

    @ServerRequests.request_log(HTTPMethods.GET)
    async def get_article_by_class(self, class_number: int) -> aiohttp.ClientResponse:
        """Получить статью по параллели классов"""
        endpoint = f"article.getByClass?classNumber={class_number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=super().url + endpoint) as response:
                return response