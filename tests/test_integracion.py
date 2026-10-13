from unittest.mock import patch

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
                RETURNING id, titulo, prioridad
                """,
                ("Prueba automatizada", "Alta")
            )

            incidencia = cursor.fetchone()

            assert incidencia is not None
            assert incidencia[1] == "Prueba automatizada"
            assert incidencia[2] == "Alta"

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
                SELECT id, titulo, prioridad
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
                RETURNING id
                """,
                ("Título original", "Baja")
            )

            id_creado = cursor.fetchone()[0]

            cursor.execute(
                """
                UPDATE incidencias
                SET titulo = %s, prioridad = %s
                WHERE id = %s
                RETURNING id, titulo, prioridad
                """,
                ("Título actualizado", "Alta", id_creado)
            )

            incidencia = cursor.fetchone()

        assert incidencia is not None
        assert incidencia[0] == id_creado
        assert incidencia[1] == "Título actualizado"
        assert incidencia[2] == "Alta"

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

            assert actualizada == {
                "id": incidencia["id"],
                "titulo": "Título actualizado",
                "prioridad": "Alta"
            }

        finally:
            crud.eliminar_incidencia(incidencia["id"])