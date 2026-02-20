from core.state import RAGState
from trulens.apps.custom import instrument
import asyncio


class GenerationStep:
    @instrument
    def __init__(self, generator):
        self.generator = generator

    @instrument
    async def run(self, state: RAGState) -> RAGState:
        """Version asynchrone (conservée pour le backend)"""
        state.answer = await self.generator.generate(
            question=state.reformulated or state.question,
            context=state.contexts,
            conversation=[]
        )
        return state

    def run_sync(self, state: RAGState) -> RAGState:
        """Version synchrone pour Streamlit"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run(state))
        finally:
            loop.close()
