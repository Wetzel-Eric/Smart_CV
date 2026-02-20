from trulens.core.guardrails.base import context_filter


def guardrail_context_not_empty(query: str, contexts: list[str]) -> float:
    return 1.0 if contexts else 0.0


def apply_context_guardrail(threshold: float = 0.5):
    return context_filter(
        guardrail_context_not_empty,
        threshold,
        keyword_for_prompt="query"
    )
