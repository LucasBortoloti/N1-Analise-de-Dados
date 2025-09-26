import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import locale

st.set_page_config(layout="wide", page_title="Dashboard de Atrasos de Voos no Brasil")

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    pass

sns.set_theme(style="whitegrid")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("../outputs/voos_tratados.csv", sep=";", encoding="utf-8-sig", low_memory=False)
    return df

with st.spinner("Carregando dados..."):
    voos = carregar_dados()

if voos.empty:
    st.error("Nenhum dado encontrado. Execute antes o tratamento para gerar `outputs/voos_tratados.csv`.")
    st.stop()

st.sidebar.header("Filtros")

anos_disponiveis = sorted(voos["ano"].unique())
anos_selecionados = st.sidebar.multiselect("Ano(s)", anos_disponiveis, default=anos_disponiveis)

empresas_disponiveis = sorted(voos["empresa_aerea"].dropna().unique())
empresas_selecionadas = st.sidebar.multiselect("Companhia(s)", empresas_disponiveis, default=[])

aeroportos_disponiveis = sorted(voos["aeroporto_origem"].dropna().unique())
aeroportos_selecionados = st.sidebar.multiselect("Aeroporto(s) de Origem", aeroportos_disponiveis, default=[])

df_filtrado = voos.copy()
if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["ano"].isin(anos_selecionados)]
if empresas_selecionadas:
    df_filtrado = df_filtrado[df_filtrado["empresa_aerea"].isin(empresas_selecionadas)]
if aeroportos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["aeroporto_origem"].isin(aeroportos_selecionados)]

df_atrasos = df_filtrado[df_filtrado["atraso"] == True]

st.title("✈️ Dashboard de Atrasos de Voos no Brasil (2016–2018)")

total_voos = len(df_filtrado)
total_atrasos = len(df_atrasos)
taxa_atraso = (total_atrasos / total_voos * 100) if total_voos > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total de Voos", f"{total_voos:,}".replace(",", "."))
col2.metric("Total de Atrasos", f"{total_atrasos:,}".replace(",", "."))
col3.metric("Taxa de Atrasos", f"{taxa_atraso:.1f}%")

st.header("Análises Detalhadas")

st.subheader("Aeroportos com mais atrasos")
fig1, ax1 = plt.subplots(figsize=(7, 5))
aeroportos_top = df_atrasos["aeroporto_origem"].value_counts().nlargest(10)
sns.barplot(x=aeroportos_top.values, y=aeroportos_top.index, palette="viridis", ax=ax1)
ax1.set_xlabel("Número de Atrasos")
ax1.set_ylabel("Aeroporto (Origem)")
st.pyplot(fig1)

st.subheader("Taxa média de atrasos por ano (%)")
fig2, ax2 = plt.subplots(figsize=(6, 4))
taxa_ano = df_filtrado.groupby("ano")["atraso"].mean() * 100
sns.barplot(x=taxa_ano.index, y=taxa_ano.values, palette="Blues", ax=ax2)
for i, v in enumerate(taxa_ano.values):
    ax2.text(i, v + 0.5, f"{v:.1f}%", ha="center")
ax2.set_ylabel("Taxa de atrasos (%)")
st.pyplot(fig2)

st.subheader("Taxa de atrasos por dia da semana (%)")
fig3, ax3 = plt.subplots(figsize=(8, 5))

traducao = {
    "Monday": "Segunda",
    "Tuesday": "Terça",
    "Wednesday": "Quarta",
    "Thursday": "Quinta",
    "Friday": "Sexta",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}
ordem_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

dias_semana = (
    df_filtrado.groupby("dia_semana")["atraso"].mean() * 100
).rename(index=traducao).reindex(ordem_dias)

sns.barplot(x=dias_semana.values, y=dias_semana.index, palette="magma", ax=ax3)
ax3.set_xlabel("Taxa de atrasos (%)")
ax3.set_ylabel("Dia da semana")
st.pyplot(fig3)

st.subheader("Taxa de atrasos por período do dia (%)")
fig4, ax4 = plt.subplots(figsize=(7, 5))
periodos = df_filtrado.groupby("periodo_dia")["atraso"].mean().reindex(["Madrugada", "Manhã", "Tarde", "Noite"]) * 100
sns.barplot(x=periodos.index, y=periodos.values, palette="coolwarm", ax=ax4)
for i, v in enumerate(periodos.values):
    ax4.text(i, v + 0.5, f"{v:.1f}%", ha="center")
ax4.set_ylabel("Taxa de atrasos (%)")
st.pyplot(fig4)

st.subheader("Companhias com maiores taxas de atraso (%)")
fig5, ax5 = plt.subplots(figsize=(8, 6))
companhias = df_filtrado.groupby("empresa_aerea")["atraso"].mean().nlargest(10) * 100
sns.barplot(x=companhias.values, y=companhias.index, palette="plasma", ax=ax5)
ax5.set_xlabel("Taxa de atrasos (%)")
ax5.set_ylabel("Companhia aérea")
st.pyplot(fig5)

st.success("✅ Dashboard carregada com sucesso!")
