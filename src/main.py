"""
Main logic
"""
import pandas as pd

from helpers import (
    load_data,
    save_data,
    list_existing_items,
    get_item_price,
    updated_datetime,
    update_item_price,
    DATA_COLUMNS,
)

from scrappers import (
    scrape_plaidonline,
    # ScrappersFunctionsMapping
)
from telegram_bot_utils import TelegramBot

telegram_bot = TelegramBot()

if __name__ == "__main__":
    # scrappers = ScrappersFunctionsMapping() # TODO
    # scrappers.start() # TODO
    # load existing items data
    existing_items_df = load_data()
    existing_items = list_existing_items(existing_items_df)

    telegram_bot.send_alert(f"Loaded {len(existing_items)} existing items.")
    telegram_bot.send_alert(f"Start scraping...")

    updated_items_df = existing_items_df.copy()
    now = updated_datetime()
    count = 0
    # 1st website:
    scaped_items = scrape_plaidonline()

    for item_data in scaped_items:
        if (item_title := item_data.get("item_title")) in existing_items:
            item_url = item_data.get("item_url")
            item_new_price = item_data.get("item_price")
            item_old_price = get_item_price(item_title)

            update_item_price(updated_items_df, item_title, item_new_price)
            telegram_bot.send_price_update(
                item_title, item_url, item_old_price, item_new_price
            )

        else:
            count += 1
            updated_items_df = pd.concat(
                [updated_items_df, pd.DataFrame([item_data], columns=DATA_COLUMNS)]
            )

    telegram_bot.send_new_items_added(count)
    updated_items_df["updated_on"] = updated_items_df["updated_on"].apply(
        lambda _: updated_datetime()
    )
    save_data(updated_items_df)
    telegram_bot.send_alert("Done.")
