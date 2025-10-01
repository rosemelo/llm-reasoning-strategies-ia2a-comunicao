import pandas as pd

# Lê o arquivo completo (que você já deve ter em data/creditcard.csv)
df = pd.read_csv("data/creditcard.csv")

# Cria uma amostra com 5000 linhas aleatórias
sample = df.sample(n=5000, random_state=42)

# Salva em data/creditcard_sample.csv
sample.to_csv("data/creditcard_sample.csv", index=False)

print("✅ Amostra criada em data/creditcard_sample.csv")
