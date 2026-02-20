import streamlit as st
from typing import Dict, Optional

def capture_user_feedback(question: str, answer: str) -> Optional[Dict]:
    with st.expander("⭐ Votre avis sur cette réponse"):
        score = st.slider("Pertinence", 1, 5, 3)
        comment = st.text_area("Commentaire")

        if st.button("Envoyer"):
            return {
                "question": question,
                "answer": answer,
                "score": score,
                "comment": comment,
            }
    return None
