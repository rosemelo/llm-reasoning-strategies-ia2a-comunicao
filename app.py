import streamlit as st
import pandas as pd
import zipfile
import os
from llama_index.experimental.query_engine import PandasQueryEngine
# REMOVA: from llama_index.llms.openai import OpenAI # Não usaremos mais OpenAI
from llama_index.llms.groq import Groq # AGORA USE GROQ
from dotenv import load_dotenv

# Carrega as variáveis de ambiente no início do script
load_dotenv()

# --- Configurações e Variáveis ---
DATA_DIR = os.getenv("DATA_DIR", "data") # Pega do .env, com fallback
CABECALHO_CSV = os.getenv("CABECALHO_FILE", "202401_NFs_Cabecalho.csv") # Pega do .env
ITENS_CSV = os.getenv("ITENS_FILE", "202401_NFs_Itens.csv") # Pega do .env
ZIP_FILENAME = "202401_NFs.zip" # Mantemos fixo, pois o zip tem um nome específico

# --- Funções de Utilitário ---
def unzip_if_needed():
    # Verifica se os CSVs já existem. Se não, tenta descompactar o ZIP.
    if not (os.path.exists(os.path.join(DATA_DIR, CABECALHO_CSV)) and os.path.exists(os.path.join(DATA_DIR, ITENS_CSV))):
        zip_path = os.path.join(DATA_DIR, ZIP_FILENAME)
        if os.path.exists(zip_path):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(DATA_DIR)
            st.success("Arquivos CSV descompactados com sucesso!")
        else:
            st.error(f"Arquivo ZIP '{ZIP_FILENAME}' não encontrado em '{DATA_DIR}'. Por favor, faça o upload.")
            st.stop() # Interrompe a execução se o ZIP não estiver presente para descompactar

def load_data():
    cabecalho = pd.read_csv(os.path.join(DATA_DIR, CABECALHO_CSV))
    itens = pd.read_csv(os.path.join(DATA_DIR, ITENS_CSV))
    
    # Limpar espaços em branco nos nomes das colunas de ambos os DataFrames
    cabecalho.columns = cabecalho.columns.str.strip()
    itens.columns = itens.columns.str.strip()

    # Converter colunas numéricas que podem ser lidas como string para float
    # Use errors='coerce' para transformar valores inválidos em NaN
    numeric_cols_cabecalho = ['VALOR NOTA FISCAL']
    for col in numeric_cols_cabecalho:
        if col in cabecalho.columns:
            cabecalho[col] = pd.to_numeric(cabecalho[col], errors='coerce')
    
    numeric_cols_itens = ['VALOR TOTAL', 'VALOR UNITÁRIO', 'QUANTIDADE']
    for col in numeric_cols_itens:
        if col in itens.columns:
            itens[col] = pd.to_numeric(itens[col], errors='coerce')

    return cabecalho, itens

# --- Função principal de resposta com LlamaIndex ---
@st.cache_resource
def get_llm():
    # AGORA OBTENHA A CHAVE DA GROQ
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key is None:
        st.error("Erro: A variável de ambiente GROQ_API_KEY não está configurada. Verifique seu arquivo .env.")
        st.stop() # Para a execução do Streamlit se a chave não for encontrada
    
    # Inicializa o modelo Groq (ex: "llama3-8b-8192" ou "mixtral-8x7b-32768")
    # Verifique os modelos disponíveis na documentação da Groq.
    return Groq(model="llama3-8b-8192", api_key=groq_api_key)

@st.cache_resource
def get_query_engine(df):
    llm = get_llm()
    return PandasQueryEngine(df=df, verbose=True, llm=llm)

def responder_pergunta_com_agente(df, pergunta):
    query_engine = get_query_engine(df)
    try:
        response = query_engine.query(pergunta)
        return str(response) # Converte a resposta do LlamaIndex para string
    except Exception as e:
        return f"Erro ao processar a pergunta com o agente: {e}. Tente reformular ou verifique os dados."


# --- Interface Streamlit ---
st.set_page_config(page_title="Agente de Consulta de Notas Fiscais", layout="wide")
st.title("🧠 Agente de Consulta de Notas Fiscais")

# Garantir pasta data
os.makedirs(DATA_DIR, exist_ok=True)

uploaded_file = st.file_uploader(f"📦 Faça upload do arquivo ZIP das notas fiscais ({ZIP_FILENAME})", type="zip")

if uploaded_file:
    # Salva o arquivo ZIP
    zip_path_to_save = os.path.join(DATA_DIR, ZIP_FILENAME)
    with open(zip_path_to_save, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Arquivo ZIP recebido com sucesso! Tentando descompactar...")
    unzip_if_needed()
    # Recarrega a página para refletir os novos arquivos extraídos e permitir o carregamento
    st.experimental_rerun()
else:
    # Se nenhum arquivo foi feito upload, verifica se os CSVs já existem ou se o ZIP existe para descompactar
    if not (os.path.exists(os.path.join(DATA_DIR, CABECALHO_CSV)) and os.path.exists(os.path.join(DATA_DIR, ITENS_CSV))):
        st.warning(f"Por favor, faça upload do arquivo ZIP ({ZIP_FILENAME}) para começar, ou coloque-o na pasta '{DATA_DIR}'.")
        # Se o ZIP estiver lá, tenta descompactar
        if os.path.exists(os.path.join(DATA_DIR, ZIP_FILENAME)):
             unzip_if_needed()
        else:
            st.stop() # Interrompe se não tiver nem ZIP nem CSVs
    else:
        st.info("Usando arquivos CSV extraídos previamente.")

try:
    cabecalho_df, itens_df = load_data()
    st.success("Dados carregados com sucesso!")
except Exception as e:
    st.error(f"Erro crítico ao carregar os dados: {e}. Certifique-se de que os arquivos CSV estão corretos e na pasta '{DATA_DIR}'.")
    st.stop() # Para a execução se não conseguir carregar os dados


aba = st.selectbox("Escolha a tabela para consultar:", ["Cabeçalho", "Itens"])

df_selecionado = cabecalho_df if aba == "Cabeçalho" else itens_df

# Exibe as colunas do DataFrame selecionado para ajudar o usuário
st.info(f"Colunas disponíveis na tabela '{aba}': **{', '.join(df_selecionado.columns.tolist())}**")

st.subheader("❓ Faça sua pergunta sobre os dados:")
pergunta = st.text_input("Digite aqui sua pergunta:")

if pergunta:
    with st.spinner("Consultando o agente..."):
        # Chamar a função do agente LlamaIndex
        resposta = responder_pergunta_com_agente(df_selecionado, pergunta)
    st.success(resposta)