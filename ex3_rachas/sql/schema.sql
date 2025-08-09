DROP TABLE IF EXISTS historia;
CREATE TABLE historia (
    identificacion TEXT NOT NULL,
    corte_mes DATE NOT NULL,
    saldo NUMERIC NOT NULL
);

DROP TABLE IF EXISTS retiros;
CREATE TABLE retiros (
    identificacion TEXT NOT NULL,
    fecha_retiro DATE NOT NULL
);