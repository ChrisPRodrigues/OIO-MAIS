import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "GLA"
    / "ORIGA"
    / "ORIGA_train.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "origa_metadata.csv"
)

# Classificação original do ORIGA.

CLASSIFICACOES = {
    0: "sem_glaucoma",
    1: "glaucoma",
}


# Faz a leitura do arquivo CSV de entrada.

df = pd.read_csv(ARQUIVO_ENTRADA)

# Criação do DataFrame de metadados.

metadata = pd.DataFrame()

metadata["id_imagem"] = range(1, len(df) + 1)

metadata["dataset"] = "ORIGA"

metadata["arquivo"] = df["ImageName"].apply(
    lambda caminho: Path(caminho).name
)

metadata["doenca"] = "glaucoma"

metadata["codigo_diagnostico"] = df["glaucoma"]

metadata["diagnostico"] = df["glaucoma"].map(CLASSIFICACOES)

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