import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "AMD (Degeneração Macular Relacionada à Idade)"
    / "RDIC"
    / "train"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "rdic_metadata.csv"
)

# Classificação do RDIC.

CLASSIFICACOES = {
    0: "sem_dmri",
    1: "dmri",
}


# Faz a leitura dos arquivos de imagem.

EXTENSOES = [".jpg", ".jpeg", ".png"]

arquivos_dmri = sorted(
    [
        arquivo
        for arquivo in (PASTA_ENTRADA / "AMD").iterdir()
        if arquivo.is_file()
        and arquivo.suffix.lower() in EXTENSOES
    ]
)

arquivos_sem_dmri = sorted(
    [
        arquivo
        for arquivo in (PASTA_ENTRADA / "Normal").iterdir()
        if arquivo.is_file()
        and arquivo.suffix.lower() in EXTENSOES
    ]
)

arquivos = arquivos_sem_dmri + arquivos_dmri

# Criação do DataFrame de metadados.

metadata = pd.DataFrame()

metadata["id_imagem"] = range(1, len(arquivos) + 1)

metadata["dataset"] = "RDIC"

metadata["arquivo"] = [arquivo.name for arquivo in arquivos]

metadata["doenca"] = "degeneracao_macular_relacionada_a_idade"

metadata["codigo_diagnostico"] = (
    [0] * len(arquivos_sem_dmri)
    + [1] * len(arquivos_dmri)
)

metadata["diagnostico"] = metadata["codigo_diagnostico"].map(
    CLASSIFICACOES
)

metadata["conjunto"] = "train"

# Validação dos metadados.

if len(metadata) != 888:
    raise ValueError(
        f"Quantidade inesperada de imagens. "
        f"Esperado: 888 | Encontrado: {len(metadata)}"
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