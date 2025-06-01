import streamlit as st
from utils.verifica_zip import check_and_unzip, load_data, create_query_engine
from llama_index.core import Settings

# *** Adicione estas linhas no início do seu app.py ***
Settings.llm = None
Settings.embed_model = None # Opcional: desabilita o modelo de embedding também

st.set_page_config(page_title="Consulta de Notas Fiscais", layout="wide")

st.title("🔍 Consulta de Notas Fiscais - Janeiro 2024")

st.sidebar.header("⚙️ Configurações")
pergunta = st.text_input("Digite sua pergunta:")

if "cabecalho_engine" not in st.session_state:
    check_and_unzip()
    cabecalho_df, itens_df = load_data()
    st.session_state.cabecalho_engine = create_query_engine(cabecalho_df, "Notas Fiscais - Cabeçalho")
    st.session_state.itens_engine = create_query_engine(itens_df, "Notas Fiscais - Itens")

if pergunta:
    with st.spinner("Consultando..."):
        try:
            resposta_cab = st.session_state.cabecalho_engine.query(pergunta)
            resposta_itens = st.session_state.itens_engine.query(pergunta)

            st.subheader("📄 Resultado - Cabeçalho")
            st.write(resposta_cab.response)

            st.subheader("📦 Resultado - Itens")
            st.write(resposta_itens.response)

        except Exception as e:
            st.error(f"Erro na consulta: {e}")