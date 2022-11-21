"""
Main logic
"""
import time
import pandas as pd

from helpers import (
    load_data,
    save_data,
    list_existing_items,
    get_item_price,
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
    now = time.time()
    scraped_items = list()

    telegram_bot.send_alert(f"Start scraping...")

    ### SCRAPPERS
    # comment a line to enable/disable/update a certain website
    scrappers = Scrapper()
    ### 1st website:
    scraped_items.extend(scrappers.scrape_plaidonline())

    ### 2nd website:
    scraped_items.extend(scrappers.scrape_enasco())

    ### 3rd website:
    scraped_items.extend(scrappers.scrape_nordstromrack())

    ### 4th website:
    scraped_items.extend(scrappers.scrape_altomusic())

    ### 5th website:
    scraped_items.extend(scrappers.scrape_muscleandstrength())

    ### 6th website:
    scraped_items.extend(scrappers.scrape_camerareadycosmetics())

    ### 7th website:
    scraped_items.extend(scrappers.scrape_officesupply())

    ### 8th website:
    scraped_items.extend(scrappers.scrape_gamestop())

    ### 9th website:
    scraped_items.extend(scrappers.scrape_scheels())

    ### 10th website:
    scraped_items.extend(scrappers.scrape_academy())

    ### 11th website:
    scraped_items.extend(scrappers.scrape_4sgm())

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
                # change send_all to `true` to get all updated items prices
                # false for only decreased prices.
                telegram_bot.send_price_update(
                    item_title=item_title,
                    item_url=item_url,
                    item_old_price=item_old_price,
                    item_new_price=item_new_price,
                    send_all=False,
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
    telegram_bot.send_success(
        f"Total elapsed time: {get_elapsed_time(start_time=now)} seconds."
        f"\nScrapped {scrappers.num_of_websites} website/s."
    )
