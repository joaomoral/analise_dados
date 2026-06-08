"""
================================================================
NAMING RIGHTS NO FUTEBOL BRASILEIRO – TCC IBMEC 2026
================================================================
PASSO A PASSO:
  PASSO 1 – Importar bibliotecas
  PASSO 2 – Buscar IGP-M via API do Banco Central (BCB/SGS)
  PASSO 3 – Montar a base de dados dos clubes (2012–2025)
  PASSO 4 – Calcular métricas (CAGR, participação comercial)
  PASSO 5 – Plotar os gráficos no terminal do VS Code (plotext)

NOTA: O acordo analisado é o da Allianz Parque (2015–2025).
      O acordo com o Nubank (2026) NÃO é escopo deste trabalho.
================================================================
"""

# ================================================================
# PASSO 1 – IMPORTAR BIBLIOTECAS
# ================================================================
import requests
import pandas as pd
import plotext as plt

print("=" * 55)
print("PASSO 1 – Bibliotecas importadas com sucesso")
print("=" * 55)


# ================================================================
# PASSO 2 – BUSCAR IGP-M VIA API DO BANCO CENTRAL
# ================================================================
# Série 189 do SGS/BCB = IGP-M mensal (FGV)
# A API retorna a variação % de cada mês.
# Acumulamos essas variações para obter o nível do índice,
# depois calculamos a média anual e reindexamos para base 2015 = 100.

print("\n" + "=" * 55)
print("PASSO 2 – Buscando IGP-M na API do Banco Central...")
print("=" * 55)

URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados"
    "?formato=json"
    "&dataInicial=01/01/2012"
    "&dataFinal=31/12/2025"
)

response = requests.get(URL)
print(f"  Status da API: {response.status_code}")  # 200 = sucesso

dados   = response.json()
df_igpm = pd.DataFrame(dados)

# Tratar colunas e acumular variação → nível do índice
df_igpm["data"]  = pd.to_datetime(df_igpm["data"], dayfirst=True)
df_igpm["valor"] = pd.to_numeric(df_igpm["valor"], errors="coerce")
df_igpm["ano"]   = df_igpm["data"].dt.year
df_igpm          = df_igpm.sort_values("data").reset_index(drop=True)
df_igpm["fator"] = 1 + df_igpm["valor"] / 100
df_igpm["nivel"] = df_igpm["fator"].cumprod()

# Média anual → reindexar para base 2015 = 100
nivel_anual = df_igpm.groupby("ano")["nivel"].mean()
base_2015   = nivel_anual[2015]
igpm        = {int(a): round(v / base_2015 * 100, 2)
               for a, v in nivel_anual.items()}

print("  IGP-M obtido com sucesso!")
print(f"  {igpm}")


# ================================================================
# PASSO 3 – MONTAR A BASE DE DADOS DOS CLUBES (2012–2025)
# ================================================================
# Receitas em R$ milhões (nominais).
# Fontes: balanços oficiais, ESPN Brasil, CNN Brasil, EY 2022/2023.
# Anos marcados com * são estimados/interpolados.

print("\n" + "=" * 55)
print("PASSO 3 – Montando base de dados dos clubes")
print("=" * 55)

anos = list(range(2012, 2026))

# Palmeiras – Receita Total (R$ mi)
rec_palm = {
    2012: 240.0,   # * estimado
    2013: 181.2,   # ESPN Brasil (Série B)
    2014: 243.0,   # * estimado (inauguração arena)
    2015: 350.5,   # Revista Época
    2016: 440.0,   # * interpolado
    2017: 530.0,   # * interpolado
    2018: 688.5,   # ESPN Brasil
    2019: 641.0,   # Gazeta Esportiva
    2020: 558.0,   # Terra / SBT Sports (pandemia)
    2021: 992.0,   # CNN Brasil / ESPN
    2022: 856.0,   # EY Football Finance
    2023: 908.0,   # ESPN
    2024: 1221.0,  # CNN Brasil / ESPN
    2025: 1628.0,  # Balanço oficial Palmeiras (mar/2026) – rec. operacional líquida
}

# Flamengo – Receita Total (R$ mi)
# Fonte: FutebolMarket; CNN Brasil (abr/2026)
rec_fla = {
    2012: 212.0,
    2013: 273.0,
    2014: 347.0,
    2015: 356.0,
    2016: 510.0,
    2017: 649.0,
    2018: 543.0,
    2019: 950.0,
    2020: 669.0,
    2021: 1080.0,
    2022: 1170.0,
    2023: 1370.0,
    2024: 1330.0,
    2025: 2089.0,  # Balanço oficial Flamengo (abr/2026) – receita bruta total
}

# Palmeiras – Receita Comercial (patrocínio + naming + publicidade)
# 2022–2025 confirmados (balanço oficial). Demais: estimados.
rec_com = {
    2012: 25.0,
    2013: 22.0,
    2014: 28.0,
    2015: 65.0,
    2016: 80.0,
    2017: 90.0,
    2018: 105.0,
    2019: 110.0,
    2020: 95.0,
    2021: 120.8,
    2022: 142.6,
    2023: 127.1,
    2024: 142.9,
    2025: 203.3,   # Balanço oficial Palmeiras (mar/2026) – publicidade e patrocínio
}

# Monta DataFrame principal
df = pd.DataFrame({
    "ano":      anos,
    "rec_palm": [rec_palm[a] for a in anos],
    "rec_fla":  [rec_fla[a]  for a in anos],
    "rec_com":  [rec_com[a]  for a in anos],
    "igpm":     [igpm[a]     for a in anos],
    "pos":      [1 if a >= 2015 else 0 for a in anos],
})

# Deflacionar para R$ de 2015
df["rec_palm_real"] = df["rec_palm"] / df["igpm"] * 100
df["rec_fla_real"]  = df["rec_fla"]  / df["igpm"] * 100
df["share_com"]     = df["rec_com"]  / df["rec_palm"] * 100
df["ratio"]         = df["rec_palm"] / df["rec_fla"]  * 100

print("  Dados prontos! Prévia:")
print(df[["ano", "rec_palm", "rec_fla", "igpm"]].to_string(index=False))


# ================================================================
# PASSO 4 – CALCULAR MÉTRICAS
# ================================================================
print("\n" + "=" * 55)
print("PASSO 4 – Calculando métricas")
print("=" * 55)

pre    = df[df["pos"] == 0]
pos_df = df[df["pos"] == 1]

def cagr(v_ini, v_fim, n):
    return (v_fim / v_ini) ** (1 / n) - 1

cagr_pre      = cagr(pre.iloc[0]["rec_palm"],         pre.iloc[-1]["rec_palm"],         2)
cagr_pos      = cagr(pos_df.iloc[0]["rec_palm"],      pos_df.iloc[-1]["rec_palm"],      10)
cagr_pre_real = cagr(pre.iloc[0]["rec_palm_real"],    pre.iloc[-1]["rec_palm_real"],    2)
cagr_pos_real = cagr(pos_df.iloc[0]["rec_palm_real"], pos_df.iloc[-1]["rec_palm_real"], 10)
cag_com       = (rec_com[2025] / rec_com[2015] - 1) * 100
ratio_pre     = pre["ratio"].mean()
ratio_pos     = pos_df["ratio"].mean()

print(f"\n  CAGR receita total (nominal):")
print(f"    Pre-acordo  (2012-2014): {cagr_pre*100:+.1f}% a.a.")
print(f"    Pos-acordo  (2015-2025): {cagr_pos*100:+.1f}% a.a.")
print(f"\n  CAGR receita total (real – IGP-M via API BCB):")
print(f"    Pre-acordo  (2012-2014): {cagr_pre_real*100:+.1f}% a.a.")
print(f"    Pos-acordo  (2015-2025): {cagr_pos_real*100:+.1f}% a.a.")
print(f"\n  Crescimento receita comercial (2015-2025): +{cag_com:.0f}%")
print(f"\n  Razao Palmeiras / Flamengo:")
print(f"    Pre-acordo: {ratio_pre:.1f}%")
print(f"    Pos-acordo: {ratio_pos:.1f}%")


# ================================================================
# PASSO 5 – GRÁFICOS NO TERMINAL DO VS CODE (plotext)
# ================================================================
# Cada grafico aparece direto no terminal.
# Pressione ENTER para passar para o proximo.

print("\n" + "=" * 55)
print("PASSO 5 – Plotando graficos no terminal")
print("=" * 55)

# ── Gráfico 1: Receita Palmeiras nominal vs real ──────────────────
plt.clf()
plt.plot(anos, df["rec_palm"].tolist(),      label="Nominal (R$ mi)",     marker="dot")
plt.plot(anos, df["rec_palm_real"].tolist(), label="Real (base 2015=100)", marker="dot")
plt.vertical_line(2014.5, color="red+")
plt.title("Grafico 1 – Palmeiras: Receita Total (2012–2025)\n| linha vermelha = inicio acordo Allianz (2015)")
plt.xlabel("Ano")
plt.ylabel("R$ milhoes")
plt.plot_size(110, 25)
plt.show()

input("\n  [ENTER para proximo grafico]")

# ── Gráfico 2: Receita comercial Palmeiras ────────────────────────
plt.clf()
plt.bar(anos, df["rec_com"].tolist(), label="Receita Comercial (R$ mi)")
plt.vertical_line(2014.5, color="red+")
plt.title("Grafico 2 – Palmeiras: Receita Comercial (2012–2025)\n| patrocinio + naming rights + publicidade")
plt.xlabel("Ano")
plt.ylabel("R$ milhoes")
plt.plot_size(110, 25)
plt.show()

input("\n  [ENTER para proximo grafico]")

# ── Gráfico 3: Palmeiras vs Flamengo ─────────────────────────────
plt.clf()
plt.plot(anos, df["rec_palm"].tolist(), label="Palmeiras", marker="dot")
plt.plot(anos, df["rec_fla"].tolist(),  label="Flamengo",  marker="dot")
plt.vertical_line(2014.5, color="red+")
plt.title("Grafico 3 – Palmeiras vs Flamengo: Receita Total Nominal (2012–2025)\n| linha vermelha = inicio acordo Allianz")
plt.xlabel("Ano")
plt.ylabel("R$ milhoes")
plt.plot_size(110, 25)
plt.show()

input("\n  [ENTER para proximo grafico]")

# ── Gráfico 4: Razão Palmeiras / Flamengo ────────────────────────
plt.clf()
plt.plot(anos, df["ratio"].tolist(), label="Razao Palm./Fla. (%)", marker="dot")
plt.horizontal_line(ratio_pre, color="red+")
plt.horizontal_line(ratio_pos, color="green+")
plt.vertical_line(2014.5, color="white+")
plt.title(
    f"Grafico 4 – Razao Palmeiras/Flamengo (%)\n"
    f"| pre-acordo: {ratio_pre:.1f}%  pos-acordo: {ratio_pos:.1f}%"
)
plt.xlabel("Ano")
plt.ylabel("% da receita do Flamengo")
plt.plot_size(110, 25)
plt.show()

input("\n  [ENTER para proximo grafico]")

# ── Gráfico 5: IGP-M via API ──────────────────────────────────────
plt.clf()
igpm_vals = [igpm[a] for a in anos]
plt.plot(anos, igpm_vals, label="IGP-M (base 2015=100)", marker="dot")
plt.horizontal_line(100, color="red+")
plt.title("Grafico 5 – IGP-M Anual (base 2015=100)\n| Fonte: API Banco Central – BCB/SGS serie 189")
plt.xlabel("Ano")
plt.ylabel("Indice")
plt.plot_size(110, 25)
plt.show()

print("\n" + "=" * 55)
print("  Analise concluida!")
print("=" * 55)
