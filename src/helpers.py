"""
Helper functions
"""

import os
import re


def load_data(path: str):
    pass


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


if __name__ == "__main__":
    os.system("cls || clear")

    texts = ["$10,22", "$2.111", "USD 102.13", "USD 13,33", "NONE", "", None]

    for price in texts:
        print(price, "\t\t", extract_price(price))
        

