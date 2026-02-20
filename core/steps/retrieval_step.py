from core.state import RAGState

class RetrievalStep:
    def __init__(self, retriever):
        self.retriever = retriever

    async def run(self, state: RAGState) -> RAGState:
        """Récupère les contextes et met à jour l'état."""
        query = state.reformulated or state.question
        state.contexts = await self.retriever.retrieve(query)
        return state
