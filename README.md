# 🧠 Agentes Autônomos — Desafio Extra (EDA Genérico)
## 📊 Dataset de Fraude em Cartão de Crédito (Kaggle)

Este projeto foi ampliado para incluir um agente de Análise Exploratória de Dados (EDA) capaz de trabalhar com qualquer arquivo CSV.
Como exemplo, utilizamos o dataset público Credit Card Fraud Detection, disponível no Kaggle:
👉 [Kaggle - Credit Card Fraud Detection]

O arquivo original (creditcard.csv) possui cerca de 150 MB e contém 284.807 transações, sendo que apenas 492 são fraudes (Class = 1).

# ⚠️ Importante sobre este repositório

Para não ultrapassar os limites do GitHub, aqui disponibilizamos apenas uma amostra reduzida:

    ```bash  
    data/creditcard_sample.csv
    ```

Essa amostra contém 5.000 transações escolhidas aleatoriamente e serve apenas para testes locais.

Para rodar a aplicação com o dataset completo, siga as instruções abaixo.

## 📥 Como obter o dataset completo

Crie uma conta gratuita no Kaggle (se ainda não tiver).

Acesse a página do dataset: [Credit Card Fraud Detection].

Clique em Download e extraia o arquivo creditcard.csv.

Coloque o arquivo extraído na pasta data/ do projeto, mantendo o nome:

    ```bash  
    data/creditcard.csv
    ```

# 🚀 Observação

A aplicação é capaz de rodar tanto com a amostra (creditcard_sample.csv) quanto com o arquivo completo (creditcard.csv).
Se o arquivo completo estiver presente, ele será priorizado.

# Agente de Consulta de Notas Fiscais

## Descrição

Projeto que permite ao usuário consultar informações sobre notas fiscais de janeiro de 2024, usando arquivos CSV fornecidos pelo Tribunal de Contas da União. O agente responde perguntas em linguagem natural sobre os dados, sem necessidade de chave API ou conexão externa.

---

## Como funciona

- O usuário faz upload do arquivo `202401_NFs.zip` contendo os dados.
- O agente descompacta os arquivos CSV e carrega os dados.
- O usuário escolhe a tabela (Cabeçalho ou Itens) para consultar.
- O usuário digita perguntas em linguagem natural.
- O agente responde baseado nos dados carregados localmente.

---

## Tecnologias usadas

- Python 3.8+
- [Streamlit](https://streamlit.io/) para interface web.
- [LlamaIndex](https://www.llamaindex.ai/) com PandasQueryEngine para consulta inteligente aos dados.
- Pandas para manipulação dos CSVs.

---

## Como rodar localmente
 1 Clone este repositório.

    ```bash
    git clone https://github.com/rosemelo/llm-reasoning-strategies-ia2a-comunicao.git    
    ```

2 Vá para a pasta do seu repositório.

    ```bash
    cd seu-repositorio
    ```

3 Instale as dependências.

    ```bash
    pip install -r requirements.txt
    ```

4 Inicie a aplicação Streamlit.

    ```bash
    streamlit run app.py
    ```

