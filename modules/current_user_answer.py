from typing import Literal


class LastUserAnswer:
    """Последний ответивший пользователь"""

    name: str = None
    lastname: str = None
    class_number: int = None
    class_letter: str = None
    subject: Literal["math", "phys", "it"] = None

    @staticmethod
    async def set(name: str, lastname: str, class_number: int, class_letter: str,
                  subject: Literal["math", "phys", "it"]):
        """Установить значения данных пользователя пользователя"""
        LastUserAnswer.name = name
        LastUserAnswer.lastname = lastname
        LastUserAnswer.class_number = class_number
        LastUserAnswer.class_letter = class_letter
        LastUserAnswer.subject = subject

    @staticmethod
    def is_none() -> bool:
        """Является ли пользователь валидным"""
        this = LastUserAnswer
        return True if this.name is None or this.lastname is None or this.class_number is None or this.class_letter is None or this.subject is None else False

    @staticmethod
    async def reset():
        """Сбросить значения последнего пользователя"""
        LastUserAnswer.name = None
        LastUserAnswer.lastname = None
        LastUserAnswer.class_number = None
        LastUserAnswer.class_letter = None
        LastUserAnswer.subject = None
