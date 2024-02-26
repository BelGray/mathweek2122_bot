
class UserList(list):
    """Список пользователей Telegram. Используется для учета пользователя ботом при выполнении команд"""

    async def add(self, telegram_id: int):
        """Добавить id, если его нет в списке"""
        self.append(telegram_id) if not self.is_involved(telegram_id) else ...

    def is_involved(self, telegram_id: int) -> bool:
        """Находится ли id пользователя в списке"""
        return True if telegram_id in self else False

    async def remove(self, telegram_id: int):
        """Удалить из списка id, если существует"""
        super().remove(telegram_id) if self.is_involved(telegram_id) else ...
