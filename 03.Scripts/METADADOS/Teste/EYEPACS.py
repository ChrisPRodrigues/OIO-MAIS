from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

EYEPACS_TEST_DIR = (
    BASE_DIR
    / "01.Originais"
    / "DR (RETINOPATIA DIABÉTICA)"
    / "EyePACS"
    / "test"
)

SAIDA = (
    BASE_DIR
    / "02.Catálogos"
    / "METADADOS"
    / "Teste"
    / "eyepacs_test_metadata.csv"
)

# Localiza as imagens do conjunto de teste.
imagens = sorted(EYEPACS_TEST_DIR.glob("*.jpeg"))

# Cria o metadata.
metadata = pd.DataFrame({
    "id_imagem": range(1, len(imagens) + 1),
    "dataset": "EyePACS",
    "arquivo": [imagem.name for imagem in imagens],
    "doenca": "retinopatia_diabetica",
    "codigo_diagnostico": pd.NA,
    "diagnostico": "nao_disponivel",
    "conjunto": "test"
})

# Garante que a pasta de saída existe.
SAIDA.parent.mkdir(parents=True, exist_ok=True)

# Salva o CSV.
metadata.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8"
)

print("Metadata criada com sucesso:")
print(SAIDA)

print("\nQuantidade de registros:")
print(len(metadata))

print("\nPrimeiras linhas:")
print(metadata.head())