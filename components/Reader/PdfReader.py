from components.base_components import Reader
from langchain_community.document_loaders import PyPDFLoader
from utils.models import Document
import logging

logger = logging.getLogger("pdf_reader")

class PDFReader(Reader):
    def __init__(self):
        # Pas d'appel à super().__init__() car Reader est une ABC
        self.name = "PDF Reader"
        self.description = "Load PDF files into documents"

    async def load(self, path: str) -> list[Document]:
        logger.info(f"Chargement du PDF: {path}")
        loader = PyPDFLoader(path)
        pages = loader.load()
        return [Document(p.page_content) for p in pages]
