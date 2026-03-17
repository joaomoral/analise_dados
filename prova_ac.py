# Questão 1: Carregar o DataFrame
# LER arquivo titanic.csv em um DataFrame pandas chamado df?
pip install pd
import pandas as pd
df = pd.read_csv("titanic.csv")

# Questão 2: Filtrar passageiros do sexo feminino
# Filtrar o DataFrame para mostrar apenas as Mulheres?
# (Dica: Filtar onde a coluna "Sex" é igual a "female")
df_female = df[df['Sex'] == 'female']
print(df_female)

# Questão 3: Contar sobreviventes
# Quantos passageiros Sobreviveram?
# (Dica: Sobreviventes têm o valor 1 na coluna "Survived")
survivors = df[df['Survived'] == 1]
num_survivors = survivors.shape[0]
print(f"Number of survivors: {num_survivors}")

# Questão 4: Calcular a média da idade
# Quantos Homens Sobreviveram?
df_male = df[df['Sex'] == 'male']
df_male_survivors = df_male[df_male['Survived'] == 1]
print(f"Number of male survivors: {df_male_survivors.shape[0]}")

# Questão 5: Calcular Nome "John"
# Calcular quantos passageiros tem o nome "John"?
# (Dica: Usar a coluna "Name")
df_john = df[df['Name'].str.contains('John')]
num_john = df_john.shape[0]
print(f"Number of passengers named John: {num_john}")