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
    scrape_enasco,
    # ScrappersFunctionsMapping
)
from telegram_bot_utils import TelegramBot

telegram_bot = TelegramBot()

if __name__ == "__main__":
    import os

    os.system("cls || clear")

    # scrappers = ScrappersFunctionsMapping() # TODO
    # scrappers.start() # TODO

    # load existing items data
    existing_items_df = load_data()
    existing_items = list_existing_items(existing_items_df)

    telegram_bot.send_alert(f"Loaded {len(existing_items)} existing items.")
    telegram_bot.send_alert(f"Start scraping...")

    updated_items_df = existing_items_df.copy()
    now = updated_datetime()

    new_items_count = 0
    updated_items_count = 0

    ### 1st website:
    scraped_items = scrape_plaidonline()

    for item_data in scraped_items:
        if (item_title := item_data.get("item_title")) in existing_items:
            item_url = item_data.get("item_url")
            item_new_price = item_data.get("item_price")
            item_old_price = get_item_price(updated_items_df, item_title)

            if item_new_price != item_old_price:
                updated_items_count += 1
                update_item_price(updated_items_df, item_title, item_new_price)
                telegram_bot.send_price_update(
                    item_title, item_url, item_old_price, item_new_price
                )

        else:
            new_items_count += 1
            item_data.update(added_on=str(now))
            updated_items_df = pd.concat(
                [updated_items_df, pd.DataFrame([item_data], columns=DATA_COLUMNS),]
            )

    ### 2nd website:
    scraped_items = scrape_enasco()

    # report to telegram
    telegram_bot.send_new_items_added(new_items_count)
    telegram_bot.send_new_items_updated(updated_items_count)

    save_data(updated_items_df)
    # telegram_bot.send_alert("Done.")
