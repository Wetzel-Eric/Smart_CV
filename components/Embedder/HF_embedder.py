import os
from typing import List
from components.base_components import Embedding
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

logger = logging.getLogger("embedder")

class HFEmbedding(Embedding):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", hf_token: str | None = None, batch_size: int = 128):
        # Pas d'appel à super().__init__()
        self.name = "HF Embedding"
        self.description = "HuggingFace Embeddings configurable"
        self.model_name = model_name
        self.hf_token = hf_token or os.getenv("HF_API_TOKEN")
        self.model_instance = None
        self.batch_size = batch_size

    async def embed(self, texts: List[str]) -> List[List[float]]:
        if self.model_instance is None:
            self.model_instance = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"use_auth_token": self.hf_token} if self.hf_token else {}
            )

        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            try:
                embeddings = self.model_instance.embed_documents(batch)
                all_embeddings.extend(embeddings)
            except Exception as e:
                logger.warning(f"Erreur sur batch {i}-{i+len(batch)}: {e}")
                dim = getattr(self.model_instance, "embedding_dimension", 384)
                all_embeddings.extend([[0.0] * dim for _ in batch])
        return all_embeddings
