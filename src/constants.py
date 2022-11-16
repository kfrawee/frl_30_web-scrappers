"""
Create a new chat group.
Add the following bots to the chat.
Constant variables.
    - TELEGRAM_BOT_API_KEY: Message (@BotFather). Create your Bot, 
        and get your Bot API key by creating a bot on Telegram .
    - CHAT_ID: Add (@RawDataBot) to your group and type: "/start" to get the chat id. 
        REF: https://www.alphr.com/find-chat-id-telegram/
"""

TELEGRAM_BOT_API_KEY = "5280766845:AAEnPZxjpBne5Dxl6x-U121VGvMDuOR4H4g"
CHAT_ID = -845543341
DATA_DIR = "data"
DATA_FILE_NAME = "data.csv"
DATA_COLUMNS = ["item_title", "item_price", "item_url", "added_on", "updated_on"]
PAGES_SLEEP_INTERVAL = 0.5
