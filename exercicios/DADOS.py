"""
============================================================
NAMING RIGHTS NO FUTEBOL BRASILEIRO: VALE A PENA PARA OS CLUBES?
Um Estudo de Caso Financeiro - IBMEC Brasília (2026)
Autor: João Petrini Moral
============================================================

Este script implementa as 4 etapas metodológicas descritas no TCC:
  Etapa 1 – Análise de séries temporais (Palmeiras, 2012–2024)
  Etapa 2 – Estudo comparativo DiD simplificado (Palmeiras vs Flamengo)
  Etapa 3 – Modelagem de ROI por cenários
  Etapa 4 – Framework de avaliação financeira

OBSERVAÇÃO: O acordo analisado é o da Allianz (2014–2025).
O acordo com o Nubank (2026) NÃO é escopo deste trabalho.

Fontes:
  - Balanços oficiais Palmeiras / Flamengo / Atlético-MG SAF
  - ESPN Brasil / CNN Brasil / FutebolMarket / EY Football Finance 2022
  - Valores estimados identificados conforme metodologia do TCC
============================================================
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 130,
})

VERDE  = "#006400"
RUBRO  = "#CC0000"
GALO   = "#000000"
NEUTRO = "#4477AA"
CINZA  = "#AAAAAA"

# ════════════════════════════════════════════════════════════════════════
# BLOCO 1 – BASE DE DADOS
# ════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("ETAPA 0 – Carregando dados financeiros")
print("=" * 60)

anos = list(range(2012, 2025))

# Palmeiras – Receita Total (R$ milhões)
# Fontes: ESPN Brasil, Gazeta Esportiva, CNN Brasil, Terra, Revista Época
# Valores marcados com * são estimados/interpolados
receita_palmeiras = {
    2012: 240.0,   # *estimado (déficit R$22mi + estrutura de custos da época)
    2013: 181.2,   # confirmado – ESPN (Série B, queda acentuada)
    2014: 243.0,   # *estimado – inauguração da arena nov/2014, sem naming rights
    2015: 350.5,   # confirmado – Revista Época (1º ano Allianz)
    2016: 440.0,   # *interpolado (350→688)
    2017: 530.0,   # *interpolado
    2018: 688.5,   # confirmado – ESPN Brasil
    2019: 641.0,   # confirmado – Gazeta Esportiva / ESPN
    2020: 558.0,   # confirmado – SBT Sports / Terra (pandemia)
    2021: 992.0,   # confirmado – CNN Brasil / ESPN (prêmios represados)
    2022: 856.0,   # confirmado – EY / CNN Brasil
    2023: 908.0,   # confirmado – ESPN
    2024: 1221.0,  # confirmado – CNN Brasil / ESPN (recorde histórico)
}

# Flamengo – Receita Total (R$ milhões)
# Fonte: FutebolMarket (histórico 2012-2024); mktesportivo.com
receita_flamengo = {
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
}

# Atlético-MG – Receita Total (R$ milhões)
# Fontes: ESPN (2021), EY/CNN (2022), NoAtaque (2023), CAM Relatório 2024
receita_atletico = {
    2020: 154.0,
    2021: 506.0,
    2022: 429.0,
    2023: 463.0,
    2024: 657.0,
}

# Palmeiras – Receita Comercial (patrocínio + publicidade + naming, R$ milhões)
# Fontes: ESPN Brasil 2022-2024; valores anteriores estimados com base na
# trajetória da Crefisa (iniciou 2015) e do naming rights Allianz (~R$15mi/ano)
receita_comercial_palmeiras = {
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
}


#API

# IGP-M acumulado (base 2015=100) – FGV / Banco Central
igpm = {
    2012: 73.4,  2013: 79.1,  2014: 86.3,  2015: 100.0,
    2016: 112.4, 2017: 115.1, 2018: 123.4, 2019: 131.9,
    2020: 158.5, 2021: 192.4, 2022: 206.8, 2023: 219.0,
    2024: 236.0,
}

df = pd.DataFrame({
    "ano":          anos,
    "rec_palm":     [receita_palmeiras[a] for a in anos],
    "rec_fla":      [receita_flamengo[a] for a in anos],
    "rec_com_palm": [receita_comercial_palmeiras[a] for a in anos],
    "igpm":         [igpm[a] for a in anos],
    "naming":       [1 if a >= 2015 else 0 for a in anos],
})

df["rec_palm_real"]     = df["rec_palm"]     / df["igpm"] * 100
df["rec_fla_real"]      = df["rec_fla"]      / df["igpm"] * 100
df["rec_com_palm_real"] = df["rec_com_palm"] / df["igpm"] * 100
df["share_com"]         = df["rec_com_palm"] / df["rec_palm"] * 100
df["ratio"]             = df["rec_palm"]     / df["rec_fla"]

anos_atl = [2020, 2021, 2022, 2023, 2024]
df_atl = pd.DataFrame({
    "ano":     anos_atl,
    "rec_atl": [receita_atletico[a] for a in anos_atl],
    "igpm":    [igpm[a] for a in anos_atl],
})
df_atl["rec_atl_real"] = df_atl["rec_atl"] / df_atl["igpm"] * 100

print("Dados carregados com sucesso.")
print(f"  Palmeiras (2012-2024): {len(df)} observações")
print(f"  Flamengo  (2012-2024): {len(df)} observações")
print(f"  Atlético  (2020-2024): {len(df_atl)} observações")
print("\nReceita Total Nominal (R$ milhões):")
print(df[["ano","rec_palm","rec_fla"]].to_string(index=False))


# ════════════════════════════════════════════════════════════════════════
# ETAPA 1 – ANÁLISE DE SÉRIES TEMPORAIS
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ETAPA 1 – Análise de Séries Temporais (Palmeiras)")
print("=" * 60)

pre = df[df["naming"] == 0]
pos = df[df["naming"] == 1]

def cagr(inicio, fim, n):
    return (fim / inicio) ** (1 / n) - 1

cagr_pre_nom  = cagr(pre.iloc[0]["rec_palm"],      pre.iloc[-1]["rec_palm"],      2)
cagr_pos_nom  = cagr(pos.iloc[0]["rec_palm"],      pos.iloc[-1]["rec_palm"],      9)
cagr_pre_real = cagr(pre.iloc[0]["rec_palm_real"], pre.iloc[-1]["rec_palm_real"], 2)
cagr_pos_real = cagr(pos.iloc[0]["rec_palm_real"], pos.iloc[-1]["rec_palm_real"], 9)

print(f"\nCAGR Receita Total – Pré-acordo  (2012-2014) nominal:  {cagr_pre_nom*100:+.1f}% a.a.")
print(f"CAGR Receita Total – Pós-acordo  (2015-2024) nominal:  {cagr_pos_nom*100:+.1f}% a.a.")
print(f"CAGR Receita Total – Pré-acordo  (2012-2014) real:     {cagr_pre_real*100:+.1f}% a.a.")
print(f"CAGR Receita Total – Pós-acordo  (2015-2024) real:     {cagr_pos_real*100:+.1f}% a.a.")

cag_com = (receita_comercial_palmeiras[2024] / receita_comercial_palmeiras[2015] - 1) * 100
print(f"\nCrescimento receita comercial (2015-2024): +{cag_com:.0f}%")
print(f"Rec. comercial 2015: R${receita_comercial_palmeiras[2015]:.0f}mi  |  2024: R${receita_comercial_palmeiras[2024]:.0f}mi")

print("\nParticipação % receita comercial / receita total:")
for _, row in df.iterrows():
    print(f"  {int(row.ano)}: {row.share_com:.1f}%")


# ════════════════════════════════════════════════════════════════════════
# ETAPA 2 – COMPARATIVO DiD SIMPLIFICADO
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ETAPA 2 – Comparativo Palmeiras vs Flamengo (DiD)")
print("=" * 60)

ratio_pre = df[df["naming"] == 0]["ratio"].mean()
ratio_pos = df[df["naming"] == 1]["ratio"].mean()
print(f"\nRazão Palmeiras/Flamengo:")
print(f"  Pré-acordo: {ratio_pre:.3f}  ({ratio_pre*100:.0f}% da receita do Flamengo)")
print(f"  Pós-acordo: {ratio_pos:.3f}  ({ratio_pos*100:.0f}% da receita do Flamengo)")

df["delta_palm"] = df["rec_palm"].pct_change()
df["delta_fla"]  = df["rec_fla"].pct_change()

cresc_pre_palm = df[df["naming"]==0]["delta_palm"].mean() * 100
cresc_pos_palm = df[df["naming"]==1]["delta_palm"].mean() * 100
cresc_pre_fla  = df[df["naming"]==0]["delta_fla"].mean()  * 100
cresc_pos_fla  = df[df["naming"]==1]["delta_fla"].mean()  * 100

delta_palm = cresc_pos_palm - cresc_pre_palm
delta_fla  = cresc_pos_fla  - cresc_pre_fla
did        = delta_palm - delta_fla

print(f"\nCrescimento médio anual:")
print(f"  Palmeiras pré: {cresc_pre_palm:.1f}%  |  pós: {cresc_pos_palm:.1f}%")
print(f"  Flamengo  pré: {cresc_pre_fla:.1f}%  |  pós: {cresc_pos_fla:.1f}%")
print(f"\nDiD estimado (crescimento médio anual):")
print(f"  Delta Palmeiras (pós-pré) = {delta_palm:+.1f} p.p.")
print(f"  Delta Flamengo  (pós-pré) = {delta_fla:+.1f} p.p.")
print(f"  DiD             = {did:+.1f} p.p.")
print(f"\n  Efeito diferencial estimado: +{did:.1f} p.p./ano (heurístico)")


# ════════════════════════════════════════════════════════════════════════
# ETAPA 3 – ROI POR CENÁRIOS
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ETAPA 3 – Modelagem de ROI por Cenários")
print("=" * 60)

# Palmeiras / Allianz (2015-2025)
# Contrato: ~R$300mi / 20 anos = R$15mi/ano (Lancenet, 2015 – estimado)
# Repasses confirmados: R$235mi em 12 anos (Times Brasil, 2026)
receita_naming_anual = 15.0       # R$ mi/ano
anos_decorridos      = 11         # 2015-2025
multiplicador_base   = 19.75      # R$ mi/ano (25% do diferencial comercial)
custo_oport_anual    = 7.5        # R$ mi/ano (50% do naming; alternativa de mercado)

def roi_palmeiras(cenario):
    fatores = {
        "otimista":   (1.20, 1.30, 0.80),
        "base":       (1.00, 1.00, 1.00),
        "pessimista": (0.75, 0.50, 1.30),
    }
    fd, fm, fc = fatores[cenario]
    rec_dir = receita_naming_anual * anos_decorridos * fd
    ef_mult = multiplicador_base   * anos_decorridos * fm
    custo   = custo_oport_anual    * anos_decorridos * fc
    benef   = rec_dir + ef_mult - custo
    roi     = benef / custo * 100
    return {"rec_dir": round(rec_dir,1), "ef_mult": round(ef_mult,1),
            "custo": round(custo,1), "benef": round(benef,1), "roi": round(roi,1)}

cenarios = ["otimista", "base", "pessimista"]
res = {c: roi_palmeiras(c) for c in cenarios}

print(f"\nPressupostos – Palmeiras/Allianz:")
print(f"  Valor estimado contrato: R$300mi / 20 anos = R${receita_naming_anual:.0f}mi/ano")
print(f"  Período analisado: {anos_decorridos} anos (2015-2025)")
print(f"  Multiplicador base: R${multiplicador_base:.2f}mi/ano")
print(f"  Custo de oportunidade: R${custo_oport_anual:.1f}mi/ano")

print(f"\n{'Variável':<32} {'Otimista':>10} {'Base':>10} {'Pessimista':>10}")
print("-" * 62)
for key, lbl in [("rec_dir","Receita direta (R$mi)"),
                 ("ef_mult","Efeito multiplicador (R$mi)"),
                 ("custo","Custo de oportunidade (R$mi)"),
                 ("benef","Benefício líquido (R$mi)"),
                 ("roi","ROI (%)")]:
    vals = [res[c][key] for c in cenarios]
    print(f"{lbl:<32} {vals[0]:>10.1f} {vals[1]:>10.1f} {vals[2]:>10.1f}")

print("\n-- Atlético-MG / Arena MRV (dados iniciais 2024) --")
mrv_receita = 88.1
mrv_naming  = 25.0   # R$500mi / 20 anos
mrv_lucro   = mrv_receita * 0.70
print(f"  Receita bruta Arena MRV 2024: R${mrv_receita:.1f}mi")
print(f"  Margem líquida: 70% -> Lucro R${mrv_lucro:.1f}mi")
print(f"  Naming Rights estimado: R${mrv_naming:.0f}mi/ano")
print(f"  Receita total arena+naming: R${mrv_receita+mrv_naming:.1f}mi/ano (projeção)")


# ════════════════════════════════════════════════════════════════════════
# SCORECARD FINANCEIRO (Módulo 1 do Framework)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ETAPA 4 – Framework de Avaliação Financeira")
print("=" * 60)

def scorecard(rec_total, rec_naming, divida, rec_com, duracao, mult_est=None, nome="Clube"):
    if mult_est is None:
        mult_est = rec_naming * 0.20
    vt = rec_naming * duracao
    part = rec_naming / rec_total * 100
    red_div = vt / divida * 100 if divida > 0 else 999
    cresc_com = (rec_naming + mult_est) / rec_com * 100
    roi_base = (rec_naming + mult_est) / (rec_naming * 0.5) * 100

    pts = 0
    pts += 2 if part >= 5 else (1 if part >= 3 else 0)
    pts += 2 if red_div >= 20 else (1 if red_div >= 10 else 0)
    pts += 2 if cresc_com >= 30 else (1 if cresc_com >= 20 else 0)
    pts += 2 if roi_base >= 150 else (1 if roi_base >= 100 else 0)
    pts += 2 if duracao <= 15 else (1 if duracao <= 20 else 0)

    rec_str = ("VANTAJOSO" if pts >= 7 else
               "CONDICIONAL" if pts >= 4 else "DESVANTAJOSO")

    print(f"\n  ── Scorecard: {nome} ──")
    print(f"  Participação naming/receita total: {part:.1f}%")
    print(f"  Equivalência contrato/dívida:      {min(red_div,999):.1f}%")
    print(f"  Crescimento comercial estimado:    {cresc_com:.1f}%")
    print(f"  ROI base estimado:                 {roi_base:.1f}%")
    print(f"  Duração do contrato:               {duracao} anos")
    print(f"  PONTUAÇÃO: {pts}/10  ->  {rec_str}")
    return pts, roi_base

p1, _ = scorecard(350.5, 15.0, 250.0, 65.0,   20, 4.0,  "Palmeiras (ex-ante 2015)")
p2, _ = scorecard(1170., 30.0, 250.0, 250.0,  15, 6.0,  "Flamengo (hipotético 2022)")
p3, _ = scorecard(463.0, 25.0, 1570., 80.0,   20, 5.0,  "Atlético-MG (ex-ante 2023)")


# ════════════════════════════════════════════════════════════════════════
# GERAÇÃO DOS GRÁFICOS
# ════════════════════════════════════════════════════════════════════════
print("\nGerando visualizações...")

fig = plt.figure(figsize=(18, 24))
gs  = gridspec.GridSpec(4, 2, figure=fig, hspace=0.48, wspace=0.32)

# Graf 1: Série temporal Palmeiras
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(df["ano"], df["rec_palm"],      color=VERDE, lw=2.5, marker="o", ms=6, label="Receita total (nominal)")
ax1.plot(df["ano"], df["rec_palm_real"], color=VERDE, lw=1.5, ls="--", marker="s", ms=5, label="Receita total (real, R$ 2015)")
ax1.axvline(x=2014.5, color="gray", ls="--", lw=1.5)
ax1.axvspan(2012, 2014.5,  alpha=0.07, color="red",   label="Pré-acordo (2012-2014)")
ax1.axvspan(2014.5, 2024.5, alpha=0.07, color="green", label="Pós-acordo Allianz (2015-2024)")
ax1.set_title("Caso 1 – Palmeiras: Receita Total (2012-2024)\nAcordo Allianz Parque vigente a partir de 2015", fontweight="bold")
ax1.set_ylabel("R$ milhões"); ax1.set_xlabel("Ano")
ax1.legend(loc="upper left"); ax1.set_xticks(anos)
ax1.set_xticklabels(anos, rotation=45); ax1.grid(axis="y", alpha=0.3)
ax1.annotate(f"CAGR nominal pré:\n{cagr_pre_nom*100:+.0f}%/ano",
             xy=(2013,230), fontsize=9, color="darkred",
             bbox=dict(boxstyle="round,pad=0.3",fc="white",alpha=0.7))
ax1.annotate(f"CAGR nominal pós:\n{cagr_pos_nom*100:+.0f}%/ano",
             xy=(2019,820), fontsize=9, color="darkgreen",
             bbox=dict(boxstyle="round,pad=0.3",fc="white",alpha=0.7))

# Graf 2: Receita comercial Palmeiras
ax2 = fig.add_subplot(gs[1, 0])
ax2.bar(df["ano"], df["rec_com_palm"],
        color=[VERDE if a >= 2015 else CINZA for a in df["ano"]], alpha=0.85)
ax2.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax2.set_title("Palmeiras: Receita Comercial\n(patrocínio + publicidade + naming rights)")
ax2.set_ylabel("R$ milhões"); ax2.set_xlabel("Ano")
ax2.set_xticks(anos); ax2.set_xticklabels(anos, rotation=45); ax2.grid(axis="y", alpha=0.3)
ax2.legend(handles=[mpatches.Patch(color=VERDE,alpha=0.85,label="Pós-acordo"),
                    mpatches.Patch(color=CINZA,alpha=0.85,label="Pré-acordo")])

# Graf 3: Palmeiras vs Flamengo
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(df["ano"], df["rec_palm"], color=VERDE, lw=2.5, marker="o", ms=6, label="Palmeiras")
ax3.plot(df["ano"], df["rec_fla"],  color=RUBRO, lw=2.5, marker="s", ms=6, label="Flamengo (controle)")
ax3.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax3.set_title("Etapa 2 – Palmeiras vs Flamengo\nReceita Total Nominal (R$ mi)")
ax3.set_ylabel("R$ milhões"); ax3.set_xlabel("Ano")
ax3.legend(); ax3.set_xticks(anos); ax3.set_xticklabels(anos, rotation=45); ax3.grid(axis="y", alpha=0.3)

# Graf 4: Razão Palmeiras/Flamengo
ax4 = fig.add_subplot(gs[2, 0])
ax4.plot(df["ano"], df["ratio"]*100, color=NEUTRO, lw=2.5, marker="D", ms=6)
ax4.axhline(ratio_pre*100, color="red",   ls="--", lw=1.2, label=f"Média pré ({ratio_pre*100:.0f}%)")
ax4.axhline(ratio_pos*100, color="green", ls="--", lw=1.2, label=f"Média pós ({ratio_pos*100:.0f}%)")
ax4.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax4.set_title("Razão Receita Palmeiras / Flamengo (%)\nConvergência pós-Allianz")
ax4.set_ylabel("%"); ax4.set_xlabel("Ano"); ax4.legend()
ax4.set_xticks(anos); ax4.set_xticklabels(anos, rotation=45); ax4.grid(axis="y", alpha=0.3)

# Graf 5: ROI cenários
ax5 = fig.add_subplot(gs[2, 1])
variaveis = ["Receita\ndireta", "Efeito\nmultipl.", "Custo de\noport.", "Benefício\nlíquido"]
x = np.arange(len(variaveis)); w = 0.26
cores_c = ["#2ecc71","#3498db","#e74c3c"]
for i, c in enumerate(cenarios):
    vals = [res[c]["rec_dir"], res[c]["ef_mult"], -res[c]["custo"], res[c]["benef"]]
    ax5.bar(x+(i-1)*w, vals, w, label=c.capitalize(), color=cores_c[i], alpha=0.85)
    ax5.text(x[-1]+(i-1)*w, res[c]["benef"]+5, f"ROI\n{res[c]['roi']:.0f}%",
             ha="center", fontsize=8, color=cores_c[i], fontweight="bold")
ax5.axhline(0, color="black", lw=0.8)
ax5.set_title("Etapa 3 – ROI Palmeiras/Allianz por Cenário\n(período 2015-2025, R$ mi)")
ax5.set_ylabel("R$ milhões"); ax5.set_xticks(x); ax5.set_xticklabels(variaveis)
ax5.legend(); ax5.grid(axis="y", alpha=0.3)

# Graf 6: Radar scorecard
ax6 = fig.add_subplot(gs[3, 0], projection="polar")
dims = ["Participação\nna receita","Impacto\nna dívida","Crescimento\ncomercial","ROI base","Duração\ncontrato"]
scores = {
    "Palmeiras":         [2,1,1,1,1],
    "Atlético-MG":       [1,0,1,1,1],
    "Flamengo (hipot.)": [1,2,1,1,2],
}
N = len(dims)
angulos = np.linspace(0,2*np.pi,N,endpoint=False).tolist() + [0]
ax6.set_theta_offset(np.pi/2); ax6.set_theta_direction(-1)
ax6.set_xticks(angulos[:-1]); ax6.set_xticklabels(dims,size=8); ax6.set_ylim(0,2)
for (nome,sc), cor in zip(scores.items(), [VERDE,GALO,RUBRO]):
    v = sc + sc[:1]
    ax6.plot(angulos,v,"o-",lw=1.8,color=cor,label=nome)
    ax6.fill(angulos,v,alpha=0.12,color=cor)
ax6.set_title("Scorecard Financeiro (Módulo 1)\nComparativo dos 3 casos", fontweight="bold", pad=15)
ax6.legend(loc="upper right", bbox_to_anchor=(1.4,1.15))

# Graf 7: Arena MRV
ax7 = fig.add_subplot(gs[3, 1])
anos_mrv = [2023, 2024]; rec_mrv=[13.6,88.1]; luc_mrv=[8.2,61.7]
x_mrv = np.arange(len(anos_mrv))
ax7.bar(x_mrv-0.2, rec_mrv, 0.35, label="Receita bruta", color=GALO,   alpha=0.75)
ax7.bar(x_mrv+0.2, luc_mrv, 0.35, label="Receita líquida", color="#666", alpha=0.75)
ax7.set_xticks(x_mrv); ax7.set_xticklabels(["2023\n(parcial)","2024\n(1ª temp. completa)"])
ax7.set_title("Caso 3 – Atlético-MG: Arena MRV\nReceita do Estádio"); ax7.set_ylabel("R$ milhões")
ax7.legend(); ax7.grid(axis="y", alpha=0.3)

fig.text(0.5, 0.005,
    "Fontes: Balanços oficiais Palmeiras/Flamengo/CAM-SAF | EY Football Finance 2022 | ESPN Brasil | CNN Brasil | FutebolMarket\n"
    "Valores nominais em R$ mi. Valores estimados identificados no código. Acordo Nubank (2026) NÃO é escopo desta análise.",
    ha="center", fontsize=8, color="gray", style="italic")
fig.suptitle("Naming Rights no Futebol Brasileiro – Análise Financeira Comparativa\n"
             "Palmeiras (Allianz Parque) | Flamengo (controle) | Atlético-MG (Arena MRV)",
             fontsize=14, fontweight="bold", y=1.0)

plt.savefig("naming_rights_analise.png", bbox_inches="tight", dpi=150)
print("Grafico 1 salvo: naming_rights_analise.png")


# ── Árvore de decisão ───────────────────────────────────────────────────────
fig2, ax = plt.subplots(figsize=(14, 10))
ax.axis("off")

def node(ax, xy, txt, fc="white", ec="black", fs=9):
    ax.text(xy[0], xy[1], txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", fc=fc, ec=ec, lw=1.5),
            transform=ax.transAxes)

def arrow(ax, de, para, lbl="", lc="black"):
    ax.annotate("", xy=para, xytext=de, xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="->", color=lc, lw=1.5))
    if lbl:
        mx=(de[0]+para[0])/2; my=(de[1]+para[1])/2
        ax.text(mx+0.01, my, lbl, fontsize=8, color=lc, ha="left", va="center",
                transform=ax.transAxes)

node(ax,(0.50,0.92),"CLUBE AVALIA\nNAMING RIGHTS","#2C3E50","black",11)
node(ax,(0.50,0.78),"ROI base estimado >= 100%?","#EBF5FB","navy")
node(ax,(0.22,0.63),"Scorecard >= 7/10?","#EBF5FB","navy")
node(ax,(0.78,0.63),"Duração <= 15 anos?","#EBF5FB","navy")
node(ax,(0.22,0.48),"Risco reputacional\ndo patrocinador baixo?","#EBF5FB","navy")
node(ax,(0.78,0.48),"Há cláusula de\nrescisão/reajuste?","#EBF5FB","navy")

node(ax,(0.10,0.28),"VANTAJOSO\nAssinar o acordo","#27AE60","darkgreen",9)
node(ax,(0.35,0.28),"CONDICIONAL\nNegociar cláusulas","#F39C12","darkorange",9)
node(ax,(0.65,0.28),"CONDICIONAL\nRever duração/valor","#F39C12","darkorange",9)
node(ax,(0.90,0.28),"DESVANTAJOSO\nRecusar o acordo","#E74C3C","darkred",9)

arrow(ax,(0.50,0.87),(0.50,0.83))
arrow(ax,(0.50,0.78),(0.22,0.68),"Sim","green")
arrow(ax,(0.50,0.78),(0.78,0.68),"Não","red")
arrow(ax,(0.22,0.63),(0.22,0.53),"Sim","green")
arrow(ax,(0.22,0.63),(0.35,0.33),"Não","orange")
arrow(ax,(0.78,0.63),(0.78,0.53),"Sim","green")
arrow(ax,(0.78,0.63),(0.90,0.33),"Não","red")
arrow(ax,(0.22,0.48)
      ,(0.10,0.33),"Sim","green")
arrow(
    ax,(0.22,0.48),(0.35,0.33),"Não","orange")
arrow(ax,(0.78,0.48),(0.65,0.33),"Sim","orange")
arrow(ax,(0.78,0.48),(0.90,0.33),"Não","red")

ax.set_title("Módulo 3 – Árvore de Decisão: Framework de Avaliação de Naming Rights\n"
             "(baseado nos estudos de caso: Palmeiras, Flamengo e Atlético-MG)",
             fontsize=12, fontweight="bold", pad=15)
fig2.text(0.5,0.01,
    "Acordo Nubank (Palmeiras, 2026) NÃO é escopo desta pesquisa.",
    ha="center", fontsize=8, color="gray", style="italic")

plt.savefig("framework_arvore_decisao.png", bbox_inches="tight", dpi=150)
print("Grafico 2 salvo: framework_arvore_decisao.png")


# ════════════════════════════════════════════════════════════════════════
# SUMÁRIO EXECUTIVO
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SUMARIO EXECUTIVO")
print("=" * 60)
print(f"""
ETAPA 1 – SÉRIES TEMPORAIS (Palmeiras 2012-2024)
  CAGR nominal pre-acordo:  {cagr_pre_nom*100:+.1f}%/ano
  CAGR nominal pos-acordo:  {cagr_pos_nom*100:+.1f}%/ano
  Crescimento rec. comercial 2015-2024: +{cag_com:.0f}%

ETAPA 2 – DiD SIMPLIFICADO
  Razão Palmeiras/Flamengo pre: {ratio_pre*100:.0f}%  pos: {ratio_pos*100:.0f}%
  Efeito diferencial estimado: {did:+.1f} p.p./ano

ETAPA 3 – ROI PALMEIRAS/ALLIANZ (2015-2025)
  Cenário otimista:   ROI {res['otimista']['roi']:.0f}%  Benefício R${res['otimista']['benef']:.0f}mi
  Cenário base:       ROI {res['base']['roi']:.0f}%  Benefício R${res['base']['benef']:.0f}mi
  Cenário pessimista: ROI {res['pessimista']['roi']:.0f}%  Benefício R${res['pessimista']['benef']:.0f}mi

ETAPA 4 – SCORECARD
  Palmeiras (ex-ante 2015):  {p1}/10
  Flamengo  (hipotético):    {p2}/10
  Atlético-MG (ex-ante):     {p3}/10

NOTA: Este script analisa exclusivamente o período do acordo Allianz
(2015-2025). O acordo com o Nubank (Palmeiras, 2026) nao e escopo.
""")

print("Analise concluida. Arquivos gerados:")
print("  naming_rights_analise.png")
print("  framework_arvore_decisao.png")