"""
Runner para ejecutar solution.sql con parámetros.
Uso: python run_solution.py --fecha_base 2025-07-31 --n 3
"""
import argparse
import sqlite3
import csv
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Ejecuta consulta de rachas")
    parser.add_argument("--fecha_base", default="2023-04-30", 
                       help="Fecha base en formato YYYY-MM-DD (default: 2023-04-30)")
    parser.add_argument("--n", type=int, default=3,
                       help="Mínimo de meses consecutivos para filtrar rachas (default: 3)")
    parser.add_argument("--output", default=None,
                       help="Archivo CSV de salida (por defecto: stdout)")
    
    args = parser.parse_args()
    
    # Rutas
    db_path = Path(__file__).parent.parent / "db" / "rachas.db"
    sql_path = Path(__file__).parent.parent / "sql" / "solution.sql"
    
    if not db_path.exists():
        print(f"Error: Base de datos no encontrada en {db_path}", file=sys.stderr)
        print("Ejecuta primero los scripts de carga de datos.", file=sys.stderr)
        sys.exit(1)
    
    if not sql_path.exists():
        print(f"Error: Script SQL no encontrado en {sql_path}", file=sys.stderr)
        sys.exit(1)
    
    # Leer consulta SQL
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_query = f.read()
    
    # Ejecutar consulta
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Parámetros nombrados
        params = {
            'fecha_base': args.fecha_base,
            'n': args.n
        }
        
        cursor.execute(sql_query, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        conn.close()
        
        # Escribir resultados
        if args.output:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
            print(f"Resultados guardados en {args.output}")
        else:
            # Imprimir a stdout como CSV
            writer = csv.writer(sys.stdout)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"Total de registros: {len(rows)}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error ejecutando consulta: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
