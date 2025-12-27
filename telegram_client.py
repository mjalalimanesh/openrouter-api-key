import requests
import logging

logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def get_new_subscribers(self):
        """Fetches chat IDs from users who sent /start to the bot."""
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url)
            response.raise_for_status()
            updates = response.json().get("result", [])
            
            chat_ids = set()
            for update in updates:
                message = update.get("message", {})
                text = message.get("text", "")
                chat_id = message.get("chat", {}).get("id")
                
                if text == "/start" and chat_id:
                    chat_ids.add(chat_id)
            return list(chat_ids)
        except Exception as e:
            logger.error(f"Error fetching Telegram updates: {e}")
            return []

    def send_message(self, chat_id, text):
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error sending Telegram message to {chat_id}: {e}")

