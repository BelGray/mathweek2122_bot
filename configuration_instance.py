from modules import bot_config

config = bot_config.BotConfig()
server_url = config.server_url  # <- Адрес сервера
telegram_token = config.telegram_token  # <- Токен Telegram API
bot_mode = config.bot_mode   # <- Режим, в котором сейчас находится бот
