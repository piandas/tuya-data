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