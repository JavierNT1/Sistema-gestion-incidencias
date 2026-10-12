
from conexion import obtener_conexion


def obtener_incidencias():
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id, titulo, prioridad FROM incidencias"
            )
            filas = cursor.fetchall()

        resultado = []

        for fila in filas:
            incidencia = {
                "id": fila[0],
                "titulo": fila[1],
                "prioridad": fila[2]
            }
            resultado.append(incidencia)

        return resultado

    finally:
        conexion.close()


def obtener_incidencia_por_id(id: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, titulo, prioridad
                FROM incidencias
                WHERE id = %s
                """,
                (id,)
            )
            fila = cursor.fetchone()

        if fila is None:
            return None

        return {
            "id": fila[0],
            "titulo": fila[1],
            "prioridad": fila[2]
        }

    finally:
        conexion.close()


def crear_incidencia(titulo: str, prioridad: str):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, prioridad)
                VALUES (%s, %s)
                RETURNING id, titulo, prioridad
                """,
                (titulo, prioridad)
            )
            fila = cursor.fetchone()

        conexion.commit()

        return {
            "id": fila[0],
            "titulo": fila[1],
            "prioridad": fila[2]
        }

    finally:
        conexion.close()


def actualizar_incidencia(id: int, titulo: str, prioridad: str):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE incidencias
                SET titulo = %s, prioridad = %s
                WHERE id = %s
                RETURNING id, titulo, prioridad
                """,
                (titulo, prioridad, id)
            )
            fila = cursor.fetchone()

        if fila is not None:
            conexion.commit()
            return {
                "id": fila[0],
                "titulo": fila[1],
                "prioridad": fila[2]
            }

        return None

    finally:
        conexion.close()


def eliminar_incidencia(id: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM incidencias
                WHERE id = %s
                RETURNING id, titulo, prioridad
                """,
                (id,)
            )
            fila = cursor.fetchone()

        if fila is None:
            return None

        conexion.commit()

        return {
            "id": fila[0],
            "titulo": fila[1],
            "prioridad": fila[2]
        }

    finally:
        conexion.close()