import argparse
from pathlib import Path
import sys

# Asegurar que la raíz del repo esté en sys.path cuando se ejecuta este archivo directamente
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ex4_html2base64.html2base64 import process


def main():
    parser = argparse.ArgumentParser(description="Inlinea imágenes locales en HTML y genera copias .inlined.html")
    parser.add_argument("paths", nargs="+", help="Archivos HTML o directorios a procesar")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Imprime el resumen en JSON")
    args = parser.parse_args()

    inputs = [Path(p) for p in args.paths]
    result = process(inputs)

    if args.as_json:
        print(result.to_json())
    else:
        # Salida legible
        print("Procesamiento completado:\n")
        print("Éxitos:")
        for html, imgs in result.success.items():
            print(f"- {html}")
            for i in imgs:
                print(f"   * {i}")
        if result.fail:
            print("\nFallos:")
            for html, imgs in result.fail.items():
                print(f"- {html}")
                for i in imgs:
                    print(f"   * {i}")


if __name__ == "__main__":
    main()
