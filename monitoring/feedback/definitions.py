from trulens.core import Feedback
from .auto_feedback import groundedness_score, relevance_score, context_relevance_score
from .user_feedback import UserFeedback

def create_feedback_definitions():
    """Centralise la création des définitions de feedback."""
    return [
        Feedback(groundedness_score, name="Groundedness").on(...),
        Feedback(relevance_score, name="Answer Relevance").on(...),
        Feedback(context_relevance_score, name="Context Relevance").on(...),
    ]

def register_user_feedback_loop():
    """Enregistre les callbacks pour le feedback utilisateur."""
    # Logique pour lier UserFeedback aux traces TruLens
    pass
