import os
import zipfile
import pandas as pd
from llama_index.query_engine.pandas import PandasQueryEngine
from utils.verifica_zip import check_and_unzip, load_data, create_query_engine
from dotenv import load_dotenv
import logging
import sys


# === Configuração de logs ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# === Carregar variáveis de ambiente ===
load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "data")
ZIP_FILE = os.getenv("ZIP_FILE", "202401_NFs.zip")
CABECALHO_FILE = os.getenv("CABECALHO_FILE", "202401_NFs_Cabecalho.csv")
ITENS_FILE = os.getenv("ITENS_FILE", "202401_NFs_Itens.csv")


# === Funções utilitárias ===

def unzip_files(zip_path, extract_to):
    """Descompacta arquivos de forma segura."""
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                extracted_path = os.path.abspath(os.path.join(extract_to, member.filename))

                if not extracted_path.startswith(os.path.abspath(extract_to)):
                    raise Exception(f"⚠️ Tentativa de path traversal detectada: {member.filename}")

                zip_ref.extract(member, extract_to)

        logging.info("✅ Arquivos descompactados com sucesso.")
    except Exception as e:
        logging.error(f"❌ Erro ao descompactar arquivos: {e}")
        raise


def check_and_unzip():
    cabecalho_path = os.path.join(DATA_DIR, CABECALHO_FILE)
    itens_path = os.path.join(DATA_DIR, ITENS_FILE)

    if os.path.exists(cabecalho_path) and os.path.exists(itens_path):
        logging.info("✔️ Arquivos CSV já estão presentes. Pulando descompactação.")
    else:
        logging.info("📦 Arquivos CSV não encontrados. Descompactando...")
        unzip_files(os.path.join(DATA_DIR, ZIP_FILE), DATA_DIR)


def validate_csv(file_path, expected_columns):
    """Valida se o CSV tem as colunas esperadas."""
    df = pd.read_csv(file_path, nrows=5)  # Lê apenas as primeiras linhas para validar
    missing = [col for col in expected_columns if col not in df.columns]
    if missing:
        raise ValueError(f"❌ CSV {file_path} está faltando as colunas: {missing}")
    return True


def load_data():
    cabecalho_path = os.path.join(DATA_DIR, CABECALHO_FILE)
    itens_path = os.path.join(DATA_DIR, ITENS_FILE)

    validate_csv(cabecalho_path, expected_columns=["ID", "Data", "Valor"])  # Ajuste conforme suas colunas reais
    validate_csv(itens_path, expected_columns=["ID", "Produto", "Quantidade", "Valor"])

    cabecalho = pd.read_csv(cabecalho_path)
    itens = pd.read_csv(itens_path)

    logging.info(f"🗂️ Dados carregados: Cabeçalho({cabecalho.shape[0]} linhas), Itens({itens.shape[0]} linhas)")
    return cabecalho, itens


def create_query_engine(df, name="Tabela"):
    logging.info(f"🔎 Criando motor de consulta para: {name}")
    engine = PandasQueryEngine(df=df, verbose=False)
    return engine


# === Função principal ===

def main():
    logging.info("🚀 Iniciando Agente de Consulta de Notas Fiscais...")

    try:
        check_and_unzip()
        cabecalho_df, itens_df = load_data()

        cabecalho_engine = create_query_engine(cabecalho_df, "Notas Fiscais - Cabeçalho")
        itens_engine = create_query_engine(itens_df, "Notas Fiscais - Itens")

        while True:
            pergunta = input("\n❓ Digite sua pergunta (ou 'sair' para encerrar):\n> ")
            if pergunta.lower() in ["sair", "exit", "quit"]:
                logging.info("👋 Encerrando agente. Até mais!")
                break

            try:
                print("\n📄 Resposta do Cabeçalho:")
                resposta_cabecalho = cabecalho_engine.query(pergunta)
                print(resposta_cabecalho.response)
            except Exception as e:
                logging.error(f"⚠️ Erro ao consultar cabeçalho: {e}")

            try:
                print("\n📦 Resposta dos Itens:")
                resposta_itens = itens_engine.query(pergunta)
                print(resposta_itens.response)
            except Exception as e:
                logging.error(f"⚠️ Erro ao consultar itens: {e}")

    except Exception as e:
        logging.critical(f"❌ Erro crítico na execução: {e}")


if __name__ == "__main__":
    main()
