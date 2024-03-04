from typing import Coroutine

import aiohttp

import dataclasses

from modules.server.data.enums import TaskTypes, Subjects

# буквы классов на момент 2023-2024 годов
student_class_letters = {
    5: ("А", "В", "Г", "Д", "И", "К", "Л", "Т"),
    6: ("А", "В", "Е", "Д", "И", "К", "Т"),
    7: ("А", "Д", "И", "К", "Л", "Т"),
    8: ("А", "Б", "Г", "И", "К", "Т"),
    9: ("А", "Б", "И", "К", "Т"),
    10: ("А", "К"),
    11: ("К",)
}

subject_symbols = {
    'math': '🔢',
    'phys': '⚛️',
    'it': '🌐'
}

days_difficulty_levels = {
    4: 1,
    5: 1,
    6: 2,
    7: 2,
    11: 3,
    12: 3,
    13: 4
}

student_class_subjects = {
    5: ((Subjects.MATH, f"{subject_symbols['math']} Математика"), (Subjects.IT, f"{subject_symbols['it']} Информатика")),
    6: ((Subjects.MATH, f"{subject_symbols['math']} Математика"), (Subjects.IT, f"{subject_symbols['it']} Информатика")),
    7: ((Subjects.MATH, f"{subject_symbols['math']} Математика"), (Subjects.IT, f"{subject_symbols['it']} Информатика"), (Subjects.PHYS, f"{subject_symbols['phys']} Физика")),
    8: ((Subjects.MATH, f"{subject_symbols['math']} Математика"), (Subjects.IT, f"{subject_symbols['it']} Информатика"), (Subjects.PHYS, f"{subject_symbols['phys']} Физика")),
    9: ((Subjects.MATH, f"{subject_symbols['math']} Математика"), (Subjects.IT, f"{subject_symbols['it']} Информатика"), (Subjects.PHYS, f"{subject_symbols['phys']} Физика")),
    10: ((Subjects.MATH, f"{subject_symbols['math']} Математика"), (Subjects.IT, f"{subject_symbols['it']} Информатика"), (Subjects.PHYS, f"{subject_symbols['phys']} Физика")),
    11: ((Subjects.MATH, f"{subject_symbols['math']} Математика"), (Subjects.IT, f"{subject_symbols['it']} Информатика"), (Subjects.PHYS, f"{subject_symbols['phys']} Физика")),
}

tasks_levels = {
    1: {
        'label': 'Базовый уровень',
        'points': 1
    },
    2: {
        'label': 'Средний уровень',
        'points': 2
    },
    3: {
        'label': 'Сложный уровень',
        'points': 3
    },
    4: {
        'label': 'Углубленный уровень',
        'points': 7
    }
}

@dataclasses.dataclass
class ServerResponse:
    result: aiohttp.ClientResponse
    json: dict
    text: str

@dataclasses.dataclass
class TaskAnswer:
    id: int
    text: str
    is_correct: bool


@dataclasses.dataclass
class Task:
    class_number: int
    day: int
    subject: Subjects
    difficulty_level: int
    type: TaskTypes
    text: str
    content: str
    answers: list[TaskAnswer, ...]
    quiz: bool


@dataclasses.dataclass
class Student:
    name: str
    lastname: str
    telegram_id: int
    class_number: int
    class_letter: str


@dataclasses.dataclass
class Article:
    class_number: int
    day: int
    subject: Subjects
    text: str


