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
                INSERT INTO incidencias (titulo, descripcion, prioridad)
                VALUES (%s, %s, %s)
                RETURNING id, titulo, descripcion, prioridad, fecha_creacion
                """,
                ("Prueba automatizada","Descripción de prueba", "Alta")
            )

            incidencia = cursor.fetchone()

            assert incidencia is not None
            assert incidencia[1] == "Prueba automatizada"
            assert incidencia[2] == "Descripción de prueba"
            assert incidencia[3] == "Alta"
            assert incidencia[4] is not None

    finally:
        conexion.rollback()
        conexion.close()


def test_consultar_incidencia_insertada():
    conexion = obtener_conexion_pruebas()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, descripcion, prioridad)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                ("Incidencia para consultar", "Descripción para consultar","Media")
            )

            id_creado = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT id, titulo, descripcion,prioridad, fecha_creacion
                FROM incidencias
                WHERE id = %s
                """,
                (id_creado,)
            )

            incidencia = cursor.fetchone()

        assert incidencia is not None
        assert incidencia[0] == id_creado
        assert incidencia[1] == "Incidencia para consultar"
        assert incidencia[2] == "Descripción para consultar"
        assert incidencia[3] == "Media"
        assert incidencia[4] is not None

    finally:
        conexion.rollback()
        conexion.close()


def test_actualizar_incidencia_postgresql():
    conexion = obtener_conexion_pruebas()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, descripcion,prioridad)
                VALUES (%s,%s,%s)
                RETURNING id, fecha_creacion
                """,
                ("Título original", "Descripción original","Baja")
            )

            id_creado, fecha_original = cursor.fetchone()

            cursor.execute(
                """
                UPDATE incidencias
                SET titulo = %s,  descripcion = %s,prioridad = %s
                WHERE id = %s
                RETURNING id, titulo, descripcion,prioridad, fecha_creacion
                """,
                ("Título actualizado", "Descripción actualizada","Alta", id_creado)
            )

            incidencia = cursor.fetchone()

        assert incidencia is not None
        assert incidencia[0] == id_creado
        assert incidencia[1] == "Título actualizado"
        assert incidencia[2] == "Descripción actualizada"
        assert incidencia[3] == "Alta"
        assert incidencia[4] == fecha_original

    finally:
        conexion.rollback()
        conexion.close()


def test_eliminar_incidencia_postgresql():
    conexion = obtener_conexion_pruebas()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, descripcion,prioridad)
                VALUES (%s,%s,%s)
                RETURNING id
                """,
                ("Incidencia para eliminar", "Descripción de prueba","Media")
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
            "Descripción de prueba",
            "Alta"
        )

        try:
            assert incidencia["id"] is not None
            assert incidencia["titulo"] == "Prueba desde CRUD"
            assert incidencia["descripcion"] == "Descripción de prueba"
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
            "Descripción para listar",
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
            assert encontrada["descripcion"] == "Descripción para listar"
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
            "Descripción original",
            "Baja"
        )

        try:
            actualizada = crud.actualizar_incidencia(
                incidencia["id"],
                "Título actualizado",
                "Descripción actualizada",
                "Alta"
            )

            assert actualizada["id"] == incidencia["id"]
            assert actualizada["titulo"] == "Título actualizado"
            assert actualizada["descripcion"] == "Descripción actualizada"
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
                        "Prueba pendiente Baja",
                        "Incidencia pendiente de prioridad baja",
                        "Baja",
                        datetime(2026, 10, 10, tzinfo=timezone.utc),
                        "Pendiente",
                    ),
                    (
                        "Prueba pendiente Alta antigua",
                        "Incidencia pendiente de prioridad alta",
                        "Alta",
                        datetime(2026, 10, 10, tzinfo=timezone.utc),
                        "Pendiente",
                    ),
                    (
                        "Prueba pendiente Alta reciente",
                        "Incidencia pendiente de prioridad alta",
                        "Alta",
                        datetime(2026, 10, 12, tzinfo=timezone.utc),
                        "Pendiente",
                    ),
                    (
                        "Prueba progreso Alta",
                        "Incidencia en progreso",
                        "Alta",
                        datetime(2026, 10, 9, tzinfo=timezone.utc),
                        "En progreso",
                    ),
                    (
                        "Prueba resuelta Alta",
                        "Incidencia resuelta",
                        "Alta",
                        datetime(2026, 10, 8, tzinfo=timezone.utc),
                        "Resuelta",
                    ),
                ]
                for titulo, descripcion, prioridad, fecha, estado in datos:
                    cursor.execute(
                        """
                        INSERT INTO incidencias
                            (titulo, descripcion, prioridad, fecha_creacion, estado)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (titulo, descripcion, prioridad, fecha, estado)
                    )
                    ids.append(cursor.fetchone()[0])

            conexion.commit()


            # 2. Comprobar el orden por estado, prioridad y fecha.
            todas = crud.obtener_incidencias()
            pruebas = [i for i in todas if i["id"] in ids]

            assert [i["titulo"] for i in pruebas] == [
                "Prueba progreso Alta",
                "Prueba pendiente Alta antigua",
                "Prueba pendiente Alta reciente",
                "Prueba pendiente Baja",
                "Prueba resuelta Alta",
            ]

            # 3. Comprobar el filtro por prioridad.
            altas = crud.obtener_incidencias("Alta")
            altas_prueba = [i for i in altas if i["id"] in ids]

            assert len(altas_prueba) == 4

            assert {i["titulo"] for i in altas_prueba} == {
                "Prueba progreso Alta",
                "Prueba pendiente Alta antigua",
                "Prueba pendiente Alta reciente",
                "Prueba resuelta Alta",
            }

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

def test_ciclo_completo_y_transiciones_no_permitidas():
    with patch("app.crud.obtener_conexion", obtener_conexion_pruebas):
        incidencia = crud.crear_incidencia(
            titulo="Prueba ciclo de vida",
            descripcion="Comprobar transiciones de estado",
            prioridad="Alta",
        )

        id_incidencia = incidencia["id"]

        try:
            # La incidencia comienza como Pendiente.
            assert incidencia["estado"] == "Pendiente"

            # No se puede resolver directamente desde Pendiente.
            assert crud.resolver_incidencia(id_incidencia) is None

            # Se puede iniciar la atención.
            en_progreso = crud.iniciar_atencion(id_incidencia)
            assert en_progreso["estado"] == "En progreso"

            # No se puede iniciar una segunda vez.
            assert crud.iniciar_atencion(id_incidencia) is None

            # Se puede resolver desde En progreso.
            resuelta = crud.resolver_incidencia(id_incidencia)
            assert resuelta["estado"] == "Resuelta"
            assert resuelta["fecha_resolucion"] is not None

            # No se puede reiniciar ni resolver de nuevo.
            assert crud.iniciar_atencion(id_incidencia) is None
            assert crud.resolver_incidencia(id_incidencia) is None

        finally:
            crud.eliminar_incidencia(id_incidencia)