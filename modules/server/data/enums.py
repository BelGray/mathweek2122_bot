import enum
import aiohttp


class HandlerType(enum.Enum):
    MESSAGE = lambda message: message['chat']['id']
    CALLBACK = lambda message: message['message']['chat']['id']


class DifficultyLevels(enum.Enum):
    EASY = 1
    MIDDLE = 2
    HARD = 3
    ADVANCED = 4

    WRONG = None


class TaskTypes(enum.Enum):
    EXPRESSION = "EXPRESSION"
    WORD_TASK = "WORD_TASK"


class DayAvailability(enum.Enum):
    UNAVAILABLE = "🔒"
    AVAILABLE = "🔑"
    PASSED = "☑️"


class TaskStatus(enum.Enum):
    SOLVED = "✅"
    MISSED = "❌"
    UNTOUCHED = "🆕"
    WAIT = "⏳"


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
