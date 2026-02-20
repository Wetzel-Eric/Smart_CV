from typing import Dict, List, Tuple

QUESTIONS: List[Tuple[str, str]] = [
    ("pain", "Quelle problématique prioritaire ce recrutement doit-il permettre de résoudre ?"),
    ("tempo", "Quel est l’horizon temporel ?"),
    ("techno", "Quelles technologies doivent être maîtrisées pour ce poste ?")
    ("success", "À quoi ressemble le succès dans 6 mois ?"),
]

def format_qualification(data: Dict[str, str]) -> str:
    return "\n".join(f"{k}: {v}" for k, v in data.items())
