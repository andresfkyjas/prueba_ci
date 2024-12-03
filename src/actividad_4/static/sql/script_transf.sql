CREATE TABLE IF NOT EXISTS {}{}
    (
        id SERIAL PRIMARY KEY,
        fecha DATE NOT NULL,
        apertura DECIMAL(10, 2),
        alto DECIMAL(10, 2) NOT NULL,
        bajo DECIMAL(10, 2) NOT NULL,
        cierre DECIMAL(10, 2) NOT NULL,
        cierre_ajustado DECIMAL(10, 2) NOT NULL,
        volumen DECIMAL(10, 2) NOT NULL,
        f_creacion TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        f_update TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
    );