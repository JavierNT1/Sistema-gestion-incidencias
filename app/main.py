from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from conexion import obtener_conexion
from enum import Enum

app = FastAPI()

class Prioridad(str, Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"

#Lo que el cliente nos envía.
class IncidenciaNueva(BaseModel):
    titulo: str
    prioridad: Prioridad

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("El título no puede estar vacío")

        if len(valor) > 200:
            raise ValueError("El título no puede superar los 200 caracteres")

        return valor

    @field_validator("prioridad", mode="before")
    @classmethod
    def normalizar_prioridad(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip().capitalize()
        return valor

#Lo que nuestra API devuelve.
class IncidenciaRespuesta(BaseModel):
    id: int
    titulo: str
    prioridad: str

@app.get("/")
def inicio():
    return {"mensaje": "Sistema de Gestión de Incidencias"}


@app.get("/incidencias", response_model=list[IncidenciaRespuesta])
def inicio1():
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


@app.get("/incidencias/{id}", response_model=IncidenciaRespuesta)
def inicio2(id: int):
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
    finally:
        conexion.close()

    if fila is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    return {
        "id": fila[0],
        "titulo": fila[1],
        "prioridad": fila[2]
    }


@app.post("/incidencias", response_model=IncidenciaRespuesta, status_code=201)
def crear_incidencia(incidencia: IncidenciaNueva):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidencias (titulo, prioridad)
                VALUES (%s, %s)
                RETURNING id, titulo, prioridad
                """,
                (incidencia.titulo, incidencia.prioridad)
            )
            fila = cursor.fetchone()

        conexion.commit()

    finally:
        conexion.close()

    return {
        "id": fila[0],
        "titulo": fila[1],
        "prioridad": fila[2]
    }


@app.put("/incidencias/{id}", response_model=IncidenciaRespuesta)
def actualizar_incidencia(incidencia: IncidenciaNueva, id: int):
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
                (incidencia.titulo, incidencia.prioridad, id)
            )
            fila = cursor.fetchone()

        if fila is not None:
            conexion.commit()

    finally:
        conexion.close()

    if fila is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    return {
        "id": fila[0],
        "titulo": fila[1],
        "prioridad": fila[2]
    }



@app.delete("/incidencias/{id}")
def eliminar_incidencia(id: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM incidencias
                WHERE id = %s
                RETURNING id
                """,
                (id,)
            )
            fila = cursor.fetchone()

        if fila is not None:
            conexion.commit()

    finally:
        conexion.close()

    if fila is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    return {
        "mensaje": "Incidencia eliminada",
        "id": fila[0]
    }
