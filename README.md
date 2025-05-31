# LLM Reasoning Strategies - IA2A Comunicação

## Descrição

Este projeto implementa um agente inteligente para consulta interativa a dados de Notas Fiscais públicas em arquivos CSV. Usamos o **LlamaIndex** com o **PandasQueryEngine** para responder perguntas em linguagem natural diretamente a partir dos dados, sem necessidade de chave API ou conexão externa.

---

## Funcionalidades

- Descompacta automaticamente o arquivo ZIP contendo os CSVs, caso ainda não estejam extraídos.
- Carrega os dados dos arquivos:
  - `202401_NFs_Cabecalho.csv` (informações gerais das notas fiscais).
  - `202401_NFs_Itens.csv` (itens detalhados de cada nota).
- Permite perguntas interativas em português sobre os dados via terminal.
- Respostas baseadas exclusivamente nos dados locais, offline e sem uso de API externa.

---

## Requisitos

- Python 3.8+
- Bibliotecas Python listadas no arquivo `requirements.txt`.

---

## Como rodar

1. Clone o repositório:

```bash
git clone https://github.com/rosemelo/llm-reasoning-strategies-ia2a-comunicao.git
cd llm-reasoning-strategies-ia2a-comunicao
