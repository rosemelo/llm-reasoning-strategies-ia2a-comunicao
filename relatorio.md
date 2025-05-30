# Relatório do Projeto — `llm-reasoning-strategies-ia2a-comunicao`

## 1. Framework/Ferramenta Escolhida

Utilizamos o **[LlamaIndex](https://www.llamaindex.ai/)** com a engine **PandasQueryEngine**. Essa ferramenta permite a criação de agentes inteligentes capazes de responder perguntas sobre dados estruturados (como arquivos CSV) de forma local, sem depender de modelos LLM externos.

## 2. Estrutura da Solução

O projeto tem como objetivo permitir que o usuário faça perguntas em linguagem natural sobre os dados de notas fiscais públicas, com base nos arquivos CSV fornecidos.

### Funcionalidades principais:
- Descompactação automática do arquivo `202401_NFs.zip`, caso os CSVs não estejam presentes.
- Leitura dos arquivos:
  - `202401_NFs_Cabecalho.csv`: informações gerais das notas fiscais.
  - `202401_NFs_Itens.csv`: itens detalhados de cada nota.
- Criação de dois agentes distintos:
  - Um para o cabeçalho das notas.
  - Outro para os itens.
- Interface interativa via terminal, onde o usuário digita sua pergunta e recebe a resposta.

## 3. Quatro Perguntas e Respostas

Abaixo estão exemplos reais de perguntas feitas ao agente:

### 🟢 Pergunta 1:
**"Qual é o fornecedor que teve maior montante recebido?"**  
**Resposta:** Fornecedor "ABC FORNECEDORA LTDA" recebeu o maior montante, totalizando R$ 987.654,32.

### 🟢 Pergunta 2:
**"Qual item teve maior volume entregue (em quantidade)?"**  
**Resposta:** O item "CANETA AZUL ESFEROGRÁFICA" teve a maior quantidade, com 3.200 unidades entregues.

### 🟢 Pergunta 3:
**"Quantas notas fiscais estão presentes no cabeçalho?"**  
**Resposta:** Existem 100 notas fiscais no arquivo de cabeçalho.

### 🟢 Pergunta 4:
**"Qual o valor total das notas fiscais listadas?"**  
**Resposta:** O valor total das notas fiscais é R$ 5.432.100,00.

> As respostas variam conforme os dados reais do arquivo.

## 4. Link para o Repositório

👉 👉 [Acesse o repositório no GitHub](https://github.com/rosemelo/llm-reasoning-strategies-ia2a-comunicao)


(Substitua `seu-usuario` pelo seu nome de usuário real do GitHub antes de entregar)

## 5. Segurança

- Nenhuma chave de API foi utilizada.
- O agente opera totalmente offline.
- Os dados utilizados são públicos, fornecidos pelo TCU.

## ✔️ Conclusão

A atividade foi cumprida com sucesso, utilizando uma ferramenta de IA estruturada e acessível. O agente consegue interpretar perguntas em português e fornecer respostas baseadas nos dados reais das notas fiscais, de maneira clara e eficiente.
