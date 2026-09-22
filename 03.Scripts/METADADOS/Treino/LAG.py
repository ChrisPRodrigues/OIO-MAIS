import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "GLA"
    / "LAG"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "lag_metadata.csv"
)

# Classificação do LAG.

CLASSIFICACOES = {
    0: "sem_glaucoma",
    1: "glaucoma",
}


# Faz a leitura dos arquivos de imagem.

arquivos_glaucoma = sorted(
    (PASTA_ENTRADA / "glaucoma").glob("*.jpg")
)

arquivos_normal = sorted(
    (PASTA_ENTRADA / "normal").glob("*.jpg")
)

arquivos = arquivos_normal + arquivos_glaucoma

# Criação do DataFrame de metadados.

metadata = pd.DataFrame()

metadata["id_imagem"] = range(1, len(arquivos) + 1)

metadata["dataset"] = "LAG"

metadata["arquivo"] = [arquivo.name for arquivo in arquivos]

metadata["doenca"] = "glaucoma"

metadata["codigo_diagnostico"] = (
    [0] * len(arquivos_normal)
    + [1] * len(arquivos_glaucoma)
)

metadata["diagnostico"] = metadata["codigo_diagnostico"].map(
    CLASSIFICACOES
)

metadata["conjunto"] = "completo"

# Validação dos metadados.

if len(metadata) != 4854:
    raise ValueError(
        f"Quantidade inesperada de imagens. "
        f"Esperado: 4854 | Encontrado: {len(metadata)}"
    )

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