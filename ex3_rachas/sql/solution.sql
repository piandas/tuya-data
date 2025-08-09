WITH RECURSIVE
params AS (
  SELECT
    date(:fecha_base) AS fecha_base,
    date(:fecha_base, 'start of month', '+1 month', '-1 day') AS fecha_base_eom,
    CAST(:n AS INTEGER) AS n
),

hist_norm AS (
  SELECT
    identificacion,
    date(corte_mes, 'start of month', '+1 month', '-1 day') AS corte_mes,
    CAST(saldo AS NUMERIC) AS saldo
  FROM historia
  WHERE date(corte_mes) <= (SELECT fecha_base FROM params)
),

retiros_norm AS (
  SELECT
    identificacion,
    date(fecha_retiro, 'start of month', '+1 month', '-1 day') AS fecha_retiro
  FROM retiros
),

first_appearance AS (
  SELECT identificacion, MIN(corte_mes) AS first_mes_eom
  FROM hist_norm
  GROUP BY identificacion
),

-- Calendario por cliente: from first_mes_eom → fecha_base_eom (siempre fin de mes)
calendario AS (
  SELECT identificacion, first_mes_eom AS corte_mes FROM first_appearance
  UNION ALL
  SELECT identificacion, date(corte_mes, 'start of month', '+2 month', '-1 day')
  FROM calendario
  WHERE corte_mes < (SELECT fecha_base_eom FROM params)
),

-- Mezcla calendario + historia + retiros; corta por retiro; ausencia -> saldo=0 (N0)
base AS (
  SELECT
    cal.identificacion,
    cal.corte_mes,
    CASE WHEN hn.saldo IS NULL OR hn.saldo < 0 THEN 0 ELSE hn.saldo END AS saldo
  FROM calendario cal
  LEFT JOIN hist_norm hn
    ON hn.identificacion = cal.identificacion AND hn.corte_mes = cal.corte_mes
  LEFT JOIN retiros_norm rn
    ON rn.identificacion = cal.identificacion
  WHERE rn.fecha_retiro IS NULL OR cal.corte_mes <= rn.fecha_retiro
),

-- Nivel
niveles AS (
  SELECT
    identificacion,
    corte_mes,
    CASE
      WHEN saldo < 300000  THEN 'N0'
      WHEN saldo < 1000000 THEN 'N1'
      WHEN saldo < 3000000 THEN 'N2'
      WHEN saldo < 5000000 THEN 'N3'
      ELSE 'N4'
    END AS nivel
  FROM base
),

-- Gaps & islands por (cliente, nivel)
grupos AS (
  SELECT
    identificacion,
    corte_mes,
    nivel,
    (CAST(strftime('%Y', corte_mes) AS INTEGER) * 12 + CAST(strftime('%m', corte_mes) AS INTEGER))
    - ROW_NUMBER() OVER (PARTITION BY identificacion, nivel ORDER BY corte_mes) AS grp
  FROM niveles
),

-- Rachas y filtro por n/fecha_base
rachas AS (
  SELECT
    identificacion,
    nivel,
    COUNT(*) AS racha,
    MAX(corte_mes) AS fecha_fin
  FROM grupos
  GROUP BY identificacion, nivel, grp
),

filtradas AS (
  SELECT r.*
  FROM rachas r
  JOIN params p
  WHERE r.racha >= p.n AND r.fecha_fin <= p.fecha_base
),

ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY identificacion ORDER BY racha DESC, fecha_fin DESC) AS rn
  FROM filtradas
)
SELECT identificacion, racha, fecha_fin, nivel
FROM ranked
WHERE rn = 1
ORDER BY identificacion;