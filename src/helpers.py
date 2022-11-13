"""
Helper functions.
"""

import os
from pathlib import Path
import re
from datetime import datetime, timezone
from typing import List
import pandas as pd


from telegram_bot_utils import TelegramBot
from constants import DATA_DIR, DATA_FILE_NAME

telegram_bot = TelegramBot()

DATA_COLUMNS = ["item_title", "item_price", "item_url", "added_on", "updated_on"]


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
    full_dir_path = os.path.join(Path(__file__).parent.resolve(), data_dir)
    full_file_path = os.path.join(full_dir_path, data_file_name)

    if not os.path.exists(full_dir_path):
        return pd.DataFrame(columns=DATA_COLUMNS)  # just first run
    try:
        return pd.read_csv(full_file_path)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame(columns=DATA_COLUMNS)


def save_data(
    data: pd.DataFrame, data_dir: str = DATA_DIR, data_file_name: str = DATA_FILE_NAME
) -> None:
    """
    Save data to a csv file.

    Args:
        data (dataframe): Data to save.
        data_dir (str): Data directory (default /data)
        data_file_name (str): Name of the CSV file (default data.csv) 
    Returns:
        None
    """

    full_dir_path = os.path.join(Path(__file__).parent.resolve(), data_dir)
    full_file_path = os.path.join(full_dir_path, data_file_name)

    if not os.path.exists(full_dir_path):
        os.makedirs(full_dir_path)

    data.to_csv(full_file_path, index=False)


def list_existing_items(dataframe: pd.DataFrame) -> List:
    """
    Return list of existing items

    Args:
        dataframe (dataframe): dataframe to extract the existing items from.
    Returns:
        items (list): List of existing items.
    """
    return dataframe["item_title"].to_list()


def get_item_price(dataframe: pd.DataFrame, item_title: str) -> float:
    """
    Get an item's existing price.
    Args:
        dataframe (dataframe): dataframe of the items.
        item_title (str): title of the item.
    Returns:
        item_price (float): Item price.
    """
    try:
        return dataframe[dataframe["item_title"] == item_title]["item_price"].values[0]
    except IndexError:
        return 0.0


def update_item_price(
    dataframe: pd.DataFrame, item_title: str, new_item_price: float
) -> pd.DataFrame:
    """
    Update existing item price.

    Args:
        dataframe (dataframe): dataframe of the items.
        item_title (str): title of the item.
        new_item_price (float): updated item price to update.
    Returns:
        dataframe (dataframe): updated dataframe of the items.

    """
    dataframe.loc[
        dataframe["item_title"] == item_title, ["item_price", "updated_at"]
    ] = [new_item_price, str(updated_datetime())]
    return dataframe


def extract_price(text_price: str = None) -> float:
    """
    Using regex; extract price from a text.

    Args:
        text_price (str): The text that contains the price.

    Returns:
        extracted_price (float): The extracted price.
    """
    if not text_price:
        return 0

    pattern = r"(\d+(?:\.\d+)?)"
    extracted_price = re.findall(pattern, text_price.replace(",", "."))

    return float(extracted_price[0]) if extracted_price else 0


def get_domain_name(url: str = None) -> str:
    """
    Using regex; extract domain name.

    Args:
        url (str): Full website url to extract thr domain from.
    Returns:
        domain (str): Extracted domain name.
    """
    pattern = r"^(?:http:\/\/|www\.|https:\/\/)([^\/]+)"

    return re.findall(pattern, url)[0]


def updated_datetime(now=datetime.now(tz=timezone.utc)) -> datetime:
    """
    Return Updated datetime

    Args:
        _
    Returns:
        now (datetime): Current datetime.
    """
    return now


def get_elapsed_time(start_date: datetime) -> float:
    """
    Return elapsed time (seconds)
    
    Args:
        start_date (datetime): start datetime.

    Returns:
        elapsed_time (float): rounded total elapsed time in seconds.
    """
    return round(
        (
            datetime.strptime(
                str(datetime.now(tz=timezone.utc))[:-6], "%Y-%m-%d %H:%M:%S.%f"
            )
            - datetime.strptime(str(start_date)[:-6], "%Y-%m-%d %H:%M:%S.%f")
        ).total_seconds(),
        2,
    )
