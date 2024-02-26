import dataclasses


@dataclasses.dataclass
class User:
    name: str
    lastname: str
    class_number: int
    class_letter: str


class UserRegData(dict):
    """Словарь пользователей Telegram. Используется для учета пользователя ботом при выполнении команд"""

    async def set(self, telegram_id: int, user: User):
        """Добавить id, если его нет в словаре"""
        if not self.is_involved(telegram_id):
            self[telegram_id] = user

    def is_involved(self, telegram_id: int) -> bool:
        """Находится ли id пользователя в словаре"""
        return True if telegram_id in self else False

    async def remove(self, telegram_id: int):
        """Удалить из словаря id, если существует"""
        if self.is_involved(telegram_id):
            del self[telegram_id]
