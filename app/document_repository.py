from app.db.supabase_client import supabase
from app.db.vectorize_db import generate_embeddings


class DocumentRepository:
    def __init__(self):
        self.client = supabase
    
    def save_document(self, nome, localizacao, job_position, categoria, skills, cursos_formacoes, experiencia ):
        
        document_data = {
            
            "nome": nome,
            "localizacao": localizacao,
            "job_position": job_position,
            "categoria": categoria,
            "skills": skills,
            "cursos_formacoes": cursos_formacoes,
            "experiencia": experiencia,
            
        }
        
        response = self.client.table("documents").insert(document_data).execute()

        if not response.data:
            raise Exception("Erro ao inserir documento")

        document_id = response.data[0]["id"]

        generate_embeddings(document_id)

        return response.data
