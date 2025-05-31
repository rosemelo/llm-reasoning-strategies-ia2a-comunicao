import os
import zipfile
import pandas as pd
from llama_index.query_engine import PandasQueryEngine

# Configurações
DATA_DIR = "data"
ZIP_FILE = "202401_NFs.zip"
CABECALHO_FILE = "202401_NFs_Cabecalho.csv"
ITENS_FILE = "202401_NFs_Itens.csv"

def unzip_files(zip_path, extract_to):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("✅ Arquivos descompactados.")

def check_and_unzip():
    cabecalho_path = os.path.join(DATA_DIR, CABECALHO_FILE)
    itens_path = os.path.join(DATA_DIR, ITENS_FILE)
    if os.path.exists(cabecalho_path) and os.path.exists(itens_path):
        print("✔️ Arquivos CSV já estão presentes. Pulando descompactação.")
    else:
        print("📦 Arquivos CSV não encontrados. Descompactando...")
        unzip_files(os.path.join(DATA_DIR, ZIP_FILE), DATA_DIR)

def load_data():
    cabecalho = pd.read_csv(os.path.join(DATA_DIR, CABECALHO_FILE))
    itens = pd.read_csv(os.path.join(DATA_DIR, ITENS_FILE))
    print(f"🗂️ Dados carregados: Cabeçalho({cabecalho.shape[0]} linhas), Itens({itens.shape[0]} linhas)")
    return cabecalho, itens

def create_query_engine(df, name="Tabela"):
    # Cria o agente para consultar o dataframe
    engine = PandasQueryEngine(df=df, verbose=True)
    # Você pode customizar prompts se quiser (ver docs do llama_index)
    return engine

def main():
    print("🔍 Iniciando agente de consulta de Notas Fiscais...")
    check_and_unzip()
    cabecalho_df, itens_df = load_data()

    cabecalho_engine = create_query_engine(cabecalho_df, "Notas Fiscais - Cabeçalho")
    itens_engine = create_query_engine(itens_df, "Notas Fiscais - Itens")

    while True:
        pergunta = input("\n❓ Digite sua pergunta (ou 'sair' para encerrar):\n> ")
        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("👋 Encerrando agente. Até mais!")
            break
        try:
            print("\n📄 Resposta do Cabeçalho:")
            resposta_cabecalho = cabecalho_engine.query(pergunta)
            print(resposta_cabecalho.response)
        except Exception as e:
            print(f"⚠️ Erro ao consultar cabeçalho: {e}")

        try:
            print("\n📦 Resposta dos Itens:")
            resposta_itens = itens_engine.query(pergunta)
            print(resposta_itens.response)
        except Exception as e:
            print(f"⚠️ Erro ao consultar itens: {e}")

if __name__ == "__main__":
    main()
