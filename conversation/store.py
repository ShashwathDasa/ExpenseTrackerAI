import json
from datetime import datetime, timedelta
from pathlib import Path


class ConversationStore:
    def __init__(self, storage_dir="data/conversations", expiry_hours=24):
        self.storage_dir = Path(storage_dir)
        self.expiry = timedelta(hours=expiry_hours)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, chat_id):
        return self.storage_dir / f"{chat_id}.json"

    def get_history(self, chat_id):
        file_path = self._get_file_path(chat_id)
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as file:
            conversation = json.load(file)
        last_updated = datetime.fromisoformat(conversation["last_updated"])
        if datetime.now() - last_updated > self.expiry:
            self.clear_history(chat_id)
            return []
        return conversation["messages"]

    def save_history(self, chat_id, messages):
        file_path = self._get_file_path(chat_id)
        conversation = {
            "chat_id": chat_id,
            "last_updated": datetime.now().isoformat(),
            "messages": messages,
        }

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(conversation, file, indent=2, ensure_ascii=False)

    def clear_history(self, chat_id):
        file_path = self._get_file_path(chat_id)
        if file_path.exists():
            file_path.unlink()