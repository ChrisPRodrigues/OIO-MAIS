import pandas as pd
from pathlib import Path

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "Messidor-2"
    / "messidor_data.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "messidor2_metadata.csv"
)

PASTA_IMAGENS = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "Messidor-2"
    / "images"
)


# Classificação original do Messidor-2.

CLASSIFICACOES = {
    0: "sem_retinopatia_diabetica",
    1: "retinopatia_diabetica_leve",
    2: "retinopatia_diabetica_moderada",
    3: "retinopatia_diabetica_grave",
    4: "retinopatia_diabetica_proliferativa",
}


# Faz a leitura do arquivo CSV de entrada.

df = pd.read_csv(ARQUIVO_ENTRADA)


# Criação do DataFrame de metadados.

metadata = pd.DataFrame()

metadata["id_imagem"] = range(1, len(df) + 1)

metadata["dataset"] = "MESSIDOR-2"

metadata["arquivo"] = df["image_id"].astype(str)

metadata["doenca"] = "retinopatia_diabetica"

metadata["codigo_diagnostico"] = df["adjudicated_dr_grade"]

metadata["diagnostico"] = (
    df["adjudicated_dr_grade"].map(CLASSIFICACOES)
)

metadata["risco_edema_macular"] = df["adjudicated_dme"]

metadata["avaliavel"] = df["adjudicated_gradable"]

metadata["conjunto"] = "unico"


# Os registros não avaliáveis não possuem diagnóstico.

metadata.loc[
    metadata["avaliavel"] == 0,
    "diagnostico"
] = "nao_avaliavel"


# Validação dos metadados.

if metadata["arquivo"].isna().any():
    raise ValueError("Existem nomes de arquivos ausentes.")

if metadata["arquivo"].duplicated().any():
    raise ValueError("Existem imagens duplicadas.")

if not metadata.loc[
    metadata["avaliavel"] == 1,
    "codigo_diagnostico"
].isin(CLASSIFICACOES.keys()).all():
    raise ValueError(
        "Existe um código de diagnóstico desconhecido."
    )


# Validação da quantidade de imagens.

arquivos_imagem = [
    arquivo.name
    for arquivo in PASTA_IMAGENS.iterdir()
    if arquivo.is_file()
]

nomes_csv = set(metadata["arquivo"])
nomes_imagens = set(arquivos_imagem)

imagens_faltando = nomes_csv - nomes_imagens
imagens_sem_csv = nomes_imagens - nomes_csv

if imagens_faltando:
    raise ValueError(
        f"Existem {len(imagens_faltando)} registros "
        "sem imagem correspondente."
    )

if imagens_sem_csv:
    raise ValueError(
        f"Existem {len(imagens_sem_csv)} imagens "
        "sem registro no CSV."
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
print(
    metadata["risco_edema_macular"]
    .value_counts(dropna=False)
    .sort_index()
)

print("\nDistribuição da avaliabilidade:")
print(
    metadata["avaliavel"]
    .value_counts()
    .sort_index()
)