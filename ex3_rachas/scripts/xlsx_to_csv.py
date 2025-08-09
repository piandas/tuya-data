import pandas as pd
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "rachas.xlsx"
DATA_DIR = Path(__file__).parent.parent / "data"

def main():
    DATA_DIR.mkdir(exist_ok=True)

    # Cargar hojas
    historia = pd.read_excel(RAW_PATH, sheet_name="historia")
    retiros = pd.read_excel(RAW_PATH, sheet_name="retiros")

    # Exportar a CSV
    historia.to_csv(DATA_DIR / "historia.csv", index=False)
    retiros.to_csv(DATA_DIR / "retiros.csv", index=False)

    print("[OK] CSV generados en", DATA_DIR)

if __name__ == "__main__":
    main()