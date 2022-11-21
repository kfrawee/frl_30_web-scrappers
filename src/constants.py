"""
CONSTANT VARIABLES:

TO SETUP TELEGRAM BOT: 
1. Create a new chat group.
2. Add the following bots to the chat.
    - TELEGRAM_BOT_API_KEY: Message (@BotFather). Create your Bot, 
        and get your Bot API key by creating a bot on Telegram .
    - CHAT_ID: Add (@RawDataBot) to your group and type: "/start" to get the chat id. 
        REF: https://www.alphr.com/find-chat-id-telegram/

DATA_DIR: The directory where the data file will be stored.
DATA_FILE_NAME: The name of the data file.
DATA_COLUMNS: Data columns names.
PAGES_SLEEP_INTERVAL: The number of seconds to sleep between requests (between pages).
SEND_ALL_UPDATES: Send notifications for both, decreased and increased prices. `False` to send only decreased prices.
SEND_NEW_ITEMS: Either to send notifications for newly added items or not.
"""

TELEGRAM_BOT_API_KEY = "5280766845:AAEnPZxjpBne5Dxl6x-U121VGvMDuOR4H4g"
CHAT_ID = -845543341
DATA_DIR = "data"
DATA_FILE_NAME = "data.csv"
DATA_COLUMNS = ["item_title", "item_price", "item_url", "added_on", "updated_on"]
PAGES_SLEEP_INTERVAL = 0.5
SEND_ALL_UPDATES = False
SEND_NEW_ITEMS = True
