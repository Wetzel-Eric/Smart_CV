from typing import List, Dict, AsyncGenerator
from components.base_components import Generator, PromptStrategy
from trulens.apps.custom import instrument

class LLMGenerator(Generator):
    """
    Generator simple et propre:
    PromptStrategy → LLM LangChain, Compatible CLI + Streamlit
    """

    def __init__(self, llm, prompt_strategy: PromptStrategy):
        super().__init__(
            name="LLM Generator",
            description="LangChain based generator with PromptStrategy"
        )
        self.llm = llm
        self.prompt_strategy = prompt_strategy

    # -------------------------
    # Mode simple (CLI)
    # -------------------------
    @instrument
    async def generate(
        self,
        question: str,
        context: List[str],
        conversation: List[Dict] | None = None
    ) -> str:

        payload, template = self.prompt_strategy.build(
            question=question,
            context=context,
            state=conversation
        )

        prompt = template.format(**payload)

        response = await self.llm.ainvoke(prompt)
        return response.content

    # -------------------------
    # Mode streaming (UI/Streamlit)
    # -------------------------
    @instrument
    async def generate_stream(
        self,
        question: str,
        context: List[str],
        conversation: List[Dict] | None = None
    ) -> AsyncGenerator[str, None]:

        payload, template = self.prompt_strategy.build(
            question=question,
            context=context,
            state=conversation
        )

        prompt = template.format(**payload)

        async for chunk in self.llm.astream(prompt):
            yield chunk.content
