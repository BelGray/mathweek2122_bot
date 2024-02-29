import datetime


class DateManager:
    """Менеджер дат"""

    weekend_days = (8, 9, 10)
    event_days = (4, 5, 6, 7, 11, 12, 13)
    send_results_day = 14

    @staticmethod
    def day() -> int:
        """Получить текущий день в марте (если на момент вызова метода не март, то вертнется -1)"""
        date = datetime.datetime.now()
        return date.day if date.month == 3 and 4 <= date.day <= 13 else -1

    @staticmethod
    def time():
        """Получить текущее время (час, минуты)"""
        date = datetime.datetime.now()
        return date.hour, date.minute

    @staticmethod
    async def set_event_time_control_loop():
        ...
        # todo: Дописать цикл-контролер времени. (получение заданий каждый день)