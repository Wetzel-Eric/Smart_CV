from components.base_components import Chunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.models import Document, Chunk

class RecursiveChunker(Chunker):
    def __init__(self):
        super().__init__(name="Recursive Chunker", description="Split documents recursively")

    async def chunk(self, documents: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?"]
        )
        for doc in documents:
            splits = splitter.split_text(doc.content)
            for i, chunk_text in enumerate(splits):
                doc.chunks.append(Chunk(chunk_text, i))
        return documents
