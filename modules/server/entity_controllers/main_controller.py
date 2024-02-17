import functools
import inspect

import aiohttp

from mathweek.logger import log
from modules.server.data.enums import HTTPMethods


class ServerRequests:
    def __init__(self, url: str = "http://localhost:8080/"):
        self.__url = url

    @property
    def url(self):
        return self.__url

    @staticmethod
    def request_log(method: HTTPMethods):
        """Декоратор для сообщения о вызове асинхронных функций отправки HTTP запросов"""

        def wrapper(call):
            @functools.wraps(call)
            async def inner(*args, **kwargs):
                result: aiohttp.ClientResponse = await call(*args, **kwargs)
                log.i(f"{method.value['label']} * {call.__name__}",
                      f"Послан {method.value['label']} запрос на сервер. Статус: {result.status}.")

            return inner

        return wrapper
