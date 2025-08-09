# Ejercicio 1 — Dataset de Teléfonos

Objetivo: un dataset único, simple y trazable de teléfonos para contactabilidad (campañas, servicio, cobranza).

## Modelo de datos
- clientes(id, ...)
- telefonos(cliente_id, telefono_e164, tipo, opt_in, updated_at, fuente, activo)
- telefonos_hist(id_hist, cliente_id, telefono_raw, normalizado_e164, tipo, opt_in, updated_at, fuente, regla_aplicada, run_id)

## Reglas clave
- E.164: `^\+[1-9]\d{7,14}$`.
- Unicidad cliente+tipo: 1 activo máximo.
- Frescura: updated_at ≤ 365 días.
- Consentimiento: solo opt_in=1 queda activo.
- Colombia: usar `+57` por defecto si la fuente es local; excluir blacklists y prefijos inválidos.

## Deduplicación
- Desempate simple y estable: ORDER BY opt_in DESC, updated_at DESC, fuente ('crm'>'batch'>otros), país '+57' primero.
- Resultado: 1 activo por cliente+tipo; el resto inactivo con motivo en `telefonos_hist.regla_aplicada`.

## Privacidad
- Trazar consentimiento (Habeas Data). No exponer `telefono_raw` fuera de auditoría.

## Pipeline
1) Ingesta → 2) Perfilado → 3) Validación → 4) Estandarización (E.164) → 5) Dedup → 6) Publicación → 7) Auditoría/observabilidad.

## Arquitectura Medallion (ligera)
- Bronze (crudo): bronze_telefonos_raw(cliente_id, telefono_raw, tipo, updated_at, fuente, opt_in, run_id). Conserva lo que llega “tal cual” para reprocess/auditoría.
- Silver (limpio): silver_telefonos y silver_telefonos_hist. Aquí van E.164, frescura, opt_in, listas negras y dedup determinístico. Se calculan KPIs y gates; si fallan, no se promueve.
- Gold (publicado): gold_telefonos_activos (1 por cliente+tipo) y gold_kpi_dashboard (KPIs para BI/exportar).
- Relación: data_contract.yaml define el pase Bronze→Silver; gates en CI definen el pase Silver→Gold.

## Versionado y despliegue
- Esquemas por tags (v1, v2). `run_id` por corrida.
- CI/CD con gates: bloquear si E.164 válidos < 95% o duplicados > 1%.

## Contrato de datos (v1)
- Input: `cliente_id, telefono, tipo, updated_at, opt_in`
- Output: `cliente_id, telefono_e164, tipo, opt_in, updated_at`
- Umbrales iniciales: E.164 ≥ 95%, duplicados ≤ 1%, frescura promedio ≤ 60 días, opt_in móviles ≥ 90%.
 
¿Qué es y para qué sirve?
- Es el “acuerdo” mínimo de columnas y reglas para que las fuentes entreguen bien y el dataset salga con calidad.
- Si algo viene mal, se detecta antes de publicar (CI/CD bloquea y avisa).
- Define reglas simples y umbrales; si no se cumplen, no se promueve a consumo.

# Ejercicio 2 — KPIs y Trazabilidad

## Lo que verá el negocio
- Calidad del dato: porcentaje de teléfonos “bien formateados” y utilizables (E.164 válidos/total).
- Duplicados: porcentaje de registros repetidos por cliente y tipo (duplicados/total por cliente+tipo).
- Actualización: días promedio desde la última actualización (avg días desde updated_at).
- Consentimiento: porcentaje con permiso vigente (opt_in=1).
- Novedades: altas, bajas y cambios por semana.
- Contactabilidad: móviles listos para usar hoy (válidos+opt_in con < 90 días).

## Auditoría
- Registro de reglas y resultados por corrida (dq_checks, kpi_runs con run_id).
- Trazabilidad de origen→transformación→destino (data_lineage por run_id).

## Dashboard
- Portada de salud de los datos: tarjetas con semáforo y tendencia semanal (calidad, duplicados, actualización, consentimiento).
- Calidad por fuente/tipo: barras + tabla de “Top errores” con botón “ver muestras” (CSV).
- Contactabilidad por segmento/campaña: móviles listos para contacto hoy.
- Novedades semanales: altas/bajas/cambios con filtro de fechas.
- Exportar: “teléfonos activos” según filtros.

## Alertas
- Se dispara si caen los mínimos: calidad < 95%, duplicados > 1%, actualización > 60 días.
- Notificación por email/Teams; queda registro (el pipeline falla si no se cumplen los mínimos y se anota en kpi_runs).

## Acciones rápidas
- Filtrar por campaña y exportar teléfonos activos.
- Descargar 100 muestras de errores para corregir en la fuente.
- Ver evolución semanal para medir impacto de acciones.

## Frecuencia y entrega
- Actualización diaria y publicación en capa analítica con diccionario.
- Reporte corto por corrida con KPIs y umbrales (CSV/Markdown, run_id).