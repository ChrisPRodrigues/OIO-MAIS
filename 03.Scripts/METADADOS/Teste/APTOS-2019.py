import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parents[3]

ARQUIVO_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "DR (RETINOPATIA DIABÉTICA)"
    / "APTOS-2019"
    / "test.csv"
)

PASTA_IMAGENS = (
    BASE_DIR
    / "01.Originais"
    / "DR (RETINOPATIA DIABÉTICA)"
    / "APTOS-2019"
    / "test_images"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "METADADOS"
    / "Teste"
    / "aptos_test_metadata.csv"
)

# Faz a leitura do CSV original.

df = pd.read_csv(ARQUIVO_ENTRADA)

# Criação do DataFrame de metadados.

metadata = pd.DataFrame()

metadata["id_imagem"] = range(1, len(df) + 1)

metadata["dataset"] = "APTOS_2019"

metadata["arquivo"] = df["id_code"] + ".png"

metadata["doenca"] = "retinopatia_diabetica"

metadata["codigo_diagnostico"] = pd.NA

metadata["diagnostico"] = "nao_disponivel"

metadata["conjunto"] = "test"

# Validação dos metadados.

arquivos_imagens = {
    arquivo.name
    for arquivo in PASTA_IMAGENS.glob("*.png")
}

arquivos_metadata = set(metadata["arquivo"])

if metadata["arquivo"].duplicated().any():
    raise ValueError("Existem nomes de imagens duplicados no metadata.")

if len(arquivos_metadata - arquivos_imagens) > 0:
    raise ValueError(
        f"Existem {len(arquivos_metadata - arquivos_imagens)} "
        f"registros sem imagem correspondente."
    )

if len(arquivos_imagens - arquivos_metadata) > 0:
    raise ValueError(
        f"Existem {len(arquivos_imagens - arquivos_metadata)} "
        f"imagens sem registro correspondente."
    )

# Salvando os metadados em um arquivo CSV.

metadata.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig"
)

print(f"Metadata criada com sucesso: {ARQUIVO_SAIDA}")
print(f"Total de registros: {len(metadata)}")
print(f"Total de imagens: {len(arquivos_imagens)}")

print("\nPrimeiras linhas:")
print(metadata.head())