from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbedding:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        """Embeds a list of texts and returns their vector representations."""
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        """Embeds a single query text."""
        return self.model.encode([text], convert_to_numpy=True).tolist()[0]

def get_embedding_function():
    """Returns an instance of the SentenceTransformer embedding function."""
    return SentenceTransformerEmbedding()