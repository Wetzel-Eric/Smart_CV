import asyncio
from trulens.apps.custom import instrument


class RetrievalStep:

    def __init__(self, retriever):
        self.retriever = retriever

    @instrument
    async def run(self, state):

        query = state.reformulated or state.question

        contexts = await self.retriever.retrieve(query)

        state.contexts = contexts
        return state
