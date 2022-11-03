"""
Helper functions.
"""

import os
import re
from datetime import datetime, timezone
from typing import List, Set
import pandas as pd


from telegram_bot_utils import TelegramBot
from constants import DATA_DIR, DATA_FILE_NAME

telegram_bot = TelegramBot()

DATA_COLUMNS = ["item_name", "item_price", "item_url", "added_on", "updated_on"]


def load_data(
    data_dir: str = DATA_DIR, data_file_name: str = DATA_FILE_NAME
) -> pd.DataFrame:
    """
    Load data from csv file if exists.
    Otherwise, create new file and return empty dataframe.

    Args:
        data_dir (str): Data directory (default /data)
        data_file_name (str): Name of the CSV file (default data.csv) 
    Returns:
        data (pd.DataFrame): Dataframe with data
    """
    full_path = os.path.join(os.path.abspath(__file__), data_dir, data_file_name)
    if not os.path.exists(full_path):
        return pd.DataFrame(columns=DATA_COLUMNS)  # first run
    try:
        return pd.read_csv(full_path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=DATA_COLUMNS)


def list_existing_items(dataframe: pd.DataFrame) -> List:
    """
    Check list of existing items
    """
    return dataframe["item_name"].to_list()


def get_item_price(dataframe: pd.DataFrame, item_name: str) -> float:
    """
    Check existing item price.
    """
    try:
        return dataframe[dataframe["item_name"] == item_name]["item_price"].values[0]
    except IndexError:
        return 0.0


def updated_datetime(now=datetime.now(tz=timezone.utc)) -> datetime:
    """
    Return Updated datetime
    """
    return now


def update_item_price(
    dataframe: pd.DataFrame, item_name: str, new_item_price: float
) -> pd.DataFrame:
    """
    Update existing item price.
    """
    dataframe[dataframe["item_name"] == item_name, ["item_price", "updated_on"]] = [
        new_item_price,
        updated_datetime(),
    ]
    return dataframe


def extract_price(text_price: str = None) -> float:
    """
    Using regex; extract price from a text.

    Args:
        text_price(`str`): The text that contains the price.

    Returns:
        extracted_price(`float`): The extracted price.
    """
    if not text_price:
        return 0

    pattern = r"(\d+(?:\.\d+)?)"
    extracted_price = re.findall(pattern, text_price.replace(",", "."))

    return float(extracted_price[0]) if extracted_price else 0


def get_domain_name(url: str = None) -> str:
    """
    Using regex; extract domain name.


        extracted_price(`float`): The extracted price.
    """
    pattern = r"^(?:http:\/\/|www\.|https:\/\/)([^\/]+)"

    return re.findall(pattern, url)[0]
