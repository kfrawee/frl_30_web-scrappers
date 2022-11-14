"""
Scrappers functions.
Each website has a different scrapping function.

# List of urls:
# https://plaidonline.com/products?closeout=True # done
# https://www.enasco.com/c/Clearance # done
# https://www.gamenerdz.com/sale-clearance # TODO check! dynamic website - JS to load content
# https://chesapeake.yankeecandle.com/chesapeake-bay-candle/sale/ # TODO check! blocked by robots.txt, <Response [403]>
# https://www.dickblick.com/products/wacky-links-sets/?fromSearch=%2Fclearance%2F # TODO check! blocked by robots.txt and dynamic website - JS to load content
# https://camerareadycosmetics.com/collections/makeup-sale # TODO check! blocked by robots.txt
# https://www.academy.com/c/shops/sale # TODO check! prices are not consistent
# https://www.officesupply.com/clearance # TODO check! blocked by robots.txt, <Response [403]>
# https://entirelypetspharmacy.com/s.html?tag=sale-specials # TODO check! dynamic website - JS to load content 
# https://www.nordstromrack.com/clearance # done
# https://www.shopatdean.com/collections/clearance-closeouts-overstock #  TODO check! dynamic website - JS to load content
# https://www.gamestop.com/deals # TODO check! dynamic website - JS to load content
# https://www.altomusic.com/by-category/hot-deals/on-sale # done
# https://www.muscleandstrength.com/store/category/clearance.html # done
# https://www.scheels.com/c/all/sale
"""
from http import HTTPStatus
from time import sleep
import traceback

from bs4 import BeautifulSoup
import requests

from helpers import get_domain_name, extract_price
from constants import PAGES_SLEEP_INTERVAL
from telegram_bot_utils import TelegramBot


class Scrapper:
    def __init__(self) -> None:
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        }
        self.telegram_bot = TelegramBot()
        self.items = list()

    def scrape_plaidonline(self):
        """
        Scrapper for domain_name = "https://plaidonline.com/"

        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://plaidonline.com/"
        base_url = "https://plaidonline.com/products?closeout=True"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
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
                print("Error getting pages", e)
                no_of_pages = 5
            # scrape pages
            for page_no in no_of_pages:
                page_url = base_url + f"&page={page_no}"
                res = requests.request("GET", url=page_url, headers=self.headers)
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

                    # append item data to the dictionary
                    self.items.append(
                        {
                            "item_title": item_title,
                            "item_price": item_price,
                            "item_url": domain_name.strip("/") + item_url
                            if item_url
                            else domain_name,
                        }
                    )

                sleep(PAGES_SLEEP_INTERVAL)
        except (
            AssertionError,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            Exception,  # un-captured exception
        ) as e:
            error_message = f"Error while trying to scrape {get_domain_name(base_url)}: '{e}'. Traceback: {traceback.format_exc()}."
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_enasco(self):
        """
        Scrapper for domain_name = "https://www.enasco.com/"
        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://www.enasco.com/"
        base_url = "https://www.enasco.com/c/Clearance"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                raw_pages_data = soup.find(class_="pagination-data_view").text
                # 'Page\n\t\t\t\t1 of 62' > get the max number after 'of'
                no_of_pages = int(raw_pages_data[raw_pages_data.find("of") + 2 :])
            except Exception as e:
                print("Error getting pages", e)
                no_of_pages = 62

            # scrape pages
            for page_no in range(no_of_pages):
                page_url = (
                    base_url
                    + f"?page={page_no}&gridstyle=gridStyle&text=&q=%3Arelevance"
                )
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(
                    class_="similar-products__item col-xs-12 col-sm-6 col-md-4 slp-eq-height"
                )
                for product in products:
                    product_data = product.find(
                        class_="row-eq-height ea-product-cell-name"
                    )
                    # item_title
                    item_title = product_data.a.string
                    # item_url
                    item_url = product_data.a.get("href")
                    # item_price
                    try:
                        # try to get after price - if exists
                        item_price = extract_price(
                            product.find(class_="ea-product-cell-price").string
                        )
                    except AttributeError:  # only old price
                        item_price = extract_price(
                            product.find(
                                class_="similar-products__data_old-price"
                            ).string
                        )

                    # append item data to the dictionary
                    self.items.append(
                        {
                            "item_title": item_title,
                            "item_price": item_price,
                            "item_url": domain_name.strip("/") + item_url
                            if item_url
                            else domain_name,
                        }
                    )

                sleep(PAGES_SLEEP_INTERVAL)

        except (
            AssertionError,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            Exception,  # un-captured exception
        ) as e:
            error_message = f"Error while trying to scrape {get_domain_name(base_url)}: '{e}'. Traceback: {traceback.format_exc()}."
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_nordstromrack(self):
        """
        Scrapper for domain_name = "https://www.nordstromrack.com/"
        
        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://www.nordstromrack.com/"
        base_url = "https://www.nordstromrack.com/clearance"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                num_of_items = int(soup.find(class_="jHG4O").text.strip(" items"))
                item_per_page = 72
                no_of_pages = round(num_of_items / item_per_page)
            except Exception as e:
                print("Error getting pages", e)
                no_of_pages = 140  # ~

            # scrape pages
            for page_no in range(1, no_of_pages + 1):
                page_url = base_url + f"?page={page_no}"
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(class_="ivm_G _PT1R")

                for product in products:
                    product_data = product.find(class_="kKGYj TpwNx")
                    # item_title
                    item_title = product_data.a.string
                    # item_url
                    item_url = product_data.a.get("href")
                    # item_price
                    try:
                        # get the lowest price
                        item_price = extract_price(
                            product.select("span.qHz0a.BkySr.EhCiu.t1yis.sxEtG.jRV6p")[
                                0
                            ].string.split("–")[0]
                        )
                    except IndexError:
                        try:
                            item_price = extract_price(
                                product.select("span.qHz0a.EhCiu.t1yis.sxEtG.jRV6p")[
                                    0
                                ].string
                            )
                        except (IndexError, Exception) as e:
                            item_price = 0.0  # no price available

                    # append item data to the dictionary
                    self.items.append(
                        {
                            "item_title": item_title,
                            "item_price": item_price,
                            "item_url": domain_name.strip("/") + item_url
                            if item_url
                            else domain_name,
                        }
                    )

                sleep(PAGES_SLEEP_INTERVAL)

        except (
            AssertionError,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            Exception,  # un-captured exception
        ) as e:
            error_message = f"Error while trying to scrape {get_domain_name(base_url)}: '{e}'. Traceback: {traceback.format_exc()}."
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_altomusic(self):
        """
        Scrapper for domain_name = "https://www.altomusic.com/"
        
        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://www.altomusic.com/"
        base_url = "https://www.altomusic.com/by-category/hot-deals/on-sale"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                raw_pages_data = soup.find_all(attrs={"class": "toolbar-number"})
                items_per_page = total_items = int(raw_pages_data[1].string)
                total_items = int(raw_pages_data[-1].string)
                no_of_pages = round(total_items / items_per_page)
            except Exception as e:
                print("Error getting pages", e)
                no_of_pages = 23  # ~

            # scrape pages
            for page_no in range(1, no_of_pages + 1):
                page_url = base_url + f"?p={page_no}"
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(attrs={"class": "details"})

                for product in products:
                    product_data = product.find(class_="product-item-link")
                    # item_title
                    item_title = product_data.string.strip()
                    # # item_url
                    item_url = product_data.get("href")
                    # item_price
                    try:
                        # combine price with decimal
                        init_price = product.find(class_="price").string
                        dec_price = product.find(class_="decimal")
                        if dec_price:
                            init_price += dec_price.string
                        item_price = extract_price(init_price)
                    except Exception:
                        item_price = 0.0  # no price available

                    # append item data to the dictionary
                    self.items.append(
                        {
                            "item_title": item_title,
                            "item_price": item_price,
                            "item_url": item_url if item_url else domain_name,
                        }
                    )

                sleep(PAGES_SLEEP_INTERVAL)

        except (
            AssertionError,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            Exception,  # un-captured exception
        ) as e:
            error_message = f"Error while trying to scrape {get_domain_name(base_url)}: '{e}'. Traceback: {traceback.format_exc()}."
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_muscleandstrength(self):
        """
        Scrapper for domain_name = "https://www.muscleandstrength.com/"

        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://www.muscleandstrength.com/"
        base_url = "https://www.muscleandstrength.com/store/category/clearance.html"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                displayed_items = int(
                    soup.find(class_="search-result-displayed-count").string
                )  # useless
                available_items = int(
                    soup.find(class_="search-result-available-count").string
                )
                item_added_per_page = 20  # tested
                no_of_pages = round(available_items / item_added_per_page)
                no_of_pages
            except Exception as e:
                print("Error getting pages", e)
                no_of_pages = 9  # ~

            # scrape pages
            for page_no in range(1, no_of_pages + 1):
                page_url = base_url + f"?p={page_no}"
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(
                    class_="cell small-12 bp600-6 bp960-4 large-3 grid-product"
                )

                for product in products:
                    product_data = product.find(class_="product-name")
                    # item_title
                    item_title = product_data.string.strip()
                    # # item_url
                    item_url = product_data.get("href")
                    # item_price
                    try:
                        item_price = extract_price(product.find(class_="price").string)
                    except Exception:
                        item_price = 0.0  # no price available

                    # append item data to the dictionary
                    self.items.append(
                        {
                            "item_title": item_title,
                            "item_price": item_price,
                            "item_url": domain_name.strip("/") + item_url
                            if item_url
                            else domain_name,
                        }
                    )

                sleep(PAGES_SLEEP_INTERVAL)

        except (
            AssertionError,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            Exception,  # un-captured exception
        ) as e:
            error_message = f"Error while trying to scrape {get_domain_name(base_url)}: '{e}'. Traceback: {traceback.format_exc()}."
            self.telegram_bot.send_error(error_message)

        return self.items
