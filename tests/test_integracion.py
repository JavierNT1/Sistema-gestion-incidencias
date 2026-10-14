from unittest.mock import patch
from datetime import datetime, timezone
from conexion import obtener_conexion_pruebas
from app import crud

def test_conexion_postgresql():
    conexion = obtener_conexion_pruebas()

    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT 1")
            resultado = cursor.fetchone()

        assert resultado == (1,)

    finally:
        conexion.close()


def test_insertar_incidencia():
    conexion = obtener_conexion_pruebas()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, prioridad)
                VALUES (%s, %s)
                RETURNING id, titulo, prioridad, fecha_creacion
                """,
                ("Prueba automatizada", "Alta")
            )

            incidencia = cursor.fetchone()

            assert incidencia is not None
            assert incidencia[1] == "Prueba automatizada"
            assert incidencia[2] == "Alta"
            assert incidencia[3] is not None

    finally:
        conexion.rollback()
        conexion.close()


def test_consultar_incidencia_insertada():
    conexion = obtener_conexion_pruebas()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, prioridad)
                VALUES (%s, %s)
                RETURNING id
                """,
                ("Incidencia para consultar", "Media")
            )

            id_creado = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT id, titulo, prioridad, fecha_creacion
                FROM incidencias
                WHERE id = %s
                """,
                (id_creado,)
            )

            incidencia = cursor.fetchone()

        assert incidencia is not None
        assert incidencia[0] == id_creado
        assert incidencia[1] == "Incidencia para consultar"
        assert incidencia[2] == "Media"
        assert incidencia[3] is not None

    finally:
        conexion.rollback()
        conexion.close()


def test_actualizar_incidencia_postgresql():
    conexion = obtener_conexion_pruebas()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, prioridad)
                VALUES (%s, %s)
                RETURNING id, fecha_creacion
                """,
                ("Título original", "Baja")
            )

            id_creado, fecha_original = cursor.fetchone()

            cursor.execute(
                """
                UPDATE incidencias
                SET titulo = %s, prioridad = %s
                WHERE id = %s
                RETURNING id, titulo, prioridad, fecha_creacion
                """,
                ("Título actualizado", "Alta", id_creado)
            )

            incidencia = cursor.fetchone()

        assert incidencia is not None
        assert incidencia[0] == id_creado
        assert incidencia[1] == "Título actualizado"
        assert incidencia[2] == "Alta"
        assert incidencia[3] == fecha_original

    finally:
        conexion.rollback()
        conexion.close()


def test_eliminar_incidencia_postgresql():
    conexion = obtener_conexion_pruebas()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, prioridad)
                VALUES (%s, %s)
                RETURNING id
                """,
                ("Incidencia para eliminar", "Media")
            )

            id_creado = cursor.fetchone()[0]

            cursor.execute(
                """
                DELETE FROM incidencias
                WHERE id = %s
                RETURNING id
                """,
                (id_creado,)
            )

            eliminada = cursor.fetchone()

            assert eliminada == (id_creado,)

            cursor.execute(
                "SELECT id FROM incidencias WHERE id = %s",
                (id_creado,)
            )

            encontrada = cursor.fetchone()

        assert encontrada is None

    finally:
        conexion.rollback()
        conexion.close()


def test_crud_crear_incidencia():
    with patch(
        "app.crud.obtener_conexion",
        obtener_conexion_pruebas
    ):
        incidencia = crud.crear_incidencia(
            "Prueba desde CRUD",
            "Alta"
        )

        try:
            assert incidencia["id"] is not None
            assert incidencia["titulo"] == "Prueba desde CRUD"
            assert incidencia["prioridad"] == "Alta"
            assert incidencia["fecha_creacion"] is not None

            encontrada = crud.obtener_incidencia_por_id(
                incidencia["id"]
            )

            assert encontrada == incidencia

        finally:
            crud.eliminar_incidencia(incidencia["id"])

        assert crud.obtener_incidencia_por_id(
            incidencia["id"]
        ) is None


def test_crud_listar_incidencias():
    with patch(
        "app.crud.obtener_conexion",
        obtener_conexion_pruebas
    ):
        incidencia = crud.crear_incidencia(
            "Incidencia para listar",
            "Media"
        )

        try:
            incidencias = crud.obtener_incidencias()

            encontrada = next(
                (
                    item for item in incidencias
                    if item["id"] == incidencia["id"]
                ),
                None
            )

            assert encontrada == incidencia
            assert encontrada["fecha_creacion"] is not None

        finally:
            crud.eliminar_incidencia(incidencia["id"])


def test_crud_actualizar_incidencia():
    with patch(
        "app.crud.obtener_conexion",
        obtener_conexion_pruebas
    ):
        incidencia = crud.crear_incidencia(
            "Título original",
            "Baja"
        )

        try:
            actualizada = crud.actualizar_incidencia(
                incidencia["id"],
                "Título actualizado",
                "Alta"
            )

            assert actualizada["id"] == incidencia["id"]
            assert actualizada["titulo"] == "Título actualizado"
            assert actualizada["prioridad"] == "Alta"
            assert actualizada["fecha_creacion"] == incidencia["fecha_creacion"]

        finally:
            crud.eliminar_incidencia(incidencia["id"])


def test_filtrar_y_ordenar_incidencias_postgresql():
    ids = []

    with patch(
        "app.crud.obtener_conexion",
        obtener_conexion_pruebas
    ):
        conexion = obtener_conexion_pruebas()

        try:
            # 1. Insertar incidencias con fechas controladas.
            with conexion.cursor() as cursor:
                datos = [
                    (
                        "Prueba orden Baja",
                        "Baja",
                        datetime(2026, 10, 10, tzinfo=timezone.utc)
                    ),
                    (
                        "Prueba orden Alta",
                        "Alta",
                        datetime(2026, 10, 12, tzinfo=timezone.utc)
                    ),
                    (
                        "Prueba orden Media",
                        "Media",
                        datetime(2026, 10, 11, tzinfo=timezone.utc)
                    ),
                ]

                for titulo, prioridad, fecha in datos:
                    cursor.execute(
                        """
                        INSERT INTO incidencias
                            (titulo, prioridad, fecha_creacion)
                        VALUES (%s, %s, %s)
                        RETURNING id
                        """,
                        (titulo, prioridad, fecha)
                    )
                    ids.append(cursor.fetchone()[0])

            conexion.commit()

            # 2. Comprobar el orden por prioridad.
            todas = crud.obtener_incidencias()
            pruebas = [i for i in todas if i["id"] in ids]

            assert [i["prioridad"] for i in pruebas] == [
                "Alta", "Media", "Baja"
            ]

            # 3. Comprobar el filtro por prioridad.
            altas = crud.obtener_incidencias("Alta")
            altas_prueba = [i for i in altas if i["id"] in ids]

            assert len(altas_prueba) == 1
            assert altas_prueba[0]["titulo"] == "Prueba orden Alta"

        finally:
            try:
                with conexion.cursor() as cursor:
                    if ids:
                        cursor.execute(
                            "DELETE FROM incidencias WHERE id = ANY(%s)",
                            (ids,)
                        )
                conexion.commit()
            finally:
                conexion.close()