# Simple wrapper para que VS Code encuentre los tests
import sys
from pathlib import Path

# Agregar scripts al path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Importar los tests del archivo original
from run_tests import test_rachas_analysis, test_database_setup, test_solution_query

class TestRachas:
    def test_rachas_analysis(self):
        test_rachas_analysis()
    
    def test_database_setup(self):
        test_database_setup()
    
    def test_solution_query(self):
        test_solution_query()
