import zipfile
import os

zip_path = 'data/202401_NFs.zip'
extract_folder = 'data/'

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)
    print(f"Arquivos extraídos para {extract_folder}")

# Checar se arquivos extraídos existem
cabecalho = os.path.join(extract_folder, '202401_NFs_Cabecalho.csv')
itens = os.path.join(extract_folder, '202401_NFs_Itens.csv')

print(f"Cabeçalho extraído? {'Sim' if os.path.exists(cabecalho) else 'Não'}")
print(f"Itens extraídos? {'Sim' if os.path.exists(itens) else 'Não'}")
