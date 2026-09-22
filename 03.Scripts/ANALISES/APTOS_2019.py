import pandas as pd
from pathlib import Path
from PIL import Image
import hashlib

# Configurações de diretórios e arquivos.

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PASTA_IMAGENS = (
    BASE_DIR
    / "01.Originais"
    / "DR (Retinopatia Diabética)"
    / "APTOS-2019"
    / "train_images"
)

ARQUIVO_METADATA = (
    BASE_DIR
    / "02.Catálogos"
    / "METADADOS"
    / "aptos_metadata.csv"
)

ARQUIVO_SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "ANALISES"
    / "aptos_analise.csv"
)

# Faz a leitura do metadata.

metadata = pd.read_csv(ARQUIVO_METADATA)

resultados = []

arquivos_corrompidos = []

hashes = {}

# Analisa cada imagem.

for indice, linha in metadata.iterrows():

    arquivo = PASTA_IMAGENS / linha["arquivo"]

    try:

        tamanho_bytes = arquivo.stat().st_size

        with Image.open(arquivo) as imagem:

            largura, altura = imagem.size
            formato = imagem.format
            modo = imagem.mode

        # Calcula hash MD5 para detectar arquivos duplicados.

        hash_md5 = hashlib.md5()

        with open(arquivo, "rb") as f:

            for bloco in iter(lambda: f.read(8192), b""):
                hash_md5.update(bloco)

        hash_imagem = hash_md5.hexdigest()

        if hash_imagem not in hashes:
            hashes[hash_imagem] = []

        hashes[hash_imagem].append(linha["arquivo"])

        resultados.append(
            {
                "arquivo": linha["arquivo"],
                "codigo_diagnostico": linha["codigo_diagnostico"],
                "diagnostico": linha["diagnostico"],
                "largura": largura,
                "altura": altura,
                "resolucao": f"{largura}x{altura}",
                "proporcao": largura / altura,
                "formato": formato,
                "modo_cor": modo,
                "tamanho_bytes": tamanho_bytes,
                "tamanho_mb": tamanho_bytes / (1024 * 1024),
                "hash_md5": hash_imagem,
            }
        )

    except Exception as erro:

        arquivos_corrompidos.append(
            {
                "arquivo": linha["arquivo"],
                "erro": str(erro),
            }
        )


# Criação do DataFrame.

analise = pd.DataFrame(resultados)

# Salvando análise detalhada.

analise.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig"
)

# RESULTADOS GERAIS

print("=" * 60)
print("ANÁLISE DO DATASET APTOS 2019")
print("=" * 60)

print(f"\nTotal esperado de imagens: {len(metadata)}")
print(f"Total analisado: {len(analise)}")
print(f"Arquivos com erro: {len(arquivos_corrompidos)}")

# DISTRIBUIÇÃO DAS CLASSES

print("\n" + "=" * 60)
print("DISTRIBUIÇÃO DAS CLASSES")
print("=" * 60)

distribuicao = (
    analise["diagnostico"]
    .value_counts()
    .rename_axis("diagnostico")
    .reset_index(name="quantidade")
)

distribuicao["porcentagem"] = (
    distribuicao["quantidade"]
    / len(analise)
    * 100
)

print(
    distribuicao.to_string(
        index=False,
        formatters={
            "porcentagem": lambda x: f"{x:.2f}%"
        }
    )
)

# DIMENSÕES

print("\n" + "=" * 60)
print("DIMENSÕES DAS IMAGENS")
print("=" * 60)

print(f"Largura mínima: {analise['largura'].min()} px")
print(f"Largura máxima: {analise['largura'].max()} px")
print(f"Largura média: {analise['largura'].mean():.2f} px")

print()

print(f"Altura mínima: {analise['altura'].min()} px")
print(f"Altura máxima: {analise['altura'].max()} px")
print(f"Altura média: {analise['altura'].mean():.2f} px")

# RESOLUÇÕES

print("\n" + "=" * 60)
print("RESOLUÇÕES")
print("=" * 60)

print(f"Quantidade de resoluções diferentes: {analise['resolucao'].nunique()}")

print("\n10 resoluções mais frequentes:")

print(
    analise["resolucao"]
    .value_counts()
    .head(10)
)

# PROPORÇÃO

print("\n" + "=" * 60)
print("PROPORÇÃO LARGURA / ALTURA")
print("=" * 60)

print(f"Mínima: {analise['proporcao'].min():.4f}")
print(f"Máxima: {analise['proporcao'].max():.4f}")
print(f"Média: {analise['proporcao'].mean():.4f}")

# TAMANHO DOS ARQUIVOS

print("\n" + "=" * 60)
print("TAMANHO DOS ARQUIVOS")
print("=" * 60)

tamanho_total_gb = (
    analise["tamanho_bytes"].sum()
    / (1024 ** 3)
)

print(f"Tamanho total: {tamanho_total_gb:.2f} GB")

print(
    f"Tamanho médio por imagem: "
    f"{analise['tamanho_mb'].mean():.2f} MB"
)

print(
    f"Menor imagem: "
    f"{analise['tamanho_mb'].min():.2f} MB"
)

print(
    f"Maior imagem: "
    f"{analise['tamanho_mb'].max():.2f} MB"
)

# FORMATOS

print("\n" + "=" * 60)
print("FORMATOS")
print("=" * 60)

print(analise["formato"].value_counts())

# MODOS DE COR

print("\n" + "=" * 60)
print("MODOS DE COR")
print("=" * 60)

print(analise["modo_cor"].value_counts())

# DUPLICATAS

duplicatas = {
    hash_imagem: arquivos
    for hash_imagem, arquivos in hashes.items()
    if len(arquivos) > 1
}

print("\n" + "=" * 60)
print("DUPLICATAS")
print("=" * 60)

print(f"Grupos de imagens duplicadas: {len(duplicatas)}")

quantidade_duplicadas = sum(
    len(arquivos)
    for arquivos in duplicatas.values()
)

print(f"Arquivos envolvidos em duplicatas: {quantidade_duplicadas}")

if duplicatas:

    print("\nDuplicatas encontradas:")

    for arquivos in duplicatas.values():
        print(arquivos)

# =========================================================
# ANÁLISE DETALHADA DAS DUPLICATAS
# =========================================================

ARQUIVO_DUPLICATAS = (
    BASE_DIR
    / "02.Catálogos"
    / "ANALISES"
    / "aptos_duplicatas.csv"
)

registros_duplicatas = []

for hash_imagem, arquivos in duplicatas.items():

    registros_grupo = analise[
        analise["hash_md5"] == hash_imagem
    ].copy()

    diagnosticos = registros_grupo["diagnostico"].unique()

    mesmo_rotulo = len(diagnosticos) == 1

    for _, linha in registros_grupo.iterrows():

        registros_duplicatas.append(
            {
                "hash_md5": hash_imagem,
                "arquivo": linha["arquivo"],
                "codigo_diagnostico": linha["codigo_diagnostico"],
                "diagnostico": linha["diagnostico"],
                "quantidade_no_grupo": len(registros_grupo),
                "mesmo_rotulo_no_grupo": mesmo_rotulo,
            }
        )

duplicatas_df = pd.DataFrame(registros_duplicatas)

duplicatas_df.to_csv(
    ARQUIVO_DUPLICATAS,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 60)
print("ANÁLISE DOS RÓTULOS DAS DUPLICATAS")
print("=" * 60)

grupos_consistentes = 0
grupos_inconsistentes = 0

for hash_imagem, grupo in duplicatas_df.groupby("hash_md5"):

    if grupo["mesmo_rotulo_no_grupo"].iloc[0]:
        grupos_consistentes += 1
    else:
        grupos_inconsistentes += 1

print(f"Grupos duplicados analisados: {len(duplicatas)}")
print(f"Grupos com mesmo rótulo: {grupos_consistentes}")
print(f"Grupos com rótulos diferentes: {grupos_inconsistentes}")

print("\nDistribuição dos arquivos duplicados por diagnóstico:")

print(
    duplicatas_df["diagnostico"]
    .value_counts()
)

# Mostra apenas os grupos problemáticos.

inconsistentes = duplicatas_df[
    duplicatas_df["mesmo_rotulo_no_grupo"] == False
]

if len(inconsistentes) == 0:

    print(
        "\n✓ Todas as imagens duplicadas possuem "
        "o mesmo diagnóstico dentro de seus grupos."
    )

else:

    print("\n⚠ Existem duplicatas com diagnósticos diferentes.")

    for hash_imagem, grupo in inconsistentes.groupby("hash_md5"):

        print("\nGrupo:")

        print(
            grupo[
                [
                    "arquivo",
                    "codigo_diagnostico",
                    "diagnostico",
                ]
            ].to_string(index=False)
        )

print(
    f"\nArquivo detalhado salvo em:\n"
    f"{ARQUIVO_DUPLICATAS}"
)

# ARQUIVOS CORROMPIDOS

print("\n" + "=" * 60)
print("INTEGRIDADE")
print("=" * 60)

if len(arquivos_corrompidos) == 0:

    print("✓ Nenhum arquivo corrompido encontrado.")

else:

    print(
        f"⚠ Foram encontrados "
        f"{len(arquivos_corrompidos)} arquivos com erro."
    )

    for item in arquivos_corrompidos:

        print(
            item["arquivo"],
            "-",
            item["erro"]
        )

# FINAL

print("\n" + "=" * 60)

print(
    f"Análise detalhada salva em:\n{ARQUIVO_SAIDA}"
)

print("=" * 60)