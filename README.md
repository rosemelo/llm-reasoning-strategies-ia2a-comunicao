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

1. Clone este repositório.

2. Instale as dependências:

```bash
pip install -r requirements.txt
