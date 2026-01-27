from google import genai
import os

client = genai.Client(api_key="AIzaSyDHnRRegaNH3K-M6MO1Ib-PGrAt0q7cnaM")


class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=('AIzaSyDHnRRegaNH3K-M6MO1Ib-PGrAt0q7cnaM'))
        self.model_id = 'models/gemini-2.5-flash'
    
    def explicar_match(self, query:str, documents: list) -> str:

        context = ""
        for i, doc in enumerate(documents):
            context += f"Canditado/Documento {i+1}:{doc['content']}"
        
        prompt = f"""
        Você é um especialista em recrutamento técnico.
        O usuário realizou a seguinte busca: "{query}"
        
        Abaixo estão os documentos encontrados no banco de dados por similaridade vetorial:
        {context}
        
        Com base nesses documentos, faça uma análise curta (máximo 2 parágrafos) explicando 
        por que esses resultados são os melhores para a busca e destaque os pontos fortes de cada um 
        em relação ao que foi pedido.
        """

        response = self.client.models.generate_content(
            model = self.model_id,
            contents = prompt
        )
        return response.text