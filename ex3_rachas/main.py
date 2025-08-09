"""
Ejecución rápida del análisis de rachas
Uso: python main.py (ejecuta con parámetros por defecto)
"""
import subprocess
import sys
from pathlib import Path

def run_script(script_path, args=None, description=""):
    print(f"[INFO] {description}...")
    try:
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, cwd=Path(__file__).parent, 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] {description} falló: {result.stderr}")
            return False
        if result.stdout.strip():
            print(result.stdout.strip())
        return True
    except Exception as e:
        print(f"[ERROR] {description} falló: {e}")
        return False

def main():
    print("Ejecutando con parámetros por defecto:")
    print("- Fecha base: 2024-12-31")
    print("- Rachas mínimas: 3 meses")
    print("- Salida: resultados.csv")
    print()
    
    # Verificar si ya existe la base de datos
    db_exists = (Path(__file__).parent / "db" / "rachas.db").exists()
    
    if not db_exists:
        print("[INFO] Primera ejecución: preparando datos...")
        
        # Convertir XLSX a CSV
        if not run_script("scripts/xlsx_to_csv.py", description="Convirtiendo XLSX a CSV"):
            sys.exit(1)
        
        # Cargar a base de datos
        if not run_script("scripts/loads_csv_to_table.py", description="Cargando datos a SQLite"):
            sys.exit(1)
    else:
        print("[INFO] Base de datos existente encontrada")
    
    # Ejecutar consulta principal
    args = ["--fecha_base", "2024-12-31", "--n", "3", "--output", "resultados.csv"]
    if not run_script("scripts/run_solution.py", args=args, description="Ejecutando consulta de rachas"):
        sys.exit(1)
    
    print()
    print("[SUCCESS] Pipeline completado exitosamente")
    print("Resultados guardados en: resultados.csv")
    print()
    print("Para usar parámetros personalizados:")
    print("python scripts/run_solution.py --fecha_base YYYY-MM-DD --n X")

if __name__ == "__main__":
    main()
