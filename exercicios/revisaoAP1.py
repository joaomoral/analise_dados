import pandas as pd
df = pd.read_csv("nome.csv")
df = pd.read_excel("nome.xlsa")
filter = 
filter = df["nome"].str.contains("Pedro", case=False)

#para rankear (decrescente)
df["ROIC"].rank(ascending=False)
df.sort_values(["ROIC"], ascending=False)

#criar nova coluna


#API
pip install requests
import requests
URL="https://...."
response = requests.get(URL)
response.status_code #200 sucesso
dados = response.json()
pd.DataFrame(dados)