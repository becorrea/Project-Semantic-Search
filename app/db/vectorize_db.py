import numpy as np
from app.db.supabase_client import supabase
from app.embedding_service import EmbeddingService

def generate_embeddings(document_id: str):
    embedder = EmbeddingService()

    response = supabase.table("documents").select("skills, cursos_formacoes, experiencia").eq("id", document_id).single().execute()
    
    doc = response.data
    
    if not doc:
            return
    skills = doc.get('skills','')
    if isinstance(skills, list):
          skills = ", ".join(skills)
    
    full_text = f"""
    Cargo: {doc.get('job_position', '')}
    Categoria: {doc.get('categoria', '')}
    Localização: {doc.get('localizacao', '')}
    Skills e Habilidades: {doc.get('skills', '')}
    Experiência Profissional: {doc.get('experiencia', '')}
    Formação Acadêmica: {doc.get('cursos_formacoes', '')}
    """.strip()

    embedding = embedder.embed(full_text)
    
    supabase.table("documents").update({ "embedding": embedding}).eq("id", document_id).execute()