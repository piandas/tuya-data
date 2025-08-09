-- Tests automatizados para CI/CD

-- Cliente con racha continua (3 meses N1)
INSERT INTO historia (identificacion, corte_mes, saldo) VALUES 
('A1', '2023-01-31', 500000),
('A1', '2023-02-28', 600000),
('A1', '2023-03-31', 700000),
('A1', '2023-04-30', 100000);

-- Cliente con huecos (ausencias = N0)
INSERT INTO historia (identificacion, corte_mes, saldo) VALUES 
('B1', '2023-01-31', 400000),
('B1', '2023-03-31', 500000),
('B1', '2023-04-30', 600000);

-- Cliente con retiro
INSERT INTO historia (identificacion, corte_mes, saldo) VALUES 
('C1', '2023-01-31', 800000),
('C1', '2023-02-28', 900000),
('C1', '2023-03-31', 750000);
INSERT INTO retiros (identificacion, fecha_retiro) VALUES ('C1', '2023-03-15');

-- Múltiples rachas diferentes
INSERT INTO historia (identificacion, corte_mes, saldo) VALUES 
('D1', '2023-01-31', 1500000),
('D1', '2023-02-28', 1600000),
('D1', '2023-03-31', 400000),
('D1', '2023-04-30', 450000),
('D1', '2023-05-31', 500000);

-- Saldos negativos → N0
INSERT INTO historia (identificacion, corte_mes, saldo) VALUES 
('E1', '2023-01-31', -50000),
('E1', '2023-02-28', 0),
('E1', '2023-03-31', 100000);