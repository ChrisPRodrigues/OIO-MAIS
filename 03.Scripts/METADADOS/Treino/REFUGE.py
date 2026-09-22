import pandas as pd
from pathlib import Path

# Configurações de diretórios.

BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_DATASET = (
    BASE_DIR
    / "01.Originais"
    / "GLA"
    / "REFUGE"
    / "Training400"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "refuge_metadata.csv"
)


# Criação dos caminhos das imagens.

PASTA_GLAUCOMA = PASTA_DATASET / "Glaucoma"
PASTA_NAO_GLAUCOMA = PASTA_DATASET / "Non-Glaucoma"


# Criação da lista de imagens.

registros = []

for arquivo in sorted(PASTA_GLAUCOMA.iterdir()):
    if arquivo.is_file():
        registros.append({
            "arquivo": arquivo.name,
            "diagnostico": "glaucoma",
            "codigo_diagnostico": 1
        })


for arquivo in sorted(PASTA_NAO_GLAUCOMA.iterdir()):
    if arquivo.is_file():
        registros.append({
            "arquivo": arquivo.name,
            "diagnostico": "sem_glaucoma",
            "codigo_diagnostico": 0
        })


# Criação do DataFrame de metadados.

metadata = pd.DataFrame(registros)

metadata.insert(
    0,
    "id_imagem",
    range(1, len(metadata) + 1)
)

metadata.insert(
    1,
    "dataset",
    "REFUGE"
)

metadata.insert(
    3,
    "doenca",
    "glaucoma"
)

metadata["conjunto"] = "train"


# Validação dos metadados.

if metadata["arquivo"].duplicated().any():
    raise ValueError(
        "Existem imagens duplicadas."
    )

if not metadata["codigo_diagnostico"].isin([0, 1]).all():
    raise ValueError(
        "Existe um código de diagnóstico desconhecido."
    )

if len(metadata) != 400:
    raise ValueError(
        f"Quantidade inesperada de imagens: {len(metadata)}"
    )


# Salvando o catálogo.

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
print(
    metadata["diagnostico"]
    .value_counts()
)