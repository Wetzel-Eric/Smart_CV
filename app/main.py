# app/main.py
import os
import streamlit as st
import asyncio
import logging
from dotenv import load_dotenv
from core.dependencies import Container
from app.services.bootstrap_service import StreamlitBootstrapService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Initialisation du conteneur
container = Container()
container.config.from_dict({
    "pdf_path": "data/raw/CV_Eric_Wetzel_2026.pdf",
    "embedder_model": "all-MiniLM-L6-v2",
    "llm_model": "mistral-large-latest",
    "temperature": 0.2,
    "max_tokens": 512,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "mistral_api_key": os.getenv("MISTRAL_API_KEY")
})

# Initialisation du service de bootstrap
bootstrap_service = StreamlitBootstrapService(container)

# Configuration de la page
st.set_page_config(page_title="CV interactif", layout="wide")

# Initialisation du pipeline
try:
    if "bootstrapped" not in st.session_state:
        pipeline = asyncio.run(bootstrap_service.initialize())
        logger.info("Pipeline initialisé avec succès")
except Exception as e:
    logger.error(f"Échec de l'initialisation: {e}", exc_info=True)
    st.error(f"Échec de l'initialisation: {e}")
    st.stop()

# Définition des pages
chat = st.Page("pages/matching_chat.py", title="🤖 Chat Matching")
reco = st.Page("pages/recommendations.py", title="💡 Recommandations")
projects = st.Page("pages/projects.py", title="🚀 Projets")

# Page GitHub qui affiche juste le badge cliquable
def github_page():
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px;">
            <a href="https://github.com/Wetzel-Eric/Smart_CV" target="_blank">
                <img src="https://github.com/codespaces/badge.svg" alt="Open in GitHub"
                     style="height: 30px; margin-bottom: 20px;">
            </a>
            <p style="font-size: 0.9em; color: #666;">Voir le code source sur GitHub</p>
        </div>
        """,
        unsafe_allow_html=True
    )

github = st.Page(github_page, title="GitHub", icon="🐙")

# Navigation avec toutes les pages y compris GitHub
pg = st.navigation([chat, reco, projects, github])
pg.run()