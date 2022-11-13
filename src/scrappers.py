"""
Scrappers functions.
Each website has a different scrapping function.
# List urls:

# https://plaidonline.com/products?closeout=True
# https://www.enasco.com/c/Clearance
# https://www.gamenerdz.com/sale-clearance
# https://chesapeake.yankeecandle.com/chesapeake-bay-candle/sale/
# https://www.dickblick.com/products/wacky-links-sets/?fromSearch=%2Fclearance%2F
# https://camerareadycosmetics.com/collections/makeup-sale
# https://www.academy.com/c/shops/sale
# https://www.officesupply.com/clearance
# https://entirelypetspharmacy.com/s.html?tag=sale-specials
# https://www.nordstromrack.com/clearance
# https://www.shopatdean.com/collections/clearance-closeouts-overstock
# https://www.gamestop.com/deals
# https://www.altomusic.com/by-category/hot-deals/on-sale
# https://www.muscleandstrength.com/store/category/clearance.html
# https://www.scheels.com/c/all/sale
"""
from http import HTTPStatus
from time import sleep
from bs4 import BeautifulSoup

import requests
from helpers import get_domain_name, extract_price, DATA_COLUMNS
from constants import PAGES_SLEEP_INTERVAL
from telegram_bot_utils import TelegramBot

telegram_bot = TelegramBot()


headers = {"Content-Type": "application/json"}


def scrape_plaidonline():
    domain_name = "https://plaidonline.com/"
    base_url = "https://plaidonline.com/products?closeout=True"
    items = []

    try:
        res = requests.request("GET", url=base_url, headers=headers)
        assert res.status_code == HTTPStatus.OK

        soup = BeautifulSoup(res.content, "lxml")

        # get number of pages
        # it is 5 pages, but I don't want to hard code it incase it increases
        try:
            raw_pages_data = soup.find(class_="PagerNumberArea").find_all("span")[3]
            no_of_pages = []
            selected_page = raw_pages_data.find(class_="SelectedPage").string
            no_of_pages.append(selected_page)
            unselected_pages = raw_pages_data.find_all(class_="UnselectedPage")
            for unselected_page in unselected_pages:
                no_of_pages.append(unselected_page.string)

            no_of_pages = sorted(map(int, no_of_pages))
        except Exception as e:  # I don't know
            print("Error getting pages", e.args)
            no_of_pages = 5  # -_-
        # scrape pages
        for page_no in no_of_pages:
            page_url = base_url + f"&page={page_no}"
            res = requests.request("GET", url=page_url, headers=headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # find all class="price" but skip the second one (each item has 2 "price" classes)
            prices = [
                _ if i % 2 == 0 else None
                for i, _ in enumerate(soup.find_all(class_="price"))
            ]
            # remove None
            prices_clean = [price for price in prices if price]
            # len(prices_clean) # 40 for full items in a page
            for raw_item_price in prices_clean:
                # item_price
                item_price = extract_price(raw_item_price.text)
                # item_title
                item_title = raw_item_price.parent.h3.text
                # item_url
                item_url = raw_item_price.parent.parent.parent.parent.find("a").get(
                    "href"
                )

                # append item dictionary
                items.append(
                    {
                        "item_title": item_title,
                        "item_price": item_price,
                        "item_url": domain_name.strip("/") + item_url
                        if item_url
                        else "/",
                    }
                )

            sleep(PAGES_SLEEP_INTERVAL)
    except (
        AssertionError,
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        Exception,  # un-captured exception
    ) as e:
        error_message = (
            f"Error while trying to contact to {get_domain_name(base_url)}: '{e}'"
        )
        telegram_bot.send_alert(error_message)

    return items


def scrape_enasco():
    domain_url = f"https://www.enasco.com/c/Clearance?page={52}&gridstyle=gridStyle&text=&q=%3Arelevance"

    # domain_name = "https://plaidonline.com/"
    # base_url = "https://plaidonline.com/products?closeout=True"
    items = []

    return items
