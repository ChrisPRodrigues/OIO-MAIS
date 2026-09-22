from pathlib import Path
import hashlib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ADAM = (
    BASE_DIR
    / "01.Originais"
    / "AMD (Degeneração Macular Relacionada à Idade)"
    / "ADAM"
    / "ADAM"
)

SPLITS = {
    "train_amd": ADAM / "Train" / "Training-image-400" / "AMD",
    "train_non_amd": ADAM / "Train" / "Training-image-400" / "Non-AMD",
    "validation": ADAM / "Validation" / "image",
    "test": ADAM / "Test" / "Test-image-400",
}

def sha256(arquivo):
    h = hashlib.sha256()

    with open(arquivo, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)

    return h.hexdigest()

registros = []

for split, pasta in SPLITS.items():
    if not pasta.exists():
        print(f"[AVISO] Pasta não encontrada: {pasta}")
        continue

    arquivos = [
        arq
        for arq in pasta.rglob("*")
        if arq.is_file() and arq.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    ]

    print(f"{split}: {len(arquivos)} imagens")

    for arquivo in arquivos:
        registros.append(
            {
                "split": split,
                "arquivo": arquivo.name,
                "caminho": str(arquivo),
                "sha256": sha256(arquivo),
            }
        )

df = pd.DataFrame(registros)

# Junta AMD e Non-AMD como um único Training Set
df["grupo_split"] = df["split"].replace(
    {
        "train_amd": "train",
        "train_non_amd": "train",
    }
)

# Duplicatas exatas em qualquer lugar

duplicados = df[df.duplicated("sha256", keep=False)].copy()

# Quantos splits diferentes aparecem para cada hash?
contagem_splits = (
    duplicados
    .groupby("sha256")["grupo_split"]
    .nunique()
    .rename("quantidade_splits")
)

duplicados = duplicados.merge(
    contagem_splits,
    on="sha256",
    how="left"
)

# Duplicatas ENTRE splits

entre_splits = duplicados[
    duplicados["quantidade_splits"] > 1
].copy()

print("\n" + "=" * 60)
print("RESULTADOS")
print("=" * 60)

print(f"Total de imagens analisadas: {len(df)}")
print(f"Arquivos envolvidos em duplicatas exatas: {len(duplicados)}")

hashes_entre_splits = entre_splits["sha256"].nunique()

print(f"Grupos repetidos entre splits: {hashes_entre_splits}")

if entre_splits.empty:
    print("\n✓ Nenhuma duplicata exata encontrada entre Train/Validation/Test.")
else:
    print("\nATENÇÃO: DUPLICATAS ENTRE SPLITS\n")

    for hash_, grupo in entre_splits.groupby("sha256"):
        print(f"SHA256: {hash_}")

        for _, linha in grupo.iterrows():
            print(
                f"  {linha['grupo_split']:10} "
                f"{linha['arquivo']}"
            )

        print()

# Salvar resultados

SAIDA = BASE_DIR / "02.Catálogos" / "ANALISES"
SAIDA.mkdir(parents=True, exist_ok=True)

duplicados.to_csv(
    SAIDA / "adam_duplicatas_todas.csv",
    index=False
)

entre_splits.to_csv(
    SAIDA / "adam_duplicatas_entre_splits.csv",
    index=False
)

print("\nArquivos salvos:")
print(SAIDA / "adam_duplicatas_todas.csv")
print(SAIDA / "adam_duplicatas_entre_splits.csv")

print("\n" + "=" * 60)
print("DUPLICATAS INTERNAS POR SPLIT")
print("=" * 60)

for split in ["train", "validation", "test"]:
    parte = duplicados[
        (duplicados["grupo_split"] == split) &
        (duplicados["quantidade_splits"] == 1)
    ]

    print(f"\n{split.upper()}")

    if parte.empty:
        print("Nenhuma duplicata interna.")
        continue

    for hash_, grupo in parte.groupby("sha256"):
        if len(grupo) > 1:
            print(f"\nSHA256: {hash_}")

            for _, linha in grupo.iterrows():
                print(f"  {linha['arquivo']}")