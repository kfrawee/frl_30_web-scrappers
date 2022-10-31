"""
Telegram bot Class and helpers methods.
"""

from telegram import Bot, ParseMode

from constants import TELEGRAM_BOT_API_KEY, CHAT_ID


class TelegramBot:
    def __init__(self) -> None:
        self.bot_client = Bot(TELEGRAM_BOT_API_KEY)
        self.chat_id = CHAT_ID
        self.emojis = {"ALERT": "⚠️⚠️", "ADD": "🆕✨", "UP": "⬆️📈", "DOWN": "⬇️📉"}

    def _send_message(self, message: str, emoji: str = None) -> None:
        """
        Send message to telegram chat.
        Args:
            message (`str`): message to send.
            emoji (`str`): prefix emoji to use before message.
        Returns:
            `None`
        """
        if emoji in self.emojis.keys():
            message = f"{self.emojis.get(emoji)} {message}"

        try:
            self.bot_client.send_message(
                chat_id=self.chat_id, text=f"{message}", parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Error sending message, {e.message}")

    def send_new_item_added(
        self, item_name: str, item_url: str, item_price: float
    ) -> None:
        """
        Send message with new item added.

        Args:
            item_name (`str`):  name of the item.
            item_url (`str`): url of the item.
            item_price (`float`): price of the item.
        Returns:
            `None`
        """
        emoji = "ADD"
        message = (
            f"<b>Hey! A new item was added!</b>\n"
            f"<a href='{item_url}'>{item_name}</a> - <b>Price:</b> ${item_price}\n"
        )

        self._send_message(message=message, emoji=emoji)

    def send_new_items_added(self, items_count: int) -> None:
        """
        Send message with new items added.

        Args:
            items_count (`int`):  number of newly added items.
        Returns:
            `None`
        """
        emoji = "ADD"
        message = f"<b>Hey! A new {items_count} items were added!</b>\n"

        self._send_message(message=message, emoji=emoji)

    def send_price_update(
        self,
        item_name: str,
        item_url: str,
        item_old_price: float,
        item_new_price: float,
    ) -> None:
        """
        Send message if item's price is updated.

        Args:
            item_name (`str`): name of the item.
            item_url (`str`): url of the item.
            item_old_price (`float`): old price of the item.
            item_new_price (`float`): new price of the item.
        Returns:
            `None`
        """
        if item_old_price == item_new_price:
            return
        elif item_old_price > item_new_price:
            emoji = "DOWN"
        else:
            emoji = "UP"
        message = (
            "<b>Hey! An item's price has been changed!</b> \n"
            f"<a href='{item_url}'>{item_name}</a> \n"
            f"<b>Old Price:</b> ${item_old_price} - <b>New Price:</b> ${item_new_price}"
        )

        self._send_message(message=message, emoji=emoji)

    def send_alert(self, message: str) -> None:
        """
        Send alert message.

        Args:
            message (`str`): message to send.
        Returns:
            `None`"""
        emoji = "ALERT"
        self._send_message(message=message, emoji=emoji)


if __name__ == "__main__":
    bot = TelegramBot()
    bot.send_price_update(
        item_name="example",
        item_url="www.example.com",
        item_old_price=13,
        item_new_price=11,
    )
