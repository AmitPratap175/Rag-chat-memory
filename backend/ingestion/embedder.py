from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    def embed_documents(self, texts):
