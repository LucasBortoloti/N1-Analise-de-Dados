import pandas as pd
import glob

pastas = ["../dados/2016/*.csv", "../dados/2017/*.csv", "../dados/2018/*.csv"]

colunas_corrigidas = {
    "ICAO Empresa AÃ©rea": "empresa_aerea",
    "NÃºmero Voo": "numero_voo",
    "CÃ³digo AutorizaÃ§Ã£o (DI)": "codigo_autorizacao",
    "CÃ³digo Tipo Linha": "codigo_tipo_linha",
    "ICAO AerÃ³dromo Origem": "aeroporto_origem",
    "ICAO AerÃ³dromo Destino": "aeroporto_destino",
    "Partida Prevista": "partida_prevista",
    "Partida Real": "partida_real",
    "Chegada Prevista": "chegada_prevista",
    "Chegada Real": "chegada_real",
    "SituaÃ§Ã£o Voo": "situacao_voo",
    "CÃ³digo Justificativa": "codigo_justificativa"
}

dfs = []

for pasta in pastas:
    arquivos = glob.glob(pasta)
    for arq in arquivos:
        print(f"Lendo: {arq}")
        df_temp = pd.read_csv(arq, sep=';', encoding='latin1', low_memory=False, skiprows=1)

        df_temp = df_temp.rename(columns=colunas_corrigidas)

        dfs.append(df_temp)

voos = pd.concat(dfs, ignore_index=True)

voos.to_csv("../outputs/voos_16a18.csv", index=False, sep=';')

print("✅ Arquivo consolidado salvo em: outputs/voos_16a18.csv")
print(f"Total de linhas: {len(voos)}")
print("Colunas disponíveis:", list(voos.columns))
