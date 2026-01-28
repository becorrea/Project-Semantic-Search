from app.db.supabase_client import supabase
from app.embedding_service import EmbeddingService
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from app.document_repository import DocumentRepository
from app.ai_service import AIService
import fitz


app = FastAPI(title="Busca Semântica API")
embedder = EmbeddingService()
repo = DocumentRepository()
ai_assistant = AIService()

@app.post("/upload_curriculo")
async def upload_curriculo(file: UploadFile = File()):

    conteudo_pdf = await file.read()
    
    pdf_extraido = ai_assistant.extrair_pdf(conteudo_pdf)
    texto_extraido = ai_assistant.extrair_dados(pdf_extraido)


    data = repo.save_document(
        nome= texto_extraido['nome'],
        content= pdf_extraido,
        tipo= texto_extraido['tipo'],
        categoria= texto_extraido['categoria'],
        localizacao= texto_extraido['localizacao']
    )

    return {"status": "sucesso", "candidato": texto_extraido['nome'] + ""}

@app.get("/buscar")
def buscar_inteligente(query: str, localizacao: str = None, tipo: str = None, categoria: str = None, top_k: int = 3):
    try:

        query_vector = embedder.embed(query)
        
        rpc_params = {
            "query_embedding": query_vector,
            "match_count": top_k,
            "filter_location": f"%{localizacao}%" if localizacao else "%",
            "filter_type": f"%{tipo}%" if tipo else "%",
            "filter_category": f"%{categoria}%" if categoria else "%"
        }
        
        response = supabase.rpc("match_documents", rpc_params).execute()
        
        cache_check = supabase.table("query_logs").select("ai_response").eq("query_text", query).execute()
        
        documents = response.data
        
        if not documents:
            return {"mensagem": "Nenhum candidato encontrado para essa busca ou localização."}

        if cache_check.data:
            return {
                "origem": "cache_do_banco",
                "resultados": documents
            }
        
        

     

        supabase.table("query_logs").insert({
            "query_text": query,
        }).execute()

        return {
            "resultados": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))