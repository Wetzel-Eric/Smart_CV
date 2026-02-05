# My RAG Project

## Objectif
Ce projet implémente un système RAG (Retrieval-Augmented Generation) pour fournir des réponses contextuelles à partir d'un corpus de documents.

## HF Embedding

Objectifs:
Lazy instantiation :
    - On ne crée l’objet HuggingFaceEmbeddings qu’au moment de l’utilisation (embed) pour ne pas charger inutilement le modèle en mémoire dès l’instanciation.

Batching :
    - Découper les textes en batch pour éviter les problèmes de mémoire ou de timeout avec de grands corpus.

Gestion d’erreurs / fallback :
    - Si embed_documents plante, on ne veut pas arrêter tout le pipeline.
    - Retourner des vecteurs nuls pour le batch problématique.

Async-friendly :
    - La méthode embed est async pour pouvoir l’intégrer dans un pipeline async (CLI, Streamlit, LLMGenerator, etc.).

##  ChromaRetriever
Objectifs:
Wrapper Chroma VectorStore :
    - Indexer les textes avec des embeddings.
    - Permettre ensuite la recherche par similarité.

Compatibilité async :
    - Appel à embedder.embed qui est async.

Robustesse minimale :
    - Vérifie que la base Chroma est initialisée avant de récupérer.

Simplicité / réutilisabilité :
    - Peut être utilisé dans différents pipelines (CLI, Streamlit, LLMGenerator, etc.) sans changement.

## Structure du projet
- `data/` : corpus, données brutes et nettoyées
- `index/` : indexes vectoriels pour retrieval
- `src/` : code source et pipeline
- `notebooks/` : exploration et tests
- `models/` : modèles et embeddings sauvegardés
- `scripts/` : scripts pour automatisation
- `tests/` : tests unitaires et d'intégration
- `docs/` : documentation technique


## Pipeline RAG - vue modulaire
┌─────────────┐
│   PDFReader │  ← Reader (async)
└─────┬───────┘
      │ list[Document]
      ▼
┌─────────────┐
│RecursiveChunker│  ← Chunker (async)
└─────┬────────┘
      │ list[Document w/ chunks]
      ▼
┌──────────────────┐
│   HFEmbedding    │  ← Embeddings
│  async.embed()   │
│  model_instance  │ → sync object pour Chroma
└─────┬───────────┘
      │ embeddings (sync pour Chroma)
      ▼
┌──────────────────┐
│ ChromaRetriever  │  ← Retriever
│  from_texts()    │  (sync)
│  similarity_search│
└─────┬───────────┘
      │ list[str] context
      ▼
┌──────────────────┐
│ LLMGenerator     │  ← Generator modulable
│  prompt_strategy │
│  generate_stream │ → Streamlit / UI
│  generate        │ → CLI
└─────┬───────────┘
      │ answer string
      ▼
┌─────────────┐
│ CLI / UI    │
│ print() /   │
│ Streamlit   │
└─────────────┘



## Installation
```bash
pip install -r requirements.txt



