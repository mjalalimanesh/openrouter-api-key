import requests
import logging

logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self._delete_webhook()

    def _delete_webhook(self):
        """Ensures the bot is in polling mode by deleting any existing webhook."""
        try:
            url = f"{self.base_url}/deleteWebhook"
            requests.get(url)
        except Exception:
            pass

    def get_new_subscribers(self):
        """Fetches chat IDs from users who sent /start to the bot."""
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            updates = data.get("result", [])
            
            logger.info(f"Telegram updates fetched: {len(updates)} found.")
            
            chat_ids = set()
            for update in updates:
                # Log the update for debugging
                logger.info(f"Processing update: {update.get('update_id')}")
                
                message = update.get("message", {})
                text = message.get("text", "")
                chat_id = message.get("chat", {}).get("id")
                
                if text.startswith("/start") and chat_id:
                    chat_ids.add(chat_id)
                    logger.info(f"Found /start from chat_id: {chat_id}")
                    
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

