import io
import os

from PIL import Image, ImageDraw, ImageFont

from mathweek.logger import log


class ContentManager:
    @staticmethod
    def init_directory(dir_name: str):
        """Создать директорию, если ее не существует"""
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
            log.s(ContentManager.init_directory.__name__, f'Успешно создана директория {dir_name}/')
            return
        log.i(ContentManager.init_directory.__name__, f'Директория {dir_name}/ уже существует')

    @staticmethod
    def make_server_error_image(http_response_status: int) -> Image:
        """Создать изображение, уведомляющее об ошибке сервера (с определенным http статус-кодом)"""
        image = Image.open('system_images/server_error_pattern.png')
        font = ImageFont.truetype('fonts/ru_Bebas.ttf', size=675)
        drawer = ImageDraw.Draw(image)
        drawer.text(
            (1845, 1000),
            str(http_response_status),
            font=font,
            fill='#7B00FF')
        buffer = io.BytesIO()
        image.save(buffer, format='png')
        buffer.seek(0)
        return buffer
