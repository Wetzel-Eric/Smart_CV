import os
from dotenv import load_dotenv

load_dotenv()

# Configuration centrale du pipeline RAG
RAG_CONFIG = {
    "pdf_path": os.getenv("PDF_PATH", "data/raw/CV_Eric_Wetzel_2026.pdf"),
    "embedder_model": os.getenv("EMBEDDER_MODEL", "all-MiniLM-L6-v2"),
    "llm_model": os.getenv("LLM_MODEL", "mistral-large-latest"),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "512")),
    "chunk_size": int(os.getenv("CHUNK_SIZE", "1000")),
    "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "200")),
}

# Configuration des retries (désactivés par défaut pour un POC)
RETRY_CONFIG = {
    "max_attempts": int(os.getenv("RETRY_MAX_ATTEMPTS", "1")),  # 1 = pas de retry
    "wait_multiplier": 1,
    "wait_min": 4,
    "wait_max": 10,
    "log_retries": False  # Désactivé pour un POC
}


# Clés API (à ne pas versionner)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
