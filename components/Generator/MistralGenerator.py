from typing import List, Dict, AsyncGenerator
from components.base_components import Generator, PromptStrategy
from trulens.apps.custom import instrument
import asyncio
import logging

logger = logging.getLogger("generator")

class LLMGenerator:
    def __init__(self, llm, prompt_strategy: PromptStrategy):
        # INITIALISATION DIRECTE (sans super().__init__)
        self.name = "LLM Generator"
        self.description = "LangChain based generator with PromptStrategy"
        self.llm = llm
        self.prompt_strategy = prompt_strategy

    # Méthode synchrone pour Streamlit (encapsulation propre)
    @instrument
    def generate_sync(self, question: str, context: List[str], conversation: List[Dict] | None = None) -> str:
        """Version synchrone ultra-simple"""
        payload, template = self.prompt_strategy.build(
            question=question,
            context=context,
            state=conversation
        )

        prompt = template.format(**payload)

        # ⭐ Utilisation directe de invoke (synchrone) au lieu de ainvoke
        response = self.llm.invoke(prompt)
        return response.content
    # -------------------------
    # Méthode ASYNCHRONE interne
    # -------------------------
    # Méthode asynchrone principale (comme dans votre ancienne version)
    @instrument
    async def generate(self, question: str, context: List[str], conversation: List[Dict] | None = None) -> str:
        """Méthode asynchrone principale (compatibilité totale)"""
        payload, template = self.prompt_strategy.build(question, context, conversation)
        prompt = template.format(**payload)
        response = await self.llm.ainvoke(prompt)
        return response.content

    # -------------------------
    # Mode streaming (conservé)
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
