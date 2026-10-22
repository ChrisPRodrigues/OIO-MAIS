from pathlib import Path
import pandas as pd


# -----------------------------
# Caminhos principais
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[3]

IDRID_DIR = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "IDRiD"
)

IDRID_LOCALIZATION_DIR = (
    IDRID_DIR
    / "C. Localization"
)

PASTA_IMAGENS = (
    IDRID_LOCALIZATION_DIR
    / "1. Original Images"
    / "b. Testing Set"
)

ARQUIVO_DISCO_OPTICO = (
    IDRID_LOCALIZATION_DIR
    / "2. Groundtruths"
    / "1. Optic Disc Center Location"
    / "b. IDRiD_OD_Center_Testing Set_Markups.csv"
)

ARQUIVO_FOVEA = (
    IDRID_LOCALIZATION_DIR
    / "2. Groundtruths"
    / "2. Fovea Center Location"
    / "IDRiD_Fovea_Center_Testing Set_Markups.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "METADADOS"
    / "Teste"
    / "idrid_localization_test_metadata.csv"
)


# -----------------------------
# Lê os ground truths
# -----------------------------

disco_optico = pd.read_csv(
    ARQUIVO_DISCO_OPTICO
)

fovea = pd.read_csv(
    ARQUIVO_FOVEA
)


# -----------------------------
# Limpa nomes das colunas
# -----------------------------

disco_optico.columns = (
    disco_optico.columns
    .str.strip()
)

fovea.columns = (
    fovea.columns
    .str.strip()
)


# -----------------------------
# Renomeia as colunas
# -----------------------------

disco_optico = disco_optico.rename(
    columns={
        "Image No": "id_imagem",
        "X- Coordinate": "disco_optico_x",
        "Y - Coordinate": "disco_optico_y"
    }
)

fovea = fovea.rename(
    columns={
        "Image No": "id_imagem",
        "X- Coordinate": "fovea_x",
        "Y - Coordinate": "fovea_y"
    }
)


# -----------------------------
# Mantém apenas as colunas usadas
# -----------------------------

disco_optico = disco_optico[
    [
        "id_imagem",
        "disco_optico_x",
        "disco_optico_y"
    ]
]

fovea = fovea[
    [
        "id_imagem",
        "fovea_x",
        "fovea_y"
    ]
]


# -----------------------------
# Remove linhas vazias
# -----------------------------

disco_optico = disco_optico.dropna(
    subset=["id_imagem"]
).copy()

fovea = fovea.dropna(
    subset=["id_imagem"]
).copy()


# -----------------------------
# Limpa espaços dos IDs
# -----------------------------

disco_optico["id_imagem"] = (
    disco_optico["id_imagem"]
    .astype(str)
    .str.strip()
)

fovea["id_imagem"] = (
    fovea["id_imagem"]
    .astype(str)
    .str.strip()
)


print(
    "Registros válidos do disco óptico:",
    len(disco_optico)
)

print(
    "Registros válidos da fóvea:",
    len(fovea)
)


# -----------------------------
# Junta disco óptico e fóvea
# -----------------------------

metadata = disco_optico.merge(
    fovea,
    on="id_imagem",
    how="outer",
    validate="one_to_one"
)


# -----------------------------
# Localiza as imagens reais
# -----------------------------

arquivos_imagens = {}

for caminho in PASTA_IMAGENS.iterdir():

    if caminho.is_file():

        arquivos_imagens[
            caminho.stem
        ] = caminho.name


metadata["arquivo"] = (
    metadata["id_imagem"]
    .map(arquivos_imagens)
)


# -----------------------------
# Adiciona informações gerais
# -----------------------------

metadata.insert(
    0,
    "numero_registro",
    range(
        1,
        len(metadata) + 1
    )
)

metadata.insert(
    2,
    "dataset",
    "IDRiD"
)

metadata.insert(
    4,
    "tarefa",
    "localization"
)

metadata.insert(
    5,
    "conjunto",
    "test"
)


# -----------------------------
# Converte coordenadas para inteiro
# -----------------------------

colunas_coordenadas = [
    "disco_optico_x",
    "disco_optico_y",
    "fovea_x",
    "fovea_y"
]

metadata[colunas_coordenadas] = (
    metadata[colunas_coordenadas]
    .astype(int)
)


# -----------------------------
# Organiza as colunas
# -----------------------------

metadata = metadata[
    [
        "numero_registro",
        "id_imagem",
        "dataset",
        "arquivo",
        "tarefa",
        "conjunto",
        "disco_optico_x",
        "disco_optico_y",
        "fovea_x",
        "fovea_y"
    ]
]


# -----------------------------
# Validações
# -----------------------------

print(
    "\nRegistros:",
    len(metadata)
)

print(
    "IDs duplicados:",
    metadata["id_imagem"]
    .duplicated()
    .sum()
)

print(
    "Imagens não encontradas:",
    metadata["arquivo"]
    .isna()
    .sum()
)

print(
    "\nValores ausentes:"
)

print(
    metadata
    .isna()
    .sum()
)


# -----------------------------
# Verifica duplicatas completas
# -----------------------------

print(
    "\nRegistros duplicados completos:",
    metadata
    .duplicated()
    .sum()
)


# -----------------------------
# Salva o catálogo
# -----------------------------

ARQUIVO_SAIDA.parent.mkdir(
    parents=True,
    exist_ok=True
)

metadata.to_csv(
    ARQUIVO_SAIDA,
    index=False
)


# -----------------------------
# Resultado
# -----------------------------

print(
    "\nCatálogo salvo em:"
)

print(
    ARQUIVO_SAIDA
)

print(
    "\nPrimeiros registros:"
)

print(
    metadata.head()
)