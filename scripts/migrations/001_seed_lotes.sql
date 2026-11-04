-- Aplicación manual y exclusiva en desarrollo. No se ejecuta desde el generador.
BEGIN;
DO $$ BEGIN
    IF current_database() <> 'incidencias_db' THEN
        RAISE EXCEPTION 'Esta migración solo admite incidencias_db';
    END IF;
END $$;
CREATE TABLE public.seed_lotes (
    lote_id text PRIMARY KEY,
    mes varchar(7) NOT NULL UNIQUE,
    cantidad integer NOT NULL CHECK (cantidad > 0),
    semilla bigint NOT NULL,
    version integer NOT NULL,
    referencia timestamptz NOT NULL
);
CREATE TABLE public.seed_registros (
    lote_id text NOT NULL REFERENCES public.seed_lotes(lote_id),
    clave text NOT NULL,
    incidencia_id integer NOT NULL UNIQUE,
    PRIMARY KEY (lote_id, clave)
);
-- Sin FK a incidencias: eliminar una incidencia desde la aplicación no borra
-- la constancia del lote ni impide el CRUD habitual.
COMMIT;
