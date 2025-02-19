import atexit
import enum
import os.path
import pickle
from BGLogger import BGC


class BotConfigError(Exception):
    """Ошибка при настройке конфигурации бота"""
    pass


class BotMode(enum.Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1
    TESTING = 2

class BotConfigKeys(enum.Enum):
    TELEGRAM_API_TOKEN = "telegram_api_token"
    SERVER_URL = "server_url"


class BotConfig:
    """Сохранение конфигурации бота для быстрого перезапуска. (Сериализация и десериализация данных)"""

    def __init__(self):

        self.__bytes_file: str = 'bot_config.pickle'

        define_mode = BGC.scan(
            'Режим бота\nt - тестирование (функционал доступен только администраторам)\nd - разработка (функционал доступен только администраторам, в консоли корректно отображаются ошибки)\np - продакшн (функционал бота полностью открыт для пользователей)\n\n/> ',
            label_color=BGC.Color.PURPLE
        )
        if define_mode.lower() == 't':
            self.__mode: BotMode = BotMode.TESTING
        elif define_mode.lower() == 'd':
            self.__mode: BotMode = BotMode.DEVELOPMENT
        elif define_mode.lower() == 'p':
            self.__mode: BotMode = BotMode.PRODUCTION
        else:
            self.__mode: BotMode = None
            raise BotConfigError(f'Введен неверный параметр: {define_mode}!')

        if not os.path.exists(self.__bytes_file):
            with open(self.__bytes_file, 'wb') as file:
                serializable = {
                    BotConfigKeys.TELEGRAM_API_TOKEN.value: None,
                    BotConfigKeys.SERVER_URL.value: None
                }
                pickle.dump(serializable, file)

        with open(self.__bytes_file, 'rb') as bytes_file:
            data = pickle.load(bytes_file)
            self.__telegram_token = data[BotConfigKeys.TELEGRAM_API_TOKEN.value]
            self.__server = data[BotConfigKeys.SERVER_URL.value]

        if self.__telegram_token is not None and self.__server is not None:
            reset = BGC.scan(
                'Сбросить текущую конфигурацию бота (Telegram API токен, base url) ?\nY - Да, настроить всё заново\n<Enter> - Нет, запустить бота с текущей конфигурацией\n\n/> ',
                label_color=BGC.Color.MUSTARD
            )
            if reset.upper() == 'Y':
                self.__telegram_token = self.set_token()
                self.__server = self.set_server_url()
            else:
                pass
        else:
            self.__telegram_token = self.get_token()
            self.__server = self.get_server_url()
        atexit.register(self.__dump_config)

    @property
    def bot_mode(self):
        return self.__mode

    @property
    def telegram_token(self):
        return self.__telegram_token

    @property
    def server_url(self):
        return self.__server

    def __dump_config(self):
        with open(self.__bytes_file, 'wb') as file:
            serializable = {
                BotConfigKeys.TELEGRAM_API_TOKEN.value: self.__telegram_token,
                BotConfigKeys.SERVER_URL.value: self.__server
            }
            pickle.dump(serializable, file)

    def __read_config(self):
        with open(self.__bytes_file, 'rb') as bytes_file:
            data = pickle.load(bytes_file)
            return data

    def get_token(self) -> str:
        token = self.__read_config()[BotConfigKeys.TELEGRAM_API_TOKEN.value]
        if token is not None:
            return token
        new_token = BGC.scan('Telegram API токен /> ', label_color=BGC.Color.CRIMSON)
        return new_token

    def get_server_url(self) -> str:
        url = self.__read_config()[BotConfigKeys.SERVER_URL.value]
        if url is not None:
            return url
        new_url = BGC.scan('Base URL (или localhost) /> ', label_color=BGC.Color.CRIMSON)
        return new_url if new_url != "localhost" else "http://localhost:8080/"

    @classmethod
    def set_token(cls) -> str:
        new_token = BGC.scan('Telegram API токен /> ', label_color=BGC.Color.CRIMSON)
        return new_token

    @classmethod
    def set_server_url(cls) -> str:
        new_url = BGC.scan('Base URL (или localhost) /> ', label_color=BGC.Color.CRIMSON)
        return new_url if new_url != "localhost" else "http://localhost:8080/"
