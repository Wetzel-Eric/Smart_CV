import json
import os
from typing import List, Dict
from pathlib import Path

FEEDBACK_FILE = Path("data/feedbacks.json")

class FeedbackStore:
    @staticmethod
    def save_feedback(feedback: Dict):
        feedbacks = FeedbackStore._load_feedbacks()
        feedbacks.append(feedback)
        FEEDBACK_FILE.parent.mkdir(exist_ok=True, parents=True)
        FEEDBACK_FILE.write_text(json.dumps(feedbacks, indent=2))

    @staticmethod
    def _load_feedbacks() -> List[Dict]:
        if not FEEDBACK_FILE.exists():
            return []
        return json.loads(FEEDBACK_FILE.read_text())

    @staticmethod
    def get_feedbacks(score: Optional[int] = None) -> List[Dict]:
        feedbacks = FeedbackStore._load_feedbacks()
        return [f for f in feedbacks if score is None or f["score"] == score]
