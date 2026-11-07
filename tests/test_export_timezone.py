import io
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook
from app.main import app


@pytest.mark.parametrize('mes,hora_chile', [(1,9), (7,8)])
def test_excel_hora_chilena_verano_invierno(mes, hora_chile):
    fecha = datetime(2026,mes,15,12,tzinfo=timezone.utc)
    incidencia = dict(id=1,titulo='Prueba',categoria='Otros',descripcion='Descripción',
        prioridad='Media',estado='Resuelta',fecha_creacion=fecha,fecha_resolucion=fecha)
    with patch('app.main.obtener_incidencias', return_value=[incidencia]):
        respuesta = TestClient(app).get('/incidencias/exportar/excel')
    assert respuesta.status_code == 200
    libro = load_workbook(io.BytesIO(respuesta.content))
    hoja = libro.active
    assert 'America/Santiago' in hoja['G1'].value
    assert 'America/Santiago' in hoja['H1'].value
    for columna in ('G2','H2'):
        assert hoja[columna].value == datetime(2026,mes,15,hora_chile)
    assert incidencia['fecha_creacion'] == fecha
    libro.close()
