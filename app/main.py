from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

#Lo que el cliente nos envía.
class IncidenciaNueva(BaseModel):
    titulo: str
    prioridad: str

#Lo que nuestra API devuelve.
class IncidenciaRespuesta(BaseModel):
    id: int
    titulo: str
    prioridad: str

@app.get("/")
def inicio():
    return {"mensaje": "Sistema de Gestión de Incidencias"}

incidencias = [
    {
        "id": 1,
        "titulo": "No puedo acceder al sistema",
        "prioridad": "Alta"
    },
    {
        "id": 2,
        "titulo": "Impresora no funciona",
        "prioridad": "Media"
    }
]

@app.get("/incidencias",  response_model=list[IncidenciaRespuesta])
def inicio1():
    return incidencias

@app.get("/incidencias/{id}",  response_model=IncidenciaRespuesta)
def inicio2(id: int):
    for num in incidencias:
        if num["id"] == id:
            return num
    raise HTTPException(status_code=404, detail="Incidencia no encontrada")

@app.post("/incidencias", response_model=IncidenciaRespuesta,status_code=201)
def crear_incidencia(incidencia: IncidenciaNueva):
    nuevo_id = len(incidencias) + 1
    nueva = {
        "id": nuevo_id,
        "titulo": incidencia.titulo,
        "prioridad": incidencia.prioridad
    }

    incidencias.append(nueva)
    return nueva

@app.put("/incidencias/{id}", response_model=IncidenciaRespuesta)
def actualizar_incidencia(incidencia: IncidenciaNueva, id: int):
    for num in incidencias:
        if num["id"] == id:
            num["titulo"] = incidencia.titulo
            num["prioridad"] = incidencia.prioridad
            return num

    raise HTTPException(status_code=404, detail="Incidencia no encontrada")

@app.delete("/incidencias/{id}")
def eliminar_incidencia( id: int):
    for num in incidencias:
        if num["id"] == id:
            incidencias.remove(num)
            return {"mensaje": "Incidencia eliminada"}
    raise HTTPException(status_code=404, detail="Incidencia no encontrada")



