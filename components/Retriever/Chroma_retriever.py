from components.base_components import Retriever
from utils.models import Document
from components.Embedder.HF_embedder import HFEmbedding
from langchain_community.vectorstores import Chroma

# TruLens instrumentation
from trulens.apps.custom import instrument
from trulens_integration.guardrails import apply_context_guardrail

class ChromaRetriever(Retriever):
    """
    Retriever basé sur Chroma vector store.
    Compatible TruLens v2 et guardrails simples.
    """

    def __init__(self):
        super().__init__(
            name="Chroma Retriever",
            description="Vector store with Chroma"
        )
        self.db = None

    async def index(self, documents: list[Document], embedder: HFEmbedding):
        texts = [chunk.content for doc in documents for chunk in doc.chunks]

        if not texts:
            return

        # S'assurer que l'embedder LangChain est instancié
        if embedder.model_instance is None:
            embedder.model_instance = embedder.model_instance = HFEmbedding(model_name=embedder.model_name).model_instance

        # Passe l'embedder à Chroma, pas la liste d'embeddings
        self.db = Chroma.from_texts(texts, embedding=embedder.model_instance)

    # =========================
    # TruLens instrumentation + guardrail
    # =========================
    @instrument
    @apply_context_guardrail(0.5)
    async def retrieve(self, query: str, k: int = 3) -> list[str]:
        if self.db is None:
            return []

        results = self.db.similarity_search(query, k=k)
        return [d.page_content for d in results]
