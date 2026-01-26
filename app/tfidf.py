from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()

def tfdif_rank(query: str, documents: list[str], top_k: int =20):
    tfidf_matrix = vectorizer.fit_transform(documents + [query])

    query_vec = tfidf_matrix[-1]
    docs_vecs = tfidf_matrix[:-1]

    similarities = cosine_similarity(query_vec, docs_vecs)[0]

    ranked = sorted(
        enumerate(similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]

