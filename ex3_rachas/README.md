# Ejercicio 3: Análisis de Rachas

Sistema para detectar rachas de niveles consecutivos en historial financiero de clientes.

## Ejecución

### Opción 1: Ejecución Rápida
```bash
python main.py
```
- Ejecuta pipeline completo automáticamente
- Parámetros por defecto: fecha_base=2024-12-31, n=3
- Genera `resultados.csv`

### Opción 2: Ejecución Modular (parámetros personalizados)
```bash
python ex3_rachas\scripts\run_solution.py --fecha_base 2024-12-31 --n 3
```

## Flujo del Pipeline

```
1. rachas.xlsx (datos crudos)
   ↓
2. xlsx_to_csv.py → genera historia.csv + retiros.csv
   ↓  
3. loads_csv_to_table.py → carga datos en rachas.db (SQLite)
   ↓
4. run_solution.py → ejecuta solution.sql → genera resultados CSV
```

### Detalle de cada paso:

1. **Datos de entrada**: `data/raw/rachas.xlsx` (2 hojas: historia, retiros)
2. **Conversión**: `scripts/xlsx_to_csv.py` extrae las hojas a CSV separados
3. **Carga BD**: `scripts/loads_csv_to_table.py` crea esquema SQLite y carga datos
4. **Análisis**: `scripts/run_solution.py` ejecuta consulta SQL con parámetros
5. **Resultado**: CSV con columnas `identificacion,racha,fecha_fin,nivel`

## Lógica de Negocio

**Niveles de Saldo:**
- N0: [0, 300k) 
- N1: [300k, 1M)
- N2: [1M, 3M)
- N3: [3M, 5M)
- N4: [5M, +∞)

**Reglas:**
1. Clasificación por rangos de saldo según corte mensual
2. Exclusión de registros posteriores a fecha de retiro
3. Racha = meses consecutivos en mismo nivel (algoritmo gaps & islands)
4. Filtro: solo rachas >= n meses
5. Desempate: mayor racha; si empate, fecha fin más reciente <= fecha_base

## Estructura Final
```
ex3_rachas/
├── main.py                     # Ejecución rápida
├── README.md                   # Esta documentación
├── resultados.csv              # Salida generada
├── data/
│   ├── raw/rachas.xlsx         # Datos origen
│   ├── historia.csv            # Datos convertidos
│   └── retiros.csv             # Datos convertidos  
├── db/rachas.db               # Base de datos SQLite
├── scripts/
│   ├── xlsx_to_csv.py         # Paso 1: XLSX → CSV
│   ├── loads_csv_to_table.py  # Paso 2: CSV → SQLite
│   └── run_solution.py        # Paso 3: Consulta + resultados
└── sql/
    ├── schema.sql             # Esquema de tablas
    └── solution.sql           # Query principal (gaps & islands)
```

## Salida
Formato CSV: `identificacion,racha,fecha_fin,nivel`

Ejemplo:
```
identificacion,racha,fecha_fin,nivel
DWJ0GFUKS12L7Y0G9,6,2023-11-30,N2
IGOQX9XYBSRDMOZXT,6,2023-12-31,N4
```