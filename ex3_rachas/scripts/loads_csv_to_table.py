import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "rachas.db"
SQL_SCHEMA = Path(__file__).parent.parent / "sql" / "schema.sql"
DATA_DIR = Path(__file__).parent.parent / "data"

def load_csv_to_table(cursor, csv_path, table_name):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        placeholders = ", ".join(["?"] * len(headers))
        cursor.executemany(
            f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})",
            reader
        )

def create_indexes(cursor):
    """Crea índices para mejorar performance en consultas"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_historia_identificacion ON historia(identificacion);",
        "CREATE INDEX IF NOT EXISTS idx_historia_corte_mes ON historia(corte_mes);",
        "CREATE INDEX IF NOT EXISTS idx_historia_id_fecha ON historia(identificacion, corte_mes);",
        "CREATE INDEX IF NOT EXISTS idx_retiros_identificacion ON retiros(identificacion);",
        "CREATE INDEX IF NOT EXISTS idx_retiros_fecha ON retiros(fecha_retiro);"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)

def main():
    # Crear directorio db si no existe
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    with open(SQL_SCHEMA, "r", encoding="utf-8") as schema_file:
        conn.executescript(schema_file.read())

    cur = conn.cursor()
    load_csv_to_table(cur, DATA_DIR / "historia.csv", "historia")
    load_csv_to_table(cur, DATA_DIR / "retiros.csv", "retiros")
    
    # Crear índices para optimizar consultas
    create_indexes(cur)

    conn.commit()
    conn.close()
    print(f"Database creada en {DB_PATH}")

if __name__ == "__main__":
    main()
