import streamlit as st
import pandas as pd
import zipfile
import os
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.llms.groq import Groq
from dotenv import load_dotenv
import json

# Carrega as variáveis de ambiente no início do script
load_dotenv()

# --- Configurações e Variáveis ---
DATA_DIR = os.getenv("DATA_DIR", "data")
CABECALHO_CSV = os.getenv("CABECALHO_FILE", "202401_NFs_Cabecalho.csv")
ITENS_CSV = os.getenv("ITENS_FILE", "202401_NFs_Itens.csv")
ZIP_FILENAME = "202401_NFs.zip"

# --- Funções de Utilitário ---
def unzip_if_needed():
    zip_path = os.path.join(DATA_DIR, ZIP_FILENAME)
    # Verifica se o ZIP existe e se os CSVs não existem ainda
    if os.path.exists(zip_path) and \
       (not os.path.exists(os.path.join(DATA_DIR, CABECALHO_CSV)) or \
        not os.path.exists(os.path.join(DATA_DIR, ITENS_CSV))):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(DATA_DIR)
            st.success("Arquivos CSV descompactados com sucesso!")
            return True # Retorna True se descompactou
        except Exception as e:
            st.error(f"Erro ao descompactar o arquivo ZIP: {e}")
            return False # Retorna False em caso de erro
    return False # Retorna False se não precisou descompactar

def load_data():
    cabecalho = pd.read_csv(os.path.join(DATA_DIR, CABECALHO_CSV))
    itens = pd.read_csv(os.path.join(DATA_DIR, ITENS_CSV))
    
    cabecalho.columns = cabecalho.columns.str.strip()
    itens.columns = itens.columns.str.strip()

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
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key is None:
        st.error("Erro: A variável de ambiente GROQ_API_KEY não está configurada. Verifique seu arquivo .env.")
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
        Você é um assistente de análise de dados. Sua tarefa é responder perguntas sobre o DataFrame fornecido.
        Quando a pergunta solicitar uma lista de itens ou dados tabulares (como 'quais as 10 notas fiscais de maior valor?', 'listar produtos mais vendidos'),
        sempre formate sua resposta como um array de objetos JSON.
        Cada objeto JSON deve representar um item da lista e incluir as chaves mais relevantes (ex: 'numero_nota', 'valor', 'data', 'produto', 'quantidade').
        Certifique-se de que o JSON é válido e formatado corretamente.
        Para outras perguntas que não resultem em dados tabulares, responda em texto claro e conciso.
        """
    )

def responder_pergunta_com_agente(df, pergunta):
    query_engine = get_query_engine(df)
    try:
        response_obj = query_engine.query(pergunta)
        response_content = str(response_obj)

        # --- NOVA LÓGICA DE PÓS-PROCESSAMENTO ---
        # 1. Tentar parsear como JSON (se o modelo decidir seguir o prompt de JSON)
        try:
            data = json.loads(response_content)
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data # Retorna lista de dicionários para st.dataframe
        except json.JSONDecodeError:
            pass # Não era JSON válido, segue para o próximo tratamento

        # 2. Tentar detectar e formatar como lista de notas fiscais ou valores
        # Este é um padrão específico para a sua pergunta de notas fiscais
        if "VALOR NOTA FISCAL, dtype: float64" in response_content:
            st.warning("Detectada resposta tipo Pandas Series. Tentando formatar para lista.")
            # Remove o cabeçalho e rodapé do Series string
            clean_content = response_content.replace("Name: VALOR NOTA FISCAL, dtype: float64", "").strip()
            
            # Divide por linha, removendo linhas vazias
            lines = [line.strip() for line in clean_content.split('\n') if line.strip()]
            
            formatted_list = []
            for line in lines:
                parts = line.split(maxsplit=1) # Divide no primeiro espaço
                if len(parts) == 2:
                    nf_numero = parts[0]
                    valor = parts[1]
                    formatted_list.append({"Número NF": nf_numero, "Valor": float(valor)})
                else:
                    formatted_list.append({"Detalhe": line}) # Caso a linha não siga o padrão

            if formatted_list:
                return formatted_list # Retorna como lista de dicionários
            
        # 3. Se nenhuma das anteriores, retorna a string bruta
        return response_content 
            
    except Exception as e:
        return f"Erro ao processar a pergunta com o agente: {e}. Tente reformular ou verifique os dados."


# --- Interface Streamlit ---
st.set_page_config(page_title="Agente de Consulta de Notas Fiscais", layout="wide")
st.title("🧠 Agente de Consulta de Notas Fiscais")
st.markdown("""
Esta aplicação utiliza Inteligência Artificial para responder a perguntas sobre dados de notas fiscais.
Você pode fazer perguntas como 'Quais são as 5 notas fiscais de maior valor?' ou 'Liste os produtos mais vendidos'.
**Experimente perguntar e veja os resultados organizados!**
---
""")

# Garantir pasta data
os.makedirs(DATA_DIR, exist_ok=True)

# Variável para controlar se os dados estão prontos
data_ready = False

# --- Lógica de Upload e Carregamento de Dados ---
uploaded_file = st.file_uploader(f"📦 Faça upload do arquivo ZIP das notas fiscais ({ZIP_FILENAME})", type="zip")

if uploaded_file:
    zip_path_to_save = os.path.join(DATA_DIR, ZIP_FILENAME)
    with open(zip_path_to_save, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Arquivo ZIP recebido com sucesso! Tentando descompactar...")
    if unzip_if_needed(): # Tenta descompactar imediatamente após o upload
        st.experimental_rerun() # Recarrega para que os arquivos sejam detectados
    else:
        st.error("Falha na descompactação ou os arquivos já existiam.")

# Verifica se os arquivos CSV necessários existem
if os.path.exists(os.path.join(DATA_DIR, CABECALHO_CSV)) and \
   os.path.exists(os.path.join(DATA_DIR, ITENS_CSV)):
    try:
        cabecalho_df, itens_df = load_data()
        st.success("Dados carregados com sucesso!")
        data_ready = True # Define que os dados estão prontos
    except Exception as e:
        st.error(f"Erro crítico ao carregar os dados: {e}. Certifique-se de que os arquivos CSV estão corretos e na pasta '{DATA_DIR}'.")
        # Não usamos st.stop() aqui, mas sim data_ready = False, para que a interface não seja bloqueada
else:
    # Se os CSVs não existem, tenta descompactar o ZIP (caso o usuário tenha colocado manualmente)
    if unzip_if_needed():
        st.experimental_rerun() # Recarrega após descompactação
    else:
        st.warning(f"Por favor, faça upload do arquivo ZIP ({ZIP_FILENAME}) para começar, ou coloque-o na pasta '{DATA_DIR}'.")

# --- Interface Principal (exibida apenas se os dados estiverem prontos) ---
if data_ready:
    aba = st.selectbox("Escolha a tabela para consultar:", ["Cabeçalho", "Itens"])

    df_selecionado = cabecalho_df if aba == "Cabeçalho" else itens_df

    st.info(f"Colunas disponíveis na tabela '{aba}': **{', '.join(df_selecionado.columns.tolist())}**")

    st.subheader("❓ Faça sua pergunta sobre os dados:")
    pergunta = st.text_input(
        "Digite aqui sua pergunta:",
        placeholder="Ex: 'Quais são as 10 notas fiscais de maior valor?', 'Qual o valor total de vendas do produto X?', 'Liste os itens com maior quantidade vendida.'"
    )

    if pergunta:
        with st.spinner("Consultando o agente..."):
            resposta = responder_pergunta_com_agente(df_selecionado, pergunta)
        
        if isinstance(resposta, list):
            if resposta:
                st.subheader("✅ Resultado da Consulta:")
                st.dataframe(pd.DataFrame(resposta), use_container_width=True)
            else:
                st.info("A consulta não retornou resultados ou os dados estão vazios.")
        else:
            st.subheader("✅ Resultado da Consulta:")
            st.write(resposta)
else:
    # Mensagem quando os dados ainda não estão prontos
    st.info("Aguardando o carregamento ou upload dos arquivos de dados para iniciar a consulta.")
