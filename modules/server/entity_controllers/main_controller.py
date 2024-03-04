import aiohttp

import state_instance
from mathweek.logger import log
from modules.server.data.dataclasses import ServerResponse
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
            async def inner(*args, **kwargs):
                await state_instance.state_manager.detect_server_request()
                result: ServerResponse = await call(*args, **kwargs)
                log.i(f"{method.value['label']} * {call.__name__}",
                      f"Послан {method.value['label']} запрос на сервер. Статус: {result.result.status}.")
                return result

            return inner

        return wrapper
