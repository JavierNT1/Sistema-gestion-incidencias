from enum import Enum
from pydantic import BaseModel, field_validator
from datetime import datetime

class Prioridad(str, Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"

#Lo que el cliente nos envía.

class IncidenciaNueva(BaseModel):
    titulo: str
    descripcion: str
    prioridad: Prioridad

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("El título no puede estar vacío")

        if len(valor) > 200:
            raise ValueError(
                "El título no puede superar los 200 caracteres"
            )

        return valor

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("La descripción no puede estar vacía")

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
    descripcion: str 
    prioridad: Prioridad
    fecha_creacion: datetime
