import os
from typing import List
from components.base_components import Embedding
from langchain_community.embeddings import HuggingFaceEmbeddings

class HFEmbedding(Embedding):
    """
    HuggingFace Embeddings avec batching, gestion d'erreurs et async-friendly.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", hf_token: str | None = None, batch_size: int = 128):
        super().__init__(name="HF Embedding", description="HuggingFace Embeddings configurable")
        self.model_name = model_name
        self.hf_token = hf_token or os.getenv("HF_API_TOKEN")
        self.model_instance = None
        self.batch_size = batch_size

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Embedding async-friendly avec batching et fallback si erreur.
        """
        if self.model_instance is None:
            # Lazy instantiation
            self.model_instance = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"use_auth_token": self.hf_token} if self.hf_token else {}
            )

        all_embeddings = []

        # Découpage en batch pour éviter mémoire/timeouts
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            try:
                embeddings = self.model_instance.embed_documents(batch)
                all_embeddings.extend(embeddings)
            except Exception as e:
                print(f"[HFEmbedding] Warning: erreur sur batch {i}-{i+len(batch)} -> {e}")
                # fallback : vecteurs nuls
                dim = getattr(self.model_instance, "embedding_dimension", 384)
                all_embeddings.extend([[0.0] * dim for _ in batch])

        return all_embeddings
