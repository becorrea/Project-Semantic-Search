import fitz 
import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

#Configuração da API OpenAI
class AIService:
    def __init__(self):
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise Exception("API não encontrada no arquivo .env")
        
        self.client = OpenAI(api_key=api_key)
        self.model = 'gpt-4o-mini'

    #Função que extrai o texto de um PDF   
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
    
    #Função que utiliza da API OpenAI para extrair conteúdos específicos do PDF
    def extrair_requisitos_vaga(self, texto_vaga: str) -> dict:
        prompt = f"""
        Você é um recrutador especialista. Analise a DESCRIÇÃO DA VAGA abaixo e extraia os requisitos técnicos e comportamentais.
        Retorne APENAS um JSON válido.
        
        REGRAS:
        1. "skills": Liste as tecnologias, ferramentas e competências EXIGIDAS.
        2. "localizacao": Se for remoto, considere a localizacao como Brasil. Se tiver cidade, padronize "Cidade - UF, País".
        3. "cargo": O título principal da vaga.
        4. "categoria": A área da vaga (ex: Tecnologia, Vendas, Saúde).
        5. "senioridade": (Junior, Pleno, Senior, Especialista) - infira pelo texto.


        FORMATO JSON:
        {{
            "cargo": "Titulo da Vaga",
            "localizacao": "Localização Padronizada",
            "categoria": "Area",
            "skills": ["Skill1", "Skill2"],
            "senioridade": "Nivel"
        }}

        DESCRIÇÃO DA VAGA:
        {texto_vaga}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    { "role": "system", "content": "Você extrai requisitos de vagas em JSON estrito." },
                    { "role": "user", "content": prompt }
                ],
                temperature=0,
                response_format={ "type": "json_object" }
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Erro na IA (Vaga): {e}")
            # Retorna estrutura vazia para não quebrar a API
            return {"cargo": "", "localizacao": "", "skills": [], "categoria": ""}
    
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
        