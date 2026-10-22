import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

IDRID_DIR = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "IDRiD"
)

IDRID_SEGMENTATION_DIR = (
    IDRID_DIR
    / "A. Segmentation"
)

PASTA_IMAGENS = (
    IDRID_SEGMENTATION_DIR
    / "1. Original Images"
    / "b. Testing Set"
)

PASTA_GROUNDTRUTHS = (
    IDRID_SEGMENTATION_DIR
    / "2. All Segmentation Groundtruths"
    / "b. Testing Set"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "METADADOS"
    / "Teste"
    / "idrid_segmentation_test_metadata.csv"
)

TIPOS_MASCARA = {
    "mascara_microaneurismas": (
        "1. Microaneurysms",
        "MA"
    ),

    "mascara_hemorragias": (
        "2. Haemorrhages",
        "HE"
    ),

    "mascara_exsudatos_duros": (
        "3. Hard Exudates",
        "EX"
    ),

    "mascara_exsudatos_moles": (
        "4. Soft Exudates",
        "SE"
    ),

    "mascara_disco_optico": (
        "5. Optic Disc",
        "OD"
    )
}

imagens = sorted(
    PASTA_IMAGENS.glob("*.jpg")
)

registros = []

for numero, imagem in enumerate(imagens, start=1):

    id_imagem = imagem.stem

    registro = {
        "numero_registro": numero,
        "id_imagem": id_imagem,
        "dataset": "IDRiD",
        "arquivo": imagem.name,
        "tarefa": "segmentation",
        "conjunto": "test"
    }

    for coluna, (pasta, sufixo) in TIPOS_MASCARA.items():

        caminho_mascara = (
            PASTA_GROUNDTRUTHS
            / pasta
            / f"{id_imagem}_{sufixo}.tif"
        )

        if caminho_mascara.exists():
            registro[coluna] = caminho_mascara.name
        else:
            registro[coluna] = pd.NA

    registros.append(registro)

metadata = pd.DataFrame(registros)

if metadata["id_imagem"].duplicated().any():
    raise ValueError("Existem IDs de imagem duplicados.")

if metadata["arquivo"].duplicated().any():
    raise ValueError("Existem nomes de arquivo duplicados.")

if len(metadata) != len(imagens):
    raise ValueError(
        "Quantidade de registros diferente da quantidade de imagens."
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

print("\nMáscaras disponíveis:")

for coluna in TIPOS_MASCARA:
    print(
        f"{coluna}:",
        metadata[coluna].notna().sum()
    )