from typing import Dict, List, Tuple

QUESTIONS: List[Tuple[str, str]] = [
    ("pain", "Quel est le problème principal que cette personne doit résoudre ?"),
    ("tempo", "Quel est l’horizon temporel ?"),
    ("success", "À quoi ressemble le succès dans 6 mois ?"),
]

def format_qualification(data: Dict[str, str]) -> str:
    return "\n".join(f"{k}: {v}" for k, v in data.items())
