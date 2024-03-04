import asyncio
import enum
import os
import time
from threading import Thread

import schedule
import atexit
import pickle

from mathweek.logger import log
import modules.date_manager as dm

class StateType(enum.Enum):
    TEMPORARY = 'bot_temp_state.pickle'
    PERMANENT = 'bot_perm_state.pickle'

class StateManager:
    """Менеджер текущего состояния бота, который путем сериализации и десериализации позволяет сохранять текущие данные о боте и не потерять их в случае выключения"""

    def __init__(self):
        state = self.read_dump(StateType.TEMPORARY)
        if state['current_event_day'] == dm.DateManager.day():
            self.__current_event_day: int = state['current_event_day']
            self.__day_answers_count: int = state['day_answers_count']
            self.__day_tasks_assignations_count: int = state['day_tasks_assignation_count']
            self.__day_commands_count: int = state['day_commands_count']
            self.__day_server_requests_count: int = state['day_server_requests_count']
        elif state['current_event_day'] != dm.DateManager.day():
            self.__current_event_day: int = dm.DateManager.day()
            self.__day_answers_count: int = 0
            self.__day_tasks_assignations_count: int = 0
            self.__day_commands_count: int = 0
            self.__day_server_requests_count: int = 0

        perm_state = self.read_dump(StateType.PERMANENT)
        self.__dict_data: dict = perm_state['dict_data']
        self.__list_data: list = perm_state['list_data']

    @property
    def dict_data(self):
        return self.__dict_data

    @property
    def list_data(self):
        return self.__list_data

    @dict_data.setter
    def dict_data(self, value):
        self.__dict_data = value

    @list_data.setter
    def list_data(self, value):
        self.__list_data = value

    def set_dict_data(self, key, value):
        self.__dict_data[key] = value

    def append_list_data(self, value):
        self.__list_data.append(value)

    def del_dict_data(self, key):
        del self.__dict_data[key]

    def pop_list_data(self, index: int):
        return self.__list_data.pop(index)

    @staticmethod
    def primary_state_dump():
        """Первичный дамп состояния (делается после самого первого запуска боте перед созданием экземпляра класса StateManager)"""
        if not os.path.exists(StateType.PERMANENT.value):
            with open(StateType.PERMANENT.value, "wb") as pickle_dump:
                data = {
                    "dict_data": {},
                    "list_data": []
                }
                pickle.dump(data, pickle_dump)
            log.s(StateManager.primary_state_dump.__name__, f'Успешно создан первый дамп постоянного состояния бота [сериализация]')
        else:
            log.i(StateManager.primary_state_dump.__name__, f'Сохраненное постоянное состояние бота уже существует')

        if not os.path.exists(StateType.TEMPORARY.value):
            with open(StateType.TEMPORARY.value, "wb") as pickle_dump:
                data = {
                    "current_event_day": dm.DateManager.day(),
                    "day_answers_count": 0,
                    "day_tasks_assignation_count": 0,
                    "day_commands_count": 0,
                    "day_server_requests_count": 0
                }
                pickle.dump(data, pickle_dump)
            log.s(StateManager.primary_state_dump.__name__, f'Успешно создан первый дамп временного состояния бота [сериализация]')
        else:
            log.i(StateManager.primary_state_dump.__name__, f'Сохраненное временное состояние бота уже существует')

    def __reset_state(self):
        """Установить начальные данные в текущем временном состоянии и сериализовать их"""
        self.__current_event_day: int = dm.DateManager.day()
        self.__day_answers_count: int = 0
        self.__day_tasks_assignations_count: int = 0
        self.__day_commands_count: int = 0
        self.__day_server_requests_count: int = 0
        with open(StateType.TEMPORARY.value, "wb") as pickle_dump:
            data = {
                "current_event_day": dm.DateManager.day(),
                "day_answers_count": 0,
                "day_tasks_assignation_count": 0,
                "day_commands_count": 0,
                "day_server_requests_count": 0
            }
            pickle.dump(data, pickle_dump)
            log.i(StateManager.__reset_state.__name__, f'Состояние бота обнулено. [сериализация]')

    def __dump_state(self, state_type: StateType):
        """Сериализация текущего состояния"""
        with open(state_type.value, "wb") as pickle_dump:
            data = {
                "current_event_day": self.__current_event_day,
                "day_answers_count": self.__day_answers_count,
                "day_tasks_assignation_count": self.__day_tasks_assignations_count,
                "day_commands_count": self.__day_commands_count,
                "day_server_requests_count": self.__day_server_requests_count
            } if state_type == StateType.TEMPORARY else {
                "dict_data": self.dict_data,
                "list_data": self.list_data
            }
            pickle.dump(data, pickle_dump)
            log.i(StateManager.__dump_state.__name__, f'Сохранено последнее состояние бота [сериализация]')

    @classmethod
    def read_dump(cls, state_type: StateType, return_data: bool = True):
        """Получить последний дамп состояния бота, сохраненного в виде байтов"""
        with open(state_type.value, "rb") as bot_state:
            last_dump = pickle.load(bot_state)
            log.i(StateManager.read_dump.__name__,
                  f'Прочитан последний дамп состояния бота [десериализация]: {last_dump}')
            if return_data:
                return last_dump

    def current_temp_state_log(self):
        """Вывод данных текущего состояния"""
        log.i(self.current_temp_state_log.__name__,
              f"Количество ответов от учеников: {self.__day_answers_count}")
        log.i(self.current_temp_state_log.__name__,
              f"Количество выданных заданий ученикам: {self.__day_tasks_assignations_count}")
        log.i(self.current_temp_state_log.__name__,
              f"Количество вызванных команд: {self.__day_commands_count}")
        log.i(self.current_temp_state_log.__name__,
              f"Количество запросов на сервер: {self.__day_server_requests_count}")

    def pull_last_dump(self, state_type: StateType):
        """Установить в значения атрибутов экземпляра класса значения последнего дампа состояния"""
        state = self.read_dump(state_type)
        if state_type == StateType.TEMPORARY:
            self.__current_event_day: int = state['current_event_day']
            self.__day_answers_count: int = state['day_answers_count']
            self.__day_tasks_assignations_count: int = state['day_tasks_assignation_count']
            self.__day_commands_count: int = state['day_commands_count']
            self.__day_server_requests_count: int = state['day_server_requests_count']
        elif state_type == StateType.PERMANENT:
            self.__dict_data: dict = state['dict_data']
            self.__list_data: list = state['list_data']

    def __day_results_output(self):
        """Вывод данных за весь день (обычно в 00:00)"""
        log.i(self.__day_results_output.__name__,
              f"Итоги дня. Количество ответов от учеников: {self.__day_answers_count}")
        log.i(self.__day_results_output.__name__,
              f"Итоги дня. Количество выданных заданий ученикам: {self.__day_tasks_assignations_count}")
        log.i(self.__day_results_output.__name__,
              f"Итоги дня. Количество вызванных команд: {self.__day_commands_count}")
        log.i(self.__day_results_output.__name__,
              f"Итоги дня. Количество запросов на сервер: {self.__day_server_requests_count}")
        log.save_logs_to_file(f"day_result_{self.__current_event_day}", remove_existing=True)

    async def detect_answer(self):
        """Зафиксировать ответ от ученика"""
        log.i(self.detect_answer.__name__, 'Зафиксирован ответ от ученика')
        self.__day_answers_count += 1

    async def detect_task_assignation(self, count: int):
        """Зафиксировать выдачу заданий"""
        log.i(self.detect_task_assignation.__name__, f'Зафиксировано {count} выданных заданий')
        self.__day_tasks_assignations_count += count

    async def detect_command_call(self):
        """Зафиксировать вызов команды"""
        log.i(self.detect_command_call.__name__, 'Зафиксирован вызов команды')
        self.__day_commands_count += 1

    async def detect_server_request(self):
        """Зафиксировать запрос к серверу"""
        log.i(self.detect_server_request.__name__, 'Зафиксирован запрос к серверу')
        self.__day_server_requests_count += 1

    def _schedule_init(self):
        """Инициализация графиков, по которым будут выполнены: сброс состояния, вывод итоговых значений за день, чтение и сохранение состояния"""
        schedule.every().day.at("00:00").do(self.__reset_state)
        log.d(self.state_control_loop.__name__, "Задано действие каждый день в 00:00: обнуление состояния")
        schedule.every().day.at("20:00").do(self.__day_results_output)
        log.d(self.state_control_loop.__name__, "Задано действие каждый день в 20:00: вывод итогов дня")
        schedule.every().minute.do(lambda: self.read_dump(StateType.TEMPORARY, False))
        schedule.every().minute.do(lambda: self.read_dump(StateType.PERMANENT, False))
        schedule.every().minute.do(self.current_temp_state_log)
        schedule.every().hour.do(lambda: self.__dump_state(StateType.TEMPORARY))
        schedule.every().hour.do(lambda: self.__dump_state(StateType.PERMANENT))
        atexit.register(lambda: self.__dump_state(StateType.TEMPORARY))
        atexit.register(lambda: self.__dump_state(StateType.PERMANENT))
        while True:
            schedule.run_pending()
            time.sleep(1)

    async def state_control_loop(self):
        """Цикл, контролирующий работу состояния."""
        log.d(self.state_control_loop.__name__, "Задано действие при выключении: сохранение состояния")
        thread = Thread(target=self._schedule_init, args=(), daemon=True)  # <- Отдельный поток для работы графиков
        thread.start()
