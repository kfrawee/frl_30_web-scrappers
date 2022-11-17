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
    get_elapsed_time,
)

from scrappers import Scrapper
from constants import DATA_COLUMNS
from telegram_bot_utils import TelegramBot

telegram_bot = TelegramBot()

if __name__ == "__main__":
    import os

    os.system("cls || clear")

    # load existing items data
    existing_items_df = load_data()
    existing_items = list_existing_items(existing_items_df)
    telegram_bot.send_alert(f"Loaded {len(existing_items)} existing items.")

    updated_items_df = existing_items_df.copy()
    now = updated_datetime()
    scraped_items = list()

    telegram_bot.send_alert(f"Start scraping...")

    ### SCRAPPERS
    # comment a line to enable/disable/update a certain website
    scrappers = Scrapper()
    ### 1st website:
    # scraped_items.extend(scrappers.scrape_plaidonline()) # ~17 sec

    ### 2nd website:
    # scraped_items.extend(scrappers.scrape_enasco())  # ~128 sec

    ### 3rd website:
    # scraped_items.extend(scrappers.scrape_nordstromrack())  # ~522.68 sec

    ### 4th website:
    # scraped_items.extend(scrappers.scrape_altomusic())  # ~ 74 - 106 sec

    ### 5th website:
    # scraped_items.extend(scrappers.scrape_muscleandstrength()) # ~ 20 sec

    ### 6th website:
    # scraped_items.extend(scrappers.scrape_camerareadycosmetics())  # ~ 9 sec

    ### 7th website:
    # scraped_items.extend(scrappers.scrape_officesupply()) # ~ 4 sec

    ### 8th website:
    # scraped_items.extend(scrappers.scrape_gamestop())  # ~ 1800 sec

    ### 9th website:
    # scraped_items.extend(scrappers.scrape_scheels())  # ~ 1800 sec

    ### 10th website:
    # scraped_items.extend(scrappers.scrape_academy())  # ~ 90 sec

    ### 11th website:
    scraped_items.extend(scrappers.scrape_4sgm())  # ~ 260 sec

    ### check/updated items
    new_items_count = 0
    updated_items_count = 0
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

    ### Save data
    save_data(updated_items_df)

    # report to telegram
    telegram_bot.send_new_items_added(new_items_count)
    telegram_bot.send_new_items_updated(updated_items_count)
    telegram_bot.send_alert(f"Finished in {get_elapsed_time(start_date=now)} seconds.")
