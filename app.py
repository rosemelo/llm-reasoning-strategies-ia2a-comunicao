import streamlit as st
import pandas as pd
import zipfile
import os

DATA_DIR = "data"
ZIP_FILENAME = "202401_NFs.zip"
CABECALHO_CSV = "202401_NFs_Cabecalho.csv"
ITENS_CSV = "202401_NFs_Itens.csv"

def unzip_if_needed():
    if not (os.path.exists(os.path.join(DATA_DIR, CABECALHO_CSV)) and os.path.exists(os.path.join(DATA_DIR, ITENS_CSV))):
        with zipfile.ZipFile(os.path.join(DATA_DIR, ZIP_FILENAME), 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)

def load_data():
    cabecalho = pd.read_csv(os.path.join(DATA_DIR, CABECALHO_CSV))
    itens = pd.read_csv(os.path.join(DATA_DIR, ITENS_CSV))
    return cabecalho, itens

def responder_pergunta(df, pergunta):
    pergunta = pergunta.lower()
    
    # Exemplos simples de perguntas suportadas
    if "quantas notas" in pergunta or "quantos registros" in pergunta:
        return f"O dataframe tem {len(df)} registros."
    elif "quais fornecedores" in pergunta or "fornecedores" in pergunta:
        fornecedores = df['Fornecedor'].unique() if 'Fornecedor' in df.columns else None
        if fornecedores is not None:
            return f"Fornecedores encontrados: {', '.join(map(str, fornecedores[:10]))} (mostrar até 10)."
        else:
            return "Coluna 'Fornecedor' não encontrada nos dados selecionados."
    elif "valores totais" in pergunta or "valor total" in pergunta:
        if 'ValorTotal' in df.columns:
            total = df['ValorTotal'].sum()
            return f"O valor total é {total:.2f}."
        else:
            return "Coluna 'ValorTotal' não encontrada nos dados selecionados."
    else:
        return "Pergunta não reconhecida. Por favor, pergunte sobre quantidade, fornecedores ou valores totais."

st.set_page_config(page_title="Agente de Consulta de Notas Fiscais", layout="wide")
st.title("🧠 Agente de Consulta de Notas Fiscais")

# Garantir pasta data
os.makedirs(DATA_DIR, exist_ok=True)

uploaded_file = st.file_uploader("📦 Faça upload do arquivo ZIP das notas fiscais (202401_NFs.zip)", type="zip")

if uploaded_file:
    with open(os.path.join(DATA_DIR, ZIP_FILENAME), "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Arquivo ZIP recebido com sucesso!")
    unzip_if_needed()
else:
    if not (os.path.exists(os.path.join(DATA_DIR, CABECALHO_CSV)) and os.path.exists(os.path.join(DATA_DIR, ITENS_CSV))):
        st.warning("Por favor, faça upload do arquivo ZIP para começar.")
        st.stop()
    else:
        st.info("Usando arquivos CSV extraídos previamente.")

try:
    cabecalho_df, itens_df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

aba = st.selectbox("Escolha a tabela para consultar:", ["Cabeçalho", "Itens"])

df_selecionado = cabecalho_df if aba == "Cabeçalho" else itens_df

st.subheader("❓ Faça sua pergunta sobre os dados:")
pergunta = st.text_input("Digite aqui:")

if pergunta:
    with st.spinner("Consultando..."):
        resposta = responder_pergunta(df_selecionado, pergunta)
    st.success(resposta)
