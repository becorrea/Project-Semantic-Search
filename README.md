# PROJETO INSANO

O projeto consiste em um buscador e assimilador semântico, transformando textos em vetores e comparando-os com uma query específica.

# OBJETIVO

Automatizar o processo de coerência em situações específicas. Ex.: Assimilar currículos com determinada vaga e ordenar do mais coerente ao menos coerente. Isso reduz muito a mão de obra humana na hora de analisar palavras-chave de inúmeros currículos, além de facilitar na pesquisa de categorias específicas.

## Tecnologias

- Python 3.14
- scikit-learn
- numpy
- sentence-transformer
- cosine_similarit


## Instalação

pip install -r requeriments.txt

## Como usar

python main.py

## Estrutura do Projeto

A pasta main.py é o core do projeto, é nela que os textos são analisados, vetorizados, relacionados e por fim rankeados

## Exemplo de Uso

## Limitações / próximos passos

- Sincronizar com uma DB
- Fazer a DB híbrida
- FastAPI + arquitetura limpa
- LLM
- Frontend (html+css)
- Frontend (react)
- MVP
- PyTorch(se possível)