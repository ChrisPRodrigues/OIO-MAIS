from pathlib import Path
from PIL import Image
import pandas as pd
import hashlib

# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

REFUGE = (
    BASE_DIR
    / "01.Originais"
    / "GLA (Glaucoma)"
    / "REFUGE"
)

SPLITS = {
    "train": REFUGE / "REFUGE-Training400",
    "validation": REFUGE / "REFUGE-Validation400",
    "test": REFUGE / "Test400",
}

# Pasta que já temos organizada por classe
TRAIN_LABELS = REFUGE / "Training400"

SAIDA = BASE_DIR / "02.Catálogos" / "ANALISES"
SAIDA.mkdir(parents=True, exist_ok=True)


# ============================================================
# FUNÇÕES
# ============================================================

def sha256_arquivo(caminho):
    h = hashlib.sha256()

    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)

    return h.hexdigest()


def imagens_da_pasta(pasta):
    extensoes = {".jpg", ".jpeg", ".png", ".bmp"}

    return sorted(
        arq
        for arq in pasta.rglob("*")
        if (
            arq.is_file()
            and arq.suffix.lower() in extensoes
            and "__MACOSX" not in arq.parts
        )
    )


# ============================================================
# MAPEAR RÓTULOS DO TRAIN
# ============================================================

rotulos_train = {}

pasta_glaucoma = TRAIN_LABELS / "Glaucoma"
pasta_normal = TRAIN_LABELS / "Non-Glaucoma"

if pasta_glaucoma.exists():

    for arquivo in imagens_da_pasta(pasta_glaucoma):
        rotulos_train[arquivo.name.lower()] = "glaucoma"

if pasta_normal.exists():

    for arquivo in imagens_da_pasta(pasta_normal):
        rotulos_train[arquivo.name.lower()] = "sem_glaucoma"


# ============================================================
# ANALISAR AS 1.200 IMAGENS
# ============================================================

registros = []

print("=" * 60)
print("REFUGE — AUDITORIA DOS SPLITS")
print("=" * 60)

for split, pasta in SPLITS.items():

    if not pasta.exists():
        print(f"\n[ERRO] Pasta não encontrada:")
        print(pasta)
        continue

    arquivos = imagens_da_pasta(pasta)

    print(f"\n{split.upper()}: {len(arquivos)} imagens")

    for arquivo in arquivos:

        registro = {
            "split": split,
            "arquivo": arquivo.name,
            "caminho": str(arquivo),
            "extensao": arquivo.suffix.lower(),
            "tamanho_mb": arquivo.stat().st_size / (1024 * 1024),
            "sha256": sha256_arquivo(arquivo),
            "erro_leitura": False,
        }

        try:

            with Image.open(arquivo) as img:

                registro["largura"] = img.width
                registro["altura"] = img.height
                registro["modo"] = img.mode
                registro["resolucao"] = f"{img.width}x{img.height}"

        except Exception as e:

            registro["erro_leitura"] = True
            registro["erro"] = str(e)
            registro["largura"] = None
            registro["altura"] = None
            registro["modo"] = None
            registro["resolucao"] = None

        # Rótulo conhecido apenas para o Training
        if split == "train":

            registro["diagnostico"] = rotulos_train.get(
                arquivo.name.lower(),
                "nao_encontrado"
            )

        else:

            registro["diagnostico"] = None

        registros.append(registro)


df = pd.DataFrame(registros)


# ============================================================
# RESUMO GERAL
# ============================================================

print("\n" + "=" * 60)
print("RESUMO")
print("=" * 60)

print(f"\nTotal analisado: {len(df)}")

print("\nImagens por split:")
print(df["split"].value_counts())

print("\nErros de leitura:")
print(df["erro_leitura"].value_counts())

print("\nFormatos:")
print(df["extensao"].value_counts())

print("\nModos de cor:")
print(df["modo"].value_counts())


# ============================================================
# RESOLUÇÕES
# ============================================================

print("\n" + "=" * 60)
print("RESOLUÇÕES POR SPLIT")
print("=" * 60)

for split in ["train", "validation", "test"]:

    parte = df[df["split"] == split]

    print(f"\n{split.upper()}")
    print(parte["resolucao"].value_counts())


# ============================================================
# CLASSES DO TRAIN
# ============================================================

print("\n" + "=" * 60)
print("DISTRIBUIÇÃO DO TRAINING SET")
print("=" * 60)

train = df[df["split"] == "train"]

print(train["diagnostico"].value_counts())

print("\nPorcentagens:")

print(
    (
        train["diagnostico"].value_counts(normalize=True)
        * 100
    ).round(2)
)


# ============================================================
# DUPLICATAS EXATAS
# ============================================================

duplicados = df[
    df.duplicated("sha256", keep=False)
].copy()

if not duplicados.empty:

    qtd_splits = (
        duplicados
        .groupby("sha256")["split"]
        .nunique()
        .rename("quantidade_splits")
    )

    duplicados = duplicados.merge(
        qtd_splits,
        on="sha256",
        how="left"
    )

else:

    duplicados["quantidade_splits"] = []


# ============================================================
# DUPLICATAS INTERNAS
# ============================================================

print("\n" + "=" * 60)
print("DUPLICATAS INTERNAS")
print("=" * 60)

for split in ["train", "validation", "test"]:

    parte = duplicados[
        (duplicados["split"] == split)
        & (duplicados["quantidade_splits"] == 1)
    ]

    grupos = []

    for hash_, grupo in parte.groupby("sha256"):

        if len(grupo) > 1:
            grupos.append((hash_, grupo))

    print(f"\n{split.upper()}")

    if not grupos:

        print("Nenhuma duplicata exata interna.")

    else:

        print(f"Grupos: {len(grupos)}")

        for hash_, grupo in grupos:

            print()

            for arquivo in grupo["arquivo"]:
                print(f"  {arquivo}")


# ============================================================
# DUPLICATAS ENTRE SPLITS
# ============================================================

entre_splits = duplicados[
    duplicados["quantidade_splits"] > 1
].copy()

print("\n" + "=" * 60)
print("DUPLICATAS ENTRE SPLITS")
print("=" * 60)

if entre_splits.empty:

    print(
        "\n✓ Nenhuma duplicata exata encontrada "
        "entre Train, Validation e Test."
    )

else:

    grupos = entre_splits["sha256"].nunique()

    print(f"\nATENÇÃO: {grupos} grupos compartilhados entre splits.\n")

    for hash_, grupo in entre_splits.groupby("sha256"):

        print(f"SHA256: {hash_}")

        for _, linha in grupo.iterrows():

            print(
                f"  {linha['split']:10} "
                f"{linha['arquivo']}"
            )

        print()


# ============================================================
# ESTATÍSTICAS DE TAMANHO
# ============================================================

print("\n" + "=" * 60)
print("TAMANHO DOS ARQUIVOS")
print("=" * 60)

print(
    df.groupby("split")["tamanho_mb"]
    .agg(["count", "min", "max", "mean", "sum"])
    .round(3)
)


# ============================================================
# SALVAR CSVs
# ============================================================

df.to_csv(
    SAIDA / "refuge_analise.csv",
    index=False
)

duplicados.to_csv(
    SAIDA / "refuge_duplicatas.csv",
    index=False
)

entre_splits.to_csv(
    SAIDA / "refuge_duplicatas_entre_splits.csv",
    index=False
)

print("\n" + "=" * 60)
print("ARQUIVOS SALVOS")
print("=" * 60)

print(SAIDA / "refuge_analise.csv")
print(SAIDA / "refuge_duplicatas.csv")
print(SAIDA / "refuge_duplicatas_entre_splits.csv")