"""
================================================================
NAMING RIGHTS NO FUTEBOL BRASILEIRO – TCC IBMEC 2026
Resultados e Conclusão
================================================================
"""

# ================================================================
# DADOS DAS TABELAS
# ================================================================

tabela_series = [
    ["Indicador",                        "Pre-Acordo (2012-2014)", "Pos-Acordo (2015-2024)"],
    ["CAGR Receita Total - Nominal",     "+0,6% a.a.",             "+14,9% a.a."           ],
    ["CAGR Receita Total - Real",        "-7,2% a.a.",             "+4,4% a.a."            ],
    ["Receita Total (inicio periodo)",   "R$ 240 mi",              "R$ 350,5 mi"           ],
    ["Receita Total (fim periodo)",      "R$ 243 mi",              "R$ 1.221 mi"           ],
    ["Receita Comercial (inicio)",       "R$ 25 mi",               "R$ 65 mi"              ],
    ["Receita Comercial (fim)",          "---",                    "R$ 142,9 mi"           ],
    ["Crescimento Receita Comercial",    "---",                    "+120% (2015-2024)"     ],
    ["Share Comercial na Receita Total", "~11%",                   "~15%"                  ],
]

tabela_did = [
    ["Metrica",                               "Pre-Acordo (2012-2014)", "Pos-Acordo (2015-2024)"],
    ["Razao Receita Palmeiras/Flamengo",      "~73%",                  "~84%"                  ],
    ["Crescimento medio anual - Palmeiras",   "+0,6% a.a.",            "+14,9% a.a."            ],
    ["Crescimento medio anual - Flamengo",    "+28,0% a.a.",           "+10,2% a.a."            ],
    ["DiD estimado (Palmeiras - Flamengo)",   "---",                   "+25 p.p./ano"           ],
]

tabela_roi = [
    ["Componente (11 anos)",          "Otimista", "Base",  "Pessimista"],
    ["Receita direta (R$ mi)",        "198,0",    "165,0", "123,8"     ],
    ["Efeito multiplicador (R$ mi)",  "282,5",    "217,2", "108,6"     ],
    ["Custo de oportunidade (R$ mi)", "66,0",     "82,5",  "107,3"     ],
    ["Beneficio liquido (R$ mi)",     "414,5",    "299,7", "125,1"     ],
    ["ROI (%)",                       "628%",     "363%",  "117%"      ],
]

tabela_atl = [
    ["Indicador",                      "Arena MRV 2023 (parcial)", "Arena MRV 2024 (completo)"],
    ["Receita bruta da arena",         "R$ 13,6 mi (~5 meses)",    "R$ 88,1 mi"              ],
    ["Receita liquida da arena",       "R$ 8,2 mi",                "R$ 61,7 mi"              ],
    ["Margem liquida",                 "~60%",                     "70%"                     ],
    ["Margem Mineirao (referencia)",   "41%",                      "41%"                     ],
    ["Ganho incremental de margem",    "+19 p.p.",                 "+29 p.p."                ],
]


# ================================================================
# FUNÇÕES SIMPLES DE FORMATAÇÃO
# ================================================================

def linha(char="=", n=70):
    print(char * n)

def titulo(texto):
    linha()
    print(texto)
    linha()

def subtitulo(texto):
    print("\n" + texto)
    linha("-", len(texto))

def imprimir_tabela(dados):
    """Imprime uma lista de listas como tabela formatada no terminal."""
    # Calcula largura de cada coluna
    larguras = [max(len(str(linha[i])) for linha in dados) for i in range(len(dados[0]))]

    for idx, linha_dados in enumerate(dados):
        linha_fmt = "  ".join(str(v).ljust(larguras[i]) for i, v in enumerate(linha_dados))
        print("  " + linha_fmt)
        if idx == 0:  # linha separadora após o cabeçalho
            print("  " + "  ".join("-" * larguras[i] for i in range(len(larguras))))


# ================================================================
# SEÇÃO 1 – RESULTADOS
# ================================================================

titulo("SECAO 1 – RESULTADOS")

print("""
Esta secao apresenta os achados quantitativos obtidos a partir da analise
de series temporais, do estudo comparativo com o Flamengo (DiD simplificado)
e da modelagem de ROI por cenarios. Os numeros a seguir fundamentam e
justificam a conclusao deste trabalho.
""")


# 1.1 Series Temporais
subtitulo("1.1  Series Temporais – Palmeiras (2012–2024)")

print("""
O grafico da receita total do Palmeiras revela uma aceleracao expressiva
apos o inicio do acordo com a Allianz (2015). A tabela abaixo apresenta
os indicadores-chave calculados a partir dos dados deflacionados pelo
IGP-M (obtido via API do Banco Central).
""")

imprimir_tabela(tabela_series)

print("""
O crescimento nominal de 14,9% a.a. no periodo pos-acordo e substancialmente
superior ao 0,6% a.a. registrado nos tres anos anteriores. Em termos reais,
a inversao e ainda mais contundente: de -7,2% (encolhimento real) para
+4,4% a.a. de crescimento consistente. A receita comercial passou de
R$ 25 milhoes em 2012 para R$ 142,9 milhoes em 2024, expansao de 472%
em doze anos, dos quais a fase mais relevante ocorre apos 2015.
""")


# 1.2 DiD
subtitulo("1.2  Estudo Comparativo DiD – Palmeiras vs. Flamengo")

print("""
O Flamengo, que nao possui acordo de naming rights no periodo analisado,
foi utilizado como grupo de controle. A comparacao entre as trajetorias
dos dois clubes permite isolar, de forma heuristica, o efeito diferencial
associado ao naming rights.
""")

imprimir_tabela(tabela_did)

print("""
A razao receita Palmeiras/Flamengo melhorou de 73% para 84%, indicando
convergencia. O estimador DiD simplificado aponta diferencial de +25 p.p./ano
no crescimento do Palmeiras em relacao ao controle.

Limitacao reconhecida: outros fatores (patrocinio Crefisa, desempenho
esportivo) tambem contribuem para o resultado; o DiD deve ser interpretado
como indicativo, nao como causalidade isolada.
""")


# 1.3 ROI
subtitulo("1.3  Modelagem de ROI por Cenarios – Palmeiras / Allianz Parque (2015–2025)")

print("""
A modelagem considerou tres componentes:
  (i)   Receita direta do naming rights (~R$ 15 mi/ano, estimado)
  (ii)  Efeito multiplicador nos demais patrocinios (+R$ 19,8 mi/ano no base)
  (iii) Custo de oportunidade (receita alternativa = 50% do valor do naming)
""")

imprimir_tabela(tabela_roi)

print("""
Em todos os cenarios o beneficio liquido e positivo. O ROI minimo (cenario
pessimista) e de 117%, o que significa que o acordo gerou mais que o dobro
do custo de oportunidade mesmo nas condicoes menos favoraveis. No cenario-
base, o retorno chega a 363% sobre o custo de oportunidade acumulado.
""")


# 1.4 Atletico-MG
subtitulo("1.4  Atletico-MG – Arena MRV (Dados Iniciais 2023–2024)")

print("""
O Atletico-MG encerrou 2024 com a primeira temporada completa na Arena MRV,
com naming rights estimados em R$ 25 mi/ano (R$ 500 mi / 20 anos). Os dados
iniciais confirmam ganhos de eficiencia expressivos em relacao ao modelo
anterior (aluguel do Mineirao).
""")

imprimir_tabela(tabela_atl)

print("""
A margem liquida de 70% na propria arena representa ganho de 29 p.p. frente
ao Mineirao (41%), gerando R$ 25,6 mi adicionais de lucro liquido so em 2024.
Somados ao naming rights estimado (R$ 25 mi/ano), o resultado projetado supera
R$ 87 mi em receita de arena+naming no primeiro exercicio completo.
""")


# ================================================================
# SEÇÃO 2 – CONCLUSÃO
# ================================================================

titulo("SECAO 2 – CONCLUSAO")

print("""
A pergunta central deste trabalho era: naming rights no futebol brasileiro
vale a pena para os clubes?

A partir da analise dos tres casos estudados — Palmeiras (Allianz Parque),
Flamengo (grupo de controle) e Atletico-MG (Arena MRV) — a resposta e:

  SIM, desde que o acordo seja estruturado com as condicoes financeiras
  adequadas.

No caso do Palmeiras, o acordo com a Allianz transformou de forma mensuravel
a estrutura de receitas do clube. A receita total saiu de R$ 243 mi em 2014
para R$ 1.221 mi em 2024 — crescimento de 403% em dez anos, com CAGR real
de +4,4% a.a., contra -7,2% no periodo pre-acordo.

Nao e possivel atribuir todo esse crescimento exclusivamente ao naming rights,
uma vez que o patrocinio master da Crefisa e o desempenho esportivo tambem
exerceram papel relevante. Porem, o naming rights criou um efeito sinergico
documentado: a credibilidade gerada pelo acordo com a Allianz contribuiu para
elevar o patamar de valorizacao do clube perante outros patrocinadores — o
que se reflete no crescimento da receita comercial de R$ 65 mi (2015) para
R$ 142,9 mi (2024).

A modelagem de ROI reforca essa conclusao de forma objetiva. Mesmo no cenario
mais conservador, o retorno sobre o custo de oportunidade foi de 117% em onze
anos. No cenario-base chegou a 363%. Em qualquer hipotese trabalhada, o acordo
gerou mais valor financeiro do que a alternativa de nao te-lo firmado.

O caso do Atletico-MG e distinto: o clube construiu sua propria arena ao mesmo
tempo em que firmou o naming rights, tornando os dois movimentos
interdependentes. Ainda assim, os dados iniciais da Arena MRV sao promissores
— margem liquida de 70% frente a 41% no Mineirao — e validam a logica
financeira do modelo.

Portanto, naming rights sao financeiramente vantajosos para clubes brasileiros
quando:
  (i)   O valor do contrato representa parcela relevante da receita total
  (ii)  O ROI estimado supera 100% ja no cenario pessimista
  (iii) O patrocinador tem reputacao compativel com a marca do clube
  (iv)  O contrato preve clausulas de reajuste e rescisao que protejam o clube

Por fim, e importante reconhecer as limitacoes desta pesquisa: o numero
reduzido de casos (n=3), a dependencia de dados estimados para anos anteriores
e a dificuldade de isolar o efeito do naming rights de outras variaveis.
Estudos futuros poderao ampliar a amostra e aplicar metodos econometricos
mais robustos para estimar o efeito causal sobre a receita dos clubes.
""")

linha()
print("NOTA: Este trabalho analisa exclusivamente o acordo da Allianz Parque")
print("(2015-2025). O acordo com o Nubank (2026) NAO e escopo desta pesquisa.")
linha()