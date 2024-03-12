import datetime
import time
from threading import Thread

import schedule
from mathweek.logger import log
from modules.server.requests_instance import task_con, student_answer_con


class DateManager:
    """Менеджер дат"""

    weekend_days = ()
    event_days = (11, 12, 13, 14, 15, 16, 17)
    send_results_day = 18

    days_text = {
        -1: "Событие скоро начнется" if datetime.datetime.now() < datetime.datetime(2024, 3, event_days[0]) else "Событие уже завершено",
        11: "День 1/7",
        12: "День 2/7",
        13: "День 3/7",
        14: "День 4/7",
        15: "День 5/7",
        16: "День 6/7",
        17: "День 7/7 (Завтра событие завершится)"
    }

    @staticmethod
    def day() -> int:
        """Получить текущий день в марте (если на момент вызова метода не март, то вертнется -1)"""
        date = datetime.datetime.now()
        return date.day if date.month == 3 and DateManager.event_days[0] <= date.day <= DateManager.event_days[-1] else -1

    @staticmethod
    def time():
        """Получить текущее время (час, минуты)"""
        date = datetime.datetime.now()
        return date.hour, date.minute

    @staticmethod
    async def __tasks_assignation():
        if DateManager.day() in DateManager.event_days:
            for klass in range(5, 12):
                day = DateManager.day()
                day_tasks = (await task_con.get_task_by_class_and_date(klass, day)).json
                for task in day_tasks:
                    if not task['quiz']:
                        await student_answer_con.assign_task_to_students_by_class(klass, task['id'])


    @staticmethod
    def _schedule_init():
        """Инициализация графиков"""
        schedule.every().day.at("00:00").do(DateManager.__tasks_assignation)
        log.d(DateManager._schedule_init.__name__, "Задано действие каждый день в 00:00: выдача заданий")
        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    async def set_event_time_control_loop():
        """Цикл ежедневной выдачи заданий ученикам"""
        thread = Thread(target=DateManager._schedule_init, args=(), daemon=True)  # <- Отдельный поток для работы графиков
        thread.start()
        # todo: Дописать цикл-контролер времени. (получение заданий каждый день)