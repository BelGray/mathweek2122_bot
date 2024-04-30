import asyncio
from typing import Union

import aiohttp.client_exceptions

from modules.server.data.dataclasses import ServerResponse
from modules.server.data.enums import Subjects
from modules.server.requests_instance import task_con


class RandomStuffGetter:
    """Механизм для гарантированного получения случайного материала"""
    @staticmethod
    async def get(subject: Subjects, interval: float = 0.25) -> Union[ServerResponse, None]:
        while True:
            try:
                material = await task_con.get_random_task(subject)
                if material.result.status == 200:
                    article = material.json['article']
                    quiz = material.json['quiz']
                    tasks = material.json['task']
                    if tasks[0]['text'].lower() == 'none' or tasks[1]['text'].lower() == 'none' or quiz[0][
                        'text'].lower() == 'none' or article[
                        'text'].lower() == 'none':
                        await asyncio.sleep(interval)
                        continue
                    return material
                await asyncio.sleep(interval)
            except aiohttp.client_exceptions.ClientConnectionError:
                return None

