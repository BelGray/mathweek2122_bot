import os


class ContentManager:
    @staticmethod
    def init_content_path():
        if not os.path.exists('content'):
            os.mkdir('content')
