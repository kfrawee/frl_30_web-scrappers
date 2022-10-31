"""
Helper functions
"""

import os
import re
from typing import List, Set


from telegram_bot_utils import TelegramBot


telegram_bot = TelegramBot()


def load_data(path: str) -> List:
    """
    Load existing csv file if exists.

    """

    pass


def create_data_file(path: str) -> None:
    """
    Create new csv file if not existing (first run).

    """

    pass


def check_itmes_updates():
    """
    Check list of existing items
    """
    pass


def check_item_price(item_name: str) -> None:
    """
    Check and update item price if updated
    """
    pass


def extract_price(text_price: str = None) -> float:
    """
    Using regex; extract price from a text.

    Args:
        text_price (`str`): The text that contains the price.

    Returns:
        extracted_price (`float`): The extracted price.
    """
    if not text_price:
        return 0

    pattern = r"(\d+(?:\.\d+)?)"
    extracted_price = re.findall(pattern, text_price.replace(",", "."))

    return float(extracted_price[0]) if extracted_price else 0


if __name__ == "__main__":
    os.system("cls || clear")

    
