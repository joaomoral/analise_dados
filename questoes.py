## 1. Como identificar uma lista em python?
# R: Para identifiar uma lista em python é preciso verificar se a variável é do tipo list, para isso podemos usar
# a função type() ou isinstance().

## 2. Como pegar o 1° elemento de uma lista em python?
# R: Para pegar o primeiro elemento de uma lista em Python, você pode usar o índice 0. Por exemplo, se você tem
# uma lista chamada minha_lista, você pode acessar o primeiro elemento com minha_lista[0]

## 3. Como identificar um dicionário em python?
# R: Para identificar um dicionário em Python, você pode verificar se a variável é do tipo dict usando a função type()
# ou isinstance().

## 4. Como pegar um elemento em dicionário?
# R: Para pegar um elemento em um dicionário em Python, você pode usar a chave correspondente. Por exemplo, se você tem
# um dicionário chamado meu_dicionário e uma chave "nome", você pode acessar o valor com meu_dicionário["nome"].

## 5. Como identificar uma lista em dicionário?
# R: Para identificar uma lista dentro de um dicionário em Python, você pode acessar o valor associado a uma chave
# específica e verificar se é do tipo list usando a função type() ou isinstance(). Por exemplo, se você tem um 
# dicionário chamado meu_dicionário e uma chave "minha_lista", você pode verificar se o valor é uma lista com 
# type(meu_dicionário["minha_lista"]) ou isinstance(meu_dicionário["minha_lista"], list). 

## 6. Como transformar uma lista de dicionário em um DataFrame?
# R: Para transformar uma lista de dicionários em um DataFrame, você pode usar a função pd.DataFrame() do pandas.
# Por exemplo, se você tem uma lista de dicionários chamada minha_lista_de_dicionarios, você pode criar um DataFrame 
# com pd.DataFrame(minha_lista_de_dicionarios).

## 7. Como consumir um arquivo csv no DataFrame?
# R: Para consumir um arquivo CSV em um DataFrame, você pode usar a função pd.read_csv() do pandas. Por exemplo, se
# você tem um arquivo chamado "meu_arquivo.csv", você pode ler o arquivo e criar um DataFrame com 
# pd.read_csv("meu_arquivo.csv").

## 8. Como consumir um arquivo excel no DataFrame?
# R: Para consumir um arquivo Excel em um DataFrame, você pode usar a função pd.read_excel() do pandas. Por exemplo, se
# você tem um arquivo chamado "meu_arquivo.xlsx", você pode ler o arquivo e criar um DataFrame com
# pd.read_excel("meu_arquivo.xlsx").

## 9. Como filtrar uma coluna de valores?
# R: Para filtrar uma coluna de valores em um DataFrame, você pode usar a sintaxe de filtragem do pandas. Por exemplo,
# se você tem um DataFrame chamado meu_dataframe e uma coluna chamada "idade", você pode filtrar os valores com
# meu_dataframe[meu_dataframe["idade"] > 18].

## 10. Como filtrar uma coluna de string?
# R: Para filtrar uma coluna de string em um DataFrame, você pode usar a função str.contains() do pandas. Por exemplo,
# se você tem um DataFrame chamado meu_dataframe e uma coluna chamada "nome", você pode filtrar os valores que contêm 
# a string "João" com meu_dataframe[meu_dataframe["nome"].str.contains("João")].

## 11. Como fazer dois filtros do DataFrame?
# R: Para fazer dois filtros em um DataFrame, você pode usar o operador lógico & para combinar as condições.
# Por exemplo, se você tem um DataFrame chamado meu_dataframe e deseja filtrar os valores   onde a coluna
# "idade" é maior que 18 e a coluna "cidade" é igual a "São Paulo", você pode usar: 
# meu_dataframe[(meu_dataframe["idade"] > 18) & (meu_dataframe["cidade"] == "São Paulo")]