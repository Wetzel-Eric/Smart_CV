import os
import asyncio
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config.settings import RAG_CONFIG, RETRY_CONFIG
from core.qualification import QUESTIONS
from core.orchestrator import Orchestrator
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever

logger = logging.getLogger("bootstrap")

class BootstrapError(Exception): pass
class PDFLoadError(BootstrapError): pass
class ChunkerError(BootstrapError): pass
class EmbeddingError(BootstrapError): pass
class ChromaIndexError(BootstrapError): pass

class BootstrapCore:
    def __init__(self, container):
        self.container = container

    def _create_pipeline(self):
        from core.orchestrator import Orchestrator
        from core.qualification import QUESTIONS
        return Orchestrator(
            questions=QUESTIONS,
            retriever=self.container.retriever(),
            reform_gen=self.container.reform_gen(),
            commercial_gen=self.container.commercial_gen(),
        )

    def _get_pdf_hash(self):
        with open(self.container.config.pdf_path(), "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _save_metadata(self, metadata):
        os.makedirs("data/chroma_index", exist_ok=True)
        with open("data/chroma_index/metadata.json", "w") as f:
            json.dump(metadata, f)

    def _load_metadata(self):
        metadata_path = "data/chroma_index/metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path) as f:
                return json.load(f)
        return None

    def _validate_dependencies(self):
        if not hasattr(self.container, 'config') or self.container.config is None:
            raise BootstrapError("Le conteneur n'est pas configuré. Appeler container.config.from_dict(...) avant.")
        if not os.path.exists(self.container.config.pdf_path()):
            raise PDFLoadError(f"PDF introuvable: {self.container.config.pdf_path()}")
        if not self.container.config.mistral_api_key():
            raise BootstrapError("Clé API Mistral manquante")

    @retry(
        stop=stop_after_attempt(RETRY_CONFIG["max_attempts"]),
        wait=wait_exponential(
            multiplier=RETRY_CONFIG["wait_multiplier"],
            min=RETRY_CONFIG["wait_min"],
            max=RETRY_CONFIG["wait_max"]
        ),
        retry=retry_if_exception_type(ChromaIndexError)
    )
    async def _index_documents(self):
        try:
            logger.info("Chargement du PDF...")
            docs = await asyncio.wait_for(
                self.container.reader().load(self.container.config.pdf_path()),
                timeout=30.0
            )
            logger.info(f"PDF chargé: {len(docs)} documents")

            logger.info("Chunking des documents...")
            docs = await asyncio.wait_for(
                self.container.chunker().chunk(docs),
                timeout=60.0
            )

            logger.info("Indexation dans Chroma...")
            await self.container.retriever().index(docs, self.container.embedder())

        except asyncio.TimeoutError as e:
            logger.error(f"Timeout: {str(e)}", exc_info=True)
            raise ChunkerError(f"Timeout lors du chunking: {str(e)}")

        except Exception as e:
            logger.error(f"Erreur détaillée:\n{str(e)}", exc_info=True)
            if "PDF" in str(e) or "PyPDFLoader" in str(e):
                raise PDFLoadError(f"Échec du chargement PDF: {str(e)}")
            elif "Chunker" in str(e) or "Recursive" in str(e):
                raise ChunkerError(f"Échec du chunking: {str(e)}")
            elif "Embedding" in str(e) or "HuggingFace" in str(e):
                raise EmbeddingError(f"Échec de l'embedding: {str(e)}")
            else:
                raise ChromaIndexError(f"Échec de l'indexation: {str(e)}")

    async def initialize(self):
        self._validate_dependencies()

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

        except PDFLoadError as e:
            raise BootstrapError(f"Échec du chargement PDF: {str(e)}")
        except ChunkerError as e:
            raise BootstrapError(f"Échec du chunking: {str(e)}")
        except EmbeddingError as e:
            raise BootstrapError(f"Échec de l'embedding: {str(e)}")
        except ChromaIndexError as e:
            raise BootstrapError(f"Échec de l'indexation: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}", exc_info=True)
            raise BootstrapError(f"Échec inattendu: {str(e)}")

    
