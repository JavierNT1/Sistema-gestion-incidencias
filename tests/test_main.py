from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


def test_categoria_obligatoria_e_invalida():
    for metodo, endpoint, mock_name in [
        ('post', '/incidencias', 'crear_incidencia'),
        ('put', '/incidencias/1', 'actualizar_incidencia'),
    ]:
        for categoria in [None, 'No existe', '']:
            datos = {'titulo': 'Prueba', 'descripcion': 'Descripción', 'prioridad': 'Alta'}
            if categoria is not None:
                datos['categoria'] = categoria
            with patch(f'app.main.{mock_name}') as operacion:
                respuesta = getattr(client, metodo)(endpoint, json=datos)
            assert respuesta.status_code == 422
            assert any(error['loc'] == ['body', 'categoria'] for error in respuesta.json()['detail'])
            operacion.assert_not_called()


def test_editar_no_cambia_categoria():
    original = {**INCIDENCIA_PENDIENTE, 'categoria': 'Seguridad'}
    with patch('app.main.actualizar_incidencia', return_value=original) as actualizar:
        respuesta = client.put('/incidencias/1', json={
            'titulo': original['titulo'], 'descripcion': original['descripcion'],
            'prioridad': original['prioridad'], 'categoria': 'Otros',
        })
    assert respuesta.status_code == 200
    assert respuesta.json()['categoria'] == 'Seguridad'
    actualizar.assert_called_once_with(1, original['titulo'], original['descripcion'], 'Alta')

INCIDENCIA_PENDIENTE = {
                           "categoria": "Otros",
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
                 "categoria": "Otros",
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
                 "categoria": "Otros",
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
                 "categoria": "Otros",
            "titulo": "Prueba de validación",
            "descripcion": "   ",
            "prioridad": "Alta"
        }
    )

    assert respuesta.status_code == 422

def test_crear_incidencia():
    incidencia_falsa = {
                           "categoria": "Otros",
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
                     "categoria": "Otros",
                "titulo": "Error en el sistema",
                "descripcion": "El sistema no responde",
                "prioridad": "Alta"
            }
        )

    assert respuesta.status_code == 201
    assert respuesta.json() == incidencia_falsa
    crear_mock.assert_called_once_with(
        "Error en el sistema",
        "Otros",
        "El sistema no responde",
        "Alta"
    )

def test_listar_incidencias():
    incidencias_falsas = [
        {
            "categoria": "Otros",
            **INCIDENCIA_PENDIENTE,
            "id": 1,
            "titulo": "Error de conexión",
        },
        {
            "categoria": "Otros",
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
                                 "categoria": "Otros",
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
                     "categoria": "Otros",
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
                     "categoria": "Otros",
                "titulo": "Título válido",
                "descripcion": "   ",
                "prioridad": "Alta"
            }
        )

    assert respuesta.status_code == 422
    actualizar_mock.assert_not_called()


def test_eliminar_incidencia():
    incidencia_eliminada = {
                               "categoria": "Otros",
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
                     "categoria": "Otros",
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
            "categoria": "Otros",
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
                 "categoria": "Otros",
            "titulo": "A" * 201,
            "descripcion": "Descripción de prueba",
            "prioridad": "Alta",
        },
    )

    assert respuesta.status_code == 422

def test_exportar_incidencias_csv():
    import csv
    import io

    with patch(
        "app.main.obtener_incidencias",
        return_value=[INCIDENCIA_PENDIENTE]
    ):
        respuesta = client.get("/incidencias/exportar/csv")

    assert respuesta.status_code == 200
    assert "text/csv" in respuesta.headers["content-type"]
    assert "incidencias.csv" in respuesta.headers["content-disposition"]

    contenido = respuesta.content.decode("utf-8-sig")
    filas = list(csv.DictReader(io.StringIO(contenido)))

    assert len(filas) == 1
    assert filas[0]["id"] == "1"
    assert filas[0]["titulo"] == "Error de conexión"
    assert filas[0]["categoria"] == "Otros"
    assert filas[0]["prioridad"] == "Alta"
    assert filas[0]["estado"] == "Pendiente"

def test_exportar_incidencias_excel():
    import io
    from openpyxl import load_workbook

    with patch(
        "app.main.obtener_incidencias",
        return_value=[INCIDENCIA_PENDIENTE]
    ):
        respuesta = client.get("/incidencias/exportar/excel")

    assert respuesta.status_code == 200
    assert "incidencias.xlsx" in respuesta.headers["content-disposition"]

    libro = load_workbook(io.BytesIO(respuesta.content))
    hoja = libro["Incidencias"]

    assert hoja.max_row == 2
    assert hoja["A1"].value == "ID"
    assert hoja["B1"].value == "Título"
    assert hoja["C1"].value == "Categoría"

    assert hoja["A2"].value == 1
    assert hoja["B2"].value == "Error de conexión"
    assert hoja["C2"].value == "Otros"
    assert hoja["E2"].value == "Alta"
    assert hoja["F2"].value == "Pendiente"

    assert hoja.freeze_panes == "A2"
    assert hoja.auto_filter.ref == hoja.dimensions

def test_exportar_csv_filtrado_por_estado():
    import csv
    import io

    incidencias = [
        {**INCIDENCIA_PENDIENTE, "id": 1},
        {**INCIDENCIA_EN_PROGRESO, "id": 2},
        {**INCIDENCIA_RESUELTA, "id": 3},
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias
    ):
        respuesta = client.get(
            "/incidencias/exportar/csv?estado=Resuelta"
        )

    assert respuesta.status_code == 200

    contenido = respuesta.content.decode("utf-8-sig")
    filas = list(csv.DictReader(io.StringIO(contenido)))

    assert len(filas) == 1
    assert filas[0]["id"] == "3"
    assert filas[0]["estado"] == "Resuelta"

def test_exportar_excel_filtrado_por_estado():
    import io
    from openpyxl import load_workbook

    incidencias = [
        {**INCIDENCIA_PENDIENTE, "id": 1},
        {**INCIDENCIA_EN_PROGRESO, "id": 2},
        {**INCIDENCIA_RESUELTA, "id": 3},
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias
    ):
        respuesta = client.get(
            "/incidencias/exportar/excel?estado=Resuelta"
        )

    assert respuesta.status_code == 200

    libro = load_workbook(io.BytesIO(respuesta.content))
    hoja = libro["Incidencias"]

    assert hoja.max_row == 2
    assert hoja["A2"].value == 3
    assert hoja["F2"].value == "Resuelta"

def test_exportar_csv_filtrado_por_prioridad():
    import csv
    import io

    incidencias = [
        {**INCIDENCIA_PENDIENTE, "id": 1, "prioridad": "Alta"},
        {**INCIDENCIA_PENDIENTE, "id": 2, "prioridad": "Media"},
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=[incidencias[0]]
    ) as obtener_mock:
        respuesta = client.get(
            "/incidencias/exportar/csv?prioridad=Alta"
        )

    assert respuesta.status_code == 200

    contenido = respuesta.content.decode("utf-8-sig")
    filas = list(csv.DictReader(io.StringIO(contenido)))

    assert len(filas) == 1
    assert filas[0]["id"] == "1"
    assert filas[0]["prioridad"] == "Alta"

    obtener_mock.assert_called_once_with("Alta")

def test_exportar_excel_filtrado_por_prioridad():
    import io
    from openpyxl import load_workbook

    incidencia_alta = {
        **INCIDENCIA_PENDIENTE,
        "id": 1,
        "prioridad": "Alta",
    }

    with patch(
        "app.main.obtener_incidencias",
        return_value=[incidencia_alta]
    ) as obtener_mock:
        respuesta = client.get(
            "/incidencias/exportar/excel?prioridad=Alta"
        )

    assert respuesta.status_code == 200

    libro = load_workbook(io.BytesIO(respuesta.content))
    hoja = libro["Incidencias"]

    assert hoja.max_row == 2
    assert hoja["A2"].value == 1
    assert hoja["E2"].value == "Alta"

    obtener_mock.assert_called_once_with("Alta")

def test_exportar_csv_filtrado_por_categoria():
    import csv
    import io

    incidencias = [
        {**INCIDENCIA_PENDIENTE, "id": 1, "categoria": "Otros"},
        {**INCIDENCIA_PENDIENTE, "id": 2, "categoria": "Seguridad"},
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias
    ):
        respuesta = client.get(
            "/incidencias/exportar/csv",
            params={"categoria": "Seguridad"}
        )

    assert respuesta.status_code == 200

    contenido = respuesta.content.decode("utf-8-sig")
    filas = list(csv.DictReader(io.StringIO(contenido)))

    assert len(filas) == 1
    assert filas[0]["id"] == "2"
    assert filas[0]["categoria"] == "Seguridad"

def test_exportar_excel_filtrado_por_categoria():
    import io
    from openpyxl import load_workbook

    incidencias = [
        {**INCIDENCIA_PENDIENTE, "id": 1, "categoria": "Otros"},
        {**INCIDENCIA_PENDIENTE, "id": 2, "categoria": "Seguridad"},
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias
    ):
        respuesta = client.get(
            "/incidencias/exportar/excel",
            params={"categoria": "Seguridad"}
        )

    assert respuesta.status_code == 200

    libro = load_workbook(io.BytesIO(respuesta.content))
    hoja = libro["Incidencias"]

    assert hoja.max_row == 2
    assert hoja["A2"].value == 2
    assert hoja["C2"].value == "Seguridad"

def test_exportar_csv_filtrado_por_titulo():
    import csv
    import io

    incidencias = [
        {**INCIDENCIA_PENDIENTE, "id": 1, "titulo": "Impresora sin conexión"},
        {**INCIDENCIA_PENDIENTE, "id": 2, "titulo": "Cámara sin señal"},
        {**INCIDENCIA_PENDIENTE, "id": 3, "titulo": "Impresora dañada"},
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias
    ):
        respuesta = client.get(
            "/incidencias/exportar/csv",
            params={"titulo": "IMPRESORA"}
        )

    assert respuesta.status_code == 200

    contenido = respuesta.content.decode("utf-8-sig")
    filas = list(csv.DictReader(io.StringIO(contenido)))

    assert len(filas) == 2
    assert {fila["id"] for fila in filas} == {"1", "3"}
    assert all("impresora" in fila["titulo"].lower() for fila in filas)

def test_exportar_excel_filtrado_por_titulo():
    import io
    from openpyxl import load_workbook

    incidencias = [
        {**INCIDENCIA_PENDIENTE, "id": 1, "titulo": "Impresora sin conexión"},
        {**INCIDENCIA_PENDIENTE, "id": 2, "titulo": "Cámara sin señal"},
        {**INCIDENCIA_PENDIENTE, "id": 3, "titulo": "Impresora dañada"},
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias
    ):
        respuesta = client.get(
            "/incidencias/exportar/excel",
            params={"titulo": "IMPRESORA"}
        )

    assert respuesta.status_code == 200

    libro = load_workbook(io.BytesIO(respuesta.content))
    hoja = libro.active

    filas = list(hoja.iter_rows(min_row=2, values_only=True))

    assert len(filas) == 2
    assert {fila[0] for fila in filas} == {1, 3}
    assert all("impresora" in fila[1].lower() for fila in filas)

    libro.close()

def test_exportar_csv_con_filtros_combinados():
    import csv
    import io

    incidencias = [
        {
            **INCIDENCIA_PENDIENTE,
            "id": 1,
            "titulo": "Impresora sin conexión",
            "prioridad": "Alta",
            "estado": "Pendiente",
        },
        {
            **INCIDENCIA_PENDIENTE,
            "id": 2,
            "titulo": "Impresora con atasco",
            "prioridad": "Baja",
            "estado": "Pendiente",
        },
        {
            **INCIDENCIA_PENDIENTE,
            "id": 3,
            "titulo": "Impresora sin tinta",
            "prioridad": "Alta",
            "estado": "En progreso",
        },
        {
            **INCIDENCIA_PENDIENTE,
            "id": 4,
            "titulo": "Cámara sin conexión",
            "prioridad": "Alta",
            "estado": "Pendiente",
        },
    ]

    def obtener_incidencias_simuladas(prioridad=None):
        if prioridad is None:
            return incidencias

        return [
            incidencia
            for incidencia in incidencias
            if incidencia["prioridad"] == prioridad
        ]

    with patch(
        "app.main.obtener_incidencias",
        side_effect=obtener_incidencias_simuladas
    ):
        respuesta = client.get(
            "/incidencias/exportar/csv",
            params={
                "titulo": "impresora",
                "prioridad": "Alta",
                "estado": "Pendiente",
            },
        )

    assert respuesta.status_code == 200

    contenido = respuesta.content.decode("utf-8-sig")
    filas = list(csv.DictReader(io.StringIO(contenido)))

    assert len(filas) == 1
    assert filas[0]["id"] == "1"
    assert filas[0]["titulo"] == "Impresora sin conexión"

def test_exportar_csv_sin_coincidencias():
    import csv
    import io

    incidencias = [
        {
            **INCIDENCIA_PENDIENTE,
            "id": 1,
            "titulo": "Impresora sin conexión",
        },
        {
            **INCIDENCIA_PENDIENTE,
            "id": 2,
            "titulo": "Cámara sin señal",
        },
    ]

    with patch(
        "app.main.obtener_incidencias",
        return_value=incidencias
    ):
        respuesta = client.get(
            "/incidencias/exportar/csv",
            params={"titulo": "ascensor espacial"},
        )

    assert respuesta.status_code == 200

    contenido = respuesta.content.decode("utf-8-sig")
    lector = csv.DictReader(io.StringIO(contenido))

    assert lector.fieldnames == [
        "id",
        "titulo",
        "categoria",
        "descripcion",
        "prioridad",
        "estado",
        "fecha_creacion",
        "fecha_resolucion",
    ]

    assert list(lector) == []