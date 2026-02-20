from typing import List, Tuple, Dict, Optional
import logging
import asyncio
from core.steps.qualification_step import QualificationStep
from core.steps.reformulation_step import ReformulationStep
from core.steps.retrieval_step import RetrievalStep
from core.steps.generation_step import GenerationStep
from core.state import RAGState

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, questions: List[Tuple[str, str]], retriever, reform_gen, commercial_gen):
        self.qualification = QualificationStep(questions)
        self.reformulation = ReformulationStep(reform_gen)
        self.retrieval = RetrievalStep(retriever)
        self.generation = GenerationStep(commercial_gen)

    def generate_sync(self, question: str, context: List[str], conversation: List[Dict] | None = None) -> str:
        """Méthode synchrone pour Streamlit - comme dans l'ancienne version"""
        return self.generation.generate_sync(question, context, conversation)

    def start_qualification_sync(self) -> str:
        """Version synchrone du démarrage de qualification"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            state = RAGState()
            return loop.run_until_complete(
                self.qualification.start(state)
            )
        finally:
            loop.close()

    def get_next_qualification_question(self, QUESTIONS, current_step: int) -> str:
        """Retourne simplement la question suivante"""
        if current_step < len(QUESTIONS) - 1:
            return QUESTIONS[current_step + 1][1]
        return ""

    def process_qualification_response_sync(self, response: str, current_step: int) -> str:
        """Version synchrone du traitement des réponses"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            state = RAGState()
            state.current_step = current_step
            state.qualification = {}
            return loop.run_until_complete(
                self.qualification.next(state, response)
            )
        finally:
            loop.close()

    def reformulate_sync(self, qualification_text: str) -> str:
        """Version synchrone de la reformulation"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            state = RAGState(qualification_text=qualification_text)
            result = loop.run_until_complete(
                self.reformulation.run(state)
            )
            return result.reformulated
        finally:
            loop.close()

    def generate_sync(self, question: str, context: List[str], conversation: List[Dict] | None = None) -> str:
        """Version ultra-simple qui délègue au générateur"""
        return self.generation.generator.generate_sync(question, context, conversation)


    def full_chat_flow_sync(self, question: str, qualification: Dict[str, str]) -> str:
        """Version synchrone du flux complet"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            state = RAGState(
                question=question,
                qualification=qualification,
                qualification_text="\n".join(f"{k}: {v}" for k, v in qualification.items())
            )

            # Exécution séquentielle synchrone
            state = loop.run_until_complete(self.reformulation.run(state))
            state = loop.run_until_complete(self.retrieval.run(state))
            state = loop.run_until_complete(self.generation.run(state))

            return state.answer
        finally:
            loop.close()

    async def full_chat_flow(self, question: str, qualification: dict) -> str:
        """Version asynchrone corrigée avec gestion d'erreur"""
        state = RAGState(
            question=question,
            qualification=qualification,
            qualification_text="\n".join(f"{k}: {v}" for k, v in qualification.items())
        )

        try:
            state = await self.reformulation.run(state)
            state = await self.retrieval.run(state)
            state = await self.generation.run(state)
            return state.answer
        except Exception as e:
            logger.error(f"Erreur dans le pipeline: {str(e)}", exc_info=True)
            return f"""Réponse basée sur votre besoin:
{state.qualification_text[:200]}...[Mode dégradé: {str(e)[:50]}]"""
