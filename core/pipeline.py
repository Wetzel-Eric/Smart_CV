from typing import List, Tuple, Optional
from trulens.core import Tru
from core.state import RAGState
from core.steps.qualification_step import QualificationStep
from core.steps.reformulation_step import ReformulationStep
from core.steps.retrieval_step import RetrievalStep
from core.steps.generation_step import GenerationStep
from monitoring.feedback.definitions import create_feedback_definitions

class Pipeline:
    def __init__(self, steps):
        self.steps = steps

    async def run(self, state: RAGState) -> RAGState:
        for step in self.steps:
            state = await step.run(state)
        return state

class SalesPipeline:
    def __init__(self, questions: List[Tuple[str, str]], retriever, reform_gen, commercial_gen):
        self.feedback_definitions = create_feedback_definitions()
        self.state = RAGState(question="", qualification={}, qualification_text="")
        self.qualification_step = QualificationStep(questions)
        self.steps = [
            ReformulationStep(reform_gen),
            RetrievalStep(retriever),
            GenerationStep(commercial_gen)
        ]

    async def start_qualification(self) -> str:
        """Démarre la qualification."""
        return await self.qualification_step.start(self.state)

    async def process_qualification_response(self, response: str) -> Optional[str]:
        """Traite une réponse de qualification."""
        return await self.qualification_step.next(self.state, response)

    async def run_reformulation(self) -> str:
        """Exécute la reformulation."""
        self.state = await ReformulationStep(self.steps[0].reform_gen).run(self.state)
        return self.state.reformulated

    async def run_chat(self, question: str) -> str:
        """Exécute le pipeline complet."""
        self.state.question = question
        pipeline = Pipeline(self.steps)
        self.state = await pipeline.run(self.state)
        return self.state.answer

# --- Wrapper TruLens (externe) ---
tru = Tru()

def with_trulens(enable: bool):
    """Décorateur conditionnel pour TruLens."""
    def decorator(func):
        return tru.instrument(func) if enable else func
    return decorator

def wrap_pipeline(pipeline: SalesPipeline, enable_trulens: bool) -> SalesPipeline:
    """Active TruLens sur les étapes critiques."""
    if enable_trulens:
        pipeline.run_reformulation = with_trulens(True)(pipeline.run_reformulation)
        pipeline.run_chat = with_trulens(True)(pipeline.run_chat)
        for step in pipeline.steps:
            step.run = with_trulens(True)(step.run)
    return pipeline
