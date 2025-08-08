from backend.memory.progress_store import ProgressStore


class MasteryLogic:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.progress_store = ProgressStore()

    def is_topic_completed(self, topic_id: str) -> bool:
        """Checks if a topic is marked as completed for the user."""
        progress = self.progress_store.get_progress(self.user_id)
        return progress.get(topic_id, {}).get("completed", False)

    def suggest_next_topic(self, syllabus: dict) -> str:
        """Suggests the next topic for the user to study."""
        progress = self.progress_store.get_progress(self.user_id)
        for topic in syllabus.get("topics", []):
            if not progress.get(topic["topic_name"], {}).get("completed", False):
                return topic["topic_name"]
        return "All topics completed!"
