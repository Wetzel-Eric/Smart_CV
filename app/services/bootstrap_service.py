# app/services/bootstrap_service.py
import asyncio
import streamlit as st
import logging
from core.dependencies import Container
from core.bootstrap_core import BootstrapCore  # Import corrigé

logger = logging.getLogger("bootstrap_service")

class StreamlitBootstrapService:
    def __init__(self, container: Container):
        self.container = container  # ← Ajout de cette ligne manquante
        self.bootstrap_core = BootstrapCore(container)

    async def initialize(self):
        try:
            if "bootstrapped" not in st.session_state:
                with st.spinner("Initialisation du pipeline..."):
                    pipeline = await self.bootstrap_core.initialize()
                    st.session_state.pipeline = pipeline
                    st.session_state.bootstrapped = True
            return st.session_state.pipeline
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}", exc_info=True)
            st.error(f"Erreur inattendue: {e}")
            raise
