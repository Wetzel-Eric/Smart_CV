from flow.pipeline import Pipeline
from flow.state import RAGState
from flow.steps.reformulation_step import ReformulationStep
from flow.steps.retrieval_step import RetrievalStep
from flow.steps.generation_step import GenerationStep

class SalesPipeline:
    def __init__(self, retriever, reform_gen, commercial_gen):
        self.steps = [  
            ReformulationStep(reform_gen),  # Step 0: Reformulation
            RetrievalStep(retriever),       # Step 1: Retrieval
            GenerationStep(commercial_gen)  # Step 2: Generation
        ]
        self.pipeline = Pipeline(self.steps) 

    async def run(self, question: str, qualification_text: str):
        state = RAGState(question=question, qualification_text=qualification_text)
        state = await self.pipeline.run(state)
        return state.answer
