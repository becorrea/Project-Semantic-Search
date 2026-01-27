from app.db.supabase_client import supabase
from app.embedding_service import EmbeddingService
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.ai_service import AIService

app = FastAPI(title="Busca Semântica API")
embedder = EmbeddingService()
ai_assistant = AIService()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    

class DocumentItem(BaseModel):
    nome: str
    content: str
    tipo: str
    categoria: str

@app.post("/adicionar")
def adicionar_documento(doc: DocumentItem):
    try:
        vector = embedder.embed(doc.content)

        data = {
            "nome": doc.nome,
            "content": doc.content,
            "tipo": doc.tipo,
            "categoria": doc.categoria,
            "embedding": vector
        }

        response = supabase.table("documents").insert(data).execute()
        return {"status": "sucesso", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/buscar")
def buscar_inteligente(query: str, top_k: int = 3):
    try:

        query_vector = embedder.embed(query)

        cache_check = supabase.table("query_logs").select("ai_response").eq("query_text", query).execute()

        if cache_check.data:
            return {
                "origem": "cache_do_banco",
                "analise_da_ia": cache_check.data[0]["ai_response"]
            }
        
        response = supabase.rpc(
            "match_documents",
            {"query_embedding": query_vector, "match_count": top_k}
        ).execute()

        documents = response.data

        if not documents:
            return {"mensagem": "Nenhum resultado encontrado"}
        
        explicacao = ai_assistant.explicar_match(query, documents)

        supabase.table("query_logs").insert({
            "query_text": query,
            "embedding": query_vector,
            "ai_response": explicacao
        }).execute()

        return {
            "origem": "gerado_pela_ia",

            

            "resultados": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))