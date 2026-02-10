import asyncio

async def run_flow(generator, user_input, conversation, enable_trulens=False, feedbacks=None):
    """
    Exécute le flow RAG pour une question utilisateur.

    :param generator: instance de LLMGenerator
    :param user_input: texte utilisateur
    :param conversation: historique messages [{"role":..,"content":..}]
    :param enable_trulens: bool, active TruLens si True
    :param feedbacks: liste de feedbacks TruLens
    :return: (réponse texte, record TruLens ou None)
    """
    if enable_trulens:
        from trulens_integration.wrap_rag import wrap_rag_with_trulens

        tru_app = wrap_rag_with_trulens(generator, feedbacks=feedbacks)
        async with tru_app as record:
            answer = await generator.generate(user_input, context=[], conversation=conversation)
            return answer, record
    else:
        answer = await generator.generate(user_input, context=[], conversation=conversation)
        return answer, None


def run_flow_sync(*args, **kwargs):
    """Wrapper Streamlit-safe pour exécuter run_flow depuis UI"""
    return asyncio.run(run_flow(*args, **kwargs))
