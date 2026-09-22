import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parents[3]

PASTA_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "GLA"
    / "ACRIMA"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "METADADOS"
    / "Treino"
    / "acrima_metadata.csv"
)

# Classificação original do ACRIMA.

CLASSIFICACOES = {
    0: "sem_glaucoma",
    1: "glaucoma",
}


# Faz a leitura dos arquivos de imagem.

arquivos = sorted(
    [
        arquivo
        for arquivo in PASTA_ENTRADA.rglob("*.jpg")
        if arquivo.is_file()
    ]
)

# Criação do DataFrame de metadados.

metadata = pd.DataFrame()

metadata["id_imagem"] = range(1, len(arquivos) + 1)

metadata["dataset"] = "ACRIMA"

metadata["arquivo"] = [arquivo.name for arquivo in arquivos]

metadata["doenca"] = "glaucoma"

metadata["codigo_diagnostico"] = [
    1 if "_g_" in arquivo.name else 0
    for arquivo in arquivos
]

metadata["diagnostico"] = metadata["codigo_diagnostico"].map(
    CLASSIFICACOES
)

metadata["conjunto"] = "completo"

# Validação dos metadados.

if len(metadata) != 705:
    raise ValueError(
        f"Quantidade inesperada de imagens. "
        f"Esperado: 705 | Encontrado: {len(metadata)}"
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