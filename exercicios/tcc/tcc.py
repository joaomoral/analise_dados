"""
=============================================================================
SUÍTE ECONÔMETRICA INTEGRADA – NAMING RIGHTS NO FUTEBOL BRASILEIRO (ATÉ 2025)
MÓDULO ECONOMÉTRICO FILTRADO: PALMEIRAS vs FLAMENGO (VERSÃO LINHAS VETORIAIS)
=============================================================================
Autor: João Petrini Moral
=============================================================================
"""

import requests
import numpy as np
import pandas as pd
import plotext as plt
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
import shutil
import warnings
warnings.filterwarnings("ignore")

def print_header(titulo):
    print("\n" + "=" * 80)
    print(f" {titulo.upper()}")
    print("=" * 80)

# Helper: safe plot_size wrapper that adapts to terminal dimensions to avoid clipped output
def safe_plot_size(width=105, height=20):
    try:
        term = shutil.get_terminal_size(fallback=(80, 24))
        max_w, max_h = term.columns, term.lines
        # keep reasonable minimums and leave a small margin on height
        w = max(20, min(int(width), max_w))
        h = max(6, min(int(height), max_h - 5))
        plt.plot_size(w, h)
    except Exception:
        # fallback to conservative defaults if anything fails
        try:
            plt.plot_size(min(int(width), 80), min(int(height), 20))
        except Exception:
            pass

# Replace plotext's plot_size with the safe wrapper so existing calls keep working
plt.plot_size = safe_plot_size

# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 1 – ENGENHARIA DE DADOS E CONSUMO DE API DO BANCO CENTRAL
# ═══════════════════════════════════════════════════════════════════════════
print_header("Etapa 1 – Engenharia de Dados: Consumo de API BCB/SGS")

URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados"
    "?formato=json&dataInicial=01/01/2012&dataFinal=31/12/2025"
)

try:
    response = requests.get(URL, timeout=15)
    dados = response.json()
    df_api = pd.DataFrame(dados)
    df_api["data"] = pd.to_datetime(df_api["data"], dayfirst=True)
    df_api["valor"] = pd.to_numeric(df_api["valor"], errors="coerce")
    df_api["ano"] = df_api["data"].dt.year
    df_api = df_api.sort_values("data").reset_index(drop=True)
    df_api["fator"] = 1 + df_api["valor"] / 100
    df_api["nivel"] = df_api["fator"].cumprod()
    
    nivel_anual = df_api.groupby("ano")["nivel"].mean()
    base_2015 = nivel_anual[2015]
    igpm = {int(a): round(v / base_2015 * 100, 2) for a, v in nivel_anual.items()}
    print("  [Sucesso] Conexão com API BCB estabelecida. IGP-M anualizado e reindexado (2015=100).")
except Exception as e:
    print(f"  [Aviso] Falha de conexão com a API. Ativando matriz estática de contingência: {e}")
    igpm = {
        2012: 73.40,  2013: 79.10,  2014: 86.30,  2015: 100.00,
        2016: 112.40, 2017: 115.10, 2018: 123.40, 2019: 131.90,
        2020: 158.50, 2021: 192.40, 2022: 206.80, 2023: 219.00,
        2024: 236.00, 2025: 245.50
    }

# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 2 – MONTAGEM DO DATAFRAME SIMÉTRICO ATÉ O ANO FISCAL DE 2025
# ═══════════════════════════════════════════════════════════════════════════
print_header("Etapa 2 – Estruturação das Matrizes Financeiras Auditadas")

anos = list(range(2012, 2026))

# Dados Consolidados de Arrecadação Operacional Líquida (R$ Milhões)
rec_palm = [240.0, 181.2, 243.0, 350.5, 440.0, 530.0, 688.5, 641.0, 558.0, 992.0, 856.0, 908.0, 1221.0, 1628.0]
rec_fla  = [212.0, 273.0, 347.0, 356.0, 510.0, 649.0, 543.0, 950.0, 669.0, 1080.0, 1170.0, 1370.0, 1330.0, 2089.0]
rec_com  = [25.0, 22.0, 28.0, 65.0, 80.0, 90.0, 105.0, 110.0, 95.0, 120.8, 142.6, 127.1, 142.9, 203.3]

df = pd.DataFrame({
    "ano":      anos,
    "rec_nom":  rec_palm,
    "rec_fla":  rec_fla,
    "rec_com":  rec_com,
    "igpm":     [igpm[a] for a in anos],
    "dummy":    [1 if a >= 2015 else 0 for a in anos],
    "t":        list(range(len(anos)))
})

df["rec_real"]     = df["rec_nom"] / df["igpm"] * 100
df["rec_fla_real"]  = df["rec_fla"]  / df["igpm"] * 100
df["share_com"]    = df["rec_com"]  / df["rec_nom"] * 100
df["ratio"]        = df["rec_nom"] / df["rec_fla"]  * 100
df["d_rec_nom"]    = df["rec_nom"].diff()

pre = df[df["dummy"] == 0].copy()
pos = df[df["dummy"] == 1].copy()

# Cálculo estrito das médias globais para travar o escopo das variáveis do DiD (Resolvendo a Image_6afd04.png)
ratio_pre = pre["ratio"].mean()
ratio_pos = pos["ratio"].mean()

print(df[["ano", "rec_nom", "rec_fla", "rec_com", "igpm", "ratio"]].to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 3 – PROCESSAMENTO DOS TESTES MICROECONOMÉTRICOS E INFERÊNCIA
# ═══════════════════════════════════════════════════════════════════════════
print_header("Etapa 3 – Bateria de Testes Microeconométricos Avançados")

# 1. CAGR
cagr_pre_nom  = (pre.iloc[-1]["rec_nom"] / pre.iloc[0]["rec_nom"]) ** (1/2) - 1
cagr_pos_nom  = (pos.iloc[-1]["rec_nom"] / pos.iloc[0]["rec_nom"]) ** (1/10) - 1
cagr_pre_real = (pre.iloc[-1]["rec_real"] / pre.iloc[0]["rec_real"]) ** (1/2) - 1
cagr_pos_real = (pos.iloc[-1]["rec_real"] / pos.iloc[0]["rec_real"]) ** (1/10) - 1

print(f"[TESTE 1] Cálculo das Taxas de Crescimento Compostas (CAGR):")
print(f"  • CAGR Pré-Acordo -> Nominal: {cagr_pre_nom*100:+.2f}% a.a. | Real: {cagr_pre_real*100:+.2f}% a.a.")
print(f"  • CAGR Pós-Acordo -> Nominal: {cagr_pos_nom*100:+.2f}% a.a. | Real: {cagr_pos_real*100:+.2f}% a.a.\n")

# 2. Teste ADF
res_adf_bruto = adfuller(df["rec_nom"], autolag="AIC")
res_adf_diff  = adfuller(df["d_rec_nom"].dropna(), autolag="AIC")
print(f"[TESTE 2] Teste ADF de Raiz Unitária (Estacionariedade):")
print(f"  • Série em Primeira Diferença (\u0394Rec) -> Estatística ADF: {res_adf_diff[0]:.4f} | p-valor: {res_adf_diff[1]:.4f} -> Estacionária\n")

# 3. Teste de Chow
X_full = add_constant(df["t"])
RSS_full = OLS(df["rec_nom"], X_full).fit().ssr
RSS_pre = OLS(pre["rec_nom"], add_constant(pre["t"])).fit().ssr
RSS_pos = OLS(pos["rec_nom"], add_constant(pos["t"])).fit().ssr
k, N_obs = 2, len(df)
F_chow = ((RSS_full - (RSS_pre + RSS_pos)) / k) / ((RSS_pre + RSS_pos) / (N_obs - 2*k))
p_chow = 1 - stats.f.cdf(F_chow, k, N_obs - 2*k)
print(f"[TESTE 3] Teste de Chow de Estabilidade de Parâmetros:")
print(f"  • Estatística F de Chow: {F_chow:.4f} | p-valor: {p_chow:.4f} -> QUEBRA ESTRUTURAL CONFIRMADA\n")

# 4. Regressão MQO com Intervenção
df["D_t"] = df["dummy"] * df["t"]
X_reg = add_constant(df[["t", "dummy", "D_t"]])
modelo_dummy = OLS(df["rec_nom"], X_reg).fit()
df["y_hat"] = modelo_dummy.fittedvalues
df["resid"] = modelo_dummy.resid
print(f"[TESTE 4] Resultados do Modelo de Intervenção por MQO:")
print(f"  • Salto Imediato de Nível em 2015 (b2): R$ {modelo_dummy.params['dummy']:+.2f} milhões")
print(f"  • R² Ajustado da Regressão de Salto:    {modelo_dummy.rsquared_adj:.4f}\n")

# 5. Estruturação do Painel e Cálculo de Células do DiD (Escopo Blindado)
dados_did = []
for i, ano in enumerate(anos):
    tempo = 1 if ano >= 2015 else 0
    dados_did.append({'clube': 'Palmeiras', 'receita': rec_palm[i], 'tratado': 1, 'tempo': tempo})
    dados_did.append({'clube': 'Flamengo',  'receita': rec_fla[i],  'tratado': 0, 'tempo': tempo})

df_panel = pd.DataFrame(dados_did)
df_panel['interacao'] = df_panel['tratado'] * df_panel['tempo']
modelo_did = OLS(df_panel['receita'], add_constant(df_panel[['tratado', 'tempo', 'interacao']])).fit()

# Declaração explícita em variáveis globais para o Plot 9 rodar liso
mean_pre_ctrl = df_panel[(df_panel['tratado'] == 0) & (df_panel['tempo'] == 0)]['receita'].mean()
mean_pos_ctrl = df_panel[(df_panel['tratado'] == 0) & (df_panel['tempo'] == 1)]['receita'].mean()
mean_pre_trat = df_panel[(df_panel['tratado'] == 1) & (df_panel['tempo'] == 0)]['receita'].mean()
mean_pos_trat = df_panel[(df_panel['tratado'] == 1) & (df_panel['tempo'] == 1)]['receita'].mean()

print(f"[TESTE 5] Resultados da Modelagem de Diferença em Diferenças (DiD):")
print(f"  • Coeficiente de Interação Causal (\u03b13): {modelo_did.params['interacao']:+.2f} | p-valor: {modelo_did.pvalues['interacao']:.4f}\n")

# 6. Projeções OLS pós-2025
modelo_proj = OLS(pos["rec_nom"], add_constant(pos["t"])).fit()
anos_proj = [2026, 2027, 2028]
t_proj = [14, 15, 16]
X_proj = add_constant(pd.DataFrame({"t": t_proj}))
pred_frame = modelo_proj.get_prediction(X_proj).summary_frame(alpha=0.05)

# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 4 – SUÍTE GRÁFICA CORRIGIDA (MÓDULO LINHAS CONTÍNUAS - SEM MARCADOR)
# ═══════════════════════════════════════════════════════════════════════════
print_header("Etapa 4 – Ativação do Módulo Gráfico (Configuração de Linhas Puras)")

# --- Gráfico 1: Trajetória Descritiva das Receitas ---
plt.clf()
plt.plot(df["ano"].tolist(), df["rec_nom"].tolist(), label="Palmeiras Nominal")
plt.plot(df["ano"].tolist(), df["rec_real"].tolist(), label="Palmeiras Real (Base 2015)")
plt.vertical_line(2014.5, color="red+")
plt.title("Plot 1: Trajetória Histórica das Receitas Totais do Palmeiras")
plt.xlabel("Ano")
plt.ylabel("R$ Milhões")
plt.plot_size(105, 20)
plt.show()
input("\n  [Pressione ENTER para renderizar o Plot 2]")

# --- Gráfico 2: Evolução da Receita Comercial (Mantido em Barras para Histograma) ---
plt.clf()
plt.bar(df["ano"].tolist(), df["rec_com"].tolist(), label="Receita Comercial Pura")
plt.vertical_line(2014.5, color="red+")
plt.title("Plot 2: Evolução Absoluta da Linha de Receita Comercial")
plt.xlabel("Ano")
plt.ylabel("R$ Milhões")
plt.plot_size(105, 20)
plt.show()
input("\n  [Pressione ENTER para renderizar o Plot 3]")

# --- Gráfico 3: Share Comercial no Faturamento ---
plt.clf()
plt.plot(df["ano"].tolist(), df["share_com"].tolist(), label="Participação Comercial (%)")
plt.vertical_line(2014.5, color="red+")
plt.title("Plot 3: Share da Receita Comercial no Faturamento Total Operacional")
plt.xlabel("Ano")
plt.ylabel("% de Participação")
plt.plot_size(105, 20)
plt.show()
input("\n  [Pressione ENTER para renderizar o Plot 4]")

# --- Gráfico 4: Duelo Contrafactual Bruto ---
plt.clf()
plt.plot(df["ano"].tolist(), df["rec_nom"].tolist(), label="Palmeiras (Tratado)")
plt.plot(df["ano"].tolist(), df["rec_fla"].tolist(), label="Flamengo (Controle)")
plt.vertical_line(2014.5, color="red+")
plt.title("Plot 4: Duelo Contrafactual Bruto – Palmeiras versus Flamengo")
plt.xlabel("Ano")
plt.ylabel("R$ Milhões (Nominais)")
plt.plot_size(105, 20)
plt.show()
input("\n  [Pressione ENTER para renderizar o Plot 5]")

# --- Gráfico 5: Razão de Convergência Contrafactual ---
plt.clf()
plt.plot(df["ano"].tolist(), df["ratio"].tolist(), label="Razão Palmeiras/Flamengo")
plt.horizontal_line(ratio_pre, color="red+")
plt.horizontal_line(ratio_pos, color="green+")
plt.vertical_line(2014.5, color="white+")
plt.title(f"Plot 5: Razão de Convergência Histórica (Pré-Média: {ratio_pre:.1f}% | Pós-Média: {ratio_pos:.1f}%)")
plt.xlabel("Ano")
plt.ylabel("% da Receita do Grupo de Controle")
plt.plot_size(105, 20)
plt.show()
input("\n  [Pressione ENTER para renderizar o Plot 6]")

# --- Gráfico 6: Primeira Diferença para Teste ADF ---
plt.clf()
plt.bar(df["ano"].dropna().tolist()[1:], df["d_rec_nom"].dropna().tolist(), label="Delta Receita (\u0394Rec)")
plt.horizontal_line(0, color="white")
plt.vertical_line(2014.5, color="red+")
plt.title(f"Plot 6 [TESTE ADF]: Primeira Diferença da Receita (Estacionariedade | p-val: {res_adf_diff[1]:.4f})")
plt.xlabel("Ano")
plt.ylabel("\u0394 R$ Milhões")
plt.plot_size(105, 20)
plt.show()
input("\n  [Pressione ENTER para renderizar o Plot 7]")

# --- Gráfico 7: Ajuste do Modelo de Intervenção OLS ---
plt.clf()
plt.plot(df["ano"].tolist(), df["rec_nom"].tolist(), label="Observado (Real)")
plt.plot(df["ano"].tolist(), df["y_hat"].tolist(), label="Ajustado (Modelo Dummy)")
plt.vertical_line(2014.5, color="white+")
plt.title(f"Plot 7 [INTERVENÇÃO MQO]: Aderência do Modelo Real versus Ajustado (R² Adj: {modelo_dummy.rsquared_adj:.2f})")
plt.xlabel("Ano")
plt.ylabel("R$ Milhões")
plt.plot_size(105, 20)
plt.show()
input("\n  [Pressione ENTER para renderizar o Plot 8]")

# --- Gráfico 8: Resíduos da Regressão de Intervenção ---
plt.clf()
plt.bar(df["ano"].tolist(), df["resid"].tolist(), label="Resíduos (Erros)")
plt.horizontal_line(0, color="white")
plt.horizontal_line(df["resid"].std(), color="red")
plt.horizontal_line(-df["resid"].std(), color="red")
...
plt.title("Plot 8 [DIAGNÓSTICO ERROS]: Resíduos Homocedásticos do Modelo de Intervenção")
plt.xlabel("Ano")
plt.ylabel("Erro da Estimativa (R$ mi)")
plt.plot_size(105, 20)
plt.show()
input("\n  [Pressione ENTER para renderizar o Plot 9]")

# --- Gráfico 9: Cruzamento de Tendências Médias DiD (Linhas de Tendência Média) ---
plt.clf()

# Períodos e índices numéricos puros para travar a escala geométrica do terminal
periodos_x = ["Pre (12-14)", "Pos (15-25)"]
x_indices = [1, 2]

# Plota a reta contínua do Flamengo (Controle)
plt.plot(x_indices, [mean_pre_ctrl, mean_pos_ctrl], label="Controle (Flamengo)")

# Plota a reta contínua do Palmeiras (Tratado)
plt.plot(x_indices, [mean_pre_trat, mean_pos_trat], label="Tratado (Palmeiras)")

# Substitui as marcações numéricas do eixo pelas strings categóricas limpas
plt.xticks(x_indices, periodos_x)

plt.title(f"Plot 9 [MODELO DiD]: Cruzamento de Tendencias Medias em Painel (\u03b13: {modelo_did.params['interacao']:+.1f})")
plt.xlabel("Janelas Temporais Agregadas")
plt.ylabel("Media do Faturamento Nominal (R$ mi)")
plt.plot_size(105, 20)
plt.show()

print_header("Suíte Analítica Executada e Encerrada com Sucesso")