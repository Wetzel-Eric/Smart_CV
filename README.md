# My RAG Project

# 🚀 RAG Pipeline pour CV Matching

Une application Streamlit pour analyser des CVs et répondre aux questions des recruteurs en utilisant un pipeline RAG (Retrieval-Augmented Generation).

## 📦 Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/Wetzel-Eric/Smart_CV.git
   cd rag-cv-matching


2. Installer les dépendances :
poetry install


3. Configurer .env :
cp .env.example .env

Ajoutez vos clés API dans .env.

## 🏃 Utilisation
Lancer l'application :
streamlit run app/main.py

## 🧪 Tests
Exécuter les tests unitaires :
pytest tests/

## 📂 Structure du Projet
.
├── app/                  # Frontend Streamlit
├── core/                 # Logique métier
├── components/           # Composants réutilisables
├── config/               # Configuration
├── data/                 # Données (PDFs, index Chroma)
├── monitoring/           # Observabilité
├── tests/                # Tests
└── docs/                 # Documentation

## 🔧 Configuration
Modifier config/settings.py pour ajuster :
- pdf_path : Chemin vers le PDF à analyser.
- chunk_size/chunk_overlap : Paramètres de découpage du texte.
- llm_model : Modèle LLM utilisé (ex: mistral-large-latest).

---

### **12.2. `docs/architecture.md`**
```markdown
# Architecture du Pipeline RAG

## 1. Couches Principales

### 1.1. Frontend (`app/`)
- **Streamlit** : Interface utilisateur pour interagir avec le pipeline.
- **Services** : Couche d'abstraction entre l'UI et le métier (ex: `bootstrap_service.py`).

### 1.2. Métier (`core/`)
- **Orchestrateur** : Coordination des étapes du pipeline RAG.
- **Bootstrap** : Initialisation des composants et du pipeline.

### 1.3. Composants (`components/`)
- **Reader** : Chargement des documents (PDF).
- **Chunker** : Découpage des documents en chunks.
- **Embedder** : Génération d'embeddings pour les chunks.
- **Retriever** : Récupération des contextes pertinents (Chroma).
- **Generator** : Génération de réponses (LLM).

### 1.4. Infrastructure (`monitoring/`, `config/`)
- **TruLens** : Observabilité et feedbacks.
- **Configuration** : Paramètres centralisés.


3. Points Clés

- **Injection de dépendances** : Via dependency_injector pour une meilleure testabilité.
- **Cache des embeddings** : Persistance de l'index Chroma pour éviter les recalculs.
- **Gestion des erreurs** : Retries exponentiels et validation des entrées.
- **Découplage UI/Métier** : Les services (app/services/) isolent Streamlit du code métier.



## Objectif
Ce projet implémente un système RAG (Retrieval-Augmented Generation) pour fournir des réponses contextuelles à partir d'un corpus de documents.

Documentation technique – Projet Sales RAG
Architecture
- Description : Le projet utilise un backend/API séparé avec une UI Streamlit stateless.
- Axe d’amélioration : Architecture solide. Vérifier que la séparation backend/frontend est maintenue pour futures évolutions.

Gestion multi-utilisateurs
- Description : Les sessions sont isolées et la mémoire conversationnelle est gérée par utilisateur.
- Axe d’amélioration : Fonctionnel, mais prévoir un stockage persistant et scalable (ex : Redis ou Pinecone) pour gérer un usage concurrent élevé.

Gestion des API Keys / Secrets
- Description : Les clés API sont gérées via un secrets manager ou des variables d’environnement.
- Axe d’amélioration : OK. Assurer la rotation régulière des clés et la sécurité sur les déploiements cloud.

Streaming LLM
- Description : Streaming optimisé avec buffering pour l’UI afin d’améliorer l’expérience utilisateur.
- Axe d’amélioration : OK. Pour de très longs prompts, ajuster la fréquence des mises à jour pour réduire la charge sur l’UI.

Historique & mémoire conversationnelle
- Description : Mémoire persistante avec token limit et mécanisme de pruning.
- Axe d’amélioration : OK. Surveiller la croissance de la mémoire pour les longues sessions et prévoir un mécanisme d’archivage si nécessaire.

Logging & monitoring
- Description : Logs structurés avec métriques de latence et suivi des erreurs.
- Axe d’amélioration : OK. Ajouter éventuellement de l’alerting automatique pour les erreurs critiques ou latence élevée.

Tests & maintainabilité
- Description : Tests unitaires et tests d’intégration avec typage Python fort.
- Axe d’amélioration : OK. Maintenir la couverture tests et ajouter des tests d’intégration multi-utilisateur si possible.

UI Streamlit
- Description : Interface minimaliste, responsive, offrant une expérience utilisateur fluide.
- Axe d’amélioration : OK. Vérifier la performance de l’UI même pour de longues sessions ou des réponses LLM volumineuses.

Support multi-LLM
- Description : Le backend permet de gérer plusieurs modèles LLM.
- Axe d’amélioration : OK. Prévoir des tests de compatibilité et un monitoring de performance par modèle.

Déploiement / production readiness
- Description : Projet déployé via Docker, avec CI/CD et monitoring.
- Axe d’amélioration : OK. Effectuer des tests de charge et prévoir le scaling automatique pour plusieurs utilisateurs simultanés.

Expérience utilisateur (UX)
- Description : UX optimisée, responsive et gestion des erreurs.
- Axe d’amélioration : OK. Améliorer les messages utilisateurs en cas de timeout LLM ou erreurs réseau.

Extensibilité
- Description : Architecture modulaire facilitant l’ajout de nouveaux modèles ou pipelines RAG.
- Axe d’amélioration : OK. Vérifier la modularité pour futurs agents ou sources de données additionnelles.

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



