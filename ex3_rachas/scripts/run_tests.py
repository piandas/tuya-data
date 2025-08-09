import sqlite3
import sys
from pathlib import Path
import pytest

def setup_test_db():
    """Configura la base de datos de pruebas"""
    db_path = Path(__file__).parent.parent / "db" / "rachas_test.db"
    schema_path = Path(__file__).parent.parent / "sql" / "schema.sql"
    
    if db_path.exists():
        db_path.unlink()
    
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.close()
    
    return db_path

def run_tests():
    """Ejecuta las pruebas para CI/CD"""
    print("🧪 Ejecutando pruebas automatizadas...")
    
    test_db = setup_test_db()
    tests_path = Path(__file__).parent.parent / "tests" / "tests.sql"
    
    try:
        conn = sqlite3.connect(test_db)
        
        # Cargar datos de prueba
        with open(tests_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        
        # Verificaciones básicas
        cursor = conn.execute("SELECT COUNT(DISTINCT identificacion) FROM historia")
        unique_clients = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM retiros")
        retiros_count = cursor.fetchone()[0]
        
        print(f"✅ {unique_clients} clientes únicos, {retiros_count} retiro(s)")
        
        # Probar solución
        solution_path = Path(__file__).parent.parent / "sql" / "solution.sql"
        with open(solution_path, 'r', encoding='utf-8') as f:
            solution_sql = f.read()
        
        # Test con rachas >= 3
        cursor = conn.execute(solution_sql, {'fecha_base': '2023-04-30', 'n': 3})
        results = cursor.fetchall()
        print(f"✅ Solución funciona: {len(results)} rachas encontradas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()
        if test_db.exists():
            test_db.unlink()

def test_rachas_analysis():
    """Test pytest para análisis de rachas"""
    success = run_tests()
    assert success, "El análisis de rachas falló"

def test_database_setup():
    """Test pytest para configuración de BD"""
    test_db = setup_test_db()
    assert test_db.exists(), "No se pudo crear la BD de pruebas"
    
    # Verificar esquema
    conn = sqlite3.connect(test_db)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Limpiar
    if test_db.exists():
        test_db.unlink()
    
    assert 'historia' in tables, "Tabla historia no existe"
    assert 'retiros' in tables, "Tabla retiros no existe"

def test_solution_query():
    """Test pytest para la consulta SQL"""
    test_db = setup_test_db()
    tests_path = Path(__file__).parent.parent / "tests" / "tests.sql"
    solution_path = Path(__file__).parent.parent / "sql" / "solution.sql"
    
    try:
        conn = sqlite3.connect(test_db)
        
        # Cargar datos de prueba
        with open(tests_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        
        # Ejecutar solución
        with open(solution_path, 'r', encoding='utf-8') as f:
            solution_sql = f.read()
        
        cursor = conn.execute(solution_sql, {'fecha_base': '2023-04-30', 'n': 3})
        results = cursor.fetchall()
        
        assert len(results) > 0, "La solución no devuelve resultados"
        assert len(results[0]) >= 3, "Formato de resultados incorrecto"
        
    finally:
        conn.close()
        if test_db.exists():
            test_db.unlink()

if __name__ == "__main__":
    success = run_tests()
    print("✅ Tests OK" if success else "❌ Tests FAIL")
    sys.exit(0 if success else 1)
