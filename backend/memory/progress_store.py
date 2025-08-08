import json
import os
from pathlib import Path


class ProgressStore:
    def __init__(self, db_path="data/memory/progress.json"):
        self.db_path = Path(db_path)
        os.makedirs(self.db_path.parent, exist_ok=True)
        if not self.db_path.exists():
            with open(self.db_path, "w") as f:
                json.dump({}, f)

    def get_progress(self, user_id: str):
        with open(self.db_path, "r") as f:
            data = json.load(f)
        return data.get(user_id, {})

    def save_progress(self, user_id: str, progress: dict):
        with open(self.db_path, "r+") as f:
            data = json.load(f)
