from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.crud import (
    obtener_incidencias,
    obtener_incidencia_por_id,
    crear_incidencia,
    actualizar_incidencia,
    eliminar_incidencia,
)

from app.schemas import (
    IncidenciaNueva,
    IncidenciaRespuesta,
    Prioridad,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def inicio():
    return {"mensaje": "Sistema de Gestión de Incidencias"}


@app.get("/incidencias", response_model=list[IncidenciaRespuesta])
def listar_incidencias(prioridad: Prioridad | None = None):
    return obtener_incidencias(
        prioridad.value if prioridad else None
    )


@app.get("/incidencias/{id}", response_model=IncidenciaRespuesta)
def consultar_incidencia(id: int):
    incidencia = obtener_incidencia_por_id(id)

    if incidencia is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    return incidencia


@app.post(
    "/incidencias",
    response_model=IncidenciaRespuesta,
    status_code=201
)
def crear_incidencia_endpoint(incidencia: IncidenciaNueva):
    return crear_incidencia(
        incidencia.titulo,
        incidencia.descripcion,
        incidencia.prioridad.value
    )


@app.put("/incidencias/{id}", response_model=IncidenciaRespuesta)
def actualizar_incidencia_endpoint(
    id: int,
    incidencia: IncidenciaNueva
):
    resultado = actualizar_incidencia(
        id,
        incidencia.titulo,
        incidencia.descripcion,
        incidencia.prioridad.value
    )

    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    return resultado


@app.delete(
    "/incidencias/{id}",
    response_model=IncidenciaRespuesta
)
def eliminar_incidencia_endpoint(id: int):
    resultado = eliminar_incidencia(id)

    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    return resultado