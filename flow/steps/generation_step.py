from trulens.apps.custom import instrument


class GenerationStep:

    def __init__(self, generator):
        self.generator = generator

    @instrument
    async def run(self, state):

        answer = await self.generator.generate(
            question=state.reformulated or state.question,
            context=state.contexts,
            conversation=[]
        )

        state.answer = answer
        return state
