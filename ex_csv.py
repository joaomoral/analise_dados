import pandas as pd

# Exercício 1 – Conhecendo o Dataset 
# 1. Quantas linhas e colunas existem? 
df.shape
>(2200,14)

# 2. Quais são os tipos de dados? 
df.dtypes

# 3. Existe coluna com valores ausentes?
df.isnull().sum()

# 4. Qual é o período de anos disponível? 
df.columns
df.loc[:,"year"].unique()

# 5. Quantos países diferentes existem?
df.loc[:,"country"].unique()

# Exercício 2 – Estatísticas Gerais 
# 1. Média do score 
df.columns
df.loc[:,"score"].mean()

# 2. Maior score 
df.loc[:,"score"].max()

# 3. Menor score 
df.loc[:,"score"].min()

# 4. Média do score por ano
df.groupby("year")["score"].mean()

# 5. Desvio padrão do score
df.loc[:,"score"].std()

# ============================================================
# FILTROS E SELEÇÕES
# ============================================================

# Exercício 3 – Top Universidades 
# 1. Mostre as 10 melhores universidades do mundo (menor world_rank)
df.columns
df.loc[0:9,["institution","world_rank","year"]].sort_values("world_rank")

# 2. Mostre as 5 melhores universidades do Brasil (se existirem)
df.columns
df.loc[0:4,["institution","world_rank"]].sort_values("world_rank")