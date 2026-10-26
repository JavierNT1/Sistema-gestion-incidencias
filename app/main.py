from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.crud import (
    obtener_incidencias,
    obtener_incidencia_por_id,
    crear_incidencia,
    actualizar_incidencia,
    eliminar_incidencia,
    iniciar_atencion,
    resolver_incidencia
)

from app.schemas import (
    IncidenciaNueva,
    IncidenciaRespuesta,
    Prioridad,
    Estado,
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
def listar_incidencias(prioridad: Prioridad | None = None, estado: Estado | None = None):
    incidencias = obtener_incidencias(
        prioridad.value if prioridad else None
    )

    if estado is not None:
        incidencias = [
            incidencia
            for incidencia in incidencias
            if incidencia["estado"] == estado.value
        ]

    return incidencias


@app.get("/incidencias/{id}", response_model=IncidenciaRespuesta)
def consultar_incidencia(id: int):
    incidencia = obtener_incidencia_por_id(id)

    if incidencia is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    return incidencia


@app.post("/incidencias",response_model=IncidenciaRespuesta,status_code=201)
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


@app.delete("/incidencias/{id}",response_model=IncidenciaRespuesta)
def eliminar_incidencia_endpoint(id: int):
    resultado = eliminar_incidencia(id)

    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    return resultado


@app.post("/incidencias/{id}/iniciar",response_model=IncidenciaRespuesta)
def iniciar_atencion_endpoint(id: int):
    resultado = iniciar_atencion(id)

    if resultado is not None:
        return resultado

    # Si no se pudo iniciar, comprobamos si la incidencia existe.
    incidencia = obtener_incidencia_por_id(id)

    if incidencia is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    raise HTTPException(
        status_code=409,
        detail="No se puede iniciar la atención porque la incidencia no está pendiente"
    )


@app.post("/incidencias/{id}/resolver",response_model=IncidenciaRespuesta)
def resolver_incidencia_endpoint(id: int):
    resultado = resolver_incidencia(id)

    if resultado is not None:
        return resultado

    incidencia = obtener_incidencia_por_id(id)

    if incidencia is None:
        raise HTTPException(
            status_code=404,
            detail="Incidencia no encontrada"
        )

    raise HTTPException(
        status_code=409,
        detail="No se puede resolver la incidencia porque no está en progreso"
    )
