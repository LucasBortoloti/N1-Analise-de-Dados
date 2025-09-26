import pandas as pd

voos = pd.read_csv("../outputs/voos_16a18.csv", sep=";", low_memory=False, encoding="latin1")

aeroportos = pd.read_csv("../dados/airport-codes.csv")
aeroportos_br = aeroportos[aeroportos["iso_country"] == "BR"]["ident"]

voos = voos[
    voos["aeroporto_origem"].isin(aeroportos_br) &
    voos["aeroporto_destino"].isin(aeroportos_br)
]

voos["partida_prevista"] = pd.to_datetime(voos["partida_prevista"], errors="coerce")
voos["partida_real"] = pd.to_datetime(voos["partida_real"], errors="coerce")

voos["ano"] = voos["partida_prevista"].dt.year
voos["mes"] = voos["partida_prevista"].dt.month
voos["dia_semana"] = voos["partida_prevista"].dt.day_name()

voos = voos[(voos["ano"] >= 2016) & (voos["ano"] <= 2018)]

def periodo(hora):
    if pd.isna(hora):
        return None
    if 5 <= hora < 12:
        return "Manhã"
    elif 12 <= hora < 18:
        return "Tarde"
    elif 18 <= hora < 24:
        return "Noite"
    else:
        return "Madrugada"

voos["hora_prevista"] = voos["partida_prevista"].dt.hour
voos["periodo_dia"] = voos["hora_prevista"].map(periodo)

voos["atraso_min"] = (voos["partida_real"] - voos["partida_prevista"]).dt.total_seconds() / 60
voos["atraso"] = voos["atraso_min"] >= 15

voos.to_csv("../outputs/voos_tratados.csv", sep=";", index=False, encoding="utf-8-sig")

print("✅ Dataset tratado salvo em: outputs/voos_tratados.csv")
print("Colunas finais:", list(voos.columns))
print("Intervalo de anos no dataset:", voos["ano"].unique())
print("Total de voos após filtro (Brasil-Brasil):", len(voos))
