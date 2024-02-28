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


