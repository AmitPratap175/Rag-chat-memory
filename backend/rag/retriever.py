import chromadb


class Retriever:
    def __init__(self, collection_name="books"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def retrieve(self, query: str, k: int = 5):
        """Retrieve relevant documents from the vector store."""
        results = self.collection.query(query_texts=[query], n_results=k)
        return results["documents"][0]


