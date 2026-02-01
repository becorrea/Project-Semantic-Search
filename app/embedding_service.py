from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    def embed(self, texto) -> list[float]:
        if texto is None:
            texto = ""

        
        if isinstance(texto, list):
            texto = " ".join(map(str, texto))

       
        if isinstance(texto, dict):
            texto = " ".join(map(str, texto.values()))

        embedding = self.model.encode(texto)

        if isinstance(embedding, np.ndarray) and embedding.ndim > 1:
            embedding = embedding[0]

        return embedding.flatten().tolist()