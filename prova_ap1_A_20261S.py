# O dataset NCR Ride Bookings contém registros de corridas urbanas realizadas em regiões da National Capital Region (NCR), que abrange Delhi, Gurgaon, Noida, Ghaziabad, Faridabad e áreas próximas.
# Utilize os arquivos : ncr_ride_bookings.csv para resolver as questoes.
# Principais informaçoes no dataset:
# Date → Data da corrida
# Time → Horário da corrida
# Booking ID → Identificador da corrida
# Booking Status → Status da corrida
# Customer ID → Identificador do cliente
# Vehicle Type → Tipo de veículo
# Pickup Location → Local de embarque
# Drop Location → Local de desembarque
# Booking Value → Valor da corrida
# Ride Distance → Distância percorrida
# Driver Ratings → Avaliação do motorista
# Customer Rating → Avaliação do cliente
# Payment Method → Método de pagamento
# Questões:
# (0,5) 1 - Quantas corridas estão com Status da Corrida como Completada ("Completed") no dataset? 
import pandas as pd
df = pd.read_csv("ncr_ride_bookings.csv")
num_completadas = completadas.shape[0]
print(f"Numero de corridas completadas: {num_completadas}")

# (0,5) 2 - Qual a proporção em relação ao total de corridas?
proporcao = num_completadas / total
print(f"Proporção em relação ao total de corridas: {proporcao*100:.2f}%")

# (0,5) 3 - Calcule a média da Distância ("Ride Distance") percorrida por cada Tipo de veículo.
media_distancia = df.groupby("Vehicle Type")["Ride Distance"].mean()
print(f"Média da distância percorrida por cada veículo: {media_distancia.to_string()}")

# (0,5) 4 - Qual o Metodo de Pagamento ("Payment Method") mais utilizado pelas bicicletas ("Bike") ?
bikes = df[df["Vehicle Type"] == "Bike"]
pagamento_mais_usado = bikes["Payment Method"].value_counts().idxmax()
print(f"Pagamento mais utilizado pelas bicicletas: {pagamento_mais_usado}")

# (0,5) 5 - Qual o valor total arrecadado ("Booking Value") apenas das corridas Completed?
valor_total = completadas["Booking Value"].sum()
print(f"Valor total arrecadado: {valor_total:,.2f}")

# (0,5) 6 - E qual o ticket médio ("Booking Value")dessas corridas Completed?
ticket_medio = completadas["Booking Value"].mean()
print(f"Ticket médio das corridas completadas: {ticket_medio:.2f}")

# (1,5) 7 - O IPEA disponibiliza uma API pública com diversas séries econômicas. 
# Para encontrar a série de interesse, é necessário primeiro acessar o endpoint de metadados.
# Acesse o endpoint de metadados: "http://www.ipeadata.gov.br/api/odata4/Metadados";
# Transforme em um DataFrame;
# Filtre para encontrar as séries da Fipe relacionadas a venda de imoveis (“vendas - Brasil”).
# Dica: 
# Utilize a coluna FNTSIGLA para encontrar a serie da Fipe;
# Utilize a coluna SERNOME para encontrar as vendas de imoveis no Brasil;
import requests
URL = "http://www.ipeadata.gov.br/api/odata4/Metadados"
response = requests.get(URL)
response.status_code
dados = response.json()
pd.DataFrame(dados)
filtro = dados[(dados["FNTSIGLA"]str.contains("FIPE"))
& (dados["SERNOME"].str.contains("vendas - brasil"))]

# (1,5) 8 -  Descubra qual é o código da série correspondente (coluna: SERCODIGO).
# CODIGO_ENCONTRADO=''
# Usando o código encontrado, acesse a API de valores: f"http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{CODIGO_ENCONTRADO}')"
# Construa um DataFrame através da chave 'value' do retorno da api
# Selecione apenas as colunas datas (VALDATA) e os valores (VALVALOR).
# Exiba a Data e o Valor que teve o valor maximo de vendas.


# (1,5) 9 - Descubra quanto rendeu a VALE no ano de 2025
 base_url = "https://laboratoriodefinancas.com/api/v2"
 token = "SEU_JWT"
 params = {"ticker": "VALE3", "data_ini": "2001-01-01", "data_fim": "2026-12-31"}
 response = requests.get(
     f"{base_url}/preco/corrigido",
     headers={"Authorization": f"Bearer {token}"},
     params=params,
 )
response.status_code
valor_vale = response.json()
pd.DataFrame(valor_vale)

# (1,5) 10 - Você tem acesso à API do Laboratório de Finanças, que fornece dados do Planilhão em formato JSON. 
# Selecione a empresa do setor de "tecnologia" que apresenta o maior ROE (Return on Equity) na data base 2024-04-01.
# Exiba APENAS AS COLUNAS "ticker", "setor" e o "roe"
base_url = "https://laboratoriodefinancas.com/api/v2"
token = "SEU_JWT"
response = requests.get(
    f"{base_url}/bolsa/planilhao",
    headers={"Authorization": f"Bearer {token}"},
    params={"data_base": "2026-04-01"},
)
response.status_code
maior_roe = response.json()
pd.DataFrame(maior_roe)
empresa_maior_roe = maior_roe["roe"]
empresa_maior_roe.rank(ascending=False)
empresa_maior_roe.sort_values(["ROIC"], ascending=False)
empresa_maior_roe[0]

# (1,5) 11 - Faça a Magic Formula através dos indicadores Return on Capital (roc) e Earning Yield (ey) no dia 2024-04-01.
# Monte uma carteira de investimento com 10 ações baseado na estratégia Magic Formula.
# base_url = "https://laboratoriodefinancas.com/api/v2"
# token = "SEU_JWT"
# response = requests.get(
#     f"{base_url}/bolsa/planilhao",
#     headers={"Authorization": f"Bearer {token}"},
#     params={"data_base": "2026-04-01"},
# )


# (1,5) 12 - Quantos setores ("setor") tem essa carteira formada por 10 ações?
