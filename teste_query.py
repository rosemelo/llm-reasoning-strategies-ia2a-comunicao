import pandas as pd
from llama_index.experimental.query_engine import PandasQueryEngine
# REMOVA: from llama_index.llms.openai import OpenAI # Não usaremos mais OpenAI
from llama_index.llms.groq import Groq   # AGORA USE GROQ
import os
from dotenv import load_dotenv # Importa load_dotenv

# Carrega as variáveis de ambiente no início do script
load_dotenv()

# --- Configuração do LLM ---
# REMOVA as linhas da OpenAI
# openai_api_key = os.getenv("OPENAI_API_KEY")
# if openai_api_key is None:
#     raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente. Verifique seu arquivo .env.")
# llm = OpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)

# AGORA OBTENHA A CHAVE DA GROQ
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key is None:
    raise ValueError("GROQ_API_KEY não encontrada nas variáveis de ambiente. Verifique seu arquivo .env.")

# Inicializa o modelo Groq (ex: "llama3-8b-8192" ou "mixtral-8x7b-32768")
# Verifique os modelos disponíveis na documentação da Groq.
llm = Groq(model="llama3-8b-8192", api_key=groq_api_key)


# Caminhos dos arquivos (agora podem vir do .env se quiser, mas para teste local, fixo é ok)
DATA_DIR = os.getenv("DATA_DIR", "data")
ITENS_CSV = os.getenv("ITENS_FILE", "202401_NFs_Itens.csv")

# Carregar CSV (recomendado usar o ITENS_CSV por ser mais completo)
csv_file_path = os.path.join(DATA_DIR, ITENS_CSV)
df = pd.read_csv(csv_file_path)

# Corrigir nomes das colunas com espaços
df.columns = df.columns.str.strip()

# Conversão de tipos de dados numéricos (muito importante para cálculos)
numeric_cols = ['VALOR NOTA FISCAL', 'VALOR TOTAL', 'VALOR UNITÁRIO', 'QUANTIDADE']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

print(f"Colunas disponíveis no {csv_file_path}:")
print(df.columns.tolist())

print("\nPrimeiras linhas do CSV:")
print(df.head())

# Criar o Query Engine
query_engine = PandasQueryEngine(df=df, verbose=True, llm=llm)

# Perguntas de exemplo (adaptadas para as colunas do seu CSV e para o modelo de linguagem)
perguntas = [
    # Esta pergunta já funcionou bem, pois é direta.
    "Quantas notas fiscais únicas existem nesta tabela, considerando a coluna 'CHAVE DE ACESSO'?",

    # Esta pergunta já funcionou bem.
    "Qual é a média do 'VALOR NOTA FISCAL' no DataFrame?", # Adicionei 'no DataFrame' para maior clareza

    # Esta pergunta já funcionou bem.
    "Liste todos os valores únicos na coluna 'UF EMITENTE'.",

    # Esta pergunta já funcionou bem.
    "Qual é a soma total dos valores da coluna 'VALOR TOTAL' dos itens?", # Mais específico sobre "itens" e "coluna"

    # Esta foi a que o agente teve dificuldade na interpretação.
    # Reforçamos o nome da coluna e o valor exato.
    "Quantas operações (linhas) na tabela 'Itens' tiveram a 'PRESENÇA DO COMPRADOR' igual a '1 - OPERAÇÃO PRESENCIAL'?",

    # Esta pergunta já funcionou bem.
    "Quais são as 3 'DESCRIÇÃO DO PRODUTO/SERVIÇO' mais frequentes e suas respectivas contagens?",

    # Esta também teve dificuldade, principalmente na coluna e no filtro.
    # Especificamos a coluna correta e o que queremos (o valor máximo).
    "Qual é o valor máximo encontrado na coluna 'VALOR UNITÁRIO' para os produtos cuja 'DESCRIÇÃO DO PRODUTO/SERVIÇO' contém 'AGUA MINERAL NATURAL, TIPO SEM GAS MATERIAL EMBALAGEM PLASTICO, TIPO RETORNAVEL'?",

    # Esta pergunta já funcionou bem.
    "Quais são as 5 'RAZÃO SOCIAL EMITENTE' que mais emitiram notas, listando-as com suas contagens?",

    # Esta pergunta já funcionou bem, mas especificamos a coluna de saída e a tabela.
    "Qual o 'VALOR TOTAL' (da coluna 'VALOR TOTAL') da nota fiscal que possui a 'CHAVE DE ACESSO' igual a '41240106267630001509550010035101291224888487' na tabela de itens?",
]

# Executar as perguntas
for pergunta in perguntas:
    print(f"\n--- Pergunta: {pergunta} ---")
    try:
        resposta = query_engine.query(pergunta)
        print(f"Resposta: {resposta}")
    except Exception as e:
        print(f"Erro ao processar esta pergunta: {e}")