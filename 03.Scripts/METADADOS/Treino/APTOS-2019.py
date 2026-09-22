import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ARQUIVO_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "APTOS-2019"
    / "train.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "METADADOS"
    / "aptos_metadata.csv"
)

# Classificação original do APTOS.

CLASSIFICACOES = {
    0: "sem_retinopatia_diabetica",
    1: "retinopatia_diabetica_leve",
    2: "retinopatia_diabetica_moderada",
    3: "retinopatia_diabetica_grave",
    4: "retinopatia_diabetica_proliferativa",
}


# Faz a leitura do arquivo CSV de entrada.

df = pd.read_csv(ARQUIVO_ENTRADA)

# Criação do DataFrame de metadados.

metadata = pd.DataFrame()

metadata["id_imagem"] = range(1, len(df) + 1)

metadata["dataset"] = "APTOS_2019"

metadata["arquivo"] = df["id_code"].astype(str) + ".png"

metadata["doenca"] = "retinopatia_diabetica"

metadata["codigo_diagnostico"] = df["diagnosis"]

metadata["diagnostico"] = df["diagnosis"].map(CLASSIFICACOES)

metadata["conjunto"] = "train"

# Validação dos metadados.

if metadata["codigo_diagnostico"].isna().any():
    raise ValueError("Existem diagnósticos ausentes.")

if metadata["arquivo"].duplicated().any():
    raise ValueError("Existem imagens duplicadas.")

if not metadata["codigo_diagnostico"].isin(CLASSIFICACOES.keys()).all():
    raise ValueError("Existe um código de diagnóstico desconhecido.")

# Salvando os metadados em um arquivo CSV.

metadata.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig"
)

print(f"Metadata criada com sucesso: {ARQUIVO_SAIDA}")
print(f"Total de imagens: {len(metadata)}")

print("\nDistribuição:")
print(metadata["diagnostico"].value_counts())