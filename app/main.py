from app.db.supabase_client import supabase
from app.embedding_service import EmbeddingService
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.document_repository import DocumentRepository
from app.ai_service import AIService
import numpy as np


app = FastAPI(title="Busca Semântica API")

#Permite que o lovable passe a página do ngroq
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Serviços (embeeding, documents, AI)
embedder = EmbeddingService()
repo = DocumentRepository()
ai_assistant = AIService()

#Endpoint de upload de um arquivo PDF
@app.post("/upload")
async def upload_curriculo(file: UploadFile = File()):

    conteudo_pdf = await file.read()
    
    #Utiliza a API da OpenAI para extrair e analisar o texto
    pdf_extraido = ai_assistant.extrair_pdf(conteudo_pdf)
    texto_extraido = ai_assistant.extrair_dados(pdf_extraido)

    #
    data = repo.save_document(
        nome = texto_extraido['nome'],
        localizacao = texto_extraido['localizacao'],
        categoria= texto_extraido['categoria'],
        job_position = texto_extraido['cargo'],
        skills = texto_extraido['skills'],
        cursos_formacoes = texto_extraido['cursos_formacoes'],
        experiencia = texto_extraido ['experiencia']    
    )

    return {"status": True}


@app.get("/search")
def buscar_inteligente(query: str, localizacao: str = None, categoria: str = None, cargo: str = None, skills: str = None, cursos_formacoes: str = None, experiencia: str = None, top_k: int = 3):
    try:

        semantic_query = f"Candidato com experiência profissional, habilidades ou formação em: {query}"

        query_vector = embedder.embed(semantic_query)

        if isinstance(query_vector, list):
            query_vector = np.array(query_vector)
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm

        query_vector_list = query_vector.tolist()    
        
        rpc_params = {
            "query_embedding": query_vector_list,
            "query_text": query,
            "match_count": top_k,
            "filter_localizacao": f"%{localizacao}%" if localizacao else "%",
            "filter_job_position": f"%{cargo}%" if cargo else "%",
            "filter_category": f"%{categoria}%" if categoria else "%",
            "filter_skills": f"%{skills}%" if skills else "%",
            "filter_cursos_formacoes": f"%{cursos_formacoes}%" if cursos_formacoes else "%",
            "filter_experiencia": f"%{experiencia}%" if experiencia else "%"
        }
        
        #Chamada RPC ao Supabase
        response = supabase.rpc("match_documents", rpc_params).execute()
        
        documents = response.data
        
        if not documents:
            return {"mensagem": "Nenhum candidato encontrado para essa busca ou localização."}

        supabase.table("query_logs").insert({
            "query_text": query,
        }).execute()

        return {
            "resultados": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))