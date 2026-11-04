import argparse
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from scripts import seed_incidencias as seed

AHORA = datetime(2026, 11, 4, 15, tzinfo=timezone.utc)


@pytest.mark.parametrize('mes', ['2026-8', '2026-13', '0000-01', 'agosto'])
def test_mes_invalido(mes):
    with pytest.raises(argparse.ArgumentTypeError):
        seed.validar_mes(mes)


@pytest.mark.parametrize('mes,dias', [('2024-02',29), ('2026-02',28), ('2026-09',30), ('2026-10',31)])
def test_fechas_mes(mes, dias):
    registros = seed.generar(mes, 400, 42, AHORA)
    assert registros == seed.generar(mes, 400, 42, AHORA)
    fechas = [r['fecha_creacion'].astimezone(seed.ZONA) for r in registros]
    assert all(f.strftime('%Y-%m') == mes and f <= AHORA for f in fechas)
    assert max(f.day for f in fechas) == dias
    assert len({f.day for f in fechas}) == dias
    assert len({r['titulo'] for r in registros}) < len(registros)
    for r in registros:
        if r['estado'] == 'Resuelta':
            assert r['fecha_creacion'] < r['fecha_resolucion'] <= AHORA
        else:
            assert r['fecha_resolucion'] is None


def test_mes_actual_y_futuro():
    assert all(r['fecha_creacion'] <= AHORA for r in seed.generar('2026-11', 100, 0, AHORA))
    with pytest.raises(ValueError, match='futuro'):
        seed.generar('2026-12', 10, 0, AHORA)


def test_catalogo_y_semillas():
    assert sum(map(len, seed.CASOS.values())) == 26
    assert len(seed.EXTRAS) == 14
    assert seed.generar('2026-09',100,1,AHORA) != seed.generar('2026-09',100,2,AHORA)
    resueltas = [r for r in seed.generar('2026-10',2000,3,AHORA) if r['fecha_resolucion']]
    horas = [(r['fecha_resolucion']-r['fecha_creacion']).total_seconds()/3600 for r in resueltas]
    assert all(any(a <= h <= b for h in horas) for a,b in seed.RANGOS_HORAS)


def conexion_falsa(tablas=True):
    conexion = MagicMock()
    conexion.__enter__.return_value = conexion
    def salir(tipo, valor, tb):
        if tipo:
            conexion.rollback()
        return False
    conexion.__exit__.side_effect = salir
    cursor = conexion.cursor.return_value.__enter__.return_value
    cursor.fetchone.side_effect = [('incidencias_db',), (100,), ('seed_lotes','seed_registros') if tablas else (None,None), None]
    return conexion, cursor


def args(apply=False):
    return SimpleNamespace(database='incidencias_db',month='2026-09',count=10,seed=0,apply=apply)


def test_simulacion_sin_escrituras():
    conexion, cursor = conexion_falsa(False)
    seed.ejecutar(args(), lambda: conexion)
    assert all(c.args[0].startswith('SELECT') for c in cursor.execute.call_args_list)
    conexion.commit.assert_not_called()


def test_destino_rechazado():
    opciones = args()
    opciones.database = 'incidencias_test'
    conectar = MagicMock()
    with pytest.raises(ValueError):
        seed.ejecutar(opciones, conectar)
    conectar.assert_not_called()
    cursor = MagicMock()
    cursor.fetchone.return_value = ('produccion',)
    with pytest.raises(ValueError):
        seed.verificar_destino(cursor,'incidencias_db')


def test_idempotencia_y_conflicto():
    cursor = MagicMock()
    cursor.fetchone.return_value = (seed.lote_id('2026-09',10,0),)
    assert not seed.insertar_lote(cursor,'2026-09',10,0,AHORA,[])
    assert 'pg_advisory_xact_lock' in cursor.execute.call_args_list[0].args[0]
    assert not any('INSERT' in c.args[0] for c in cursor.execute.call_args_list)
    with pytest.raises(ValueError, match='otro lote'):
        seed.insertar_lote(cursor,'2026-09',20,0,AHORA,[])


def test_rollback_ante_error():
    conexion, cursor = conexion_falsa()
    def fallar(sql, parametros=None):
        if sql.startswith('INSERT'):
            raise RuntimeError('fallo de escritura')
    cursor.execute.side_effect = fallar
    cursor.fetchone.side_effect = [('incidencias_db',),(100,),('a','b'),None,None]
    with pytest.raises(RuntimeError):
        seed.ejecutar(args(True),lambda: conexion,lambda _: 'CARGAR incidencias_db 2026-09 10')
    conexion.commit.assert_not_called()
    assert conexion.rollback.call_count >= 2


def test_solo_actualiza_ids_nuevos():
    cursor = MagicMock()
    cursor.fetchone.side_effect = [None, (9876,)]
    cursor.rowcount = 1
    registro = seed.generar('2026-09',1,0,AHORA)[0]
    registro['estado'] = 'Resuelta'
    registro['fecha_resolucion'] = AHORA
    assert seed.insertar_lote(cursor,'2026-09',1,0,AHORA,[registro])
    actualizaciones = [c for c in cursor.execute.call_args_list if c.args[0].startswith('UPDATE')]
    assert len(actualizaciones) == 2
    assert all(c.args[1][-1] == 9876 for c in actualizaciones)
    assert not any('DELETE' in c.args[0] for c in cursor.execute.call_args_list)
