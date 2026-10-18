import { useState, useEffect } from 'react'
import './App.css'
import {
  Layers,
  AlertTriangle,
  Clock,
  CheckCircle,
} from 'lucide-react'

function App() {
const [incidencias, setIncidencias] = useState([])
const [todasLasIncidencias, setTodasLasIncidencias] = useState([])
const [cargando, setCargando] = useState(true)
const [error, setError] = useState('')
const [mostrarFormulario, setMostrarFormulario] = useState(false)
const [titulo, setTitulo] = useState('')
const [descripcion, setDescripcion] = useState('')
const [prioridad, setPrioridad] = useState('Media')
const [filtroPrioridad, setFiltroPrioridad] = useState('')
const [incidenciaSeleccionada, setIncidenciaSeleccionada] = useState(null)
const [modoEdicion, setModoEdicion] = useState(false)
const [tituloEditado, setTituloEditado] = useState('')
const [descripcionEditada, setDescripcionEditada] = useState('')
const [prioridadEditada, setPrioridadEditada] = useState('')
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

const nuevaIncidencia = await respuesta.json()


setTodasLasIncidencias((anteriores) => [
  ...anteriores,
  nuevaIncidencia,
])

setTitulo('')
setDescripcion('')
setPrioridad('Media')
setMostrarFormulario(false)

if (filtroPrioridad === '') {
  setIncidencias((anteriores) => [
    ...anteriores,
    nuevaIncidencia,
  ])
} else {
  setFiltroPrioridad('')
}


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

  const respuesta = await fetch(url)

  if (!respuesta.ok) {
    throw new Error('No se pudieron obtener las incidencias')
  }

  const datos = await respuesta.json()
  setIncidencias(datos)

  if (filtroPrioridad === '') {
    setTodasLasIncidencias(datos)
  }
} catch (error) {
  setError(error.message)
} finally {
  setCargando(false)
}

}

cargarIncidencias()
}, [filtroPrioridad])

const totalIncidencias = todasLasIncidencias.length

const prioridadAlta = todasLasIncidencias.filter(
  (incidencia) => incidencia.prioridad === 'Alta'
).length

const prioridadMedia = todasLasIncidencias.filter(
  (incidencia) => incidencia.prioridad === 'Media'
).length

const prioridadBaja = todasLasIncidencias.filter(
  (incidencia) => incidencia.prioridad === 'Baja'
).length

function iniciarEdicion() {
  setTituloEditado(incidenciaSeleccionada.titulo)
  setDescripcionEditada(incidenciaSeleccionada.descripcion)
  setPrioridadEditada(incidenciaSeleccionada.prioridad)
  setModoEdicion(true)
}


async function guardarEdicion() {
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

    setIncidencias((anteriores) => {
      let actualizadas = anteriores.map((incidencia) =>
        incidencia.id === incidenciaActualizada.id
          ? incidenciaActualizada
          : incidencia
      )

      if (
        filtroPrioridad !== '' &&
        incidenciaActualizada.prioridad !== filtroPrioridad
      ) {
        actualizadas = actualizadas.filter(
          (incidencia) => incidencia.id !== incidenciaActualizada.id
        )
      }

      const ordenPrioridad = {
        Alta: 1,
        Media: 2,
        Baja: 3,
      }

      return actualizadas.sort((a, b) => {
        const diferenciaPrioridad =
          ordenPrioridad[a.prioridad] - ordenPrioridad[b.prioridad]

        if (diferenciaPrioridad !== 0) {
          return diferenciaPrioridad
        }

        return (
          new Date(a.fecha_creacion).getTime() -
          new Date(b.fecha_creacion).getTime()
        )
      })


    })

    setTodasLasIncidencias((anteriores) =>
      anteriores.map((incidencia) =>
        incidencia.id === incidenciaActualizada.id
          ? incidenciaActualizada
          : incidencia
      )
    )

    setModoEdicion(false)
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
    <button
      className="btn-primary"
      type="button"
      onClick={() => setMostrarFormulario(true)}
    >
      + Nueva incidencia
    </button>
  </header>


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
  </section>


  {mostrarFormulario && (
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
            onClick={() => setMostrarFormulario(false)}
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

  <section className="incidents-panel">
    <div className="incidents-toolbar">
      <h2>Incidencias registradas</h2>

      <div className="filter-control">
        <label htmlFor="filtro-prioridad">
          Prioridad:
        </label>

        <select
          id="filtro-prioridad"
          value={filtroPrioridad}
          onChange={(evento) => setFiltroPrioridad(evento.target.value)}
        >
          <option value="">Todas</option>
          <option value="Alta">Alta</option>
          <option value="Media">Media</option>
          <option value="Baja">Baja</option>
        </select>
      </div>
    </div>


    {cargando ? (
      <p className="message">Cargando incidencias...</p>
    ) : error ? (
      <p className="message error">{error}</p>
    ) : incidencias.length === 0 ? (
      <p className="message">No hay incidencias registradas.</p>
    ) : (
      <table className="incidents-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Descripción</th>
            <th>Prioridad</th>
            <th>Fecha de creación</th>
          </tr>
        </thead>

        <tbody>
          {incidencias.map((incidencia) => (
            <tr 
            key={incidencia.id}
            onClick={() => {
            setModoEdicion(false)
            setIncidenciaSeleccionada(incidencia)
            }}
            className="incident-row"
            >
              
              <td>{incidencia.id}</td>
              <td>{incidencia.titulo}</td>
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
                {new Date(incidencia.fecha_creacion).toLocaleDateString(
                  'es-CL',
                  {     timeZone: 'America/Santiago',
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false}
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </section>
  {incidenciaSeleccionada && (
    <div className="modal-overlay" onClick={() => {setModoEdicion(false) ; setIncidenciaSeleccionada(null)}}>
      <div
        className="incident-modal"
        onClick={(evento) => evento.stopPropagation()}
      >
        <div className="modal-header">
          <h2>Detalle de incidencia #{incidenciaSeleccionada.id}</h2>

          <button
            type="button"
            className="modal-close"
            onClick={() => {
              setModoEdicion(false)
              setIncidenciaSeleccionada(null)
            }}
            aria-label="Cerrar detalle"
          >
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
                onChange={(evento) => setTituloEditado(evento.target.value)}
                maxLength={200}
                required
              />

              <label htmlFor="descripcionEditada">Descripción</label>
              <textarea
                id="descripcionEditada"
                value={descripcionEditada}
                onChange={(evento) => setDescripcionEditada(evento.target.value)}
                rows={4}
                maxLength={2000}
                required
              />

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
            </>
          ) : (
            <>
              <label>Título</label>
              <p>{incidenciaSeleccionada.titulo}</p>

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
                onClick={() => {
                  setModoEdicion(false)
                  setTituloEditado(incidenciaSeleccionada.titulo)
                  setDescripcionEditada(incidenciaSeleccionada.descripcion)
                  setPrioridadEditada(incidenciaSeleccionada.prioridad)
                }}
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
              <button
                type="button"
                className="btn-secondary"
                onClick={() => {
                  setModoEdicion(false)
                  setIncidenciaSeleccionada(null)
                }}
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