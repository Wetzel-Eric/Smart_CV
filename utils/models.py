class Document:
    def __init__(self, content: str):
        self.content = content
        self.chunks = []

class Chunk:
    def __init__(self, content: str, chunk_id: int):
        self.content = content
        self.chunk_id = chunk_id
