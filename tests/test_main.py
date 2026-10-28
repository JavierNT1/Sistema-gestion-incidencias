from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

INCIDENCIA_PENDIENTE = {
    "id": 1,
    "titulo": "Error de conexión",
    "descripcion": "El sistema no responde",
    "prioridad": "Alta",
    "fecha_creacion": "2026-10-10T12:00:00Z",
    "estado": "Pendiente",
    "fecha_resolucion": None,
}

INCIDENCIA_EN_PROGRESO = {
    **INCIDENCIA_PENDIENTE,
    "estado": "En progreso",
}

INCIDENCIA_RESUELTA = {
    **INCIDENCIA_PENDIENTE,
    "estado": "Resuelta",
    "fecha_resolucion": "2026-10-19T13:25:04.949889Z",
}


def test_inicio():
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Sistema de Gestión de Incidencias"
    }

def test_rechazar_prioridad_invalida():
    respuesta = client.post(
        "/incidencias",
        json={
            "titulo": "Prueba de validación",
            "descripcion": "Descripción de prueba",
            "prioridad": "Urgente"
        }
    )

    assert respuesta.status_code == 422

def test_rechazar_titulo_vacio():
    respuesta = client.post(
        "/incidencias",
        json={
            "titulo": "   ",
            "descripcion": "Descripción de prueba",
            "prioridad": "Alta"
        }
    )

    assert respuesta.status_code == 422

def test_rechazar_descripcion_vacia():
    respuesta = client.post(
        "/incidencias",
        json={
            "titulo": "Prueba de validación",
            "descripcion": "   ",
            "prioridad": "Alta"
        }
    )

    assert respuesta.status_code == 422

def test_crear_incidencia():
    incidencia_falsa = {
        **INCIDENCIA_PENDIENTE,
        "id": 100,
        "titulo": "Error en el sistema",
    }

    with patch(
        "app.main.crear_incidencia",
        return_value=incidencia_falsa
    ) as crear_mock:
        respuesta = client.post(
            "/incidencias",
            json={
                "titulo": "Error en el sistema",
                "descripcion": "El sistema no responde",
                "prioridad": "Alta"
            }
        )

    assert respuesta.status_code == 201
    assert respuesta.json() == incidencia_falsa
    crear_mock.assert_called_once_with(
        "Error en el sistema",
        "El sistema no responde",
        "Alta"
    )

def test_listar_incidencias():
    incidencias_falsas = [
        {
            **INCIDENCIA_PENDIENTE,
            "id": 1,
            "titulo": "Error de conexión",
        },
        {
            **INCIDENCIA_PENDIENTE,
            "id": 2,
            "titulo": "Problema de impresión",
            "prioridad": "Media",
        },
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias_falsas
    ) as obtener_mock:
        respuesta = client.get("/incidencias")

    assert respuesta.status_code == 200
    assert respuesta.json() == incidencias_falsas
    obtener_mock.assert_called_once_with(None)


def test_incidencia_no_encontrada():
    with patch(
        "app.main.obtener_incidencia_por_id",
        return_value=None
    ):
        respuesta = client.get("/incidencias/9999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "Incidencia no encontrada"
    }

def test_actualizar_incidencia():
    incidencia_actualizada = {
        **INCIDENCIA_PENDIENTE,
        "titulo": "Error corregido",
        "prioridad": "Media",
    }

    with patch(
        "app.main.actualizar_incidencia",
        return_value=incidencia_actualizada
    ) as actualizar_mock:
        respuesta = client.put(
            "/incidencias/1",
            json={
                "titulo": "Error corregido",
                "descripcion": "El sistema no responde",
                "prioridad": "Media"
            }
        )

    assert respuesta.status_code == 200
    assert respuesta.json() == incidencia_actualizada
    actualizar_mock.assert_called_once_with(
        1,
        "Error corregido",
        "El sistema no responde",
        "Media"
    )

def test_rechazar_descripcion_vacia_al_actualizar():
    with patch(
        "app.main.actualizar_incidencia"
    ) as actualizar_mock:
        respuesta = client.put(
            "/incidencias/1",
            json={
                "titulo": "Título válido",
                "descripcion": "   ",
                "prioridad": "Alta"
            }
        )

    assert respuesta.status_code == 422
    actualizar_mock.assert_not_called()


def test_eliminar_incidencia():
    incidencia_eliminada = {
        **INCIDENCIA_PENDIENTE,
        "titulo": "Error de prueba",
    }

    with patch(
        "app.main.eliminar_incidencia",
        return_value=incidencia_eliminada
    ) as eliminar_mock:
        respuesta = client.delete("/incidencias/1")

    assert respuesta.status_code == 200
    assert respuesta.json() == incidencia_eliminada
    eliminar_mock.assert_called_once_with(1)

def test_actualizar_incidencia_inexistente():
    with patch(
        "app.main.actualizar_incidencia",
        return_value=None
    ):
        respuesta = client.put(
            "/incidencias/9999",
            json={
                "titulo": "Prueba",
                "descripcion": "El sistema no responde",
                "prioridad": "Alta"
            }
        )

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "Incidencia no encontrada"
    }


def test_eliminar_incidencia_inexistente():
    with patch(
        "app.main.eliminar_incidencia",
        return_value=None
    ):
        respuesta = client.delete("/incidencias/9999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "Incidencia no encontrada"
    }


def test_filtrar_incidencias_por_prioridad():
    incidencias_falsas = [
        {
            **INCIDENCIA_PENDIENTE,
            "titulo": "Error crítico",
        }
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias_falsas
    ) as obtener_mock:
        respuesta = client.get(
            "/incidencias?prioridad=Alta"
        )

    assert respuesta.status_code == 200
    assert respuesta.json() == incidencias_falsas
    obtener_mock.assert_called_once_with("Alta")


def test_rechazar_filtro_prioridad_invalida():
    respuesta = client.get(
        "/incidencias?prioridad=Urgente"
    )

    assert respuesta.status_code == 422

def test_iniciar_atencion():
    with patch(
        "app.main.iniciar_atencion",
        return_value=INCIDENCIA_EN_PROGRESO
    ) as iniciar_mock:
        respuesta = client.post("/incidencias/1/iniciar")

    assert respuesta.status_code == 200
    assert respuesta.json() == INCIDENCIA_EN_PROGRESO
    iniciar_mock.assert_called_once_with(1)

def test_iniciar_atencion_inexistente():
    with patch(
        "app.main.iniciar_atencion",
        return_value=None
    ), patch(
        "app.main.obtener_incidencia_por_id",
        return_value=None
    ):
        respuesta = client.post("/incidencias/9999/iniciar")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "Incidencia no encontrada"
    }

def test_iniciar_atencion_estado_incorrecto():
    with patch(
        "app.main.iniciar_atencion",
        return_value=None
    ), patch(
        "app.main.obtener_incidencia_por_id",
        return_value=INCIDENCIA_RESUELTA
    ):
        respuesta = client.post("/incidencias/1/iniciar")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede iniciar la atención porque "
            "la incidencia no está pendiente"
        )
    }

def test_resolver_incidencia():
    with patch(
        "app.main.resolver_incidencia",
        return_value=INCIDENCIA_RESUELTA
    ) as resolver_mock:
        respuesta = client.post("/incidencias/1/resolver")

    assert respuesta.status_code == 200
    assert respuesta.json() == INCIDENCIA_RESUELTA
    resolver_mock.assert_called_once_with(1)

def test_resolver_incidencia_inexistente():
    with patch(
        "app.main.resolver_incidencia",
        return_value=None
    ), patch(
        "app.main.obtener_incidencia_por_id",
        return_value=None
    ):
        respuesta = client.post("/incidencias/9999/resolver")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "Incidencia no encontrada"
    }

def test_resolver_incidencia_estado_incorrecto():
    with patch(
        "app.main.resolver_incidencia",
        return_value=None
    ), patch(
        "app.main.obtener_incidencia_por_id",
        return_value=INCIDENCIA_PENDIENTE
    ):
        respuesta = client.post("/incidencias/1/resolver")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede resolver la incidencia porque "
            "no está en progreso"
        )
    }

    
def test_ciclo_completo_de_incidencia():
    with patch(
        "app.main.iniciar_atencion",
        return_value=INCIDENCIA_EN_PROGRESO
    ) as iniciar_mock, patch(
        "app.main.resolver_incidencia",
        return_value=INCIDENCIA_RESUELTA
    ) as resolver_mock:
        respuesta_iniciar = client.post("/incidencias/1/iniciar")

        assert respuesta_iniciar.status_code == 200
        assert respuesta_iniciar.json()["estado"] == "En progreso"

        respuesta_resolver = client.post("/incidencias/1/resolver")

        assert respuesta_resolver.status_code == 200
        assert respuesta_resolver.json()["estado"] == "Resuelta"

        iniciar_mock.assert_called_once_with(1)
        resolver_mock.assert_called_once_with(1)

def test_filtrar_incidencias_por_estado():
    incidencias = [
        {**INCIDENCIA_PENDIENTE, "id": 1},
        {**INCIDENCIA_EN_PROGRESO, "id": 2},
        {**INCIDENCIA_RESUELTA, "id": 3},
    ]

    with patch("app.main.obtener_incidencias", return_value=incidencias):
        respuesta = client.get("/incidencias?estado=En%20progreso")

    assert respuesta.status_code == 200
    datos = respuesta.json()

    assert len(datos) == 1
    assert datos[0]["id"] == 2
    assert datos[0]["estado"] == "En progreso"


def test_consultar_incidencia_existente():
    with patch(
        "app.main.obtener_incidencia_por_id",
        return_value=INCIDENCIA_PENDIENTE
    ) as obtener_mock:
        respuesta = client.get("/incidencias/1")

    assert respuesta.status_code == 200
    assert respuesta.json() == INCIDENCIA_PENDIENTE
    obtener_mock.assert_called_once_with(1)

def test_rechazar_titulo_muy_largo():
    respuesta = client.post(
        "/incidencias",
        json={
            "titulo": "A" * 201,
            "descripcion": "Descripción de prueba",
            "prioridad": "Alta",
        },
    )

    assert respuesta.status_code == 422
