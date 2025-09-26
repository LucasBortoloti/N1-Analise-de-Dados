import pandas as pd
import matplotlib.pyplot as plt

voos = pd.read_csv("../outputs/voos_tratados.csv", sep=";", low_memory=False, encoding="utf-8-sig")

aeroportos = pd.read_csv("../dados/airport-codes.csv")

aeroportos_br = aeroportos[aeroportos["iso_country"] == "BR"][["ident", "name", "municipality"]]

voos = voos.merge(aeroportos_br, left_on="aeroporto_origem", right_on="ident", how="left")
voos = voos.rename(columns={"name": "aeroporto_origem_nome", "municipality": "cidade_origem"})
voos = voos.drop(columns=["ident"])

voos = voos.merge(aeroportos_br, left_on="aeroporto_destino", right_on="ident", how="left")
voos = voos.rename(columns={"name": "aeroporto_destino_nome", "municipality": "cidade_destino"})
voos = voos.drop(columns=["ident"])

print("\n📊 === ANÁLISE DE ATRASOS EM VOOS (2016-2018) ===\n")

aeroporto_mais_atrasos = (
    voos.groupby(["aeroporto_origem", "aeroporto_origem_nome"])["atraso"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("✈️ Top 10 aeroportos com mais atrasos (2016-2018):")
for (codigo, nome), atrasos in aeroporto_mais_atrasos.items():
    print(f"   - {codigo} ({nome}): {atrasos} atrasos")

top5_aeroportos = (
    voos.groupby("aeroporto_origem")["atraso"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

aeroporto_ano = (
    voos[voos["aeroporto_origem"].isin(top5_aeroportos)]
    .groupby(["aeroporto_origem", "aeroporto_origem_nome", "ano"])["atraso"]
    .sum()
    .unstack(fill_value=0)
)

aeroporto_ano["total"] = aeroporto_ano.sum(axis=1)
aeroporto_ano = aeroporto_ano.sort_values("total", ascending=False).drop(columns="total")

print("\n📈 Evolução de atrasos (Top 5 aeroportos com mais atrasos):")
print(aeroporto_ano)

atrasos_por_ano = voos.groupby("ano")["atraso"].mean() * 100
print("\n📅 Taxa média de atrasos por ano:")
for ano, perc in atrasos_por_ano.items():
    print(f"   - {int(ano)}: {perc:.1f}% dos voos atrasaram")

plt.figure(figsize=(6, 4))
bars = plt.bar(atrasos_por_ano.index.astype(int), atrasos_por_ano.values, color="#1f77b4")

plt.title("Taxa média de atrasos por ano")
plt.xlabel("Ano")
plt.ylabel("Taxa de atrasos (%)")
plt.ylim(0, 20)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.3, f"{yval:.1f}%", ha="center", va="bottom")

plt.tight_layout()
plt.savefig("../outputs/atrasos_por_ano.png", dpi=120)
plt.close()

ordem_semana = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dias_semana = voos.groupby(["ano", "dia_semana"])["atraso"].mean() * 100
dias_semana = dias_semana.unstack().reindex(columns=ordem_semana)

traducao = {
    "Monday": "Segunda",
    "Tuesday": "Terça",
    "Wednesday": "Quarta",
    "Thursday": "Quinta",
    "Friday": "Sexta",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}
dias_semana = dias_semana.rename(columns=traducao)

print("\n📆 Taxa média de atrasos por dia da semana (em %):")
dias_semana_fmt = dias_semana.round(1).fillna("-")
print(dias_semana_fmt.to_string())

periodo_dia = voos.groupby(["ano", "periodo_dia"])["atraso"].mean() * 100

ordem_periodo = ["Madrugada", "Manhã", "Tarde", "Noite"]
periodo_dia_fmt = periodo_dia.unstack().reindex(columns=ordem_periodo).round(1).fillna("-")

print("\n🕑 Taxa média de atrasos por período do dia (em %):")
print(periodo_dia_fmt.to_string())

companhias = voos.groupby(["ano", "empresa_aerea"])["atraso"].mean() * 100

print("\n🏢 Companhias com maiores taxas de atraso (Top 5 por ano, em %):")
for ano, grupo in companhias.groupby("ano"):
    top5 = grupo.sort_values(ascending=False).head(5).round(1)
    print(f"\n   {int(ano)}:")
    print(top5.to_string())

print("\n✅ Análises concluídas. Gráfico salvo em outputs/atrasos_por_ano.png")
