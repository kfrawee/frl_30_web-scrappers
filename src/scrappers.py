"""
Scrappers functions.
Each website has a different scrapping function.

# List of urls:
# COMPLETED
# https://plaidonline.com/products?closeout=True
# https://www.enasco.com/c/Clearance
# https://www.nordstromrack.com/clearance
# https://www.altomusic.com/by-category/hot-deals/on-sale
# https://www.muscleandstrength.com/store/category/clearance.html
# https://camerareadycosmetics.com/collections/makeup-sale 
# https://www.officesupply.com/clearance
# https://www.gamestop.com/deals
# https://www.scheels.com/c/all/sale
# https://www.academy.com/c/shops/sale 


# CHECKED - NOT WORKING ¯\_(ツ)_/¯
# https://chesapeake.yankeecandle.com/chesapeake-bay-candle/sale/ # blocked by robots.txt, <Response [403]>
# https://www.gamenerdz.com/sale-clearance # dynamic website - JS to load content
# https://www.dickblick.com/products/wacky-links-sets/?fromSearch=%2Fclearance%2F # dynamic website - JS to load content
# https://entirelypetspharmacy.com/s.html?tag=sale-specials # dynamic website - JS to load content 
# https://www.shopatdean.com/collections/clearance-closeouts-overstock #  dynamic website - JS to load content
# https://www.4sgm.com/category/536/Top-Deals.html?minPrice=&maxPrice=&minQty=&sort=inventory_afs&facetNameValue=Category_value_Top+Deals&size=100&page={page}

# TODO RE-CHECK
# WIP


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
        Scrapper for: "https://plaidonline.com/"

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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_enasco(self):
        """
        Scrapper for: "https://www.enasco.com/"
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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_nordstromrack(self):
        """
        Scrapper for: "https://www.nordstromrack.com/"

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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_altomusic(self):
        """
        Scrapper for: "https://www.altomusic.com/"

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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_muscleandstrength(self):
        """
        Scrapper for: "https://www.muscleandstrength.com/"

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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_camerareadycosmetics(self):
        """
        Scrapper for: "https://camerareadycosmetics.com/"

        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://camerareadycosmetics.com/"
        base_url = "https://camerareadycosmetics.com/collections/makeup-sale"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                raw_pages_data = soup.find_all(class_="page")
                no_of_pages = int(raw_pages_data[-1].a.string)
            except Exception as e:
                print("Error getting pages", e)
                no_of_pages = 2  # ~

            # scrape pages
            for page_no in range(1, no_of_pages + 1):
                page_url = base_url + f"?page={page_no}"
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(attrs={"class": "grid-item"})

                for product in products:
                    product_data = product.find(class_="grid-product__title")
                    # item_title
                    item_title = product_data.a.string.strip()
                    # # item_url
                    item_url = product_data.a.get("href")
                    # item_price
                    try:

                        item_price = extract_price(
                            product.find(
                                attrs={"class": "grid-product__price--current"}
                            )
                            .find("span", class_="money")
                            .string
                        )
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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_officesupply(self):
        """
        Scrapper for: "https://www.officesupply.com/"

        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://www.officesupply.com/"
        base_url = "https://www.officesupply.com/clearance"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            # try:
            #     raw_pages_data = soup.find_all(class_="page")
            #     no_of_pages = int(raw_pages_data[-1].a.string)
            # except Exception as e:
            #     print("Error getting pages", e)
            no_of_pages = 1

            # scrape pages
            for page_no in range(1, no_of_pages + 1):
                # page_url = base_url + f"?page={page_no}"
                # res = requests.request("GET", url=page_url, headers=self.headers)
                # assert res.status_code == HTTPStatus.OK

                # soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(class_="product-details")

                for product in products:
                    product_data = product.find(class_="title")
                    # item_title
                    item_title = product_data.span.string
                    # # item_url
                    item_url = product_data.a.get("href")
                    # item_price
                    try:
                        item_price = extract_price(
                            product.parent.find(class_="price")
                            .find("span")
                            .string.strip()
                        )
                    except Exception as e:
                        traceback.format_exc()
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

                # sleep(PAGES_SLEEP_INTERVAL)

        except (
            AssertionError,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            Exception,  # un-captured exception
        ) as e:
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_gamestop(self):
        """
        Scrapper for: "https://www.gamestop.com/"

        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://www.gamestop.com/"
        base_url = "https://www.gamestop.com/deals"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                # raw_pages_data = soup.find_all(class_="pagination-numbering")
                # no_of_pages = int(raw_pages_data[-1].a.string)

                products_count = soup.find("span", class_="pageResults")
                products_count = int(
                    extract_price(products_count.string, thousands_comma_separator=True)
                )
            except Exception as e:
                print("Error getting pages", e)
                products_count = 12412  # ~

            # scrape pages
            # item_per_page: increase by multiples of 24 to increase speed.
            # NOTE the request will take more time.
            item_per_page = 24 * 4
            # i = 0 # DEBUG
            for product_idx in range(0, products_count + 1, item_per_page):
                # if i > 2:
                #     break # DEBUG: 3 iterations
                # i += 1
                # if product_idx % item_per_page == 0:
                #     print(product_idx)  # DEBUG: check if the script is stuck
                page_url = base_url + f"?start={product_idx}&sz={item_per_page}"
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products_raw = soup.find(class_="product-grid-wrapper")
                products = products_raw.find_all(class_="product grid-tile")

                for product in products:
                    product_data = product.find(class_="tile-body")
                    # item_title
                    item_title = product_data.find(class_="link-name").p.string
                    # # item_url
                    item_url = product_data.find(class_="link-name").get("href")
                    # item_price
                    try:
                        item_price = extract_price(
                            product.find(class_="actual-price").string.strip()
                        )
                    except Exception as e:
                        traceback.format_exc()
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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_scheels(self):
        """
        Scrapper for: "https://www.scheels.com/"

        Args:
            _
        Return:
            items (list): list of scrapped items.
        """
        domain_name = "https://www.scheels.com/"
        base_url = "https://www.scheels.com/c/all/sale"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                no_of_pages = int(extract_price(soup.find(class_="page-last").text))
            except Exception as e:
                print("Error getting pages", e)
                no_of_pages = 265

            # scrape pages
            # item_per_page: increase by multiples of 24 - 1 (one ad) to increase speed.
            # NOTE the request will take more time.
            item_per_page = 47  # Optimum number of items per page
            # i = 0 # DEBUG
            for product_idx in range(0, item_per_page * no_of_pages, item_per_page):
                # if i > 2:
                #     break # DEBUG: 3 iterations
                # i += 1
                # if product_idx % item_per_page == 0:
                #   print(product_idx)  # DEBUG: check if the script is stuck
                page_url = base_url + f"?start={product_idx}&sz={item_per_page}"
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(class_="tile-inner")

                for product in products:
                    product_data = product.find(class_="name-link")
                    # item_title
                    item_title = product_data.string.strip()
                    # item_url
                    item_url = product_data.get("href")
                    # item_price
                    try:
                        item_price = extract_price(
                            product.find(attrs={"itemprop": "price"}).string.strip(),
                            thousands_comma_separator=True,
                        )
                    except Exception as e:
                        traceback.format_exc()
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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_academy(self):
        """
            Scrapper for: "https://www.academy.com/"

            Args:
                _
            Return:
                items (list): list of scrapped items.
            """
        domain_name = "https://www.academy.com/"
        base_url = "https://www.academy.com/c/shops/sale"

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                no_of_pages_raw = soup.find(
                    attrs={"data-auid": "NumberRangeNavigation"}
                ).find_all("a")
                no_of_pages = int(extract_price(no_of_pages_raw[-1].text))

            except Exception as e:
                print("Error getting pages", e)
                no_of_pages = 52  # ~

            # scrape pages
            for page_no in range(1, no_of_pages):  # no_of_pages -1
                page_url = base_url + f"?&page_{page_no}"
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(class_="css-18cbcd1")

                for product in products:
                    product_data = product.find(
                        class_="product-card-simple-title css-dfh7vc"
                    )
                    # item_title
                    item_title = product_data.string.strip()
                    # # item_url
                    item_url = product_data.get("href")
                    # item_price
                    try:
                        price_data = product.find(class_="product-price").find("span")
                        # combine price with decimal
                        init_price = price_data.find("span").string
                        dec_price = price_data.find_all("sup")[-1]
                        if dec_price and int(dec_price.string):
                            init_price += f".{dec_price.string}"
                        item_price = extract_price(init_price)
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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items

    def scrape_4sgm(self):
        """
            Scrapper for: "https://www.4sgm.com/"

            Args:
                _
            Return:
                items (list): list of scrapped items.
            """
        domain_name = "https://www.4sgm.com/"
        base_url = (
            "https://www.4sgm.com/category/536/Top-Deals.html"
            "?minPrice=&maxPrice=&minQty=&sort=inventory_afs&facetNameValue=Category_value_Top+Deals&size=100"
        )

        try:
            res = requests.request("GET", url=base_url, headers=self.headers)
            assert res.status_code == HTTPStatus.OK

            soup = BeautifulSoup(res.content, "lxml")

            # get num_of_pages
            try:
                no_of_pages_raw = (
                    soup.find(class_="pageNumber")
                    .find_all(attrs={"class": "control-label"})[-1]
                    .string
                )
                no_of_pages = int(extract_price(no_of_pages_raw))
                no_of_pages

            except Exception as e:
                print("Error getting pages", e)
                no_of_pages = 53  # ~

            # scrape pages
            for page_no in range(1, no_of_pages + 1):  # no_of_pages -1
                page_url = base_url + f"&page={page_no}"
                res = requests.request("GET", url=page_url, headers=self.headers)
                assert res.status_code == HTTPStatus.OK

                soup = BeautifulSoup(res.content, "lxml")

                products = soup.find_all(class_="product_item_sm")

                for product in products:
                    product_data = product.find(class_="product_name")
                    # item_title
                    item_title = product_data.string.strip()
                    # item_url
                    item_url = product_data.a.get("href")
                    # item_price
                    try:
                        price_data = product.find(class_="price")
                        item_price = extract_price(price_data.string)
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
            error_message = (
                f"""Error while trying to scrape {get_domain_name(base_url)}: '{e}'. \n"""
                f"""StatusCode: {res.status_code}. \n"""
                f"""Traceback: {traceback.format_exc()}."""
            )
            self.telegram_bot.send_error(error_message)

        return self.items
