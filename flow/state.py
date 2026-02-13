from dataclasses import dataclass, field
from typing import List


@dataclass
class RAGState:
    question: str
    qualification_text: str

    reformulated: str | None = None
    contexts: List[str] = field(default_factory=list)
    answer: str | None = None
    
    judge_score: float | None = None
