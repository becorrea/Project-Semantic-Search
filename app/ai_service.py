import fitz 
import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self):
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise Exception("API não encontrada no arquivo .env")
        
        self.client = OpenAI(api_key=api_key)
        self.model = 'gpt-4o-mini'
        
    def extrair_pdf(self, content: bytes) -> str:
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for pagina in doc:
                text += pagina.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            raise Exception(f"Erro ao ler o arquivo PDF: {str(e)}")
    
    def _parse_json_seguro(self, texto: str) -> dict:
        try:
            texto = texto.replace("```json", "").replace("```", "").strip()
            return json.loads(texto)
        except json.JSONDecodeError:
            raise Exception("Resposta da IA não é um JSON válido")
    
    def extrair_requisitos_vaga(self, texto_vaga: str) -> dict:
        prompt = f"""
        Você é um especialista em Recrutamento. Analise a descrição da vaga abaixo e extraia:
        1. Um resumo focado APENAS nas habilidades técnicas, responsabilidades e requisitos obrigatórios.
        2. A localização da vaga (Cidade/Estado) se houver.
        3. A categoria da vaga (Tecnologia, Vendas, etc).
        

        Texto da vaga:
        {texto_vaga}

        Responda estritamente um JSON neste formato:
        {{
            "localizacao": "Cidade - UF" (ou null),
            "categoria": "Area" (ou null),
            "descricao": "Descricao da vaga, sobre a empresa etc"
        }}
        """
        raise Exception("Erro ao processar vaga no Gemini")
    
    def extrair_dados(self, texto_pdf: str):
        prompt = f"""
            Você é um sistema de extração de dados estruturados a partir de currículos.

            Sua tarefa é:
            - Analisar o texto fornecido
            - Extrair informações EXATAMENTE no formato JSON abaixo
            - NÃO inventar dados
            - NÃO explicar nada
            - NÃO usar markdown
            - NÃO retornar texto fora do JSON

            Formato obrigatório da resposta:
            {{
            "nome": "",
            "categoria": "",
            "localizacao": "",
            "cargo": "",
            "skills": [],
            "cursos_formacoes": "",
            "experiencia": ""
            }}

            REGRAS IMPORTANTES:
            - Padronize SEMPRE para o formato: "Cidade - Estado (Sigla), País (em Português)"
            - Exemplo: "São Paulo - SP, Brasil" (mesmo que no texto esteja 'Sao Paulo, Brazil')
            - Se não houver cidade, coloque apenas o País: "Brasil"
            - Categoria significa a área de atuação (Ex: Tecnologia, Vendas, Marketing etc.)
            - Se uma informação não existir claramente no texto, use string vazia "" ou lista vazia []
            - "skills" DEVE ser uma lista de strings
            - Não traduza nem reescreva informações, apenas extraia
            - Preserve termos técnicos
            

            Texto do currículo:
            <<<
            {texto_pdf}
            >>>
            """

        for tentativa in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você responde apenas JSON válido. Nunca escreva texto fora do JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0,
                    response_format={"type": "json_object"}
                )

                conteudo = response.choices[0].message.content
                return self._parse_json_seguro(conteudo)

            except Exception as e:
                if tentativa < 2:
                    time.sleep(1.5)
                    continue
                raise Exception(f"Erro ao extrair currículo: {str(e)}")
        