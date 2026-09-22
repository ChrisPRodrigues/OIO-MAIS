from pathlib import Path
from PIL import Image
import pandas as pd
import hashlib

# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PASTA_IMAGENS = (
    BASE_DIR
    / "01.Originais"
    / "AMD (Degeneração Macular Relacionada à Idade)"
    / "ADAM"
    / "ADAM"
    / "Train"
    / "Training-image-400"
)

PASTA_SAIDA = BASE_DIR / "02.Catálogos" / "ANALISES"
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

ARQUIVO_ANALISE = PASTA_SAIDA / "adam_analise.csv"
ARQUIVO_DUPLICATAS = PASTA_SAIDA / "adam_duplicatas.csv"


# ============================================================
# MD5
# ============================================================

def calcular_md5(caminho):
    hash_md5 = hashlib.md5()

    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(8192), b""):
            hash_md5.update(bloco)

    return hash_md5.hexdigest()


# ============================================================
# LOCALIZAR AS 400 IMAGENS
# ============================================================

imagens = list(PASTA_IMAGENS.glob("*/*.jpg"))

print("=" * 60)
print("ANÁLISE DO ADAM — TRAINING SET")
print("=" * 60)

print(f"\nPasta: {PASTA_IMAGENS}")
print(f"Imagens encontradas: {len(imagens)}")


# ============================================================
# ANALISAR
# ============================================================

registros = []
erros = []

for numero, caminho in enumerate(imagens, start=1):

    try:
        diagnostico = caminho.parent.name

        with Image.open(caminho) as img:

            # força a leitura completa para detectar arquivo danificado
            img.load()

            largura, altura = img.size

            registros.append({
                "arquivo": caminho.name,
                "diagnostico": diagnostico,
                "extensao": caminho.suffix.lower(),
                "formato": img.format,
                "modo": img.mode,
                "largura": largura,
                "altura": altura,
                "resolucao": f"{largura}x{altura}",
                "proporcao": round(largura / altura, 4),
                "pixels": largura * altura,
                "tamanho_bytes": caminho.stat().st_size,
                "tamanho_mb": round(
                    caminho.stat().st_size / (1024 ** 2),
                    4
                ),
                "md5": calcular_md5(caminho)
            })

    except Exception as erro:
        erros.append({
            "arquivo": caminho.name,
            "erro": str(erro)
        })

    if numero % 50 == 0:
        print(f"Processadas: {numero}/{len(imagens)}")


df = pd.DataFrame(registros)


# ============================================================
# SALVAR
# ============================================================

df.to_csv(
    ARQUIVO_ANALISE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# RESULTADOS GERAIS
# ============================================================

print("\n" + "=" * 60)
print("RESULTADOS")
print("=" * 60)

print(f"\nImagens esperadas: 400")
print(f"Imagens analisadas: {len(df)}")
print(f"Erros reais de leitura: {len(erros)}")


# ============================================================
# CLASSES
# ============================================================

print("\nDISTRIBUIÇÃO POR CLASSE")
print("-" * 40)

for classe, quantidade in df["diagnostico"].value_counts().items():

    percentual = quantidade / len(df) * 100

    print(
        f"{classe}: {quantidade} "
        f"({percentual:.2f}%)"
    )


# ============================================================
# FORMATOS
# ============================================================

print("\nFORMATOS")
print("-" * 40)

print(df["formato"].value_counts())


print("\nMODOS DE COR")
print("-" * 40)

print(df["modo"].value_counts())


# ============================================================
# RESOLUÇÕES
# ============================================================

resolucoes = df["resolucao"].value_counts()

print("\nRESOLUÇÕES")
print("-" * 40)

print(
    f"Quantidade de resoluções diferentes: "
    f"{len(resolucoes)}"
)

for resolucao, quantidade in resolucoes.head(10).items():

    percentual = quantidade / len(df) * 100

    print(
        f"{resolucao}: "
        f"{quantidade} "
        f"({percentual:.2f}%)"
    )


# ============================================================
# DIMENSÕES
# ============================================================

print("\nDIMENSÕES")
print("-" * 40)

print(
    f"Largura: mín {df['largura'].min()} | "
    f"máx {df['largura'].max()} | "
    f"média {df['largura'].mean():.2f}"
)

print(
    f"Altura: mín {df['altura'].min()} | "
    f"máx {df['altura'].max()} | "
    f"média {df['altura'].mean():.2f}"
)

print(
    f"Proporção: mín {df['proporcao'].min():.4f} | "
    f"máx {df['proporcao'].max():.4f} | "
    f"média {df['proporcao'].mean():.4f}"
)


# ============================================================
# TAMANHO
# ============================================================

print("\nTAMANHO DOS ARQUIVOS")
print("-" * 40)

print(
    f"Total: "
    f"{df['tamanho_bytes'].sum() / (1024 ** 3):.2f} GB"
)

print(
    f"Média: "
    f"{df['tamanho_mb'].mean():.2f} MB"
)

print(
    f"Mínimo: "
    f"{df['tamanho_mb'].min():.2f} MB"
)

print(
    f"Máximo: "
    f"{df['tamanho_mb'].max():.2f} MB"
)


# ============================================================
# DUPLICATAS
# ============================================================

duplicatas = []

grupos_duplicados = 0
grupos_conflitantes = 0

for md5, grupo in df.groupby("md5"):

    if len(grupo) > 1:

        grupos_duplicados += 1

        diagnosticos = grupo["diagnostico"].unique()

        conflito = len(diagnosticos) > 1

        if conflito:
            grupos_conflitantes += 1

        for _, linha in grupo.iterrows():

            duplicatas.append({
                "md5": md5,
                "arquivo": linha["arquivo"],
                "diagnostico": linha["diagnostico"],
                "conflito_rotulo": conflito
            })


df_dup = pd.DataFrame(duplicatas)


print("\nDUPLICATAS EXATAS")
print("-" * 40)

if len(df_dup) == 0:

    print("Nenhuma duplicata exata encontrada.")

else:

    df_dup.to_csv(
        ARQUIVO_DUPLICATAS,
        index=False,
        encoding="utf-8-sig"
    )

    arquivos_duplicados = len(df_dup)

    redundantes = (
        arquivos_duplicados
        - grupos_duplicados
    )

    percentual = arquivos_duplicados / len(df) * 100

    print(f"Grupos duplicados: {grupos_duplicados}")

    print(
        f"Arquivos envolvidos: "
        f"{arquivos_duplicados}"
    )

    print(
        f"Ocorrências redundantes: "
        f"{redundantes}"
    )

    print(
        f"Arquivos em grupos duplicados: "
        f"{percentual:.2f}%"
    )

    print(
        f"Grupos com conflito AMD / Non-AMD: "
        f"{grupos_conflitantes}"
    )

# ERROS

if erros:

    pd.DataFrame(erros).to_csv(
        PASTA_SAIDA / "adam_erros.csv",
        index=False,
        encoding="utf-8-sig"
    )


print("\n" + "=" * 60)
print("CONCLUÍDO")
print("=" * 60)

print(f"\n{ARQUIVO_ANALISE}")

if len(df_dup) > 0:
    print(ARQUIVO_DUPLICATAS)