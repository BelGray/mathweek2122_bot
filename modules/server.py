import enum
import inspect

from mathweek.logger import log
import aiohttp


# todo: Дописать ServerRequests и контроллеры

class HTTPMethods(enum.Enum):
    POST = {
        'label': 'POST',
        'method': aiohttp.ClientSession.post
    }
    GET = {
        'label': 'GET',
        'method': aiohttp.ClientSession.get
    }
    DELETE = {
        'label': 'DELETE',
        'method': aiohttp.ClientSession.delete
    }
    PUT = {
        'label': 'PUT',
        'method': aiohttp.ClientSession.put
    }

class ServerRequests:
    def __init__(self, url: str):
        self.__url = url

    @staticmethod
    def request_log(method: HTTPMethods):
        def wrapper(call):
            def inner(*args, **kwargs):
                log.i(f"{method.value['label']} * {inspect.currentframe().f_back.f_code.co_name}", f"Послан {method.value['label']} запрос. Данные: {kwargs}")
                call(*args, **kwargs)
            return inner
        return wrapper


class TaskController(ServerRequests):
    ...