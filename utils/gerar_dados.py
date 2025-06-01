import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os
import zipfile

fake = Faker('pt_BR')

# Geração de dados do cabeçalho da nota fiscal
def gerar_cabecalho(n=100):
    dados = []
    for i in range(1, n + 1):
        data = fake.date_between(start_date='-6M', end_date='today')
        valor = round(random.uniform(100, 10000), 2)
        cliente = fake.company()
        status = random.choice(['Emitida', 'Cancelada', 'Pendente'])
        dados.append([i, data.strftime('%Y-%m-%d'), valor, cliente, status])
    return pd.DataFrame(dados, columns=['ID', 'Data', 'Valor', 'Cliente', 'Status'])

# Geração de itens por nota fiscal
def gerar_itens(cabecalho_df):
    dados = []
    for _, row in cabecalho_df.iterrows():
        qtd_itens = random.randint(1, 5)
        for item in range(qtd_itens):
            produto = fake.word().capitalize()
            quantidade = random.randint(1, 10)
            valor_unitario = round(random.uniform(10, 500), 2)
            dados.append([row['ID'], produto, quantidade, valor_unitario])
    return pd.DataFrame(dados, columns=['ID_NF', 'Produto', 'Quantidade', 'ValorUnitario'])

# Criar pasta data
os.makedirs('data', exist_ok=True)

# Gerar dados
cabecalho_df = gerar_cabecalho(200)
itens_df = gerar_itens(cabecalho_df)

# Salvar CSVs
cabecalho_path = 'data/202401_NFs_Cabecalho.csv'
itens_path = 'data/202401_NFs_Itens.csv'

cabecalho_df.to_csv(cabecalho_path, index=False, encoding='utf-8')
itens_df.to_csv(itens_path, index=False, encoding='utf-8')

# Compactar CSVs em ZIP
zip_path = 'data/202401_NFs.zip'
with zipfile.ZipFile(zip_path, 'w') as zipf:
    zipf.write(cabecalho_path, os.path.basename(cabecalho_path))
    zipf.write(itens_path, os.path.basename(itens_path))

print("✅ Dados gerados e ZIP criado com sucesso!")
