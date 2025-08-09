# ex4_html2base64 — Procesamiento de archivos HTML (inline Base64)

## Objetivo (ex4)
- Recibir una lista de archivos y/o directorios con HTML (recursivo).
- Para cada HTML, convertir imágenes locales referenciadas en `img[src]` a Base64 (data URI).
- No sustituir el archivo original; generar uno nuevo con sufijo `.inlined.html`.
- Retornar un objeto con imágenes procesadas y fallidas por HTML.

## Uso rápido (CLI)
## Ejemplo incluido (paso a paso)
- Carpeta de ejemplo: `ex4_html2base64\examples`
1) Ejecuta:

```cmd
python ex4_html2base64\scripts\run_html2base64.py ex4_html2base64\examples --json
```

2) Resultado esperado (similar a):

```json
{
	"success": {
		"C:\\...\\ex4_html2base64\\examples\\index.html": [
			"C:\\...\\ex4_html2base64\\examples\\images\\tuya.svg"
		]
	},
	"fail": {}
}
```

3) Se generará `index.inlined.html` junto al original. Ábrelo en el navegador:
- La primera imagen (local) estará inline como `data:image/svg+xml;base64,...`
- La segunda (remota https) se mantiene igual.

## Detalles de implementación
- Solo se inlinean imágenes locales (relativas, absolutas y `file://`). Se ignoran `http/https` y `data:`.
- Limpieza de `src`: se eliminan querystrings/fragmentos (`?v=1`, `#id`).
- Salida: nuevo archivo con sufijo `.inlined.html`, no se toca el original.

## Estructura de la carpeta y descripción de archivos

```text
ex4_html2base64/
├─ README.md                     # Guía de uso, ejemplo y detalles del ejercicio
├─ __init__.py                   # Hace que el directorio sea un paquete Python
├─ html2base64.py                # Módulo principal: búsqueda de HTMLs, inline de <img> y resumen
├─ scripts/
│  └─ run_html2base64.py         # CLI para ejecutar el procesamiento desde la terminal
├─ examples/
│  ├─ index.html                 # HTML de ejemplo con una imagen local y otra remota
│  ├─ index.inlined.html         # (Generado por el ejemplo) HTML con imágenes inline Base64
│  └─ images/
│     └─ tuya.svg                # Imagen local usada por el ejemplo (se inlinea)
└─ tests/
	└─ test_smoke.py              # Prueba mínima (smoke test) del inline sobre un HTML simple
```

Notas:
- El archivo generado por el proceso del ejemplo es `examples/index.inlined.html` (no se versiona por defecto).
- Las dependencias se instalan desde el `requirements.txt` en la raíz del repositorio.