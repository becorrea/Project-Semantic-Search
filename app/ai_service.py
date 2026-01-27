from google import genai
import fitz
import os
import json


client = genai.Client(api_key="AIzaSyDHnRRegaNH3K-M6MO1Ib-PGrAt0q7cnaM")


class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=('AIzaSyDHnRRegaNH3K-M6MO1Ib-PGrAt0q7cnaM'))
        self.model_id = 'models/gemini-2.5-flash'
    
    def extrair_pdf(self, content: bytes) -> str:
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for pagina in doc:
                text += pagina.get_text()
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Erro ao ler o arquivo PDF: {str(e)}")
    
    def extrair_dados(self, texto_pdf: str):
        prompt = f"""
        Você é um sistema especializado em triagem de currículos. Analise o texto abaixo e extraia as informações estritamente como um objeto JSON:
        - nome: nome completo do candidato
        - categoria: (ex: Tecnologia, Marketing, Vendas Finanças, etc.)
        - localizacao: (Cidade e Estado). Se nao encontrar, use "Não informado"
        - tipo: (ex: Sênior, Pleno, Chef, Estágiario, etc.)

        Texto do currículo:
        {texto_pdf}

        Responda APENAS o JSON, sem textos adicionais.
        """
        response = self.client.models.generate_content(
            model= self.model_id,
            contents = prompt
        )

        limpo = response.text.replace("```json", "").replace("```", "").strip()

        return json.loads(limpo)
    def explicar_match(self, query, documentos):
        prompt = f"Com base na pergunta '{query}', explique porque estes candidatos são ideais: {documentos}"

        response = self.client.models.generate_content(model=self.model_id, contents=prompt)

        
        return response.text