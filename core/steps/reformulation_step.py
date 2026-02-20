from core.state import RAGState

class ReformulationStep:
    def __init__(self, reform_gen):
        self.reform_gen = reform_gen

    async def run(self, state: RAGState) -> RAGState:
        """Reformule la question et met à jour l'état."""
        state.reformulated = await self.reform_gen.generate(
            question=state.qualification_text,
            context=[],
            conversation=[]
        )
        return state
