from app.db.supabase_client import supabase
from app.embedding_service import EmbeddingService
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.document_repository import DocumentRepository
from app.ai_service import AIService
import numpy as np
import traceback


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

    #Insere na table do banco de dados as informações extraídas
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

@app.post("/match-job")
async def match_vaga_hibrida(
    file: UploadFile = File(),         
    localizacao: str = None,        
    categoria: str = None,          
    top_k: int = 3
):
    try:
        # 1. Extração do PDF
        conteudo_pdf = await file.read()
        texto_vaga = ai_assistant.extrair_pdf(conteudo_pdf)
        dados_vaga = ai_assistant.extrair_requisitos_vaga(texto_vaga)

        # 2. Lógica Híbrida de Filtros
        # Se você preencher no formulário, ele ignora o que a IA achou no PDF
        filtros = {
            "localizacao": localizacao if localizacao else dados_vaga.get('localizacao', ''),
            "categoria": categoria if categoria else dados_vaga.get('categoria', '')
        }

        #Criar a Query Semântica focada no perfil do candidato
        skills_vaga = ", ".join(dados_vaga.get('skills', []))
        query_para_embedding = f"""
        Perfil Profissional: {dados_vaga.get('cargo', 'Candidato')}. 
        Habilidades e Experiência: {skills_vaga}. 
        Atuação na área de {filtros['categoria']}.
        """

        # Gerar Vetor
        query_vector = embedder.embed(query_para_embedding)
        
        # Chamar o Banco com os parâmetros de filtro
        def f(val): return f"%{val}%" if (val and val.strip()) else "%"

        rpc_params = {
            "query_embedding": query_vector,
            "query_text": query_para_embedding,
            "match_count": top_k,
            "filter_localizacao": f(filtros['localizacao']),
            "filter_category": f(filtros['categoria']),
            "filter_job_position": "%",
            "filter_skills": "%",
            "filter_cursos_formacoes": "%",
            "filter_experiencia": "%"
        }

        response = supabase.rpc("match_documents", rpc_params).execute()

        # 6. Retorno focado nos candidatos
        if not response.data:
            return {
                "mensagem": "Nenhum candidato encontrado para os requisitos desta vaga.",
                "analise_vaga": dados_vaga,
                "candidatos": []
            }

        return {
            "vaga_analisada": dados_vaga,
            "melhores_candidatos": response.data  # Aqui virá a lista ordenada por 'similarity'
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


#Endpoint de busca
@app.get("/search")
def buscar_inteligente(query: str, localizacao: str = None, categoria: str = None, cargo: str = None, skills: str = None, cursos_formacoes: str = None, experiencia: str = None, top_k: int = 3):
    try:

        semantic_query = f"Candidato com experiência profissional, habilidades ou formação em: {query}"

        #Vetorização da query
        query_vector = embedder.embed(semantic_query)

        #Normalização da query
        if isinstance(query_vector, list):
            query_vector = np.array(query_vector)
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm

        query_vector_list = query_vector.tolist()    
        
        def f(val): 
            if val and "remoto" in val.lower(): return "%"
            return f"%{val}%" if (val and val.strip()) else "%"
        
        #Parâmetros para a função do supabase
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