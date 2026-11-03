import csv
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from fastapi.responses import StreamingResponse
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
    Categoria,
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
def listar_incidencias(
    prioridad: Prioridad | None = None,
    estado: Estado | None = None,
    categoria: Categoria | None = None,
    titulo: str | None = None,
):
    incidencias = obtener_incidencias(
        prioridad.value if prioridad else None
    )

    if estado is not None:
        incidencias = [
            incidencia
            for incidencia in incidencias
            if incidencia["estado"] == estado.value
        ]

    if categoria is not None:
        incidencias = [
            incidencia
            for incidencia in incidencias
            if incidencia["categoria"] == categoria.value
        ]

    if titulo is not None and titulo.strip():
        texto_buscado = titulo.strip().casefold()

        incidencias = [
            incidencia
            for incidencia in incidencias
            if texto_buscado in incidencia["titulo"].casefold()
        ]

    return incidencias

@app.get("/incidencias/exportar/csv")
def exportar_incidencias_csv(
    prioridad: Prioridad | None = None,
    estado: Estado | None = None,
    categoria: Categoria | None = None,
    titulo: str | None = None,
):
    incidencias = listar_incidencias(
        prioridad=prioridad,
        estado=estado,
        categoria=categoria,
        titulo=titulo,
    )

    archivo = io.StringIO(newline="")

    columnas = [
        "id",
        "titulo",
        "categoria",
        "descripcion",
        "prioridad",
        "estado",
        "fecha_creacion",
        "fecha_resolucion",
    ]

    escritor = csv.DictWriter(
        archivo,
        fieldnames=columnas,
        extrasaction="ignore",
    )

    escritor.writeheader()

    for incidencia in incidencias:
        fila = {
            columna: incidencia.get(columna)
            for columna in columnas
        }

        for columna in ("titulo", "categoria", "descripcion", "prioridad", "estado"):
            valor = fila[columna]
            if isinstance(valor, str) and valor.lstrip().startswith(
                ("=", "+", "-", "@", "\t", "\r", "\n")
            ):
                fila[columna] = "'" + valor

        escritor.writerow({
            clave: "" if valor is None else valor
            for clave, valor in fila.items()
        })

    contenido = archivo.getvalue()
    archivo.close()

    return StreamingResponse(
        iter(["\ufeff", contenido]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="incidencias.csv"'
        },
    )


@app.get("/incidencias/exportar/excel")
def exportar_incidencias_excel(
    prioridad: Prioridad | None = None,
    estado: Estado | None = None,
    categoria: Categoria | None = None,
    titulo: str | None = None,
):
    incidencias = listar_incidencias(
        prioridad=prioridad,
        estado=estado,
        categoria=categoria,
        titulo=titulo,
    )

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Incidencias"

    columnas = [
        ("ID", "id"),
        ("Título", "titulo"),
        ("Categoría", "categoria"),
        ("Descripción", "descripcion"),
        ("Prioridad", "prioridad"),
        ("Estado", "estado"),
        ("Fecha de creación", "fecha_creacion"),
        ("Fecha de resolución", "fecha_resolucion"),
    ]

    hoja.append([titulo for titulo, _ in columnas])

    for celda in hoja[1]:
        celda.font = Font(color="FFFFFF", bold=True)
        celda.fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78",
        )
        celda.alignment = Alignment(horizontal="center")

    for incidencia in incidencias:
        fila = []

        for _, campo in columnas:
            valor = incidencia.get(campo)

            # Evitar que el contenido de usuarios se interprete
            # como una fórmula de Excel.
            if isinstance(valor, str) and valor.startswith("="):
                valor = "'" + valor

            # Excel no admite fechas con zona horaria.
            if hasattr(valor, "tzinfo") and valor.tzinfo is not None:
                valor = valor.replace(tzinfo=None)

            fila.append(valor)

        hoja.append(fila)

    anchos = [10, 35, 30, 55, 16, 18, 24, 24]

    for indice, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[
            hoja.cell(row=1, column=indice).column_letter
        ].width = ancho

    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = hoja.dimensions

    archivo = io.BytesIO()
    libro.save(archivo)
    archivo.seek(0)

    return StreamingResponse(
        archivo,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": 'attachment; filename="incidencias.xlsx"'
        },
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


@app.post("/incidencias",response_model=IncidenciaRespuesta,status_code=201)
def crear_incidencia_endpoint(incidencia: IncidenciaNueva):
    return crear_incidencia(
        incidencia.titulo,
        incidencia.categoria.value,
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
