from typing import Dict, Any, List, Tuple, Optional
from core.state import RAGState

class QualificationStep:
    def __init__(self, questions: List[Tuple[str, str]]):
        self.questions = questions

    async def start(self, state: RAGState) -> str:
        """Démarre la qualification et met à jour l'état."""
        state.current_step = 0
        state.qualification = {}
        return self.questions[state.current_step][1]

    async def next(self, state: RAGState, response: str) -> Optional[str]:
        """Traite une réponse et met à jour l'état."""
        key, _ = self.questions[state.current_step]
        state.qualification[key] = response
        state.current_step += 1
        state.qualification_text = self._get_qualification_text(state)
        if state.current_step < len(self.questions):
            return self.questions[state.current_step][1]
        return None

    def _get_qualification_text(self, state: RAGState) -> str:
        """Génère le texte de qualification depuis l'état."""
        return "\n".join(f"{k}: {v}" for k, v in state.qualification.items())
