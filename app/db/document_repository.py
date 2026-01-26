from app.db.supabase_client import supabase
from app.embedding_service import EmbeddingService

class DocumentRepository:
    def __init__(self,supabase_client ,embedding_service):
        self.client = supabase_client
        self.embedder = embedding_service
    
    def save_document(self, nome, content, tipo, categoria):
        
        vector = self.embedder.embed(content)

        document_data = {
            "nome": nome,
            "content": content,
            "tipo": tipo,
            "categoria": categoria,
            "embedding": vector
        }
        
        response = self.client.table("documents").insert(document_data).execute()

        return response.data
