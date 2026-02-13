from trulens.apps.custom import instrument


class ReformulationStep:

    def __init__(self, generator):
        self.generator = generator

    @instrument
    async def run(self, state):

        reformulated = await self.generator.generate(
            question=state.question,
            context=[state.qualification_text],
            conversation=[]
        )

        state.reformulated = reformulated
        return state
