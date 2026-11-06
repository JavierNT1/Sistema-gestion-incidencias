import { afterEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { cleanup } from '@testing-library/react'
import App from './App'

// Incidencias ficticias utilizadas exclusivamente durante la prueba
const incidenciasPrueba = [
  {
    id: 1,
    titulo: 'Impresora sin conexión',
    categoria: 'Informática (TI)',
    descripcion: 'La impresora no responde.',
    prioridad: 'Media',
    estado: 'Pendiente',
    fecha_creacion: '2026-10-05T12:00:00Z',
    fecha_resolucion: null,
  },
  {
    id: 2,
    titulo: 'Filtración en el techo',
    categoria: 'Mantenimiento e instalaciones',
    descripcion: 'Se detectó una filtración.',
    prioridad: 'Alta',
    estado: 'En progreso',
    fecha_creacion: '2026-10-06T12:00:00Z',
    fecha_resolucion: null,
  },
]

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('Buscador de incidencias', () => {
  it('filtra las incidencias por título', async () => {
    // Simulamos las respuestas del backend FastAPI
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPrueba,
      })
    )

    const usuario = userEvent.setup()

    // Mostramos la aplicación dentro del entorno de pruebas
    render(<App />)

    // Esperamos a que React cargue las incidencias simuladas
    expect(await screen.findByText('Impresora sin conexión')).toBeInTheDocument()
    expect(screen.getByText('Filtración en el techo')).toBeInTheDocument()

    // Buscamos el campo de búsqueda por título
    const buscador = screen.getByRole('searchbox', {
    name: /buscar incidencia por título/i,
    })

    // Simulamos que el usuario escribe "impresora"
    await usuario.type(buscador, 'impresora')

    // Comprobamos que solo aparece la incidencia correspondiente
    await waitFor(() => {
      expect(screen.getByText('Impresora sin conexión')).toBeInTheDocument()
      expect(screen.queryByText('Filtración en el techo')).not.toBeInTheDocument()
    })
  })

    it('filtra las incidencias por ID', async () => {
    vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPrueba,
        })
    )

    const usuario = userEvent.setup()

    render(<App />)

    // Esperamos a que se carguen ambas incidencias.
    expect(
        await screen.findByText('Impresora sin conexión')
    ).toBeInTheDocument()

    // Cambiamos la búsqueda de título a ID.
    await usuario.click(
        screen.getByRole('button', { name: 'ID', pressed: false })
    )

    // Buscamos la incidencia con ID 2.
    const buscador = screen.getByRole('spinbutton', {
        name: /buscar incidencia por ID/i,
    })

    await usuario.type(buscador, '2')

    // Solo debe permanecer visible la incidencia con ID 2.
    expect(
        screen.getByText('Filtración en el techo')
    ).toBeInTheDocument()

    expect(
        screen.queryByText('Impresora sin conexión')
    ).not.toBeInTheDocument()
    })  

})

describe('Filtros de incidencias', () => {
  it('filtra las incidencias por prioridad alta', async () => {
    vi.stubGlobal(
    'fetch',
    vi.fn(async (url) => {
        const peticion = new URL(url)
        const prioridad = peticion.searchParams.get('prioridad')

        const resultado = prioridad
        ? incidenciasPrueba.filter(
            (incidencia) => incidencia.prioridad === prioridad
            )
        : incidenciasPrueba

        return {
        ok: true,
        json: async () => resultado,
        }
    })
    )

    const usuario = userEvent.setup()

    render(<App />)

    // Esperar que se carguen las dos incidencias.
    expect(
      await screen.findByText('Impresora sin conexión')
    ).toBeInTheDocument()

    // Abrir el filtro de prioridad.
    await usuario.click(
      screen.getByText('Prioridad', { selector: 'summary' })
    )

    // Seleccionar la prioridad Alta.
    await usuario.click(
      screen.getByRole('button', { name: 'Alta' })
    )

    // Solo debe aparecer la incidencia de prioridad Alta.
    expect(
      await screen.findByText('Filtración en el techo')
    ).toBeInTheDocument()

    await waitFor(() => {
      expect(
        screen.queryByText('Impresora sin conexión')
      ).not.toBeInTheDocument()
    })
  })

  it('filtra las incidencias por estado pendiente', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url) => {
        const peticion = new URL(url)
        const estado = peticion.searchParams.get('estado')

        const resultado = estado
          ? incidenciasPrueba.filter(
              (incidencia) => incidencia.estado === estado
            )
          : incidenciasPrueba

        return {
          ok: true,
          json: async () => resultado,
        }
      })
    )

    const usuario = userEvent.setup()

    render(<App />)

    // Esperamos que se carguen ambas incidencias.
    expect(
      await screen.findByText('Impresora sin conexión')
    ).toBeInTheDocument()

    // Abrimos el filtro de estado.
    await usuario.click(
      screen.getByText('Estado', { selector: 'summary' })
    )

    // Seleccionamos Pendiente.
    await usuario.click(
      screen.getByRole('button', { name: 'Pendiente' })
    )

    // Debe quedar visible la incidencia pendiente.
    expect(
      screen.getByText('Impresora sin conexión')
    ).toBeInTheDocument()

    // La incidencia en progreso debe desaparecer de la tabla.
    await waitFor(() => {
      expect(
        screen.queryByText('Filtración en el techo')
      ).not.toBeInTheDocument()
    })
  })

  it('filtra las incidencias por categoría', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPrueba,
      })
    )

    const usuario = userEvent.setup()

    render(<App />)

    // Esperamos que se carguen ambas incidencias.
    expect(
      await screen.findByText('Impresora sin conexión')
    ).toBeInTheDocument()

    // Abrimos el filtro de categoría.
    await usuario.click(
      screen.getByText('Categoría', { selector: 'summary' })
    )

    // Seleccionamos Informática (TI).
    await usuario.click(
      screen.getByRole('button', { name: 'Informática (TI)' })
    )

    // La incidencia informática debe permanecer visible.
    expect(
      screen.getByText('Impresora sin conexión')
    ).toBeInTheDocument()

    // La incidencia de mantenimiento debe desaparecer.
    expect(
      screen.queryByText('Filtración en el techo')
    ).not.toBeInTheDocument()
  })  

})

describe('Ordenamiento de incidencias', () => {
  it('ordena las incidencias por ID al hacer clic en el encabezado', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPrueba,
      })
    )

    const usuario = userEvent.setup()

    render(<App />)

    // Esperamos a que carguen las incidencias.
    expect(
      await screen.findByText('Impresora sin conexión')
    ).toBeInTheDocument()

    // Buscamos el encabezado ID dentro de la tabla.
    const encabezadoId = screen.getByRole('columnheader', {
      name: 'ID',
    }).querySelector('button')

    // Primer clic: orden ascendente (ID 1, ID 2).
    await usuario.click(encabezadoId)

    let filas = screen.getAllByRole('row').slice(1)

    expect(filas[0]).toHaveTextContent('Impresora sin conexión')
    expect(filas[1]).toHaveTextContent('Filtración en el techo')

    // Segundo clic: orden descendente (ID 2, ID 1).
    await usuario.click(encabezadoId)

    filas = screen.getAllByRole('row').slice(1)

    expect(filas[0]).toHaveTextContent('Filtración en el techo')
    expect(filas[1]).toHaveTextContent('Impresora sin conexión')
    })

  it('ordena las incidencias por prioridad', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPrueba,
      })
    )

    const usuario = userEvent.setup()

    render(<App />)

    expect(
      await screen.findByText('Impresora sin conexión')
    ).toBeInTheDocument()

    // Seleccionamos el botón de ordenamiento de la columna Prioridad.
    const encabezadoPrioridad = screen
      .getByRole('columnheader', { name: 'Prioridad' })
      .querySelector('button')

    // Primer clic: Alta antes que Media.
    await usuario.click(encabezadoPrioridad)

    let filas = screen.getAllByRole('row').slice(1)

    expect(filas[0]).toHaveTextContent('Filtración en el techo')
    expect(filas[1]).toHaveTextContent('Impresora sin conexión')

    // Segundo clic: Media antes que Alta.
    await usuario.click(encabezadoPrioridad)

    filas = screen.getAllByRole('row').slice(1)

    expect(filas[0]).toHaveTextContent('Impresora sin conexión')
    expect(filas[1]).toHaveTextContent('Filtración en el techo')
  })

  it('ordena las incidencias por estado', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPrueba,
      })
    )

    const usuario = userEvent.setup()

    render(<App />)

    expect(
      await screen.findByText('Impresora sin conexión')
    ).toBeInTheDocument()

    const encabezadoEstado = screen
      .getByRole('columnheader', { name: 'Estado' })
      .querySelector('button')

    // Primer clic: Pendiente antes que En progreso.
    await usuario.click(encabezadoEstado)

    let filas = screen.getAllByRole('row').slice(1)

    expect(filas[0]).toHaveTextContent('Impresora sin conexión')
    expect(filas[1]).toHaveTextContent('Filtración en el techo')

    // Segundo clic: En progreso antes que Pendiente.
    await usuario.click(encabezadoEstado)

    filas = screen.getAllByRole('row').slice(1)

    expect(filas[0]).toHaveTextContent('Filtración en el techo')
    expect(filas[1]).toHaveTextContent('Impresora sin conexión')
  })  

  it('ordena las incidencias por fecha de creación', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPrueba,
      })
    )

    const usuario = userEvent.setup()

    render(<App />)

    expect(
      await screen.findByText('Impresora sin conexión')
    ).toBeInTheDocument()

    const encabezadoFecha = screen
      .getByRole('columnheader', { name: 'Fecha de creación' })
      .querySelector('button')

    // Primer clic: fecha más reciente primero.
    await usuario.click(encabezadoFecha)

    let filas = screen.getAllByRole('row').slice(1)

    expect(filas[0]).toHaveTextContent('Filtración en el techo')
    expect(filas[1]).toHaveTextContent('Impresora sin conexión')

    // Segundo clic: fecha más antigua primero.
    await usuario.click(encabezadoFecha)

    filas = screen.getAllByRole('row').slice(1)

    expect(filas[0]).toHaveTextContent('Impresora sin conexión')
    expect(filas[1]).toHaveTextContent('Filtración en el techo')
  })

})

describe('Paginación de incidencias', () => {
  it('muestra 20 incidencias en la primera página', async () => {
    // Generamos 25 incidencias ficticias a partir de un modelo válido.
    const incidenciasPaginacion = Array.from(
      { length: 25 },
      (_, indice) => ({
        ...incidenciasPrueba[0],
        id: indice + 1,
        titulo: `Incidencia de prueba ${indice + 1}`,
      })
    )

    // Simulamos la respuesta de FastAPI.
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPaginacion,
      })
    )

    render(<App />)

    // Esperamos que carguen los datos.
    expect(
      await screen.findByText('Incidencia de prueba 1')
    ).toBeInTheDocument()

    // Comprobamos que la tabla muestra exactamente 20 registros.
    const tabla = screen.getByRole('table')
    const filas = tabla.querySelectorAll('tbody tr')

    expect(filas).toHaveLength(20)

    const indicadorPagina = document.querySelector('.pagination-current')

    expect(indicadorPagina).toBeInTheDocument()
    expect(indicadorPagina).toHaveTextContent(/Página\s*1\s*de\s*2/i)
  })

  it('permite avanzar y retroceder entre páginas', async () => {
    const incidenciasPaginacion = Array.from(
      { length: 25 },
      (_, indice) => ({
        ...incidenciasPrueba[0],
        id: indice + 1,
        titulo: `Incidencia de prueba ${indice + 1}`,
      })
    )

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => incidenciasPaginacion,
      })
    )

    const usuario = userEvent.setup()

    render(<App />)

    expect(
      await screen.findByText('Incidencia de prueba 1')
    ).toBeInTheDocument()

    const tabla = screen.getByRole('table')

    // Primera página: 20 registros.
    expect(tabla.querySelectorAll('tbody tr')).toHaveLength(20)
    expect(screen.queryByText('Incidencia de prueba 21')).not.toBeInTheDocument()

    // Avanzar a la segunda página.
    await usuario.click(
      screen.getByRole('button', { name: /ir a la página siguiente/i })
    )

    expect(tabla.querySelectorAll('tbody tr')).toHaveLength(5)
    expect(screen.getByText('Incidencia de prueba 21')).toBeInTheDocument()
    expect(screen.queryByText('Incidencia de prueba 1')).not.toBeInTheDocument()

    // Comprobar el indicador de página.
    expect(document.querySelector('.pagination-current'))
      .toHaveTextContent(/Página\s*2\s*de\s*2/i)

    // Regresar a la primera página.
    await usuario.click(
      screen.getByRole('button', { name: /ir a la página anterior/i })
    )

    expect(tabla.querySelectorAll('tbody tr')).toHaveLength(20)
    expect(screen.getByText('Incidencia de prueba 1')).toBeInTheDocument()
    expect(screen.queryByText('Incidencia de prueba 21')).not.toBeInTheDocument()

    expect(document.querySelector('.pagination-current'))
      .toHaveTextContent(/Página\s*1\s*de\s*2/i)
  })

})