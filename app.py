import streamlit as st
import pandas as pd
import numpy as np
import os
import zipfile
import json
import re
from dotenv import load_dotenv

# --- Imports do agente de NF (LLM) ---
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.llms.groq import Groq

# --- Imports do agente EDA ---
from utils import eda, memory

# --- Configurações ---
load_dotenv()
st.set_page_config(page_title="Agentes Autônomos", layout="wide")

DATA_DIR = os.getenv("DATA_DIR", "data")
CABECALHO_CSV = os.getenv("CABECALHO_FILE", "202401_NFs_Cabecalho.csv")
ITENS_CSV = os.getenv("ITENS_FILE", "202401_NFs_Itens.csv")
ZIP_FILENAME = "202401_NFs.zip"

# ===============================
# Funções para Notas Fiscais (desafio anterior)
# ===============================
def unzip_if_needed():
    zip_path = os.path.join(DATA_DIR, ZIP_FILENAME)
    if os.path.exists(zip_path) and \
       (not os.path.exists(os.path.join(DATA_DIR, CABECALHO_CSV)) or \
        not os.path.exists(os.path.join(DATA_DIR, ITENS_CSV))):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(DATA_DIR)
            st.success("Arquivos CSV descompactados com sucesso!")
            return True
        except Exception as e:
            st.error(f"Erro ao descompactar: {e}")
            return False
    return False

def load_data_nf():
    cabecalho = pd.read_csv(os.path.join(DATA_DIR, CABECALHO_CSV))
    itens = pd.read_csv(os.path.join(DATA_DIR, ITENS_CSV))
    cabecalho.columns = cabecalho.columns.str.strip()
    itens.columns = itens.columns.str.strip()
    for col in ['VALOR NOTA FISCAL']:
        if col in cabecalho.columns:
            cabecalho[col] = pd.to_numeric(cabecalho[col], errors="coerce")
    for col in ['VALOR TOTAL', 'VALOR UNITÁRIO', 'QUANTIDADE']:
        if col in itens.columns:
            itens[col] = pd.to_numeric(itens[col], errors="coerce")
    return cabecalho, itens

@st.cache_resource
def get_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key is None:
        st.error("Erro: GROQ_API_KEY não configurada.")
        st.stop()
    return Groq(model="llama3-8b-8192", api_key=groq_api_key)

@st.cache_resource
def get_query_engine(df):
    llm = get_llm()
    return PandasQueryEngine(
        df=df,
        verbose=True,
        llm=llm,
        system_prompt="""
        Você é um assistente de análise de dados.
        Responda perguntas sobre o DataFrame fornecido.
        Se a resposta for tabular, retorne como JSON válido (lista de objetos).
        """
    )

def responder_pergunta_com_agente(df, pergunta):
    query_engine = get_query_engine(df)
    try:
        response_obj = query_engine.query(pergunta)
        content = str(response_obj)
        try:
            data = json.loads(content)
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
        except:
            pass
        return content
    except Exception as e:
        return f"Erro: {e}"

# ===============================
# Funções para EDA (desafio extra)
# ===============================
def handle_question(question, df):
    q = question.lower()
    if "tipo" in q:
        return ("Tipos de colunas:", eda.get_column_types(df))
    m = re.search(r'm[eé]dia(?: de| da| do)?\s+([A-Za-z0-9_]+)', q)
    if m:
        col = m.group(1)
        if col in df.columns:
            return (f"Média de {col}: {df[col].mean()}", None)
    if "hist" in q or "distribui" in q:
        m = re.search(r'(?:de|da|do)\s+([A-Za-z0-9_]+)', q)
        if m and m.group(1) in df.columns:
            imgs = eda.generate_histograms(df, [m.group(1)])
            return (f"Histograma de {m.group(1)} gerado.", imgs.get(m.group(1)))
        imgs = eda.generate_histograms(df)
        return ("Histogramas gerados.", ", ".join(list(imgs.values())[:5]))
    if "correl" in q:
        corr, path = eda.correlation_matrix(df)
        return ("Matriz de correlação gerada.", path)
    if "outlier" in q or "atípico" in q:
        idxs, details = eda.detect_outliers_iqr(df)
        return (f"Foram encontrados {len(idxs)} outliers.", details)
    if "cluster" in q or "agrup" in q:
        labels, path = eda.cluster_analysis(df, n_clusters=3)
        return ("Cluster analysis executada.", path)
    return ("Não entendi a pergunta.", None)

# ===============================
# Interface principal
# ===============================
st.title("🧠 Agentes Autônomos")
aba = st.sidebar.radio("Escolha o agente:", ["Notas Fiscais (LLM)", "EDA Genérico"])

if aba == "Notas Fiscais (LLM)":
    st.header("Agente de Consulta de Notas Fiscais")
    os.makedirs(DATA_DIR, exist_ok=True)
    uploaded_file = st.file_uploader(f"📦 Upload ZIP ({ZIP_FILENAME})", type="zip")
    if uploaded_file:
        zip_path = os.path.join(DATA_DIR, ZIP_FILENAME)
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("ZIP recebido! Tentando descompactar...")
        if unzip_if_needed():
            st.experimental_rerun()
    if os.path.exists(os.path.join(DATA_DIR, CABECALHO_CSV)) and \
       os.path.exists(os.path.join(DATA_DIR, ITENS_CSV)):
        cabecalho_df, itens_df = load_data_nf()
        tabela = st.selectbox("Escolha a tabela:", ["Cabeçalho", "Itens"])
        df = cabecalho_df if tabela == "Cabeçalho" else itens_df
        st.write("Colunas disponíveis:", df.columns.tolist())
        pergunta = st.text_input("Pergunta sobre os dados")
        if pergunta:
            resp = responder_pergunta_com_agente(df, pergunta)
            if isinstance(resp, list):
                st.dataframe(pd.DataFrame(resp))
            else:
                st.write(resp)
    else:
        st.info("Faça upload do ZIP para começar.")

elif aba == "EDA Genérico":
    st.header("Agente EDA Genérico (qualquer CSV)")
    uploaded = st.sidebar.file_uploader("📂 Upload de CSV", type=["csv", "txt"])
    if uploaded:
        df = eda.load_csv(uploaded)
        st.write("### Visualização inicial")
        st.dataframe(df.head())
        if st.button("Descrição básica"):
            st.dataframe(eda.describe_numeric(df))
        if st.button("Histogramas"):
            imgs = eda.generate_histograms(df)
            for c, path in imgs.items():
                if path.endswith(".png"):
                    st.image(path, caption=c)
        if st.button("Correlação"):
            corr, path = eda.correlation_matrix(df)
            st.dataframe(corr)
            st.image(path)
        if st.button("Outliers (IQR)"):
            idxs, details = eda.detect_outliers_iqr(df)
            st.write(f"{len(idxs)} outliers detectados.")
            st.write(details)
        st.write("---")
        q = st.text_input("Pergunta em linguagem natural")
        if st.button("Perguntar"):
            ans, extra = handle_question(q, df)
            st.write("Resposta:", ans)
            if extra and isinstance(extra, str) and extra.endswith(".png"):
                st.image(extra)
            memory.add_memory(q, ans)
        if st.checkbox("Mostrar memória"):
            st.write(memory.get_memory())
    else:
        st.info("Envie um CSV para iniciar a análise.")
