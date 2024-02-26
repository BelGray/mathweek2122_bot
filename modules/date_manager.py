import datetime


class DateManager:
    @staticmethod
    def day() -> int:
        """Получить текущий день в марте (если на момент вызова метода не март, то вертнется -1)"""
        date = datetime.datetime.now()
        return date.day if date.month == 3 else -1

    @staticmethod
    def time():
        """Получить текущее время (час, минуты)"""
        date = datetime.datetime.now()
        return date.hour, date.minute
