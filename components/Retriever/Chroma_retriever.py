from components.base_components import Retriever
from utils.models import Document, Chunk
from components.Embedder.HF_embedder import HFEmbedding
from langchain_community.vectorstores import Chroma

class ChromaRetriever(Retriever):
    """
    Wrapper pour Chroma VectorStore, indexation et retrieval.
    """

    def __init__(self):
        super().__init__(name="Chroma Retriever", description="Vector store with Chroma")
        self.db = None

    async def index(self, documents: list[Document], embedder: HFEmbedding):
        """
        Indexation des chunks via l'embedding async-friendly
        """
        # Récupérer tous les chunks
        texts = [chunk.content for doc in documents for chunk in doc.chunks]

        if not texts:
            print("[ChromaRetriever] Aucun texte à indexer")
            return

        # Embed en batch async
        embeddings = await embedder.embed(texts)

        # Initialisation Chroma
        try:
            self.db = Chroma.from_texts(texts, embeddings)
        except Exception as e:
            print(f"[ChromaRetriever] Erreur lors de l'indexation Chroma: {e}")
            self.db = None

    async def retrieve(self, query: str, k: int = 3) -> list[str]:
        """
        Recherche par similarité via Chroma
        """
        if self.db is None:
            return []
        results = self.db.similarity_search(query, k=k)
        return [d.page_content for d in results]
