import os
import zipfile
import pandas as pd
from llama_index.experimental.query_engine import PandasQueryEngine


# 🚀 Descompactar
zip_path = 'data/202401_NFs.zip'
extract_folder = 'data/'

if zipfile.is_zipfile(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
        print("✅ Arquivo descompactado!")

# 🚀 Ler CSV
cabecalho_path = os.path.join(extract_folder, '202401_NFs_Cabecalho.csv')
itens_path = os.path.join(extract_folder, '202401_NFs_Itens.csv')

df_cabecalho = pd.read_csv(cabecalho_path)
df_itens = pd.read_csv(itens_path)

print(f"→ Cabeçalho: {df_cabecalho.shape}")
print(f"→ Itens: {df_itens.shape}")

# 🚀 Query Engines
cabecalho_engine = PandasQueryEngine(df_cabecalho)
itens_engine = PandasQueryEngine(df_itens)

# 🚀 Loop de Perguntas
print("\n❓ Pergunte sobre os dados (digite 'sair' para encerrar)\n")

while True:
    pergunta = input("👉 Sua pergunta: ")

    if pergunta.lower() in ["sair", "exit", "quit"]:
        print("👋 Encerrando...")
        break

    print("\n🔍 Cabeçalho:")
    resp_cab = cabecalho_engine.query(pergunta)
    print(resp_cab.response)

    print("\n🔍 Itens:")
    resp_itens = itens_engine.query(pergunta)
    print(resp_itens.response)

    print("\n" + "-" * 50 + "\n")
