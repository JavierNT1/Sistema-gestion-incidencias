"""Datos de demostración; simulación por defecto y lotes mensuales atómicos."""
import argparse
import calendar
import hashlib
import random
import re
from datetime import date
from zoneinfo import ZoneInfo
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conexion import obtener_conexion
from app.schemas import IncidenciaNueva

DESTINO = 'incidencias_db'
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


# Configuración del generador: cambiar la versión si cambia el algoritmo o catálogo.
VERSION = 2
ZONA = ZoneInfo('America/Santiago')
PESOS_ESTADO = (0.40, 0.35, 0.25)
RANGOS_HORAS = ((0.5, 12), (12.01, 24), (24.01, 48), (48.01, 72), (72.01, 168))
EXTRAS = [
    ('Informática (TI)', 'Carpeta compartida inaccesible', 'El equipo perdió permisos sobre los documentos del turno.', 'Media'),
    ('Informática (TI)', 'Actualización de seguridad pendiente', 'Una estación no completa la instalación del parche aprobado.', 'Alta'),
    ('Informática (TI)', 'Telefonía interna sin audio', 'Las llamadas conectan pero no transmiten voz desde el puesto.', 'Media'),
    ('Mantenimiento e instalaciones', 'Grifería con fuga', 'El lavamanos pierde agua incluso con la llave cerrada.', 'Media'),
    ('Mantenimiento e instalaciones', 'Ascensor fuera de servicio', 'El ascensor muestra una alarma y quedó bloqueado para inspección.', 'Alta'),
    ('Seguridad', 'Alarma de acceso intermitente', 'El sensor informa aperturas sin movimiento visible en el registro.', 'Alta'),
    ('Seguridad', 'Extintor con inspección vencida', 'La etiqueta de mantenimiento requiere revisión del proveedor.', 'Alta'),
    ('Administración', 'Contrato pendiente de firma', 'La renovación está aprobada pero falta la firma del responsable.', 'Media'),
    ('Administración', 'Certificado de proveedor vencido', 'El expediente requiere un documento vigente antes del próximo pago.', 'Media'),
    ('Operaciones y logística', 'Equipo de traslado averiado', 'El carro de carga tiene una rueda trabada y fue retirado del turno.', 'Media'),
    ('Operaciones y logística', 'Recepción con bultos faltantes', 'La cantidad recibida no coincide con la guía del transportista.', 'Alta'),
    ('Operaciones y logística', 'Ruta de entrega sin confirmar', 'El destino solicitó cambiar la ventana de recepción del pedido.', 'Media'),
    ('Otros', 'Solicitud de apoyo para evento', 'La reunión ampliada requiere coordinar equipamiento adicional.', 'Baja'),
    ('Otros', 'Aviso interno con enlace incorrecto', 'El comunicado dirige a un formulario que ya no está disponible.', 'Baja'),
]


def validar_mes(texto):
    if not re.fullmatch(r'\d{4}-\d{2}', texto):
        raise argparse.ArgumentTypeError('El mes debe tener formato AAAA-MM.')
    try:
        date.fromisoformat(texto + '-01')
    except ValueError as error:
        raise argparse.ArgumentTypeError('Mes o año inválido.') from error
    return texto


def cantidad_positiva(texto):
    valor = int(texto)
    if valor <= 0:
        raise argparse.ArgumentTypeError('La cantidad debe ser mayor que cero.')
    return valor


def limites_mes(mes, ahora):
    inicio = datetime.fromisoformat(mes + '-01').replace(tzinfo=ZONA)
    siguiente = (inicio.replace(day=28) + timedelta(days=4)).replace(day=1)
    if inicio > ahora:
        raise ValueError('El mes solicitado pertenece al futuro.')
    return inicio, min(siguiente - timedelta(microseconds=1), ahora)


def generar(mes, cantidad, semilla=0, ahora=None):
    ahora = ahora or datetime.now(timezone.utc)
    inicio, fin = limites_mes(mes, ahora)
    rng = random.Random(f'{VERSION}:{mes}:{cantidad}:{semilla}')
    casos = [(categoria, *caso) for categoria, lista in CASOS.items() for caso in lista] + EXTRAS
    # Muestreo estratificado: cubre todo el intervalo, con variación entre días.
    segundos = (fin.astimezone(timezone.utc) - inicio.astimezone(timezone.utc)).total_seconds()
    registros = []
    for indice in range(cantidad):
        creada = inicio.astimezone(timezone.utc) + timedelta(seconds=segundos * (indice + rng.random()) / cantidad)
        categoria, titulo, descripcion, prioridad = rng.choice(casos)
        lugar = rng.choice(LUGARES)
        datos = IncidenciaNueva(titulo=f'{titulo} — {lugar}', categoria=categoria,
            descripcion=f'{descripcion} Aviso recibido desde {lugar}.', prioridad=prioridad)
        estado = rng.choices(['Pendiente', 'En progreso', 'Resuelta'], weights=PESOS_ESTADO)[0]
        resuelta = None
        if estado == 'Resuelta':
            duracion = rng.uniform(*rng.choice(RANGOS_HORAS))
            candidata = creada + timedelta(hours=duracion)
            if candidata <= ahora:
                resuelta = candidata
            else:
                estado = 'En progreso'
        registros.append(dict(datos.model_dump(mode='json'), fecha_creacion=creada,
            estado=estado, fecha_resolucion=resuelta, clave=f'{indice + 1:08d}'))
    return registros


def lote_id(mes, cantidad, semilla):
    contenido = f'{VERSION}:{mes}:{cantidad}:{semilla}'
    return hashlib.sha256(contenido.encode()).hexdigest()


def verificar_destino(cursor, solicitado):
    if solicitado != DESTINO:
        raise ValueError('Solo se autoriza incidencias_db como base de desarrollo.')
    cursor.execute('SELECT current_database()')
    if cursor.fetchone()[0] != DESTINO:
        raise ValueError('La conexión no corresponde a incidencias_db; operación detenida.')


def buscar_lote(cursor, mes, identificador):
    cursor.execute('SELECT lote_id FROM public.seed_lotes WHERE mes = %s', (mes,))
    fila = cursor.fetchone()
    if fila and fila[0] != identificador:
        raise ValueError('El mes ya tiene otro lote: cantidad, semilla o versión diferentes. No se mezclan lotes.')
    return bool(fila)


def insertar_lote(cursor, mes, cantidad, semilla, referencia, registros):
    identificador = lote_id(mes, cantidad, semilla)
    # Serializa por mes; la restricción UNIQUE es la segunda barrera concurrente.
    cursor.execute('SELECT pg_advisory_xact_lock(%s, %s)', (735201, int(mes.replace('-', ''))))
    if buscar_lote(cursor, mes, identificador):
        return False
    cursor.execute('''INSERT INTO public.seed_lotes (lote_id, mes, cantidad, semilla, version, referencia)
        VALUES (%s,%s,%s,%s,%s,%s)''', (identificador, mes, cantidad, semilla, VERSION, referencia))
    for registro in registros:
        cursor.execute('''INSERT INTO public.incidencias (titulo,categoria,descripcion,prioridad,fecha_creacion)
            VALUES (%s,%s,%s,%s,%s) RETURNING id''', tuple(registro[k] for k in
            ('titulo', 'categoria', 'descripcion', 'prioridad', 'fecha_creacion')))
        nuevo_id = cursor.fetchone()[0]
        if registro['estado'] != 'Pendiente':
            cursor.execute("UPDATE public.incidencias SET estado='En progreso' WHERE id=%s AND estado='Pendiente'", (nuevo_id,))
            if cursor.rowcount != 1:
                raise ValueError('Falló la transición a En progreso.')
        if registro['estado'] == 'Resuelta':
            cursor.execute("UPDATE public.incidencias SET estado='Resuelta',fecha_resolucion=%s WHERE id=%s AND estado='En progreso'",
                (registro['fecha_resolucion'], nuevo_id))
            if cursor.rowcount != 1:
                raise ValueError('Falló la transición a Resuelta.')
        cursor.execute('INSERT INTO public.seed_registros (lote_id,clave,incidencia_id) VALUES (%s,%s,%s)',
            (identificador, registro['clave'], nuevo_id))
    return True


def resumen(args, total, registros):
    print(f'Base de destino: {DESTINO}\nMes solicitado: {args.month}\nCantidad: {args.count}')
    print(f'Lote: {lote_id(args.month, args.count, args.seed)}\nRegistros existentes: {total}')
    dias = calendar.monthrange(int(args.month[:4]), int(args.month[5:]))[1]
    grupos = Counter(min((r['fecha_creacion'].astimezone(ZONA).day - 1) // 7, 4) for r in registros)
    for indice in range(5):
        primero = indice * 7 + 1
        if primero <= dias:
            print(f'{primero}–{min(primero + 6, dias)}: {grupos[indice]} creadas')
    for campo in ('estado', 'categoria', 'prioridad'):
        print(campo.capitalize() + ':', dict(Counter(r[campo] for r in registros)))
    resueltas = [r for r in registros if r['fecha_resolucion']]
    mismo = sum(r['fecha_resolucion'].astimezone(ZONA).strftime('%Y-%m') == args.month for r in resueltas)
    print(f'Resoluciones en el mes: {mismo}; posteriores: {len(resueltas) - mismo}')


def ejecutar(args, conectar=obtener_conexion, confirmar=input):
    if args.database != DESTINO:
        raise ValueError('Solo se autoriza incidencias_db.')
    referencia = datetime.now(timezone.utc)
    registros = generar(args.month, args.count, args.seed, referencia)
    with conectar() as conexion:
        conexion.read_only = True
        with conexion.cursor() as cursor:
            verificar_destino(cursor, args.database)
            cursor.execute('SELECT count(*) FROM public.incidencias')
            resumen(args, cursor.fetchone()[0], registros)
            cursor.execute('SELECT to_regclass(%s),to_regclass(%s)', ('public.seed_lotes','public.seed_registros'))
            tablas = all(cursor.fetchone())
            if tablas and buscar_lote(cursor, args.month, lote_id(args.month, args.count, args.seed)):
                print('Lote ya cargado. No se insertan ni modifican registros.')
                return
        conexion.rollback()
        if not args.apply:
            if not tablas:
                print('Para cargar hace falta aplicar la migración 001_seed_lotes.sql.')
            print('Modo simulación: no se realizaron escrituras.')
            return
        if not tablas:
            raise ValueError('Falta la migración 001_seed_lotes.sql; el script no modifica el esquema.')
        frase = f'CARGAR {DESTINO} {args.month} {args.count}'
        if confirmar(f'Confirma desarrollo escribiendo {frase}: ').strip() != frase:
            print('Cancelado; sin escrituras.')
            return
        conexion.read_only = False
        with conexion.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '5s'")
            cargado = insertar_lote(cursor, args.month, args.count, args.seed, referencia, registros)
        conexion.commit()
        print('Lote insertado correctamente.' if cargado else 'Lote ya cargado; sin duplicados.')


def argumentos():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True)
    parser.add_argument('--month', required=True, type=validar_mes)
    parser.add_argument('--count', required=True, type=cantidad_positiva)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--apply', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        ejecutar(argumentos())
    except (ValueError, EOFError) as error:
        print(f'Operación detenida: {error}', file=sys.stderr)
        sys.exit(1)
    except (Exception, KeyboardInterrupt) as error:
        print(f'Operación abortada ({type(error).__name__}); transacción revertida. Revisar conexión, permisos y migración.', file=sys.stderr)
        sys.exit(1)
