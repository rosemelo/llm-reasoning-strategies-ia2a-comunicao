import pandas as pd
from llama_index.query_engine.pandas import PandasQueryEngine

# Carregar CSV
df = pd.read_csv("data/202401_NFs_Cabecalho.csv")

# Criar o Query Engine
query_engine = PandasQueryEngine(df)

# Fazer uma pergunta
response = query_engine.query("Quantas notas fiscais tem na tabela?")

print(response)

