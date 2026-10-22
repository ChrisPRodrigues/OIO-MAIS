import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

ARQUIVO_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "IDRiD"
    / "B. Disease Grading"
    / "2. Groundtruths"
    / "b. IDRiD_Disease Grading_Testing Labels.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "METADADOS"
    / "Teste"
    / "idrid_test_metadata.csv"
)

CLASSIFICACOES = {
    0: "sem_retinopatia_diabetica",
    1: "retinopatia_diabetica_leve",
    2: "retinopatia_diabetica_moderada",
    3: "retinopatia_diabetica_grave",
    4: "retinopatia_diabetica_proliferativa",
}

df = pd.read_csv(ARQUIVO_ENTRADA)

df = df.dropna(axis=1, how="all")
df.columns = df.columns.str.strip()

metadata = pd.DataFrame()

metadata["numero_registro"] = range(1, len(df) + 1)

metadata["id_imagem"] = df["Image name"].astype(str)

metadata["dataset"] = "IDRiD"

metadata["arquivo"] = df["Image name"].astype(str) + ".jpg"

metadata["doenca"] = "retinopatia_diabetica"

metadata["codigo_diagnostico"] = df["Retinopathy grade"]

metadata["diagnostico"] = (
    df["Retinopathy grade"].map(CLASSIFICACOES)
)

metadata["risco_edema_macular"] = df["Risk of macular edema"]

metadata["conjunto"] = "test"

if metadata["codigo_diagnostico"].isna().any():
    raise ValueError("Existem diagnósticos ausentes.")

if metadata["risco_edema_macular"].isna().any():
    raise ValueError("Existem valores de risco de edema macular ausentes.")

if metadata["arquivo"].duplicated().any():
    raise ValueError("Existem imagens duplicadas.")

if not metadata["codigo_diagnostico"].isin(CLASSIFICACOES.keys()).all():
    raise ValueError("Existe um código de diagnóstico desconhecido.")

PASTA_IMAGENS = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "IDRiD"
    / "B. Disease Grading"
    / "1. Original Images"
    / "b. Testing Set"
)

imagens = list(PASTA_IMAGENS.glob("*.jpg"))

if len(imagens) != len(metadata):
    raise ValueError(
        f"Quantidade de imagens ({len(imagens)}) "
        f"é diferente da quantidade de registros ({len(metadata)})."
    )

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