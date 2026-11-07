-- Solo para la primera inicialización de un volumen PostgreSQL vacío.
-- No contiene datos de demostración ni altera tablas existentes.
BEGIN;

CREATE TABLE public.incidencias (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    prioridad VARCHAR(20) NOT NULL,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descripcion TEXT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    fecha_resolucion TIMESTAMPTZ,
    categoria VARCHAR(50) NOT NULL
);

COMMIT;
