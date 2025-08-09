# Santiago Bustos Pianda - Tuya SAS — Prueba de Ingeniería de Datos

Repositorio con las soluciones a los 4 numerales de la prueba técnica. Este README resume el qué, cómo y dónde; los detalles están en cada carpeta.

## Diagrama general

<picture>
	<source srcset="Documents/diagrama-final.png" type="image/png">
	<img alt="Diagrama general de la solución" src="Documents/diagrama-final.svg" />
</picture>

## Resumen ejecutivo
- Ejercicio 1 (Dataset de teléfonos): se definió un modelo y proceso simple para tener un único teléfono activo por cliente y tipo, con validación E.164, frescura y consentimiento. Logro: dataset claro y trazable listo para consumo, cumpliendo el objetivo de calidad y autogestión.
- Ejercicio 2 (KPIs y trazabilidad): se planteó un dashboard con semáforos y tendencias para calidad, duplicados, actualización, consentimiento y contactabilidad, con alertas por umbrales y registro por corrida. Logro: mecanismo práctico de veeduría que bloquea publicaciones si no hay calidad mínima.
- Ejercicio 3 (Rachas): se construyó un pipeline reproducible (XLSX→CSV→SQLite→SQL) que entrega rachas por nivel y cliente parametrizadas por fecha_base y n. Logro: resultados consistentes y testeables que cumplen todas las reglas pedidas.
- Ejercicio 4 (HTML→Base64): se desarrolló un script con librería estándar que inlinea imágenes locales y genera copias .inlined.html, devolviendo un resumen de éxitos/fallos. Logro: solución simple, portable y orientada a objetos.

## 🗂️ Estructura

```
.
├─ ex1_ex2_telefonos_kpis/     # Diseño conceptual: dataset teléfonos, KPIs, dashboard, contrato
├─ ex3_rachas/                 # Pipeline SQL + SQLite para rachas por niveles de saldo
├─ ex4_html2base64/            # Script(s) Python stdlib: inline de imágenes en HTML a Base64
├─ requirements.txt            # Dependencias (pandas/openpyxl/pytest) para ex3 y tests
└─ README.md                   # Este documento
```

## ⚙️ Setup rápido
- Python 3.11+ recomendado
- Instalar dependencias (para ex3 y tests):
```
pip install -r requirements.txt
```

---

## 1) Dataset de Teléfonos (conceptual)
Ruta: `ex1_ex2_telefonos_kpis/README.md` y `ex1_ex2_telefonos_kpis/data_contract.yaml`.

- Modelo simple: `telefonos` y `telefonos_hist` (trazabilidad de regla aplicada).
- Reglas: E.164, 1 activo por cliente+tipo, frescura, opt-in, +57 por defecto (local), exclusión de blacklists.
- Deduplicación determinística: opt_in DESC, updated_at DESC, fuente (crm>batch>otros), país ‘+57’ primero.
- Privacidad: evidencia de consentimiento (Habeas Data) y mínimo acceso a PII.
- Pipeline: Ingesta → Validación/Estandarización → Dedup → Publicación → Auditoría/Observabilidad.
- Medallion (ligero): bronze_ (crudo) → silver_ (limpio con KPIs/gates) → gold_ (publicado).

> Data contract: acuerdo mínimo de columnas y umbrales; si no se cumplen, el pipeline no publica (gate en CI/CD).

---

## 2) KPIs y Trazabilidad (conceptual)
Ruta: `ex1_ex2_telefonos_kpis/READ.md` (sección “Ejercicio 2”).

- Vista negocio: calidad (E.164), duplicados, actualización (días), consentimiento, novedades y contactabilidad.
- Dashboard: portada con semáforos y tendencias, calidad por fuente/tipo con “ver muestras”, contactabilidad por segmento, novedades y exportar “teléfonos activos”.
- Alertas: mínimos (calidad < 95%, duplicados > 1%, actualización > 60 días) bloquean publicación y notifican.
- Auditoría: registro de reglas/resultados y lineage por corrida (run_id).

---

## 3) Rachas — SQL + SQLite
Ruta: `ex3_rachas/` (README con detalle y scripts).

- Flujo: XLSX → CSV → SQLite → SQL → resultados.csv
- Resultado: `identificacion, racha, fecha_fin, nivel`

Ejecución rápida:
```
cd ex3_rachas
python main.py
```

Ejecución con parámetros:
```
python ex3_rachas\scripts\run_solution.py --fecha_base 2024-12-31 --n 3 --output resultados.csv
```

---

## 4) HTML → Base64 (stdlib)
Ruta: `ex4_html2base64/` (README con ejemplo y CLI).

Ejemplo incluido:
```
python ex4_html2base64\scripts\run_html2base64.py ex4_html2base64\examples --json
```
- Genera `.inlined.html` sin modificar el original.
- Retorna resumen `{ success: {}, fail: {} }` por HTML.

---

## 🔍 Calidad y contratos
- Data Contract (`ex1_ex2_telefonos_kpis/data_contract.yaml`): columnas y reglas básicas; umbrales mínimos (E.164 ≥ 95%, duplicados ≤ 1%).
- Gates: si fallan mínimos, no se promueve de silver_ a gold_ y se notifica.
- Auditoría/lineage: registro por corrida (`run_id`) de reglas, KPIs y transformaciones.

## Notas
- ex4 usa solo librería estándar; ex3 usa pandas/openpyxl para preparación y pytest para pruebas.
