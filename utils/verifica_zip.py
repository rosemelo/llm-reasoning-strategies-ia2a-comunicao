import os
import zipfile
import pandas as pd
from llama_index.core.query_engine import PandasQueryEngine

import logging
from llama_index.core import PromptTemplate

DATA_DIR = "data"
ZIP_FILE = "202401_NFs.zip"
CABECALHO_FILE = "202401_NFs_Cabecalho.csv"
ITENS_FILE = "202401_NFs_Itens.csv"

# === Configuração de logs (opcional, mas útil) ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

def unzip_files(zip_path, extract_to):
    """Descompacta arquivos de forma segura."""
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
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

def load_data():
    cabecalho_path = os.path.join(DATA_DIR, CABECALHO_FILE)
    itens_path = os.path.join(DATA_DIR, ITENS_FILE)
    try:
        cabecalho = pd.read_csv(cabecalho_path)
        itens = pd.read_csv(itens_path)
        logging.info(f"🗂️ Dados carregados: Cabeçalho({cabecalho.shape[0]} linhas), Itens({itens.shape[0]} linhas)")
        return cabecalho, itens
    except FileNotFoundError:
        logging.error("❌ Um ou ambos os arquivos CSV não foram encontrados. Verifique se a descompactação ocorreu corretamente.")
        raise
    except pd.errors.EmptyDataError:
        logging.error("❌ Um ou ambos os arquivos CSV estão vazios.")
        raise
    except pd.errors.ParserError as e:
        logging.error(f"❌ Erro ao ler os arquivos CSV: {e}")
        raise

class TextOutputProcessor:
    def parse(self, output: str):
        return output  # Retorna a resposta textual simples

    def get_format_instructions(self) -> str:
        return "Retorne a resposta em texto simples."

def create_query_engine(df, name="Tabela"):
    logging.info(f"🔎 Criando motor de consulta para: {name}")
    pandas_prompt = PromptTemplate(
        """\
Você é um agente capaz de responder perguntas sobre um DataFrame do Pandas.
Dado o DataFrame abaixo, cuja representação (e cabeçalho) é:
{df_str}

Responda à pergunta "{query_str}" de forma concisa.
Você DEVE retornar APENAS a resposta textual e nada mais.
NÃO inclua nenhuma formatação adicional, como explicações ou código Python.
"""
    )
    engine = PandasQueryEngine(
        df=df,
        verbose=False,
        llm=None,
        pandas_prompt=pandas_prompt,
        output_processor=TextOutputProcessor()
    )
    return engine

if __name__ == "__main__":
    logging.info("🚀 Iniciando script de utilidades (para testes).")
    check_and_unzip()
    try:
        cabecalho_df, itens_df = load_data()
        cabecalho_engine = create_query_engine(cabecalho_df, "Notas Fiscais - Cabeçalho")
        itens_engine = create_query_engine(itens_df, "Notas Fiscais - Itens")

        while True:
            pergunta = input("\n❓ Digite sua pergunta (ou 'sair' para encerrar):\n> ")
            if pergunta.lower() in ["sair", "exit", "quit"]:
                logging.info("👋 Encerrando agente de teste.")
                break

            try:
                resposta_cab = cabecalho_engine.query(pergunta)
                print(f"\n📄 Resposta do Cabeçalho: {resposta_cab.response}")
            except Exception as e:
                logging.error(f"⚠️ Erro ao consultar o cabeçalho: {e}")

            try:
                resposta_itens = itens_engine.query(pergunta)
                print(f"\n📦 Resposta dos Itens: {resposta_itens.response}")
            except Exception as e:
                logging.error(f"⚠️ Erro ao consultar os itens: {e}")

    except Exception as e:
        logging.critical(f"❌ Erro crítico na execução: {e}")
