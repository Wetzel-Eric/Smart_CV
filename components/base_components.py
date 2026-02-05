from abc import ABC, abstractmethod
from utils.models import Document

# ---------------- Reader ----------------
class Reader(ABC):
    def __init__(self, name: str = "", description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    async def load(self, path: str) -> list[Document]:
        pass

# ---------------- Chunker ----------------
class Chunker(ABC):
    def __init__(self, name: str = "", description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    async def chunk(self, documents: list[Document]) -> list[Document]:
        pass

# ---------------- Embedding ----------------
class Embedding(ABC):
    def __init__(self, name: str = "", description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    async def embed(self, texts: list[str]):
        pass

# ---------------- Retriever ----------------
class Retriever(ABC):
    def __init__(self, name: str = "", description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    async def index(self, documents: list[Document], embedder: Embedding):
        pass

    @abstractmethod
    async def retrieve(self, query: str, k: int = 3) -> list[str]:
        pass

# ---------------- PromptStrategy ----------------
class PromptStrategy(ABC):
    @abstractmethod
    def build(self, question: str, context: list[str], state: dict) -> tuple[dict, any]:
        pass

# ---------------- Generator ----------------
class Generator(ABC):
    def __init__(self, name: str = "", description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    async def generate(self, question: str, context: list[str], state: dict = None) -> str:
        pass
