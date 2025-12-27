import requests

class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/keys"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def list_keys(self):
        all_keys = []
        offset = 0
        while True:
            url = f"{self.BASE_URL}?offset={offset}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json().get("data", [])
            
            if not data:
                break
                
            all_keys.extend(data)
            offset += len(data)
            
            # If we got fewer than 100 keys, we've reached the end
            if len(data) < 100:
                break
                
        return all_keys

    def update_key_limit(self, key_hash, new_limit):
        url = f"{self.BASE_URL}/{key_hash}"
        payload = {"limit": new_limit}
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

