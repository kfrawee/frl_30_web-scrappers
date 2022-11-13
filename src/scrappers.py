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
    """
    Scrapper for domain_name = "https://plaidonline.com/"
    Args:
        _
    Return:
        items (list): list of scrapped items.
    """
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
        except Exception as e:
            print("Error getting pages", e.args)
            no_of_pages = 5
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
            f"Error while trying to scrape  {get_domain_name(base_url)}: '{e}'"
        )
        print(error_message)
        telegram_bot.send_error(error_message)

    return items


def scrape_enasco():
    """
    Scrapper for domain_name = "https://www.enasco.com/"
    Args:
        _
    Return:
        items (list): list of scrapped items.
    """
    domain_name = "https://www.enasco.com/"
    base_url = "https://www.enasco.com/c/Clearance"
    items = []
    # https://www.enasco.com/c/Clearance?page=0&gridstyle=gridStyle&text=&q=%3Arelevance

    try:
        res = requests.request("GET", url=base_url, headers=headers)
        assert res.status_code == HTTPStatus.OK

        soup = BeautifulSoup(res.content, "lxml")

        # get num_of_pages
        try:
            raw_pages_data = soup.find(class_="pagination-data_view").text
            # 'Page\n\t\t\t\t1 of 62' > get the max number after 'of'
            no_of_pages = int(raw_pages_data[raw_pages_data.find("of") + 2 :])
        except Exception as e:
            print("Error getting pages", e.args)
            no_of_pages = 62

        # scrape pages
        for page_no in range(no_of_pages):
            page_url = (
                base_url + f"?page={page_no}&gridstyle=gridStyle&text=&q=%3Arelevance"
            )
            res = requests.request("GET", url=page_url, headers=headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            products = soup.find_all(
                class_="similar-products__item col-xs-12 col-sm-6 col-md-4 slp-eq-height"
            )
            for product in products:
                product_data = product.find(
                    class_="row-eq-height ea-product-cell-name"
                ).a
                # item_title
                item_title = product_data.string
                # item_url
                item_url = product_data.get("href")
                # item_price
                try:
                    # try to get after price - if exists
                    item_price = extract_price(
                        product.find(class_="ea-product-cell-price text-red").string
                    )
                except AttributeError:  # only old price
                    item_price = extract_price(
                        product.find(class_="similar-products__data_old-price").string
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
            f"Error while trying to scrape  {get_domain_name(base_url)}: '{e}'"
        )
        print(error_message)
        telegram_bot.send_error(error_message)

    return items
