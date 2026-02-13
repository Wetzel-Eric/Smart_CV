class Pipeline:

    def __init__(self, steps):
        self.steps = steps

    async def run(self, state):
        for step in self.steps:
            state = await step.run(state)
        return state
