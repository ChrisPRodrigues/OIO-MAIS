import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "EyePACS"
    / "trainLabels.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "eyepacs_metadata.csv"
)

# Classificação original do EyePACS.

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

metadata["numero_registro"] = range(1, len(df) + 1)

metadata["id_imagem"] = df["image"].astype(str)

metadata["dataset"] = "EyePACS"

metadata["arquivo"] = df["image"].astype(str) + ".jpeg"

metadata["doenca"] = "retinopatia_diabetica"

metadata["codigo_diagnostico"] = df["level"]

metadata["diagnostico"] = df["level"].map(CLASSIFICACOES)

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