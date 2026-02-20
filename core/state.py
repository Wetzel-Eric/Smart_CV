from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class RAGState:
    """État complet du RAG avec valeurs par défaut"""
    question: str = ""
    qualification: Dict[str, str] = field(default_factory=dict)
    qualification_text: str = ""
    reformulated: Optional[str] = None
    contexts: List[str] = field(default_factory=list)
    answer: str = ""
    current_step: Optional[int] = None
    metadata: Dict[str, str] = field(default_factory=dict)
    conversation: List[Dict] = field(default_factory=list)
