# Ejercicio 1 — Dataset de Teléfonos

## Resumen Ejecutivo

Se diseñó una solución integral para consolidar y gestionar datos de teléfonos de contactabilidad empresarial, implementando una arquitectura Medallion que garantiza calidad, trazabilidad y cumplimiento normativo. La solución aborda el problema de múltiples fuentes fragmentadas de datos telefónicos mediante un pipeline automatizado que normaliza a estándar E.164, elimina duplicados con reglas determinísticas, y mantiene auditoría completa del consentimiento (Habeas Data). El objetivo es proporcionar un dataset único y confiable que permita a las áreas de campañas, servicio al cliente y cobranza acceder a información de contacto actualizada y válida, con KPIs en tiempo real y alertas automáticas para mantener estándares de calidad superiores al 95%.

## Objetivo
Dataset único, simple y trazable de teléfonos para contactabilidad (campañas, servicio, cobranza).

## Modelo de Datos
- **clientes**: `(id, ...)`
- **telefonos**: `(cliente_id, telefono_e164, tipo, opt_in, updated_at, fuente, activo)`
- **telefonos_hist**: `(id_hist, cliente_id, telefono_raw, normalizado_e164, tipo, opt_in, updated_at, fuente, regla_aplicada, run_id)`

## Reglas de Negocio

### Estándares
- **E.164**: `^\+[1-9]\d{7,14}$`
- **Unicidad**: 1 activo máximo por cliente+tipo
- **Frescura**: `updated_at` ≤ 365 días
- **Consentimiento**: Solo `opt_in=1` activos
- **Colombia**: `+57` por defecto, excluir blacklists

### Deduplicación
**Orden**: `opt_in DESC, updated_at DESC, fuente ('crm'>'batch'>otros), país '+57' primero`

**Resultado**: 1 activo por cliente+tipo, resto inactivo con motivo en `telefonos_hist.regla_aplicada`

## Arquitectura Medallion

### Bronze (Crudo)
`bronze_telefonos_raw` - Conserva datos originales para auditoría

### Silver (Limpio)
`silver_telefonos` + `silver_telefonos_hist` - E.164, frescura, opt_in, dedup + KPIs/gates

### Gold (Publicado)
`gold_telefonos_activos` (1 por cliente+tipo) + `gold_kpi_dashboard` (BI)

### Promoción
- **Bronze→Silver**: `data_contract.yaml`
- **Silver→Gold**: Gates CI/CD

## Contrato de Datos (v1)

**Input**: `cliente_id, telefono, tipo, updated_at, opt_in`
**Output**: `cliente_id, telefono_e164, tipo, opt_in, updated_at`

**Umbrales**: E.164 ≥95%, duplicados ≤1%, frescura ≤60 días, opt_in móviles ≥90%

Establece el "acuerdo mínimo" entre fuentes y consumo para garantizar calidad.

## Stack Tecnológico Recomendado

### Implementación Inicial (Sencilla)
**Base de datos**: PostgreSQL para todo (transaccional + analítico)\
**Procesamiento**: Python + Pandas para ETL y validaciones\
**Orquestación**: Apache Airflow o cron jobs para scheduling diario\
**Monitoreo**: Great Expectations para data contracts y validaciones

### Escalabilidad Futura
Si el volumen crece significativamente, migrar a Apache Spark (procesamiento distribuido), Apache Parquet (almacenamiento columnar), y Redis (cache de validaciones).

---

# Ejercicio 2 — KPIs y Trazabilidad

## Resumen Ejecutivo

Se implementó un sistema completo de monitoreo y observabilidad que proporciona visibilidad en tiempo real sobre la calidad y utilidad de los datos telefónicos. La solución incluye un dashboard interactivo con métricas de negocio (calidad E.164, duplicados, frescura, consentimiento), sistema de alertas automáticas que bloquea el pipeline cuando se incumplen umbrales críticos, y capacidades de auditoría completa con trazabilidad origen-destino por ejecución. El sistema permite a los equipos de negocio tomar decisiones informadas, exportar datos filtrados para campañas específicas, y mantener cumplimiento normativo mediante registro exhaustivo de todas las transformaciones y cambios de consentimiento.

## Métricas de Negocio

### Indicadores Principales
- **Calidad**: % teléfonos E.164 válidos
- **Duplicados**: % registros repetidos por cliente+tipo
- **Actualización**: Días promedio desde `updated_at`
- **Consentimiento**: % con `opt_in=1`
- **Contactabilidad**: Móviles válidos+opt_in+<90días

### Novedades
Altas, bajas y cambios por semana

## Auditoría y Trazabilidad
- **Registro completo**: `dq_checks`, `kpi_runs` con `run_id`
- **Linaje**: Origen → transformación → destino por ejecución
- **Habeas Data**: Trazabilidad de consentimiento

## Dashboard

### Salud General
**Portada**: Tarjetas con semáforo + tendencia semanal (calidad, duplicados, actualización, consentimiento)

### Análisis Detallado
- **Por fuente/tipo**: Barras + "Top errores" con muestras CSV
- **Contactabilidad**: Por segmento/campaña
- **Evolution**: Novedades semanales con filtros de fecha

### Acciones Rápidas
- Exportar teléfonos activos por filtros
- Descargar 100 muestras de errores
- Ver evolución para medir impacto

## Alertas Automáticas
**Umbrales**: Calidad <95%, duplicados >1%, actualización >60 días
**Notificación**: Email/Teams + registro + bloqueo pipeline

## Entrega
- **Frecuencia**: Diaria con publicación analítica
- **Reporte**: CSV/Markdown por `run_id` con KPIs y umbrales

## Stack Tecnológico para Monitoreo

### Implementación Inicial (Sencilla)
**Dashboard**: Power BI conectado directamente a PostgreSQL para reportes empresariales\
**Base de datos**: PostgreSQL con vistas para KPIs y métricas históricas\
**Alertas**: Python + SMTP para emails automáticos cuando se rompen umbrales\
**Tiempo real**: Actualización cada 15-30 minutos via refresh automático de Power BI

### Escalabilidad Futura
Para mayor volumen y tiempo real estricto: Apache Superset (dashboards empresariales open source), Apache Kafka (streaming), entre otras.