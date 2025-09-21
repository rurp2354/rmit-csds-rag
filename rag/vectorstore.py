from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore:
    def __init__(self):
        self.docs = []  # list of {"file": ..., "text": ..., "page": ...}
        self.vectorizer = TfidfVectorizer()
        self.doc_vectors = None

    def fit(self):
        """Build TF–IDF vectors from all document texts."""
        texts = [doc["text"] for doc in self.docs]
        if texts:
            self.doc_vectors = self.vectorizer.fit_transform(texts)

    def search(self, query, top_k=7):
        """Return top_k most similar docs to the query."""
        if self.doc_vectors is None or len(self.docs) == 0:
            return []

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.doc_vectors).flatten()
        top_idx = sims.argsort()[::-1][:top_k]
        return [self.docs[i] for i in top_idx]
