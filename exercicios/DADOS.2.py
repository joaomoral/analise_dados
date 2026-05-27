"""
============================================================
ETAPA 1 – ANÁLISE DE SÉRIES TEMPORAIS (VERSÃO COMPLETA)
Naming Rights no Futebol Brasileiro – TCC IBMEC 2026
============================================================

Testes implementados:
  1. CAGR (pré vs pós acordo)
  2. Participação % receita comercial
  3. Teste de Chow (quebra estrutural em 2015)
  4. Teste de Dickey-Fuller Aumentado (estacionariedade)
  5. Regressão com variável dummy de intervenção
  6. Intervalo de confiança nas projeções

VISUALIZAÇÃO: plt.show() abre os gráficos interativos no VS Code
(requer extensão Python + Jupyter, ou rodar direto no terminal)
============================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
import warnings
warnings.filterwarnings("ignore")

# ── Configuração: gráficos interativos no VS Code ───────────────────────────
# Se estiver no terminal normal: abre janela interativa
# Se estiver no VS Code com extensão Jupyter: renderiza inline
plt.rcParams.update({
    "font.family":    "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize":10,
    "ytick.labelsize":10,
    "legend.fontsize":10,
    "figure.dpi":     110,
    "axes.grid":      True,
    "grid.alpha":     0.3,
})

VERDE = "#006400"
CINZA = "#888888"
AZUL  = "#2C6FAC"
LARANJA = "#D35400"

# ════════════════════════════════════════════════════════════════════════════
# DADOS
# ════════════════════════════════════════════════════════════════════════════
anos = list(range(2012, 2025))

receita_palmeiras = {
    2012: 240.0,  2013: 181.2,  2014: 243.0,
    2015: 350.5,  2016: 440.0,  2017: 530.0,
    2018: 688.5,  2019: 641.0,  2020: 558.0,
    2021: 992.0,  2022: 856.0,  2023: 908.0,
    2024: 1221.0,
}
receita_comercial = {
    2012: 25.0,   2013: 22.0,   2014: 28.0,
    2015: 65.0,   2016: 80.0,   2017: 90.0,
    2018: 105.0,  2019: 110.0,  2020: 95.0,
    2021: 120.8,  2022: 142.6,  2023: 127.1,
    2024: 142.9,
}
igpm = {
    2012: 73.4,  2013: 79.1,  2014: 86.3,  2015: 100.0,
    2016: 112.4, 2017: 115.1, 2018: 123.4, 2019: 131.9,
    2020: 158.5, 2021: 192.4, 2022: 206.8, 2023: 219.0,
    2024: 236.0,
}

df = pd.DataFrame({
    "ano":      anos,
    "rec_nom":  [receita_palmeiras[a] for a in anos],
    "rec_com":  [receita_comercial[a] for a in anos],
    "igpm":     [igpm[a] for a in anos],
    "dummy":    [1 if a >= 2015 else 0 for a in anos],   # 1 = pós-acordo
    "t":        list(range(len(anos))),                   # tendência linear (0,1,2...)
})
df["rec_real"]     = df["rec_nom"] / df["igpm"] * 100
df["rec_com_real"] = df["rec_com"] / df["igpm"] * 100
df["share_com"]    = df["rec_com"] / df["rec_nom"] * 100
df["log_rec"]      = np.log(df["rec_nom"])

pre = df[df["dummy"] == 0].copy()
pos = df[df["dummy"] == 1].copy()

estimados = {2012, 2014, 2016, 2017}  # anos com valores estimados/interpolados


# ════════════════════════════════════════════════════════════════════════════
# TESTE 1 – CAGR
# ════════════════════════════════════════════════════════════════════════════
def cagr(v_ini, v_fim, n): return (v_fim / v_ini) ** (1/n) - 1

cagr_pre_nom  = cagr(pre.iloc[0]["rec_nom"],  pre.iloc[-1]["rec_nom"],  2)
cagr_pos_nom  = cagr(pos.iloc[0]["rec_nom"],  pos.iloc[-1]["rec_nom"],  9)
cagr_pre_real = cagr(pre.iloc[0]["rec_real"], pre.iloc[-1]["rec_real"], 2)
cagr_pos_real = cagr(pos.iloc[0]["rec_real"], pos.iloc[-1]["rec_real"], 9)

print("=" * 60)
print("TESTE 1 – CAGR")
print("=" * 60)
print(f"  Pré-acordo (2012-2014) nominal:  {cagr_pre_nom*100:+.1f}% a.a.")
print(f"  Pós-acordo (2015-2024) nominal:  {cagr_pos_nom*100:+.1f}% a.a.")
print(f"  Pré-acordo (2012-2014) real:     {cagr_pre_real*100:+.1f}% a.a.")
print(f"  Pós-acordo (2015-2024) real:     {cagr_pos_real*100:+.1f}% a.a.")


# ════════════════════════════════════════════════════════════════════════════
# TESTE 2 – PARTICIPAÇÃO % RECEITA COMERCIAL
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TESTE 2 – PARTICIPAÇÃO % RECEITA COMERCIAL")
print("=" * 60)
media_pre_share = pre["share_com"].mean()
media_pos_share = pos["share_com"].mean()
print(f"  Média pré-acordo: {media_pre_share:.1f}%")
print(f"  Média pós-acordo: {media_pos_share:.1f}%")
print(f"  Diferença:        {media_pos_share - media_pre_share:+.1f} p.p.")


# ════════════════════════════════════════════════════════════════════════════
# TESTE 3 – DICKEY-FULLER AUMENTADO (estacionariedade)
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TESTE 3 – DICKEY-FULLER AUMENTADO (ADF)")
print("=" * 60)
print("  H0: a série possui raiz unitária (não-estacionária)")
print("  H1: a série é estacionária")
print()

for serie, nome in [(df["rec_nom"], "Receita nominal"),
                    (df["rec_real"], "Receita real"),
                    (df["log_rec"],  "Log(receita nominal)")]:
    result = adfuller(serie, autolag="AIC")
    adf_stat, p_val = result[0], result[1]
    conclusao = "Estacionária (rejeita H0)" if p_val < 0.05 else "Não-estacionária (não rejeita H0)"
    print(f"  {nome}:")
    print(f"    ADF Estatística: {adf_stat:.4f}")
    print(f"    p-valor:         {p_val:.4f}  →  {conclusao}")
    print()

# Primeira diferença
df["d_rec_nom"] = df["rec_nom"].diff()
result_d1 = adfuller(df["d_rec_nom"].dropna(), autolag="AIC")
print(f"  Δ Receita nominal (1ª diferença):")
print(f"    ADF Estatística: {result_d1[0]:.4f}")
print(f"    p-valor:         {result_d1[1]:.4f}  →  {'Estacionária' if result_d1[1]<0.05 else 'Não-estacionária'}")


# ════════════════════════════════════════════════════════════════════════════
# TESTE 4 – TESTE DE CHOW (quebra estrutural em 2015)
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TESTE 4 – TESTE DE CHOW (quebra estrutural em 2015)")
print("=" * 60)
print("  H0: não há quebra estrutural (coeficientes iguais nos dois períodos)")
print("  H1: há quebra estrutural em 2015")
print()

# Regressão irrestrita (dados completos)
X_full = add_constant(df["t"])
modelo_full = OLS(df["rec_nom"], X_full).fit()
RSS_full = modelo_full.ssr   # Soma dos quadrados dos resíduos – geral

# Regressão período pré
X_pre = add_constant(pre["t"])
modelo_pre = OLS(pre["rec_nom"], X_pre).fit()
RSS_pre = modelo_pre.ssr

# Regressão período pós
X_pos = add_constant(pos["t"])
modelo_pos = OLS(pos["rec_nom"], X_pos).fit()
RSS_pos = modelo_pos.ssr

# Estatística F de Chow
k  = 2                      # parâmetros por subgrupo (intercepto + tendência)
n1 = len(pre)               # obs pré
n2 = len(pos)               # obs pós
N  = n1 + n2

RSS_restrito   = RSS_full
RSS_irrestrito = RSS_pre + RSS_pos

F_chow = ((RSS_restrito - RSS_irrestrito) / k) / (RSS_irrestrito / (N - 2*k))
p_chow = 1 - stats.f.cdf(F_chow, k, N - 2*k)

print(f"  RSS geral (restrito):       {RSS_restrito:,.1f}")
print(f"  RSS pré + RSS pós (irrest): {RSS_irrestrito:,.1f}")
print(f"  F de Chow:  {F_chow:.4f}")
print(f"  p-valor:    {p_chow:.4f}")
if p_chow < 0.05:
    print("  → Rejeita H0: HÁ quebra estrutural em 2015 (p < 0,05)")
elif p_chow < 0.10:
    print("  → Rejeita H0 a 10%: indício de quebra estrutural (p < 0,10)")
else:
    print("  → Não rejeita H0: evidência insuficiente de quebra estrutural")
print()
print("  NOTA: Com apenas 13 observações, o poder do teste é limitado.")
print("  O resultado deve ser interpretado como indicativo, não definitivo.")


# ════════════════════════════════════════════════════════════════════════════
# TESTE 5 – REGRESSÃO COM DUMMY DE INTERVENÇÃO
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TESTE 5 – REGRESSÃO COM DUMMY DE INTERVENÇÃO")
print("=" * 60)

# Modelo: rec = b0 + b1*t + b2*D + b3*(D*t) + ε
# Onde D = 1 se pós-acordo, t = tendência linear, D*t = mudança de inclinação
df["D_t"] = df["dummy"] * df["t"]   # interação: muda a inclinação
X_reg = add_constant(df[["t","dummy","D_t"]])
modelo_dummy = OLS(df["rec_nom"], X_reg).fit()

print(modelo_dummy.summary())

b0, b1, b2, b3 = modelo_dummy.params
print(f"\n  Interpretação:")
print(f"  b0 (intercepto base):       {b0:.1f}  → receita esperada em 2012 (t=0)")
print(f"  b1 (tendência pré):         {b1:.1f}  → crescimento anual (R$mi/ano) pré-acordo")
print(f"  b2 (salto nível em 2015):   {b2:.1f}  → mudança imediata de nível ao assinar o acordo")
print(f"  b3 (mudança de inclinação): {b3:.1f}  → aceleração adicional de crescimento pós-acordo")
print(f"\n  Tendência pré:  +R${b1:.1f}mi/ano")
print(f"  Tendência pós:  +R${b1+b3:.1f}mi/ano  (b1 + b3)")
print(f"  R² ajustado:   {modelo_dummy.rsquared_adj:.3f}")


# ════════════════════════════════════════════════════════════════════════════
# TESTE 6 – INTERVALO DE CONFIANÇA (projeção tendência pós-acordo)
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TESTE 6 – INTERVALO DE CONFIANÇA (projeção)")
print("=" * 60)

# Regressão linear simples nos dados pós-acordo para projeção
X_pos_t = add_constant(pos[["t"]])
modelo_proj = OLS(pos["rec_nom"], X_pos_t).fit()

# Projeção 2025-2027
anos_proj = [2025, 2026, 2027]
t_proj    = [13, 14, 15]   # continuação de t (2012=0, 2024=12, 2025=13...)
X_proj    = add_constant(pd.DataFrame({"t": t_proj}, columns=["t"]))
pred      = modelo_proj.get_prediction(X_proj)
pred_df   = pred.summary_frame(alpha=0.05).reset_index(drop=True)

print(f"  Modelo (pós-acordo, 2015-2024): rec = {modelo_proj.params['const']:.1f} + {modelo_proj.params['t']:.1f} * t")
print(f"  R²: {modelo_proj.rsquared:.3f}")
print()
print(f"  {'Ano':>6}  {'Projeção':>12}  {'IC 95% Inf':>12}  {'IC 95% Sup':>12}")
print(f"  {'-'*46}")
for i, ano in enumerate(anos_proj):
    p  = pred_df.iloc[i]["mean"]
    lo = pred_df.iloc[i]["obs_ci_lower"]
    hi = pred_df.iloc[i]["obs_ci_upper"]
    print(f"  {ano:>6}  {p:>12.1f}  {lo:>12.1f}  {hi:>12.1f}")
print("\n  (valores em R$ milhões, nominais)")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICOS – abre interativo no VS Code / terminal
# ════════════════════════════════════════════════════════════════════════════
print("\nGerando gráficos...")

fig = plt.figure(figsize=(16, 22))
gs  = gridspec.GridSpec(4, 2, figure=fig, hspace=0.50, wspace=0.35)

def marca_estimados(ax, df_plot, col_y, estimados):
    """Destaca pontos estimados com marcador diferente."""
    for _, row in df_plot.iterrows():
        if row["ano"] in estimados:
            ax.scatter(row["ano"], row[col_y], marker="^", s=80,
                       color="orange", zorder=5, label="_nolegend_")

# ── Graf 1: Série receita total (nominal + real) ─────────────────────────────
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(df["ano"], df["rec_nom"],  color=VERDE, lw=2.5, marker="o", ms=6, label="Nominal (R$mi)")
ax1.plot(df["ano"], df["rec_real"], color=VERDE, lw=1.5, ls="--", marker="s", ms=5, label="Real – base 2015 (R$mi)")
marca_estimados(ax1, df, "rec_nom", estimados)

# Faixa pré/pós
ax1.axvspan(2011.5, 2014.5, alpha=0.08, color="red",   label="Pré-acordo (2012-2014)")
ax1.axvspan(2014.5, 2024.5, alpha=0.08, color="green", label="Pós-acordo Allianz (2015-2024)")
ax1.axvline(x=2014.5, color="gray", ls="--", lw=1.5)

# Anotações CAGR
ax1.annotate(f"CAGR nominal\npré: {cagr_pre_nom*100:+.0f}%/ano",
             xy=(2013, 225), fontsize=9, color="darkred",
             bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
ax1.annotate(f"CAGR nominal\npós: {cagr_pos_nom*100:+.0f}%/ano",
             xy=(2019.5, 820), fontsize=9, color="darkgreen",
             bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))

# Linha de tendência pré e pós (regressão)
t_pre_line = np.linspace(pre["t"].min(), pre["t"].max(), 50)
t_pos_line = np.linspace(pos["t"].min(), pos["t"].max(), 50)
y_pre_line = modelo_pre.params["const"] + modelo_pre.params["t"] * t_pre_line
y_pos_line = modelo_pos.params["const"] + modelo_pos.params["t"] * t_pos_line
anos_pre_line = [2012 + tt for tt in t_pre_line]
anos_pos_line = [2012 + tt for tt in t_pos_line]
ax1.plot(anos_pre_line, y_pre_line, color="red",   ls=":", lw=1.8, label="Tendência pré (OLS)")
ax1.plot(anos_pos_line, y_pos_line, color="green", ls=":", lw=1.8, label="Tendência pós (OLS)")

# Triângulo laranja = estimado
tri = plt.scatter([], [], marker="^", color="orange", s=80, label="Valor estimado/interpolado")
ax1.set_title("Palmeiras – Receita Total (2012–2024)\nSérie temporal com quebra estrutural em 2015 (Allianz Parque)",
              fontweight="bold")
ax1.set_ylabel("R$ milhões"); ax1.set_xlabel("Ano")
ax1.set_xticks(anos); ax1.set_xticklabels(anos, rotation=45)
ax1.legend(loc="upper left", fontsize=9)

# ── Graf 2: Receita comercial e participação % ───────────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
cores_bar = ["orange" if a in estimados else (VERDE if a >= 2015 else "#AAAAAA") for a in df["ano"]]
ax2.bar(df["ano"], df["rec_com"], color=cores_bar, alpha=0.85, zorder=3)
ax2.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax2_r = ax2.twinx()
ax2_r.plot(df["ano"], df["share_com"], color=AZUL, lw=2, marker="D", ms=5, label="Share %")
ax2_r.set_ylabel("Participação % na receita total", color=AZUL)
ax2_r.tick_params(axis="y", colors=AZUL)
ax2.set_title("Receita Comercial Palmeiras\ne participação % na receita total")
ax2.set_ylabel("R$ milhões"); ax2.set_xlabel("Ano")
ax2.set_xticks(anos); ax2.set_xticklabels(anos, rotation=45)
p1 = mpatches.Patch(color=VERDE, alpha=0.85, label="Pós-acordo")
p2 = mpatches.Patch(color="#AAAAAA", alpha=0.85, label="Pré-acordo")
p3 = mpatches.Patch(color="orange", alpha=0.85, label="Estimado")
ax2.legend(handles=[p1,p2,p3], fontsize=8, loc="upper left")

# ── Graf 3: Teste ADF – 1ª diferença ─────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
diff_rec = df["rec_nom"].diff().dropna()
diff_anos = anos[1:]
ax3.bar(diff_anos, diff_rec,
        color=[VERDE if v >= 0 else LARANJA for v in diff_rec], alpha=0.8)
ax3.axhline(0, color="black", lw=0.8)
ax3.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax3.set_title(f"1ª Diferença da Receita (ΔRec)\n"
              f"ADF p-valor: {result_d1[1]:.3f} "
              f"({'estacionária' if result_d1[1]<0.05 else 'não-estacionária'})")
ax3.set_ylabel("Δ R$ milhões"); ax3.set_xlabel("Ano")
ax3.set_xticks(diff_anos); ax3.set_xticklabels(diff_anos, rotation=45)

# ── Graf 4: Regressão dummy – valores ajustados vs reais ─────────────────────
ax4 = fig.add_subplot(gs[2, 0])
y_hat = modelo_dummy.fittedvalues
resid = modelo_dummy.resid
ax4.scatter(df["ano"], df["rec_nom"], color=VERDE, s=50, zorder=5, label="Observado")
ax4.plot(df["ano"], y_hat, color=AZUL, lw=2, marker=None, label=f"Ajustado (R²={modelo_dummy.rsquared:.2f})")

# Linha vertical na intervenção
ax4.axvline(x=2014.5, color="gray", ls="--", lw=1.2)
ax4.set_title(f"Regressão com Dummy de Intervenção\n"
              f"Salto de nível: +R${b2:.0f}mi | Aceleração: +R${b3:.0f}mi/ano | R²={modelo_dummy.rsquared:.3f}")
ax4.set_ylabel("R$ milhões"); ax4.set_xlabel("Ano")
ax4.set_xticks(anos); ax4.set_xticklabels(anos, rotation=45)
ax4.legend()

# ── Graf 5: Resíduos da regressão com dummy ───────────────────────────────────
ax5 = fig.add_subplot(gs[2, 1])
ax5.bar(df["ano"], resid,
        color=[VERDE if v >= 0 else LARANJA for v in resid], alpha=0.8)
ax5.axhline(0, color="black", lw=1)
ax5.axhline(resid.std(),  color="gray", ls="--", lw=1, label=f"+1σ ({resid.std():.0f})")
ax5.axhline(-resid.std(), color="gray", ls="--", lw=1, label=f"-1σ ({-resid.std():.0f})")
ax5.set_title("Resíduos da Regressão\n(verde = acima do ajustado | laranja = abaixo)")
ax5.set_ylabel("Resíduo (R$ mi)"); ax5.set_xlabel("Ano")
ax5.set_xticks(anos); ax5.set_xticklabels(anos, rotation=45)
ax5.legend(fontsize=8)

# ── Graf 6: Projeção com intervalo de confiança 95% ──────────────────────────
ax6 = fig.add_subplot(gs[3, :])

# Dados históricos pós-acordo
ax6.plot(pos["ano"], pos["rec_nom"], color=VERDE, lw=2.5, marker="o", ms=6,
         label="Histórico pós-acordo (2015-2024)")
ax6.plot(pre["ano"], pre["rec_nom"], color=CINZA, lw=1.5, marker="s", ms=5,
         ls="--", label="Histórico pré-acordo (2012-2014)")

# Linha projetada
anos_hist_pos  = list(pos["ano"]) + anos_proj
t_hist_pos     = list(pos["t"])   + t_proj
y_fitted_pos   = [modelo_proj.params['const'] + modelo_proj.params['t']*t for t in t_hist_pos]

# IC 95% para toda a linha pós-acordo + projeção
X_full_pos = add_constant(pd.DataFrame({"t": t_hist_pos}, columns=["t"]))
pred_full  = modelo_proj.get_prediction(X_full_pos).summary_frame(alpha=0.05)

ax6.plot(anos_hist_pos, y_fitted_pos, color=AZUL, lw=2, ls=":", label="Tendência linear (OLS pós-acordo)")
ax6.fill_between(anos_hist_pos,
                 pred_full["obs_ci_lower"],
                 pred_full["obs_ci_upper"],
                 alpha=0.15, color=AZUL, label="IC 95% (projeção)")
ax6.fill_between(anos_hist_pos,
                 pred_full["mean_ci_lower"],
                 pred_full["mean_ci_upper"],
                 alpha=0.25, color=AZUL, label="IC 95% (média)")

# Pontos projetados
for i, ano in enumerate(anos_proj):
    p  = pred_df.iloc[i]["mean"]
    lo = pred_df.iloc[i]["obs_ci_lower"]
    hi = pred_df.iloc[i]["obs_ci_upper"]
    ax6.scatter(ano, p, color=AZUL, s=60, zorder=5)
    ax6.annotate(f"R${p:.0f}mi\n[{lo:.0f}–{hi:.0f}]",
                 xy=(ano, p), xytext=(ano+0.05, p+60),
                 fontsize=8, color=AZUL,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))

ax6.axvline(x=2024.5, color="gray", ls="--", lw=1.5, label="Início projeção (2025)")
ax6.axvline(x=2014.5, color="gray", ls=":",  lw=1.2)
ax6.set_title("Projeção de Receita (2025–2027) com Intervalo de Confiança 95%\n"
              "Baseado na tendência OLS do período pós-acordo (2015–2024)",
              fontweight="bold")
ax6.set_ylabel("R$ milhões"); ax6.set_xlabel("Ano")
ax6.set_xticks(list(range(2012, 2028)))
ax6.set_xticklabels(list(range(2012, 2028)), rotation=45)
ax6.legend(loc="upper left", fontsize=9)

fig.suptitle("Etapa 1 – Análise de Séries Temporais: Palmeiras / Allianz Parque\n"
             "Acordo Nubank (2026) NÃO é escopo desta análise.",
             fontsize=13, fontweight="bold", y=1.0)

fig.text(0.5, 0.003,
    "Fontes: ESPN Brasil, CNN Brasil, Gazeta Esportiva, EY Football Finance 2022 | "
    "Valores estimados em triângulos laranja | IGP-M: FGV/BCB",
    ha="center", fontsize=8, color="gray", style="italic")

plt.tight_layout()

# Salvar PNG (para referência)
plt.savefig("series_temporais_completo.png", bbox_inches="tight", dpi=150)
print("\nGráfico salvo como: series_temporais_completo.png")
print("Abrindo visualização interativa...")

# Abre gráfico interativo (VS Code / terminal)
plt.show()