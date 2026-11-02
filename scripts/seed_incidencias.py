"""Datos de demostración; simulación por defecto y carga atómica hasta 100."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conexion import obtener_conexion
from app.schemas import IncidenciaNueva

DESTINO = 'incidencias_db'
OBJETIVO = 100
CASOS = {
    'Informática (TI)': [
        ('Impresora sin conexión', 'Los documentos quedan en cola y el equipo no responde por la red.', 'Media'),
        ('Acceso al correo bloqueado', 'La cuenta corporativa rechaza el inicio de sesión tras renovar la contraseña.', 'Alta'),
        ('Conexión Wi-Fi intermitente', 'Las videollamadas se interrumpen y se pierde acceso a los recursos compartidos.', 'Media'),
        ('Respaldo nocturno incompleto', 'El informe de respaldo registra archivos pendientes y requiere revisar la copia.', 'Alta'),
        ('Monitor con imagen inestable', 'La pantalla presenta parpadeos al conectar el equipo al puesto de trabajo.', 'Baja'),
    ],
    'Mantenimiento e instalaciones': [
        ('Filtración en el cielo', 'Después de la lluvia aparecen gotas cerca de las luminarias; se delimitó el sector.', 'Alta'),
        ('Climatización sin respuesta', 'El equipo mantiene una temperatura elevada pese al ajuste del termostato.', 'Media'),
        ('Luminaria apagada', 'Una luminaria no enciende y reduce la iluminación del área de circulación.', 'Baja'),
        ('Enchufe con sobrecalentamiento', 'Se percibió olor a plástico en el tomacorriente; el punto quedó fuera de uso.', 'Alta'),
        ('Puerta con cierre defectuoso', 'La hoja roza el marco y necesita ajuste para permitir un cierre normal.', 'Media'),
    ],
    'Seguridad': [
        ('Credencial de acceso extraviada', 'Una persona informó la pérdida de su tarjeta y solicitó bloquear el acceso.', 'Alta'),
        ('Cámara sin señal', 'El monitor de vigilancia dejó de recibir imagen y requiere verificar alimentación y enlace.', 'Alta'),
        ('Registro de visitas incompleto', 'Faltan datos de salida en el libro de visitas del turno anterior.', 'Media'),
        ('Señal de evacuación deteriorada', 'El letrero perdió legibilidad y se solicita su reposición.', 'Baja'),
    ],
    'Administración': [
        ('Factura registrada dos veces', 'La conciliación detectó el mismo documento en dos solicitudes de pago.', 'Alta'),
        ('Orden de compra sin aprobación', 'El proveedor espera autorización y la solicitud no llegó al responsable.', 'Media'),
        ('Datos de proveedor desactualizados', 'La ficha conserva una dirección anterior y debe contrastarse con el documento vigente.', 'Baja'),
        ('Comprobante de gasto pendiente', 'La rendición incluye un gasto respaldado por una imagen ilegible.', 'Media'),
    ],
    'Operaciones y logística': [
        ('Despacho retenido por documentación', 'El transportista no puede retirar el pedido porque falta la guía validada.', 'Alta'),
        ('Diferencia en inventario', 'El conteo físico no coincide con el saldo registrado y requiere conciliación.', 'Media'),
        ('Embalaje recibido dañado', 'Se detectó una caja abierta durante la recepción y se apartó para inspección.', 'Media'),
        ('Etiqueta de ubicación ilegible', 'La identificación del estante está desgastada y dificulta preparar los pedidos.', 'Baja'),
        ('Entrega fuera de horario', 'El proveedor llegó después del turno acordado y debe coordinarse una nueva recepción.', 'Media'),
    ],
    'Otros': [
        ('Objeto encontrado sin identificar', 'Se recibió un objeto olvidado y debe registrarse para gestionar su devolución.', 'Baja'),
        ('Reserva de sala duplicada', 'Dos equipos tienen confirmación para el mismo horario y solicitan coordinación.', 'Media'),
        ('Material informativo desactualizado', 'El panel conserva instrucciones anteriores y necesita revisión del responsable.', 'Baja'),
    ],
}
LUGARES = ['recepción', 'oficina central', 'sucursal norte', 'sucursal sur']


def catalogo():
    registros = []
    for categoria, casos in CASOS.items():
        cantidad = 18 if categoria in ('Mantenimiento e instalaciones', 'Operaciones y logística') else len(casos) * 4
        generados = 0
        for lugar in LUGARES:
            for titulo, descripcion, prioridad in casos:
                if generados >= cantidad:
                    continue
                registros.append(IncidenciaNueva(
                    titulo=f'{titulo} — {lugar}', categoria=categoria,
                    descripcion=f'{descripcion} El aviso corresponde a {lugar}; el responsable del sector solicita seguimiento.',
                    prioridad=prioridad,
                ))
                generados += 1
    assert len(registros) == OBJETIVO
    assert len({r.titulo for r in registros}) == OBJETIVO
    return registros


def plan(cursor):
    cursor.execute('SELECT titulo FROM public.incidencias')
    existentes = cursor.fetchall()
    faltan = max(0, OBJETIVO - len(existentes))
    titulos = {fila[0] for fila in existentes}
    candidatos = [r for r in catalogo() if r.titulo not in titulos]
    if len(candidatos) < faltan:
        raise RuntimeError('El catálogo no alcanza sin repetir títulos; no se realizará la carga.')
    return len(existentes), candidatos[:faltan]


def resumen(actual, registros):
    print(f'Actuales: {actual}; por insertar: {len(registros)}; total previsto: {actual + len(registros)}')
    print('Categorías nuevas:', dict(Counter(r.categoria.value for r in registros)))
    print('Prioridades nuevas:', dict(Counter(r.prioridad.value for r in registros)))


def ejecutar(args):
    if args.database != DESTINO:
        raise RuntimeError(f'Solo se permite el destino de desarrollo {DESTINO}.')
    with obtener_conexion() as conexion:
        conexion.read_only = True
        with conexion.cursor() as cursor:
            cursor.execute('SELECT current_database()')
            destino = cursor.fetchone()[0]
            print(f'Base de destino: {destino}')
            if destino != DESTINO:
                raise RuntimeError('La conexión no coincide con la base de desarrollo autorizada.')
            actual, registros = plan(cursor)
            resumen(actual, registros)
        conexion.rollback()
        if not args.apply or not registros:
            print('Simulación sin escrituras.' if not args.apply else 'No hacen falta inserciones.')
            return
        frase = f'CARGAR {DESTINO} HASTA {OBJETIVO}'
        if input(f'Confirma que es desarrollo escribiendo {frase}: ').strip() != frase:
            print('Carga cancelada; sin escrituras.')
            return
        conexion.read_only = False
        # Un único commit; cualquier excepción revierte el lote completo.
        with conexion.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '5s'")
            cursor.execute('LOCK TABLE public.incidencias IN SHARE ROW EXCLUSIVE MODE')
            actual, registros = plan(cursor)
            ahora = datetime.now(timezone.utc)
            ids = []
            estados = Counter()
            for indice, registro in enumerate(registros):
                estado = 'Pendiente' if indice % 20 < 8 else ('En progreso' if indice % 20 < 15 else 'Resuelta')
                creada = ahora - timedelta(days=30, hours=indice)
                cursor.execute('''INSERT INTO public.incidencias
                    (titulo, categoria, descripcion, prioridad, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id''',
                    (registro.titulo, registro.categoria.value, registro.descripcion, registro.prioridad.value, creada))
                identificador = cursor.fetchone()[0]
                ids.append(identificador)
                if estado != 'Pendiente':
                    cursor.execute('''UPDATE public.incidencias SET estado = 'En progreso'
                        WHERE id = %s AND estado = 'Pendiente' ''', (identificador,))
                    if cursor.rowcount != 1:
                        raise RuntimeError('No se pudo iniciar la incidencia nueva.')
                if estado == 'Resuelta':
                    cursor.execute('''UPDATE public.incidencias SET estado = 'Resuelta', fecha_resolucion = %s
                        WHERE id = %s AND estado = 'En progreso' ''', (creada + timedelta(days=2), identificador))
                    if cursor.rowcount != 1:
                        raise RuntimeError('No se pudo resolver la incidencia nueva.')
                estados[estado] += 1
            cursor.execute('SELECT count(*) FROM public.incidencias')
            total = cursor.fetchone()[0]
            if registros and total != OBJETIVO:
                raise RuntimeError('El total final no coincide con el objetivo.')
            cursor.execute('''SELECT count(*) FROM public.incidencias WHERE id = ANY(%s) AND
                ((estado = 'Resuelta' AND (fecha_resolucion IS NULL OR fecha_resolucion < fecha_creacion))
                OR (estado <> 'Resuelta' AND fecha_resolucion IS NOT NULL))''', (ids,))
            if cursor.fetchone()[0]:
                raise RuntimeError('Se detectaron fechas inconsistentes.')
        conexion.commit()
        print(f'Carga confirmada: {len(ids)} insertadas; total: {total}. Estados nuevos: {dict(estados)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True, help='Nombre explícito de la base de desarrollo')
    parser.add_argument('--apply', action='store_true', help='Solicitar confirmación e insertar')
    try:
        ejecutar(parser.parse_args())
    except (Exception, KeyboardInterrupt) as error:
        # No imprimir errores del controlador que puedan incluir información de conexión.
        print(f'Operación abortada ({type(error).__name__}). No se confirmó la carga.', file=sys.stderr)
        sys.exit(1)
