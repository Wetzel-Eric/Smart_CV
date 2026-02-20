from trulens.apps.custom import instrument


class JudgeStep:

    def __init__(self, judge_llm):
        self.judge_llm = judge_llm

    @instrument
    async def run(self, state):

        if not state.answer:
            return state

        score = await self.judge_llm.evaluate(state.answer)

        state.judge_score = score

        return state
