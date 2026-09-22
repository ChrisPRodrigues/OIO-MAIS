import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "IDRiD"
    / "B. Disease Grading"
    / "2. Groundtruths"
    / "a. IDRiD_Disease Grading_Training Labels.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "idrid_metadata.csv"
)

# Classificação original do IDRiD.

CLASSIFICACOES = {
    0: "sem_retinopatia_diabetica",
    1: "retinopatia_diabetica_leve",
    2: "retinopatia_diabetica_moderada",
    3: "retinopatia_diabetica_grave",
    4: "retinopatia_diabetica_proliferativa",
}

# Faz a leitura do arquivo CSV de entrada.

df = pd.read_csv(ARQUIVO_ENTRADA)

# Remove colunas completamente vazias.

df = df.dropna(axis=1, how="all")

# Remove espaços extras dos nomes das colunas.

df.columns = df.columns.str.strip()

# Criação do DataFrame de metadados.

metadata = pd.DataFrame()

metadata["id_imagem"] = range(1, len(df) + 1)

metadata["dataset"] = "IDRiD"

metadata["arquivo"] = df["Image name"].astype(str) + ".jpg"

metadata["doenca"] = "retinopatia_diabetica"

metadata["codigo_diagnostico"] = df["Retinopathy grade"]

metadata["diagnostico"] = (
    df["Retinopathy grade"].map(CLASSIFICACOES)
)

metadata["risco_edema_macular"] = df["Risk of macular edema"]

metadata["conjunto"] = "train"

# Validação dos metadados.

if metadata["codigo_diagnostico"].isna().any():
    raise ValueError("Existem diagnósticos ausentes.")

if metadata["risco_edema_macular"].isna().any():
    raise ValueError("Existem valores de risco de edema macular ausentes.")

if metadata["arquivo"].duplicated().any():
    raise ValueError("Existem imagens duplicadas.")

if not metadata["codigo_diagnostico"].isin(CLASSIFICACOES.keys()).all():
    raise ValueError("Existe um código de diagnóstico desconhecido.")

# Validação da quantidade de imagens.

PASTA_IMAGENS = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "IDRiD"
    / "B. Disease Grading"
    / "1. Original Images"
    / "a. Training Set"
)

imagens = list(PASTA_IMAGENS.glob("*.jpg"))

if len(imagens) != len(metadata):
    raise ValueError(
        f"Quantidade de imagens ({len(imagens)}) "
        f"é diferente da quantidade de registros ({len(metadata)})."
    )

# Salvando os metadados em um arquivo CSV.

ARQUIVO_SAIDA.parent.mkdir(
    parents=True,
    exist_ok=True
)

metadata.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig"
)

print(f"Metadata criada com sucesso: {ARQUIVO_SAIDA}")
print(f"Total de imagens: {len(metadata)}")

print("\nDistribuição:")
print(metadata["diagnostico"].value_counts())

print("\nDistribuição do risco de edema macular:")
print(metadata["risco_edema_macular"].value_counts())