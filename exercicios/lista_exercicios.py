#21
nomes = ["Ana", "Pedro", "Maria","João"]

#22
for nome in nomes:
    print(nome)

#23 
nomes_maiusculo = ["ANA", "PEDRO", "MARIA","JOÃO"]
for nome in nomes_maiusculo:
    print(nome)

#24
numeros = range(1,21)
for n in numeros:
    if n % 2 == 0:
        print(n)

#25
numeros = list(range(1, 21))
quadrados = [numero ** 2 for numero in numeros]
print(quadrados)

#26
palavras = ["python", "java", "c", "javascript"]
for palavra in palavras:
    print(f"'{palavra}' tem {len(palavra)} letras")

#27
idades = [12, 18, 25, 40, 60]
for idade in idades:
    if idade >= 18:
        print(f"{idade} anos: Maior de idade")
    else:
        print(f"{idade} anos: Menor de idade")

#28
notas = [5.5, 7.0, 8.3, 4.9, 6.2]
aprovados = 0
reprovados = 0
for nota in notas:
    if nota >= 7:
        aprovados += 1
    else:
        reprovados += 1
print(f"Aprovados: {aprovados}")
print(f"Reprovados: {reprovados}")

#29
compras = ["arroz", "feijão", "batata", "carne"]
for item in compras:
    print(f"Preciso comprar: {item}")