from conexion import obtener_conexion


def obtener_incidencias(prioridad: str | None = None):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            consulta = """
                SELECT id, titulo, categoria, descripcion, prioridad, fecha_creacion, estado, fecha_resolucion
                FROM incidencias
            """
            parametros = ()

            if prioridad is not None:
                consulta += " WHERE prioridad = %s"
                parametros = (prioridad,)

            consulta += """
                ORDER BY
                    CASE
                        WHEN estado = 'Resuelta' THEN 1
                        ELSE 0
                    END,
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
                "categoria": fila[2],
                "descripcion": fila[3],
                "prioridad": fila[4],
                "fecha_creacion": fila[5],
                "estado": fila[6],
                "fecha_resolucion": fila[7],
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
                SELECT id, titulo, categoria, descripcion, prioridad, fecha_creacion, estado, fecha_resolucion
                FROM incidencias
                WHERE id = %s
                """,
                (id,),
            )
            fila = cursor.fetchone()

        if fila is None:
            return None

        return {
            "id": fila[0],
            "titulo": fila[1],
            "categoria": fila[2],
            "descripcion": fila[3],
            "prioridad": fila[4],
            "fecha_creacion": fila[5],
            "estado": fila[6],
            "fecha_resolucion": fila[7],
        }

    finally:
        conexion.close()


def crear_incidencia(titulo: str, categoria: str, descripcion: str, prioridad: str):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, categoria, descripcion, prioridad)
                VALUES (%s, %s, %s, %s)
                RETURNING id, titulo, categoria, descripcion, prioridad, fecha_creacion, estado, fecha_resolucion
                """,
                (titulo, categoria, descripcion, prioridad),
            )
            fila = cursor.fetchone()

        conexion.commit()

        return {
            "id": fila[0],
            "titulo": fila[1],
            "categoria": fila[2],
            "descripcion": fila[3],
            "prioridad": fila[4],
            "fecha_creacion": fila[5],
            "estado": fila[6],
            "fecha_resolucion": fila[7],
        }
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def actualizar_incidencia(
    id: int,
    titulo: str,
    descripcion: str,
    prioridad: str,
):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE incidencias
                SET titulo = %s, descripcion = %s, prioridad = %s
                WHERE id = %s
                RETURNING id, titulo, categoria, descripcion, prioridad, fecha_creacion, estado, fecha_resolucion 
                """,
                (titulo,descripcion, prioridad, id),
            )
            fila = cursor.fetchone()

        if fila is not None:
            conexion.commit()

            return {
                "id": fila[0],
                "titulo": fila[1],
                "categoria": fila[2],                
                "descripcion": fila[3],
                "prioridad": fila[4],
                "fecha_creacion": fila[5],
                "estado": fila[6],
                "fecha_resolucion": fila[7],
            }

        return None
    
    except Exception:
        conexion.rollback()
        raise
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
                RETURNING id, titulo, categoria, descripcion, prioridad, fecha_creacion, estado, fecha_resolucion 
                """,
                (id,),
            )
            fila = cursor.fetchone()

        if fila is None:
            return None

        conexion.commit()

        return {
            "id": fila[0],
            "titulo": fila[1],
            "categoria": fila[2],
            "descripcion": fila[3],
            "prioridad": fila[4],
            "fecha_creacion": fila[5],
            "estado": fila[6],
            "fecha_resolucion": fila[7],
        }
    
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def iniciar_atencion(id: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE incidencias
                SET estado = 'En progreso'
                WHERE id = %s
                  AND estado = 'Pendiente'
                RETURNING
                    id,
                    titulo,
                    categoria,
                    descripcion,
                    prioridad,
                    fecha_creacion,
                    estado,
                    fecha_resolucion
                """,
                (id,),
            )
            fila = cursor.fetchone()

        if fila is None:
            return None

        conexion.commit()

        return {
            "id": fila[0],
            "titulo": fila[1],
            "categoria": fila[2],
            "descripcion": fila[3],
            "prioridad": fila[4],
            "fecha_creacion": fila[5],
            "estado": fila[6],
            "fecha_resolucion": fila[7],
        }
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()



def resolver_incidencia(id: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE incidencias
                SET estado = 'Resuelta',
                    fecha_resolucion = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND estado = 'En progreso'
                RETURNING
                    id,
                    titulo,
                    categoria,
                    descripcion,
                    prioridad,
                    fecha_creacion,
                    estado,
                    fecha_resolucion
                """,
                (id,),
            )
            fila = cursor.fetchone()

        if fila is None:
            return None

        conexion.commit()

        return {
            "id": fila[0],
            "titulo": fila[1],
            "categoria": fila[2],
            "descripcion": fila[3],
            "prioridad": fila[4],
            "fecha_creacion": fila[5],
            "estado": fila[6],
            "fecha_resolucion": fila[7],
        }
    
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
