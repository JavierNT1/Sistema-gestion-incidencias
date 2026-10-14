
from conexion import obtener_conexion


def obtener_incidencias(prioridad: str | None = None):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            consulta = """
                SELECT id, titulo, prioridad, fecha_creacion
                FROM incidencias
            """
            parametros = ()

            if prioridad is not None:
                consulta += " WHERE prioridad = %s"
                parametros = (prioridad,)

            consulta += """
                ORDER BY
                    CASE prioridad
                        WHEN 'Alta' THEN 1
                        WHEN 'Media' THEN 2
                        WHEN 'Baja' THEN 3
                        ELSE 4
                    END,
                    fecha_creacion ASC
            """

            cursor.execute(consulta, parametros)
            filas = cursor.fetchall()

        resultado = []

        for fila in filas:
            incidencia = {
                "id": fila[0],
                "titulo": fila[1],
                "prioridad": fila[2],
                "fecha_creacion": fila[3]
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
                SELECT id, titulo, prioridad, fecha_creacion
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
            "prioridad": fila[2],
            "fecha_creacion": fila[3]
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
                RETURNING id, titulo, prioridad, fecha_creacion
                """,
                (titulo, prioridad)
            )
            fila = cursor.fetchone()

        conexion.commit()

        return {
            "id": fila[0],
            "titulo": fila[1],
            "prioridad": fila[2],
            "fecha_creacion": fila[3]
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
                RETURNING id, titulo, prioridad, fecha_creacion
                """,
                (titulo, prioridad, id)
            )
            fila = cursor.fetchone()

        if fila is not None:
            conexion.commit()
            return {
                "id": fila[0],
                "titulo": fila[1],
                "prioridad": fila[2],
                "fecha_creacion": fila[3]
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
                RETURNING id, titulo, prioridad, fecha_creacion
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
            "prioridad": fila[2],
            "fecha_creacion": fila[3]
        }

    finally:
        conexion.close()
