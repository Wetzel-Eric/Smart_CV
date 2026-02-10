import streamlit as st
from typing import Dict


def capture_user_feedback() -> Dict | None:
    """
    Capture uniquement le feedback utilisateur.
    Ne touche PAS aux objets TruLens.

    Retourne un dict exploitable par une couche storage.
    """

    with st.expander("⭐ Votre avis sur cette réponse"):

        score = st.slider("Pertinence", 1, 5, 3)
        comment = st.text_area("Commentaire")

        if st.button("Envoyer"):

            return {
                "score": score,
                "comment": comment,
            }

    return None
