import enum
import aiohttp


class DifficultyLevels(enum.Enum):
    EASY = 1
    MIDDLE = 2
    HARD = 3
    ADVANCED = 4

    WRONG = None


class TaskTypes(enum.Enum):
    EXPRESSION = "EXPRESSION"
    WORD_TASK = "WORD_TASK"


class Subjects(enum.Enum):
    MATH = "MATH"
    PHYS = "PHYS"
    IT = "IT"


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