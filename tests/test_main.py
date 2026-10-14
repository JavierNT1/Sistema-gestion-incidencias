from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


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
            "prioridad": "Urgente"
        }
    )

    assert respuesta.status_code == 422

def test_rechazar_titulo_vacio():
    respuesta = client.post(
        "/incidencias",
        json={
            "titulo": "   ",
            "prioridad": "Alta"
        }
    )

    assert respuesta.status_code == 422

def test_crear_incidencia():
    incidencia_falsa = {
        "id": 100,
        "titulo": "Error en el sistema",
        "prioridad": "Alta",
        "fecha_creacion": "2026-10-10T12:00:00Z"
    }
    with patch(
        "app.main.crear_incidencia",
        return_value=incidencia_falsa
    ) as crear_mock:
        respuesta = client.post(
            "/incidencias",
            json={
                "titulo": "Error en el sistema",
                "prioridad": "Alta"
            }
        )

    assert respuesta.status_code == 201
    assert respuesta.json() == incidencia_falsa
    crear_mock.assert_called_once_with(
        "Error en el sistema",
        "Alta"
    )

def test_listar_incidencias():
    incidencias_falsas = [
        {
            "id": 1,
            "titulo": "Error de conexión",
            "prioridad": "Alta",
            "fecha_creacion": "2026-10-10T12:00:00Z"
        },
        {
            "id": 2,
            "titulo": "Problema de impresión",
            "prioridad": "Media",
            "fecha_creacion": "2026-10-10T12:00:00Z"
        }
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
        "id": 1,
        "titulo": "Error corregido",
        "prioridad": "Media",
        "fecha_creacion": "2026-10-10T12:00:00Z"
    }

    with patch(
        "app.main.actualizar_incidencia",
        return_value=incidencia_actualizada
    ) as actualizar_mock:
        respuesta = client.put(
            "/incidencias/1",
            json={
                "titulo": "Error corregido",
                "prioridad": "Media"
            }
        )

    assert respuesta.status_code == 200
    assert respuesta.json() == incidencia_actualizada
    actualizar_mock.assert_called_once_with(
        1,
        "Error corregido",
        "Media"
    )


def test_eliminar_incidencia():
    incidencia_eliminada = {
        "id": 1,
        "titulo": "Error de prueba",
        "prioridad": "Alta",
        "fecha_creacion": "2026-10-10T12:00:00Z"
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
            "id": 1,
            "titulo": "Error crítico",
            "prioridad": "Alta",
            "fecha_creacion": "2026-10-10T12:00:00Z"
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