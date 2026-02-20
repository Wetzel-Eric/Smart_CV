from components.base_components import Retriever
from utils.models import Document
from components.Embedder.HF_embedder import HFEmbedding
from langchain_community.vectorstores import Chroma
import asyncio
import logging
import os

logger = logging.getLogger("retriever")

class ChromaRetriever(Retriever):
    def __init__(self, persist_directory: str = None):
        # Pas d'appel à super().__init__()
        self.name = "Chroma Retriever"
        self.description = "Vector store with Chroma"
        self.persist_directory = persist_directory or "data/chroma_index"
        self.db = None

    async def index(self, documents: list[Document], embedder: HFEmbedding):
        texts = [chunk.content for doc in documents for chunk in doc.chunks]

        if not texts:
            logger.warning("Aucun texte à indexer")
            return

        logger.info(f"Indexation de {len(texts)} chunks dans Chroma...")

        try:
            self.db = Chroma.from_texts(
                texts=texts,
                embedding=embedder.model_instance,
                persist_directory=self.persist_directory
            )
            logger.info("Indexation Chroma terminée avec succès")
        except Exception as e:
            logger.error(f"Erreur ChromaDB: {str(e)}", exc_info=True)
            raise RuntimeError(f"Échec de l'indexation Chroma: {str(e)}")

    async def retrieve(self, query: str, k: int = 3) -> list[str]:
        if self.db is None:
            logger.warning("Aucune base de données Chroma chargée")
            return []

        try:
            results = self.db.similarity_search(query, k=k)
            return [d.page_content for d in results]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}", exc_info=True)
            return []
