from components.base_components import Reader
from langchain_community.document_loaders import PyPDFLoader
from utils.models import Document

class PDFReader(Reader):
    def __init__(self):
        super().__init__(name="PDF Reader", description="Load PDF files into documents")

    async def load(self, path: str) -> list[Document]:
        loader = PyPDFLoader(path)
        pages = loader.load()
        return [Document(p.page_content) for p in pages]
