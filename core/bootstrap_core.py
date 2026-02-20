import os
import asyncio
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep
)
from core.dependencies import Container
from core.orchestrator import Orchestrator
from core.qualification import QUESTIONS
from config.settings import RAG_CONFIG, RETRY_CONFIG

logger = logging.getLogger("bootstrap")
logging.basicConfig(level=logging.INFO)

class BootstrapError(Exception):
    """Exception de base pour les erreurs de bootstrap."""
    pass

class PDFLoadError(BootstrapError):
    """Erreur de chargement du PDF."""
    pass

class ChromaIndexError(BootstrapError):
    """Erreur d'indexation Chroma."""
    pass

class BootstrapCore:
    """Classe principale pour l'initialisation du pipeline RAG."""

    def __init__(self, container: Container):
        self.container = container
        self._validate_dependencies()

    def _validate_dependencies(self):
        """Valide que toutes les dépendances sont disponibles."""
        if not os.path.exists(self.container.config.pdf_path()):
            raise PDFLoadError(f"PDF introuvable: {self.container.config.pdf_path()}")
        if not self.container.config.mistral_api_key():
            raise BootstrapError("Clé API Mistral manquante")

    def _get_pdf_hash(self) -> str:
        """Calcule le hash du PDF pour détecter les modifications."""
        with open(self.container.config.pdf_path(), "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _save_metadata(self, metadata: Dict[str, Any]):
        """Sauvegarde les métadonnées de l'index."""
        os.makedirs("data/chroma_index", exist_ok=True)
        with open("data/chroma_index/metadata.json", "w") as f:
            json.dump(metadata, f)

    def _load_metadata(self) -> Optional[Dict[str, Any]]:
        """Charge les métadonnées de l'index si elles existent."""
        metadata_path = "data/chroma_index/metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path) as f:
                return json.load(f)
        return None

    @retry(
        stop=stop_after_attempt(RETRY_CONFIG["max_attempts"]),
        wait=wait_exponential(
            multiplier=RETRY_CONFIG["wait_multiplier"],
            min=RETRY_CONFIG["wait_min"],
            max=RETRY_CONFIG["wait_max"]
        ),
        retry=retry_if_exception_type(ChromaIndexError),
        before_sleep=lambda retry_state: logger.warning(
            f"Retry {retry_state.attempt_number} for {retry_state.fn.__name__}"
        ) if RETRY_CONFIG["log_retries"] else None
    )
    async def _index_documents(self):
        """Indexe les documents dans Chroma avec retry exponentiel."""
        try:
            logger.info("Chargement du PDF...")
            docs = await asyncio.wait_for(
                self.container.reader().load(self.container.config.pdf_path()),
                timeout=10.0
            )

            logger.info("Chunking des documents...")
            docs = await asyncio.wait_for(
                self.container.chunker().chunk(docs),
                timeout=10.0
            )

            logger.info("Indexation dans Chroma...")
            await asyncio.wait_for(
                self.container.retriever().index(docs, self.container.embedder()),
                timeout=30.0
            )

        except asyncio.TimeoutError:
            raise ChromaIndexError("Timeout lors de l'indexation (30s)")
        except Exception as e:
            raise ChromaIndexError(f"Échec de l'indexation: {e}")

    async def initialize(self):
        """Initialise le pipeline RAG avec gestion des états et cache."""
        try:
            current_hash = self._get_pdf_hash()
            metadata = self._load_metadata()

            if metadata and metadata.get("pdf_hash") == current_hash:
                logger.info("Utilisation de l'index Chroma existant.")
                return self._create_pipeline()

            await self._index_documents()
            self._save_metadata({
                "pdf_hash": current_hash,
                "timestamp": asyncio.get_event_loop().time(),
                "embedder": RAG_CONFIG["embedder_model"],
                "llm_model": RAG_CONFIG["llm_model"]
            })
            return self._create_pipeline()

        except BootstrapError as e:
            logger.error(f"Erreur lors du bootstrap: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}", exc_info=True)
            raise BootstrapError(f"Échec inattendu: {e}")

    def _create_pipeline(self):
        """Crée et retourne le pipeline RAG."""
        return Orchestrator(
            questions=QUESTIONS,
            retriever=self.container.retriever(),
            reform_gen=self.container.reform_gen(),
            commercial_gen=self.container.commercial_gen(),
        )
