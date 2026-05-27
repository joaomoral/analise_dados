"""
================================================================
NAMING RIGHTS NO FUTEBOL BRASILEIRO – TCC IBMEC 2026
================================================================
PASSO A PASSO:
  PASSO 1 – Importar bibliotecas
  PASSO 2 – Buscar IGP-M via API do Banco Central (BCB/SGS)
  PASSO 3 – Montar a base de dados dos clubes
  PASSO 4 – Calcular métricas (CAGR, participação comercial)
  PASSO 5 – Plotar os gráficos no VS Code

NOTA: O acordo analisado é o da Allianz Parque (2015–2025).
      O acordo com o Nubank (2026) NÃO é escopo deste trabalho.
================================================================
"""

# ================================================================
# PASSO 1 – IMPORTAR BIBLIOTECAS
# ================================================================
import requests
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches

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
    "&dataFinal=31/12/2024"
)

response = requests.get(URL)
print(f"  Status da API: {response.status_code}")  # 200 = sucesso

dados = response.json()
df_igpm = pd.DataFrame(dados)
print(f"  Dados recebidos: {len(df_igpm)} meses")
print(df_igpm)

# Tratar colunas e acumular variação → nível do índice
df_igpm["data"]  = pd.to_datetime(df_igpm["data"], dayfirst=True)
df_igpm["valor"] = pd.to_numeric(df_igpm["valor"], errors="coerce")
df_igpm["ano"]   = df_igpm["data"].dt.year
df_igpm          = df_igpm.sort_values("data").reset_index(drop=True)
df_igpm["fator"] = 1 + df_igpm["valor"] / 100
df_igpm["nivel"] = df_igpm["fator"].cumprod()

# Média anual do nível → reindexar para base 2015 = 100
nivel_anual = df_igpm.groupby("ano")["nivel"].mean()
base_2015   = nivel_anual[2015]
igpm        = {int(a): round(v / base_2015 * 100, 2)
               for a, v in nivel_anual.items()}

print(f"\n  IGP-M anual (base 2015 = 100):")
print(f"  {igpm}")


# ================================================================
# PASSO 3 – MONTAR A BASE DE DADOS DOS CLUBES
# ================================================================
# Receitas em R$ milhões (nominais).
# Fontes: balanços oficiais, ESPN Brasil, CNN Brasil, EY 2022.
# Anos com * são estimados/interpolados.

print("\n" + "=" * 55)
print("PASSO 3 – Montando base de dados dos clubes")
print("=" * 55)

anos = list(range(2012, 2025))

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
    2024: 1221.0,  # CNN Brasil / ESPN (recorde)
}

# Flamengo – Receita Total (R$ mi) – FutebolMarket (série histórica)
rec_fla = {
    2012: 212.0,  2013: 273.0,  2014: 347.0,
    2015: 356.0,  2016: 510.0,  2017: 649.0,
    2018: 543.0,  2019: 950.0,  2020: 669.0,
    2021: 1080.0, 2022: 1170.0, 2023: 1370.0,
    2024: 1330.0,
}

# Palmeiras – Receita Comercial (patrocínio + naming + publicidade)
# 2022–2024 confirmados (ESPN). Demais: estimados.
rec_com = {
    2012: 25.0,  2013: 22.0,  2014: 28.0,
    2015: 65.0,  2016: 80.0,  2017: 90.0,
    2018: 105.0, 2019: 110.0, 2020: 95.0,
    2021: 120.8, 2022: 142.6, 2023: 127.1,
    2024: 142.9,
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

print("  Dados carregados. Prévia:")
print(df[["ano", "rec_palm", "rec_fla", "igpm"]].to_string(index=False))


# ================================================================
# PASSO 4 – CALCULAR MÉTRICAS
# ================================================================
print("\n" + "=" * 55)
print("PASSO 4 – Calculando métricas")
print("=" * 55)

pre   = df[df["pos"] == 0]
pos_df= df[df["pos"] == 1]

def cagr(v_ini, v_fim, n):
    return (v_fim / v_ini) ** (1 / n) - 1

cagr_pre      = cagr(pre.iloc[0]["rec_palm"],         pre.iloc[-1]["rec_palm"],         2)
cagr_pos      = cagr(pos_df.iloc[0]["rec_palm"],      pos_df.iloc[-1]["rec_palm"],      9)
cagr_pre_real = cagr(pre.iloc[0]["rec_palm_real"],    pre.iloc[-1]["rec_palm_real"],    2)
cagr_pos_real = cagr(pos_df.iloc[0]["rec_palm_real"], pos_df.iloc[-1]["rec_palm_real"], 9)
cag_com       = (rec_com[2024] / rec_com[2015] - 1) * 100
ratio_pre     = pre["ratio"].mean()
ratio_pos     = pos_df["ratio"].mean()

print(f"\n  CAGR receita total (nominal):")
print(f"    Pré-acordo (2012-2014): {cagr_pre*100:+.1f}% a.a.")
print(f"    Pós-acordo (2015-2024): {cagr_pos*100:+.1f}% a.a.")
print(f"\n  CAGR receita total (real – IGP-M via API BCB):")
print(f"    Pré-acordo (2012-2014): {cagr_pre_real*100:+.1f}% a.a.")
print(f"    Pós-acordo (2015-2024): {cagr_pos_real*100:+.1f}% a.a.")
print(f"\n  Crescimento receita comercial (2015→2024): +{cag_com:.0f}%")
print(f"\n  Razão Palmeiras / Flamengo:")
print(f"    Pré-acordo: {ratio_pre:.1f}%")
print(f"    Pós-acordo: {ratio_pos:.1f}%")


# ================================================================
# PASSO 5 – PLOTAR OS GRÁFICOS NO VS CODE
# ================================================================
print("\n" + "=" * 55)
print("PASSO 5 – Gerando gráficos (aguarde...)")
print("=" * 55)

VERDE  = "#006400"
RUBRO  = "#CC0000"
AZUL   = "#2C6FAC"
CINZA  = "#888888"
LARANJ = "#E67E22"

plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   12,
    "axes.labelsize":   10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
    "axes.grid":        True,
    "grid.alpha":       0.3,
    "figure.facecolor": "white",
})

estimados = {2012, 2014, 2016, 2017}

fig = plt.figure(figsize=(16, 20))
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.50, wspace=0.35)

# ── Gráfico 1 (topo largo): Série receita Palmeiras nominal + real ───────────
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(df["ano"], df["rec_palm"],      color=VERDE, lw=2.5, marker="o", ms=6,
         label="Nominal (R$ mi)")
ax1.plot(df["ano"], df["rec_palm_real"], color=VERDE, lw=1.5, ls="--", marker="s", ms=5,
         label="Real – deflacionado (IGP-M via API BCB, base 2015=100)")
for _, row in df[df["ano"].isin(estimados)].iterrows():
    ax1.scatter(row["ano"], row["rec_palm"], marker="^", color=LARANJ, s=100, zorder=5)
ax1.axvspan(2011.5, 2014.5, alpha=0.07, color="red",   label="Pré-acordo (2012-2014)")
ax1.axvspan(2014.5, 2024.5, alpha=0.07, color="green", label="Pós-acordo Allianz (2015-2024)")
ax1.axvline(x=2014.5, color="gray", ls="--", lw=1.5)
ax1.annotate(f"CAGR pré\n{cagr_pre*100:+.0f}%/ano", xy=(2013, 215), fontsize=9,
             color="darkred",   bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
ax1.annotate(f"CAGR pós\n{cagr_pos*100:+.0f}%/ano", xy=(2020, 830), fontsize=9,
             color="darkgreen", bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
ax1.scatter([], [], marker="^", color=LARANJ, s=80, label="Valor estimado/interpolado")
ax1.set_title("Palmeiras – Receita Total (2012–2024)\n"
              "Série temporal com quebra em 2015 (início do acordo Allianz Parque)",
              fontweight="bold")
ax1.set_ylabel("R$ milhões")
ax1.set_xlabel("Ano")
ax1.set_xticks(anos)
ax1.set_xticklabels(anos, rotation=45)
ax1.legend(loc="upper left")

# ── Gráfico 2 (meio-esq.): Receita comercial ────────────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
cores = [LARANJ if a in estimados else (VERDE if a >= 2015 else CINZA) for a in df["ano"]]
ax2.bar(df["ano"], df["rec_com"], color=cores, alpha=0.85)
ax2.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax2r = ax2.twinx()
ax2r.plot(df["ano"], df["share_com"], color=AZUL, lw=2, marker="D", ms=5)
ax2r.set_ylabel("Participação % na receita total", color=AZUL)
ax2r.tick_params(axis="y", colors=AZUL)
ax2.set_title("Receita Comercial Palmeiras\n(patrocínio + naming Allianz + publicidade)")
ax2.set_ylabel("R$ milhões")
ax2.set_xlabel("Ano")
ax2.set_xticks(anos)
ax2.set_xticklabels(anos, rotation=45)
ax2.legend(handles=[
    mpatches.Patch(color=VERDE,  alpha=0.85, label="Pós-acordo"),
    mpatches.Patch(color=CINZA,  alpha=0.85, label="Pré-acordo"),
    mpatches.Patch(color=LARANJ, alpha=0.85, label="Estimado"),
], loc="upper left", fontsize=8)

# ── Gráfico 3 (meio-dir.): Palmeiras vs Flamengo ────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(df["ano"], df["rec_palm"], color=VERDE, lw=2.5, marker="o", ms=6, label="Palmeiras")
ax3.plot(df["ano"], df["rec_fla"],  color=RUBRO, lw=2.5, marker="s", ms=6,
         label="Flamengo (grupo controle)")
ax3.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax3.set_title("Palmeiras vs Flamengo – Receita Total Nominal\n"
              "(base para o estudo comparativo DiD)")
ax3.set_ylabel("R$ milhões")
ax3.set_xlabel("Ano")
ax3.set_xticks(anos)
ax3.set_xticklabels(anos, rotation=45)
ax3.legend()

# ── Gráfico 4 (baixo-esq.): Razão Palmeiras / Flamengo ──────────────────────
ax4 = fig.add_subplot(gs[2, 0])
ax4.plot(df["ano"], df["ratio"], color=AZUL, lw=2.5, marker="D", ms=6)
ax4.axhline(ratio_pre, color="red",   ls="--", lw=1.2, label=f"Média pré: {ratio_pre:.1f}%")
ax4.axhline(ratio_pos, color="green", ls="--", lw=1.2, label=f"Média pós: {ratio_pos:.1f}%")
ax4.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax4.set_title("Razão Receita Palmeiras / Flamengo (%)\nConvergência após acordo Allianz")
ax4.set_ylabel("% da receita do Flamengo")
ax4.set_xlabel("Ano")
ax4.set_xticks(anos)
ax4.set_xticklabels(anos, rotation=45)
ax4.legend()

# ── Gráfico 5 (baixo-dir.): IGP-M obtido da API ─────────────────────────────
ax5 = fig.add_subplot(gs[2, 1])
igpm_vals = [igpm[a] for a in anos]
ax5.plot(anos, igpm_vals, color=LARANJ, lw=2.5, marker="o", ms=6)
ax5.axhline(100, color="gray", ls="--", lw=1, label="Base = 100 (2015)")
ax5.fill_between(anos, 100, igpm_vals,
                 where=[v > 100 for v in igpm_vals],
                 alpha=0.15, color=LARANJ, label="Inflação acumulada pós-2015")
ax5.set_title("IGP-M – Índice Anual (base 2015 = 100)\nFonte: API Banco Central (BCB/SGS – série 189)")
ax5.set_ylabel("Índice (base 2015 = 100)")
ax5.set_xlabel("Ano")
ax5.set_xticks(anos)
ax5.set_xticklabels(anos, rotation=45)
ax5.legend()

fig.suptitle(
    "Naming Rights no Futebol Brasileiro – Análise Financeira (TCC IBMEC 2026)\n"
    "Palmeiras / Allianz Parque (2015–2025)  |  Acordo Nubank (2026) NÃO é escopo",
    fontsize=13, fontweight="bold"
)
fig.text(
    0.5, 0.005,
    "Fontes: ESPN Brasil, CNN Brasil, EY Football Finance 2022, FutebolMarket "
    "| IGP-M: API Banco Central (BCB/SGS) | Triângulos laranja = valores estimados",
    ha="center", fontsize=8, color="gray", style="italic"
)

plt.tight_layout(rect=[0, 0.02, 1, 0.97])
print("  Gráficos prontos! Abrindo no VS Code...")
plt.show()