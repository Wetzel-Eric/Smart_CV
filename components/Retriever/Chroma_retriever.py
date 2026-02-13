from components.base_components import Retriever
from utils.models import Document
from components.Embedder.HF_embedder import HFEmbedding
from langchain_community.vectorstores import Chroma
import asyncio

# TruLens instrumentation
from trulens.apps.custom import instrument

class ChromaRetriever(Retriever):
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

        if embedder.model_instance is None:
            embedder.model_instance = HFEmbedding(model_name=embedder.model_name).model_instance

        self.db = Chroma.from_texts(texts, embedding=embedder.model_instance)

    @instrument
    async def retrieve(self, query: str, k: int = 3) -> list[str]:
        if self.db is None:
            return []

        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.db.similarity_search(query, k=k)
        )

        contexts = [d.page_content for d in results]

        # Filtrez les contextes trop courts
        filtered_contexts = [c for c in contexts if len(c.split()) > 5]  # Ajustez le seuil selon vos besoins

        return filtered_contexts
