# Couche MÉTIER pure (zéro UI, zéro input, zéro Streamlit)
from typing import Dict, List, Tuple


# Source de vérité unique
QUESTIONS: List[Tuple[str, str]] = [
    ("pain", "Quel est le problème principal que cette personne doit résoudre ?"),
    ("tempo", "Quel est l’horizon temporel ?"),
    ("success", "À quoi ressemble le succès dans 6 mois ?"),
]


def format_qualification(data: Dict[str, str]) -> str:
    """
    Transforme les réponses en texte structuré pour le LLM.
    Utilisable par Streamlit, API, batch, tests, etc.
    """
    return "\n".join(f"{k}: {v}" for k, v in data.items())

# CLI helper optionnel (debug / terminal seulement), ne PAS utiliser dans Streamlit
def qualify_need_cli() -> str:
    """
    Version console uniquement.
    """
    answers = {}

    print("Avant de continuer, quelques questions rapides :\n")

    for key, question in QUESTIONS:
        answers[key] = input(f"{question}\n> ")

    return format_qualification(answers)
