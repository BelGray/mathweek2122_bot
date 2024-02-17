# -*- coding: utf-8 -*-
from aiogram import types

class Admin:
    __admins = (1066757578, 995631274, 1498070696, 5255516914)

    @staticmethod
    def is_admin(user_id: int):
        '''Есть ли ID пользователя в списке админов'''
        return True if user_id in Admin.__admins else False

    @staticmethod
    def test(test_mode: bool):
        '''Декоратор тестирования функционала бота. Команда становится доступной только админам в режиме тестирования'''
        def wrapper(call):
            async def inner(message: types.Message):
                if test_mode:
                    if Admin.is_admin(message.from_user.id):
                        await call(message)
                else:
                    await call(message)
            return inner
        return wrapper
