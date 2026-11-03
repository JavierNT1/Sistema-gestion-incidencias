import { useState, useEffect } from 'react'
import './App.css'
import {
  Layers,
  AlertTriangle,
  Clock,
  CheckCircle,
  Plus,
  SlidersHorizontal,
  X,
  Download,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  BarChart3,
} from 'lucide-react'
import { PieChart, Pie, Cell, Label, ResponsiveContainer, Tooltip } from 'recharts'

function App() {
const [incidencias, setIncidencias] = useState([])
const [todasLasIncidencias, setTodasLasIncidencias] = useState([])
const [cargando, setCargando] = useState(true)
const [error, setError] = useState('')
const [erroresEdicion, setErroresEdicion] = useState({})
const [vistaActual, setVistaActual] = useState('inicio')
const [titulo, setTitulo] = useState('')
const [categoria, setCategoria] = useState('')
const [descripcion, setDescripcion] = useState('')
const [prioridad, setPrioridad] = useState('Media')
const [filtroPrioridad, actualizarFiltroPrioridad] = useState('')
const [filtroEstado, actualizarFiltroEstado] = useState('')
const [filtroCategoria, actualizarFiltroCategoria] = useState('')
const [busquedaId, actualizarBusquedaId] = useState('')
const [busquedaTitulo, actualizarBusquedaTitulo] = useState('')
const [tipoBusqueda, setTipoBusqueda] = useState('titulo')
const [paginaActual, setPaginaActual] = useState(1)
const incidenciasPorPagina = 20
const [ordenColumna, setOrdenColumna] = useState(null)
const [ordenDireccion, setOrdenDireccion] = useState('asc')

function cambiarVista(vista) {
  setVistaActual(vista)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cambiarOrden(columna) {
  if (ordenColumna === columna) {
    setOrdenDireccion((anterior) =>
      anterior === 'asc' ? 'desc' : 'asc'
    )
  } else {
    setOrdenColumna(columna)
    setOrdenDireccion(columna === 'fecha_creacion' ? 'desc' : 'asc')
  }

  setPaginaActual(1)
}

function setFiltroPrioridad(valor) {
  actualizarFiltroPrioridad(valor)
  setPaginaActual(1)
}
function setFiltroEstado(valor) {
  actualizarFiltroEstado(valor)
  setPaginaActual(1)
}
function setFiltroCategoria(valor) {
  actualizarFiltroCategoria(valor)
  setPaginaActual(1)
}
function setBusquedaId(valor) {
  actualizarBusquedaId(valor)
  setPaginaActual(1)
}
function setBusquedaTitulo(valor) {
  actualizarBusquedaTitulo(valor)
  setPaginaActual(1)
}
function cambiarTipoBusqueda(tipo) {
  setTipoBusqueda(tipo)
  actualizarBusquedaTitulo('')
  actualizarBusquedaId('')
  setPaginaActual(1)
}

const [incidenciaSeleccionada, setIncidenciaSeleccionada] = useState(null)
const [modoEdicion, setModoEdicion] = useState(false)
const [tituloEditado, setTituloEditado] = useState('')
const [descripcionEditada, setDescripcionEditada] = useState('')
const [prioridadEditada, setPrioridadEditada] = useState('')

function descargarIncidencias(formato) {
  if (exportacionDeshabilitada) return

  const url = new URL(
    `http://127.0.0.1:8000/incidencias/exportar/${formato}`
  )

  if (filtroPrioridad) {
    url.searchParams.set('prioridad', filtroPrioridad)
  }

  if (filtroEstado) {
    url.searchParams.set('estado', filtroEstado)
  }

  if (filtroCategoria) {
    url.searchParams.set('categoria', filtroCategoria)
  }

  if (tipoBusqueda === 'titulo' && busquedaTitulo.trim()) {
  url.searchParams.set('titulo', busquedaTitulo.trim())
  }

  window.location.href = url.toString()
}

async function guardarIncidencia(evento) {
evento.preventDefault()

setError('')

try {
const respuesta = await fetch('http://127.0.0.1:8000/incidencias', {
method: 'POST',
headers: {
'Content-Type': 'application/json',
},
body: JSON.stringify({
titulo: titulo,
categoria: categoria,
descripcion: descripcion,
prioridad: prioridad,
}),
})

if (!respuesta.ok) {
  const detalle = await respuesta.json()
  throw new Error(
    detalle.detail?.[0]?.msg || 'No se pudo crear la incidencia'
  )
}


await respuesta.json()

// Obtener todas las incidencias con el orden del backend
const respuestaLista = await fetch(
  'http://127.0.0.1:8000/incidencias'
)

if (!respuestaLista.ok) {
  throw new Error('No se pudo actualizar la lista de incidencias')
}

const todas = await respuestaLista.json()

// Actualizar los datos completos para las tarjetas
setTodasLasIncidencias(todas)

// Aplicar los filtros actuales a la tabla
const incidenciasFiltradas = todas.filter((incidencia) => {
  const coincidePrioridad =
    filtroPrioridad === '' ||
    incidencia.prioridad === filtroPrioridad

  const coincideEstado =
    filtroEstado === '' ||
    incidencia.estado === filtroEstado

  return coincidePrioridad && coincideEstado
})

setIncidencias(incidenciasFiltradas)

setTitulo('')
setCategoria('')
setDescripcion('')
setPrioridad('Media')
cambiarVista('inicio')

} catch (error) {
setError(error.message)
}
}

useEffect(() => {
async function cargarIncidencias() {
setCargando(true)
setError('')

try {
  const url = new URL('http://127.0.0.1:8000/incidencias')

  if (filtroPrioridad !== '') {
    url.searchParams.set('prioridad', filtroPrioridad)
  }

  if (filtroEstado !== '') {
    url.searchParams.set('estado', filtroEstado)
  }

  const respuesta = await fetch(url)

  if (!respuesta.ok) {
    throw new Error('No se pudieron obtener las incidencias')
  }

  const datos = await respuesta.json()
  setIncidencias(datos)

  const respuestaCompleta = await fetch(
    'http://127.0.0.1:8000/incidencias'
  )

  if (!respuestaCompleta.ok) {
    throw new Error('No se pudieron obtener todas las incidencias')
  }

  const todas = await respuestaCompleta.json()
  setTodasLasIncidencias(todas)

} catch (error) {
  setError(error.message)
} finally {
  setCargando(false)
}

}

cargarIncidencias()
}, [filtroPrioridad, filtroEstado])

const totalIncidencias = todasLasIncidencias.length
const incidenciasVisibles = incidencias.filter((incidencia) => {
  const coincideCategoria =
    filtroCategoria === '' || incidencia.categoria === filtroCategoria

  const coincideId =
    busquedaId === '' || incidencia.id === Number(busquedaId)

  const coincideTitulo = incidencia.titulo
    .toLocaleLowerCase('es')
    .includes(busquedaTitulo.trim().toLocaleLowerCase('es'))

  return coincideCategoria && coincideId && coincideTitulo
})

const incidenciasOrdenadas = [...incidenciasVisibles].sort((a, b) => {
  if (ordenColumna === null) return 0

  let comparacion = 0

  if (ordenColumna === 'id') {
    comparacion = a.id - b.id
  }

  if (ordenColumna === 'prioridad') {
    const ordenPrioridad = {
      Alta: 1,
      Media: 2,
      Baja: 3,
    }

    comparacion =
      ordenPrioridad[a.prioridad] - ordenPrioridad[b.prioridad]
  }

  if (ordenColumna === 'estado') {
    const ordenEstado = {
      Pendiente: 1,
      'En progreso': 2,
      Resuelta: 3,
    }

    comparacion =
      ordenEstado[a.estado] - ordenEstado[b.estado]
  }

  if (ordenColumna === 'fecha_creacion') {
    comparacion =
      new Date(a.fecha_creacion).getTime() -
      new Date(b.fecha_creacion).getTime()
  }

  return ordenDireccion === 'asc' ? comparacion : -comparacion
})

const totalPaginas = Math.max(
  1,
  Math.ceil(incidenciasVisibles.length / incidenciasPorPagina)
)

const paginaMostrada = Math.min(paginaActual, totalPaginas)

const inicioPagina = (paginaMostrada - 1) * incidenciasPorPagina

const incidenciasPaginadas = incidenciasOrdenadas.slice(
  inicioPagina,
  inicioPagina + incidenciasPorPagina
)

const exportacionDeshabilitada =
  busquedaId !== '' ||
  cargando ||
  Boolean(error) ||
  incidenciasVisibles.length === 0

const prioridadAlta = todasLasIncidencias.filter(
  (incidencia) => incidencia.prioridad === 'Alta'
).length

const prioridadMedia = todasLasIncidencias.filter(
  (incidencia) => incidencia.prioridad === 'Media'
).length

const prioridadBaja = todasLasIncidencias.filter(
  (incidencia) => incidencia.prioridad === 'Baja'
).length

const pendientes = todasLasIncidencias.filter(
  (incidencia) => incidencia.estado === 'Pendiente'
).length

const enProgreso = todasLasIncidencias.filter(
  (incidencia) => incidencia.estado === 'En progreso'
).length

const resueltas = todasLasIncidencias.filter(
  (incidencia) => incidencia.estado === 'Resuelta'
).length

const datosGraficoEstados = [
  { nombre: 'Pendientes', cantidad: pendientes, color: '#F59E0B' },
  { nombre: 'En progreso', cantidad: enProgreso, color: '#3B82F6' },
  { nombre: 'Resueltas', cantidad: resueltas, color: '#22C55E' },
]

const datosGraficoPrioridades = [
  { nombre: 'Alta', cantidad: prioridadAlta, color: '#EF4444' },
  { nombre: 'Media', cantidad: prioridadMedia, color: '#F59E0B' },
  { nombre: 'Baja', cantidad: prioridadBaja, color: '#22C55E' },
]

function abrirIncidencia(incidencia) {
  setErroresEdicion({})
  setModoEdicion(false)
  setIncidenciaSeleccionada(incidencia)
}

function cerrarDetalle() {
  setErroresEdicion({})
  setModoEdicion(false)
  setIncidenciaSeleccionada(null)
}

function cancelarEdicion() {
  setErroresEdicion({})
  setModoEdicion(false)
  setTituloEditado(incidenciaSeleccionada.titulo)
  setDescripcionEditada(incidenciaSeleccionada.descripcion)
  setPrioridadEditada(incidenciaSeleccionada.prioridad)
}

function iniciarEdicion() {
  setErroresEdicion({})
  setTituloEditado(incidenciaSeleccionada.titulo)
  setDescripcionEditada(incidenciaSeleccionada.descripcion)
  setPrioridadEditada(incidenciaSeleccionada.prioridad)
  setModoEdicion(true)
}


async function guardarEdicion() {
  const nuevosErrores = {}

  if (!tituloEditado.trim()) {
    nuevosErrores.titulo = 'El título no puede estar vacío.'
  }

  if (!descripcionEditada.trim()) {
    nuevosErrores.descripcion = 'La descripción no puede estar vacía.'
  }

  if (Object.keys(nuevosErrores).length > 0) {
    setErroresEdicion(nuevosErrores)
    return
  }

  setErroresEdicion({})

  try {
    const respuesta = await fetch(
      `http://127.0.0.1:8000/incidencias/${incidenciaSeleccionada.id}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          titulo: tituloEditado,
          categoria: incidenciaSeleccionada.categoria,
          descripcion: descripcionEditada,
          prioridad: prioridadEditada,
        }),
      }
    )

    if (!respuesta.ok) {
      const errorApi = await respuesta.json()
      throw new Error(
        errorApi.detail || 'No se pudo actualizar la incidencia'
      )
    }

    const incidenciaActualizada = await respuesta.json()

    setIncidenciaSeleccionada(incidenciaActualizada)


    const incidenciasActualizadas = todasLasIncidencias.map((incidencia) =>
      incidencia.id === incidenciaActualizada.id
        ? incidenciaActualizada
        : incidencia
    )

    setTodasLasIncidencias(incidenciasActualizadas)

    const incidenciasFiltradas = incidenciasActualizadas.filter((incidencia) => {
      const coincidePrioridad =
        filtroPrioridad === '' || incidencia.prioridad === filtroPrioridad

      const coincideEstado =
        filtroEstado === '' || incidencia.estado === filtroEstado

      return coincidePrioridad && coincideEstado
    })

    const ordenEstado = {
      Pendiente: 0,
      'En progreso': 0,
      Resuelta: 1,
    }

    const ordenPrioridad = {
      Alta: 1,
      Media: 2,
      Baja: 3,
    }

    incidenciasFiltradas.sort((a, b) => {
      const diferenciaEstado = ordenEstado[a.estado] - ordenEstado[b.estado]
      if (diferenciaEstado !== 0) return diferenciaEstado

      const diferenciaPrioridad =
        ordenPrioridad[a.prioridad] - ordenPrioridad[b.prioridad]
      if (diferenciaPrioridad !== 0) return diferenciaPrioridad

      return new Date(a.fecha_creacion).getTime() -
        new Date(b.fecha_creacion).getTime()
    })

    setIncidencias(incidenciasFiltradas)

    setErroresEdicion({})
    setModoEdicion(false)
  } catch (error) {
    setErroresEdicion({ general: error.message })
  }
}

async function cambiarEstadoIncidencia() {
  const endpoint =
    incidenciaSeleccionada.estado === 'Pendiente'
      ? 'iniciar'
      : 'resolver'

  try {
    const respuesta = await fetch(
      `http://127.0.0.1:8000/incidencias/${incidenciaSeleccionada.id}/${endpoint}`,
      { method: 'POST' }
    )

    if (!respuesta.ok) {
      const errorApi = await respuesta.json()
      throw new Error(
        errorApi.detail || 'No se pudo cambiar el estado de la incidencia'
      )
    }

    const incidenciaActualizada = await respuesta.json()

   // Actualizar el detalle que está abierto en el modal.
    setIncidenciaSeleccionada(incidenciaActualizada)

    // Volver a consultar la lista completa y obtener el orden del backend.
    const respuestaLista = await fetch(
      'http://127.0.0.1:8000/incidencias'
    )

    if (!respuestaLista.ok) {
      throw new Error('No se pudo actualizar la lista de incidencias')
    }

    const incidenciasActualizadas = await respuestaLista.json()    

    setTodasLasIncidencias(incidenciasActualizadas)

    // Mantener ambos filtros y el orden recibido del backend.
    const incidenciasFiltradas = incidenciasActualizadas.filter((incidencia) => {
      const coincidePrioridad =
        filtroPrioridad === '' || incidencia.prioridad === filtroPrioridad

      const coincideEstado =
        filtroEstado === '' || incidencia.estado === filtroEstado

      return coincidePrioridad && coincideEstado
    })

    setIncidencias(incidenciasFiltradas)
  } catch (error) {
    alert(error.message)
  }
}

async function eliminarIncidencia() {
  const confirmar = window.confirm(
    `¿Estás seguro de que deseas eliminar la incidencia "${incidenciaSeleccionada.titulo}"?`
  )

  if (!confirmar) {
    return
  }

  try {
    const respuesta = await fetch(
      `http://127.0.0.1:8000/incidencias/${incidenciaSeleccionada.id}`,
      {
        method: 'DELETE',
      }
    )

    if (!respuesta.ok) {
      throw new Error('No se pudo eliminar la incidencia')
    }

    setIncidencias((anteriores) =>
      anteriores.filter(
        (incidencia) => incidencia.id !== incidenciaSeleccionada.id
      )
    )

    setTodasLasIncidencias((anteriores) =>
      anteriores.filter(
        (incidencia) => incidencia.id !== incidenciaSeleccionada.id
      )
    )

    setIncidenciaSeleccionada(null)
    setErroresEdicion({})
    setModoEdicion(false)
  } catch (error) {
    alert(error.message)
  }
}


return (
<main className="dashboard">
<header className="dashboard-header">
<div>
<h1>Sistema de Gestión de Incidencias</h1>
<p>Administra y consulta las incidencias registradas.</p>
</div>
    <div className="header-actions">
      {vistaActual !== 'inicio' && (
        <button
          type="button"
          className="btn-secondary"
          onClick={() => cambiarVista('inicio')}
        >
          Volver al inicio
        </button>
      )}      
      <button
        className="btn-secondary"
        type="button"
        onClick={() => cambiarVista('estadisticas')}
      >
        <BarChart3 size={18} aria-hidden="true" />
        <span>Estadísticas</span>
      </button>

      <button
        className="btn-primary"
        type="button"
        onClick={() => cambiarVista('nueva')}
      >
        <Plus size={18} aria-hidden="true" />
        <span>Nueva incidencia</span>
      </button>
    </div>
  </header>

  {vistaActual === 'inicio' && (
    <>
  <section className="summary">
    <article className="summary-card">
      <div className="summary-label">
        <span>Total de incidencias</span>
        <span className="summary-icon icon-total"><Layers size={20} /></span>
      </div>
      <strong>{totalIncidencias}</strong>
      <p>Incidencias registradas</p>
    </article>

    <article className="summary-card">
      <div className="summary-label">
        <span>Prioridad alta</span>
        <span className="summary-icon icon-alta"><AlertTriangle size={20} /></span>
      </div>
      <strong>{prioridadAlta}</strong>
      <p>Requieren mayor atención</p>
    </article>

    <article className="summary-card">
      <div className="summary-label">
        <span>Prioridad media</span>
        <span className="summary-icon icon-media"><Clock size={20} /></span>
      </div>
      <strong>{prioridadMedia}</strong>
      <p>Requieren cierta atención</p>
    </article>

    <article className="summary-card">
      <div className="summary-label">
        <span>Prioridad baja</span>
        <span className="summary-icon icon-baja"><CheckCircle size={20} /></span>
      </div>
      <strong>{prioridadBaja}</strong>
      <p>Menor urgencia</p>
    </article>

    <article className="summary-card">
      <div className="summary-label">
        <span>Pendientes</span>
        <span className="summary-icon icon-alta">
          <Clock size={20} />
        </span>
      </div>
      <strong>{pendientes}</strong>
      <p>Esperando atención</p>
    </article>

    <article className="summary-card">
      <div className="summary-label">
        <span>En progreso</span>
        <span className="summary-icon icon-media">
          <Clock size={20} />
        </span>
      </div>
      <strong>{enProgreso}</strong>
      <p>Incidencias en atención</p>
    </article>

    <article className="summary-card">
      <div className="summary-label">
        <span>Resueltas</span>
        <span className="summary-icon icon-baja">
          <CheckCircle size={20} />
        </span>
      </div>
      <strong>{resueltas}</strong>
      <p>Incidencias solucionadas</p>
    </article>
  </section>
  </>
)}
  {vistaActual === 'estadisticas' && (
  <section className="charts-grid">
    {[
      {
        titulo: 'Incidencias por estado',
        descripcion: 'Distribución según el estado actual',
        datos: datosGraficoEstados,
      },
      {
        titulo: 'Incidencias por prioridad',
        descripcion: 'Distribución según el nivel de urgencia',
        datos: datosGraficoPrioridades,
      },
    ].map((grafico) => (
      <article className="chart-panel" key={grafico.titulo}>
        <div className="chart-header">
          <h2>{grafico.titulo}</h2>
          <p>{grafico.descripcion}</p>
        </div>

        <div className="chart-content">
          <div className="chart-container">
            {totalIncidencias > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={grafico.datos}
                    dataKey="cantidad"
                    nameKey="nombre"
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={90}
                    paddingAngle={2}
                    stroke="none"
                  >
                    {grafico.datos.map((dato) => (
                      <Cell key={dato.nombre} fill={dato.color} />
                    ))}
                    <Label
                      content={({ viewBox }) => {
                        if (!viewBox || !('cx' in viewBox)) return null

                        const { cx, cy } = viewBox

                        return (
                          <text
                            x={cx}
                            y={cy}
                            textAnchor="middle"
                            dominantBaseline="middle"
                          >
                            <tspan
                              x={cx}
                              dy="-7"
                              fontSize="28"
                              fontWeight="700"
                              fill="#0f172a"
                            >
                              {totalIncidencias}
                            </tspan>
                            <tspan
                              x={cx}
                              dy="22"
                              fontSize="11"
                              fill="#64748b"
                            >
                              Incidencias
                            </tspan>
                          </text>
                        )
                      }}
                    />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p>No hay incidencias para mostrar.</p>
            )}
          </div>

          <div className="chart-legend">
            {grafico.datos.map((dato) => (
              <div className="chart-legend-item" key={dato.nombre}>
                <span
                  className="chart-legend-color"
                  style={{ backgroundColor: dato.color }}
                />
                <span>{dato.nombre}</span>
                <strong>{dato.cantidad}</strong>
                <span className="chart-percentage">
                  {totalIncidencias > 0
                    ? `${Math.round((dato.cantidad / totalIncidencias) * 100)}%`
                    : '0%'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </article>
    ))}
      </section>
    )}

    {vistaActual === 'nueva' && (
    <section className="incidents-panel form-panel">
      <h2>Nueva incidencia</h2>
      {error && <p className="message error">{error}</p>}
      <form className="incident-form" onSubmit={guardarIncidencia}>

        <label htmlFor="titulo">Título de la incidencia</label>

        <input
          id="titulo"
          type="text"
          value={titulo}
          onChange={(evento) => setTitulo(evento.target.value)}
          placeholder="Ej. La impresora no funciona"
          maxLength={200}
          required
        />
        <label htmlFor="categoria">Categoría</label>

        <select
          id="categoria"
          value={categoria}
          onChange={(evento) => setCategoria(evento.target.value)}
          required
        >
          <option value="">Selecciona una categoría</option>
          <option value="Informática (TI)">Informática (TI)</option>
          <option value="Mantenimiento e instalaciones">Mantenimiento e instalaciones</option>
          <option value="Seguridad">Seguridad</option>
          <option value="Administración">Administración</option>
          <option value="Operaciones y logística">Operaciones y logística</option>
          <option value="Otros">Otros</option>
        </select>

        <label htmlFor="descripcion">Descripción del problema</label>

        <textarea
          id="descripcion"
          value={descripcion}
          onChange={(evento) => setDescripcion(evento.target.value)}
          placeholder="Explica qué ocurre, cuándo comenzó y qué has observado..."
          rows={4}
          maxLength={2000}
          required
        />
        <label htmlFor="prioridad">Prioridad</label>

        <select
          id="prioridad"
          value={prioridad}
          onChange={(evento) => setPrioridad(evento.target.value)}
        >
          <option value="Alta">Alta</option>
          <option value="Media">Media</option>
          <option value="Baja">Baja</option>
        </select>

        <div className="form-actions">
          <button
            className="btn-secondary"
            type="button"
            onClick={() => cambiarVista('inicio')}
          >
            Cancelar
          </button>

          <button className="btn-primary" type="submit">
            Guardar incidencia
          </button>
        </div>
      </form>
    </section>
  )}
{vistaActual === 'inicio' && (
  <section className="incidents-panel">
    <div className="incidents-toolbar">
    <div className="incidents-toolbar-title">
      <h2>Incidencias registradas</h2>

      <div className="export-actions">
        <button
          type="button"
          className="btn-export"
          onClick={() => descargarIncidencias('excel')}
          disabled={exportacionDeshabilitada}
          aria-describedby={
            exportacionDeshabilitada && !cargando && !error
              ? 'exportacion-no-disponible'
              : undefined
          }
        >
          <Download size={16} aria-hidden="true" />
          Excel
        </button>

        <button
          type="button"
          className="btn-export"
          onClick={() => descargarIncidencias('csv')}
          disabled={exportacionDeshabilitada}
          aria-describedby={
            exportacionDeshabilitada && !cargando && !error
              ? 'exportacion-no-disponible'
              : undefined
          }
        >
          <Download size={16} aria-hidden="true" />
          CSV
        </button>
          {exportacionDeshabilitada && !cargando && !error && (
            <p id="exportacion-no-disponible" className="export-hint" role="status">
              {busquedaId !== ''
                ? 'Limpia la búsqueda por ID para exportar Excel o CSV.'
                : 'No hay incidencias disponibles para exportar con los filtros actuales.'}
            </p>
          )}
      </div>
    </div>

    <div className="filtros">
        <div className="search-unified">
          <div className="search-mode" role="group" aria-label="Tipo de búsqueda">
            <button
              type="button"
              className={tipoBusqueda === 'titulo' ? 'active' : ''}
              aria-pressed={tipoBusqueda === 'titulo'}
              onClick={() => cambiarTipoBusqueda('titulo')}
            >
              Título
            </button>

            <button
              type="button"
              className={tipoBusqueda === 'id' ? 'active' : ''}
              aria-pressed={tipoBusqueda === 'id'}
              onClick={() => cambiarTipoBusqueda('id')}
            >
              ID
            </button>
          </div>

          <input
            type={tipoBusqueda === 'id' ? 'number' : 'search'}
            min={tipoBusqueda === 'id' ? '1' : undefined}
            placeholder={tipoBusqueda === 'id' ? 'Buscar ID...' : 'Buscar por título...'}
            aria-label={tipoBusqueda === 'id' ? 'Buscar incidencia por ID' : 'Buscar incidencia por título'}
            value={tipoBusqueda === 'id' ? busquedaId : busquedaTitulo}
            onChange={(evento) => {
              if (tipoBusqueda === 'id') {
                setBusquedaId(evento.target.value)
              } else {
                setBusquedaTitulo(evento.target.value)
              }
            }}
            className="search-unified-input"
          />
        </div>
        <SlidersHorizontal className="filters-icon" size={17} aria-hidden="true" />
        {[
          { nombre: 'Categoría', valor: filtroCategoria, cambiar: setFiltroCategoria,
            opciones: ['Informática (TI)', 'Mantenimiento e instalaciones', 'Seguridad',
              'Administración', 'Operaciones y logística', 'Otros'] },
          { nombre: 'Prioridad', valor: filtroPrioridad, cambiar: setFiltroPrioridad,
            opciones: ['Alta', 'Media', 'Baja'] },
          { nombre: 'Estado', valor: filtroEstado, cambiar: setFiltroEstado,
            opciones: ['Pendiente', 'En progreso', 'Resuelta'] },
        ].map(({ nombre, valor, cambiar, opciones }) => (
          <details className="filter-chip" name="filtros-incidencias" key={nombre}
            onToggle={(evento) => {
              if (evento.currentTarget.open) {
                evento.currentTarget.parentElement.querySelectorAll('details').forEach((detalle) => {
                  if (detalle !== evento.currentTarget) detalle.removeAttribute('open')
                })
              }
            }}
            onKeyDown={(evento) => {
              if (evento.key === 'Escape') {
                evento.currentTarget.removeAttribute('open')
                evento.currentTarget.querySelector('summary').focus()
              }
            }}>
            <summary className={valor ? 'is-active' : ''}>
              {valor && <span aria-hidden="true">✓ </span>}
              {nombre}{valor ? `: ${valor}` : ''}
              <span className="chip-chevron" aria-hidden="true">⌄</span>
            </summary>
            <div className="chip-options" role="group" aria-label={`Filtrar por ${nombre.toLowerCase()}`}>
              {opciones.map((opcion) => (
                <button type="button" key={opcion} aria-pressed={valor === opcion}
                  onClick={(evento) => {
                    cambiar(valor === opcion ? '' : opcion)
                    const detalle = evento.currentTarget.closest('details')
                    detalle.removeAttribute('open')
                    detalle.querySelector('summary').focus()
                  }}>
                  {opcion}<span aria-hidden="true">{valor === opcion ? '✓' : ''}</span>
                </button>
              ))}
            </div>
          </details>
        ))}
        {(filtroPrioridad || filtroEstado || filtroCategoria || busquedaId || busquedaTitulo) && (
          <button type="button" className="filters-clear" onClick={() => {
            setFiltroPrioridad('')
            setFiltroEstado('')
            setFiltroCategoria('')
            setBusquedaId('')
            setBusquedaTitulo('')
          }}>Limpiar filtros</button>
        )}
      </div>
    </div>


    {cargando ? (
      <p className="message">Cargando incidencias...</p>
    ) : error ? (
      <p className="message error">{error}</p>
    ) : incidenciasVisibles.length === 0 ? (
      <p className="message">No hay incidencias registradas.</p>
    ) : (
      <><div className="incidents-table-scroll">
                <table className="incidents-table">
                  <thead>
                    <tr>
                      {[
                        { campo: 'id', nombre: 'ID' },
                        { campo: null, nombre: 'Título' },
                        { campo: null, nombre: 'Categoría' },
                        { campo: null, nombre: 'Descripción' },
                        { campo: 'prioridad', nombre: 'Prioridad' },
                        { campo: 'estado', nombre: 'Estado' },
                        { campo: 'fecha_creacion', nombre: 'Fecha de creación' },
                      ].map(({ campo, nombre }) => (
                        <th
                          key={nombre}
                          aria-sort={
                            campo && ordenColumna === campo
                              ? ordenDireccion === 'asc'
                                ? 'ascending'
                                : 'descending'
                              : undefined
                          }
                        >
                          {campo ? (
                            <button
                              type="button"
                              className="table-sort-button"
                              onClick={() => cambiarOrden(campo)}
                            >
                              {nombre}

                              {ordenColumna === campo ? (
                                ordenDireccion === 'asc' ? (
                                  <ArrowUp size={14} aria-hidden="true" />
                                ) : (
                                  <ArrowDown size={14} aria-hidden="true" />
                                )
                              ) : (
                                <ArrowUpDown size={14} aria-hidden="true" />
                              )}
                            </button>
                          ) : (
                            nombre
                          )}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    {incidenciasPaginadas.map((incidencia) => (
                      <tr
                        key={incidencia.id}
                        onClick={() => abrirIncidencia(incidencia)}
                        className="incident-row"
                        tabIndex={0}
                        onKeyDown={(evento) => {
                          if (evento.key === 'Enter' || evento.key === ' ') {
                            evento.preventDefault()
                            abrirIncidencia(incidencia)
                          }
                        } }
                        aria-label={`Abrir detalle de la incidencia ${incidencia.titulo}`}
                      >

                        <td>{incidencia.id}</td>
                        <td>{incidencia.titulo}</td>
                        <td>{incidencia.categoria}</td>
                        <td className="description-cell">
                          {incidencia.descripcion.length > 70
                            ? `${incidencia.descripcion.slice(0, 70)}...`
                            : incidencia.descripcion}
                        </td>
                        <td>
                          <span
                            className={`priority priority-${{
                              Alta: 'high',
                              Media: 'medium',
                              Baja: 'low',
                            }[incidencia.prioridad]}`}
                          >
                            {incidencia.prioridad}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`status ${incidencia.estado === 'Pendiente'
                                ? 'status-pending'
                                : incidencia.estado === 'En progreso'
                                  ? 'status-progress'
                                  : 'status-resolved'}`}
                          >
                            {incidencia.estado}
                          </span>
                        </td>
                        <td>
                          {new Date(incidencia.fecha_creacion).toLocaleDateString(
                            'es-CL',
                            {
                              timeZone: 'America/Santiago',
                              day: '2-digit',
                              month: '2-digit',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                              hour12: false
                            }
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div><div className="pagination">
                  <span className="pagination-info">
                    Mostrando <strong>{inicioPagina + 1}–{Math.min(inicioPagina + incidenciasPorPagina, incidenciasVisibles.length)}</strong>
                    {' '}de <strong>{incidenciasVisibles.length}</strong> incidencias
                  </span>

                  <div className="pagination-controls">
                    <button
                      type="button"
                      disabled={paginaMostrada === 1}
                      onClick={() => setPaginaActual(paginaMostrada - 1)}
                      aria-label="Ir a la página anterior"
                    >
                      <ChevronLeft size={16} aria-hidden="true" />
                      Anterior
                    </button>

                    <span className="pagination-current" aria-live="polite" aria-atomic="true">
                      Página <strong>{paginaMostrada}</strong> de {totalPaginas}
                    </span>

                    <button
                      type="button"
                      disabled={paginaMostrada === totalPaginas}
                      onClick={() => setPaginaActual(paginaMostrada + 1)}
                      aria-label="Ir a la página siguiente"
                    >
                      Siguiente
                      <ChevronRight size={16} aria-hidden="true" />
                    </button>
                  </div>
                </div></>
    )}
  </section>
  )}
  {incidenciaSeleccionada && (
    <div className="modal-overlay" onClick={cerrarDetalle}>
      <div
        className="incident-modal"
        onClick={(evento) => evento.stopPropagation()}
      >
        <div className="modal-header">
          <h2>Detalle de incidencia #{incidenciaSeleccionada.id}</h2>

          <button
            type="button"
            className="modal-close"
            onClick={cerrarDetalle}
            aria-label="Cerrar detalle"
          >
            <X size={20} aria-hidden="true" />
          </button>
        </div>
        <div className="modal-body">
          {modoEdicion ? (
            <>
              <label htmlFor="tituloEditado">Título</label>
              <input
                id="tituloEditado"
                type="text"
                value={tituloEditado}
                onChange={(evento) => {
                  setTituloEditado(evento.target.value)
                  setErroresEdicion((anteriores) => ({ ...anteriores, titulo: '' }))
                }}
                maxLength={200}
                aria-invalid={Boolean(erroresEdicion.titulo)}
                aria-describedby={erroresEdicion.titulo ? 'error-titulo-editado' : undefined}
                required
              />
              {erroresEdicion.titulo && (
                <p id="error-titulo-editado" className="error-edicion" role="alert">
                  {erroresEdicion.titulo}
                </p>
              )}

              <label htmlFor="descripcionEditada">Descripción</label>
              <textarea
                id="descripcionEditada"
                value={descripcionEditada}
                onChange={(evento) => {
                  setDescripcionEditada(evento.target.value)
                  setErroresEdicion((anteriores) => ({ ...anteriores, descripcion: '' }))
                }}
                rows={4}
                maxLength={2000}
                aria-invalid={Boolean(erroresEdicion.descripcion)}
                aria-describedby={erroresEdicion.descripcion ? 'error-descripcion-editada' : undefined}
                required
              />
              {erroresEdicion.descripcion && (
                <p id="error-descripcion-editada" className="error-edicion" role="alert">
                  {erroresEdicion.descripcion}
                </p>
              )}

              <label htmlFor="prioridadEditada">Prioridad</label>
              <select
                id="prioridadEditada"
                value={prioridadEditada}
                onChange={(evento) => setPrioridadEditada(evento.target.value)}
              >
                <option value="Alta">Alta</option>
                <option value="Media">Media</option>
                <option value="Baja">Baja</option>
              </select>

              {erroresEdicion.general && (
                <p className="error-edicion" role="alert">
                  {erroresEdicion.general}
                </p>
              )}
            </>
          ) : (
            <>
              <label>Título</label>
              <p>{incidenciaSeleccionada.titulo}</p>

              <label>Categoría</label>
              <p>{incidenciaSeleccionada.categoria}</p>

              <label>Descripción</label>
              <p className="modal-description">
                {incidenciaSeleccionada.descripcion}
              </p>

              <label>Prioridad</label>
              <p>
                <span
                  className={`priority priority-${{
                    Alta: 'high',
                    Media: 'medium',
                    Baja: 'low',
                  }[incidenciaSeleccionada.prioridad]}`}
                >
                  {incidenciaSeleccionada.prioridad}
                </span>
              </p>

              <label>Estado</label>
              <p>
                <span
                  className={`status status-${{
                    'Pendiente': 'pending',
                    'En progreso': 'progress',
                    'Resuelta': 'resolved',
                  }[incidenciaSeleccionada.estado]}`}
                >
                  {incidenciaSeleccionada.estado}
                </span>
              </p>

              {incidenciaSeleccionada.fecha_resolucion && (
                <>
                  <label>Fecha de resolución</label>
                  <p>
                    {new Date(
                      incidenciaSeleccionada.fecha_resolucion
                    ).toLocaleString('es-CL', {
                      timeZone: 'America/Santiago',
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false,
                    })}
                  </p>
                </>
              )}

              <label>Fecha de creación</label>
              <p>
                {new Date(
                  incidenciaSeleccionada.fecha_creacion
                ).toLocaleString('es-CL', {
                  timeZone: 'America/Santiago',
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                })}
              </p>
            </>
          )}
        </div>
        <div className="modal-footer">
          {modoEdicion ? (
            <>
              <button
                type="button"
                className="btn-secondary"
                onClick={cancelarEdicion}
              >
                Cancelar edición
              </button>

              <button
                type="button"
                className="btn-primary"
                onClick={guardarEdicion}
              >
                Guardar cambios
              </button>
            </>
          ) : (
            <>
              {incidenciaSeleccionada.estado !== 'Resuelta' && (
                <button
                  type="button"
                  className={
                  incidenciaSeleccionada.estado === 'Pendiente'
                    ? 'btn-estado btn-iniciar'
                    : 'btn-estado btn-resolver'
                  }
                  onClick={cambiarEstadoIncidencia}
                >
                  {incidenciaSeleccionada.estado === 'Pendiente'
                    ? 'Iniciar atención'
                    : 'Resolver incidencia'}
                </button>
              )}

              <button
                type="button"
                className="btn-secondary"
                onClick={cerrarDetalle}
              >
                Cerrar
              </button>

              <button
                type="button"
                className="btn-primary"
                onClick={iniciarEdicion}
              >
                Editar incidencia
              </button>

              <button
                type="button"
                className="btn-eliminar"
                onClick={eliminarIncidencia}
              >
                Eliminar incidencia
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )}

</main>

)
}

export default App
