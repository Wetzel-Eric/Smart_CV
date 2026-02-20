from components.base_components import Chunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.models import Document, Chunk
import logging

logger = logging.getLogger("chunker")

class RecursiveChunker(Chunker):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # Pas d'appel à super().__init__()
        self.name = "Recursive Chunker"
        self.description = "Split documents recursively"
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?"]
        )

    async def chunk(self, documents: list[Document]) -> list[Document]:
        logger.info(f"Chunking {len(documents)} documents...")
        for doc in documents:
            splits = self.text_splitter.split_text(doc.content)
            doc.chunks = [Chunk(text, i) for i, text in enumerate(splits)]
        logger.info(f"Generated {sum(len(doc.chunks) for doc in documents)} chunks")
        return documents
