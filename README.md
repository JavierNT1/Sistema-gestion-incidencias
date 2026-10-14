# Sistema de Gestión y Análisis de Incidencias

API REST desarrollada en Python con FastAPI y PostgreSQL para gestionar incidencias mediante operaciones CRUD (crear, consultar, actualizar y eliminar). El proyecto incluye validaciones de datos, filtrado por prioridad, ordenamiento por fecha de creación, pruebas automatizadas y ejecución mediante Docker.

## Tecnologías utilizadas

- **Python 3.14:** lenguaje de programación.
- **FastAPI:** framework para desarrollar la API REST.
- **PostgreSQL:** sistema de gestión de bases de datos relacionales.
- **Psycopg 3:** conexión entre Python y PostgreSQL.
- **Pydantic:** validación de datos de entrada y salida.
- **Pytest:** ejecución de pruebas automatizadas.
- **Docker y Docker Compose:** creación y ejecución de contenedores.
- **Git:** control de versiones.

## Funcionalidades

- Crear incidencias.
- Consultar todas las incidencias.
- Consultar una incidencia por su identificador.
- Actualizar incidencias existentes.
- Eliminar incidencias.
- Validar los títulos y las prioridades.
- Filtrar incidencias por prioridad: Alta, Media o Baja.
- Ordenar las incidencias por prioridad y fecha de creación.
- Registrar automáticamente la fecha de creación.
- Manejar errores cuando una incidencia no existe.
- Ejecutar pruebas automatizadas y de integración con PostgreSQL.

## Estructura del proyecto

```text
sistema-incidencias/
├── app/
│   ├── main.py
│   ├── schemas.py
│   └── crud.py
├── tests/
│   ├── test_main.py
│   └── test_integracion.py
├── .env
├── .gitignore
├── .dockerignore
├── Dockerfile
├── compose.yaml
├── conexion.py
├── requirements.txt
└── README.md
```

### Descripción de los archivos principales

- `app/main.py`: define los endpoints de la API.
- `app/schemas.py`: define los modelos de datos y las validaciones.
- `app/crud.py`: contiene las operaciones para interactuar con PostgreSQL.
- `conexion.py`: administra las conexiones a las bases de datos.
- `tests/test_main.py`: contiene pruebas automatizadas de la API.
- `tests/test_integracion.py`: contiene pruebas de integración con PostgreSQL.
- `requirements.txt`: lista las dependencias de Python.
- `Dockerfile`: define cómo construir la imagen de la API.
- `compose.yaml`: configura la ejecución de la API mediante Docker Compose.
- `.env`: almacena las variables de entorno y las credenciales de la base de datos.

## Requisitos previos

Para ejecutar el proyecto localmente, se necesita:

- Python 3.14.
- PostgreSQL.
- Git.
- Un entorno virtual de Python.

Para ejecutarlo mediante Docker, se necesita Docker Desktop con Docker Compose.

## Instalación y ejecución local

### 1. Clonar el repositorio

```bash
git clone [(https://github.com/JavierNT1/Sistema-gestion-incidencias)]
cd sistema-incidencias
```

### 2. Crear y activar el entorno virtual

En Linux o WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crea un archivo `.env` en la raíz del proyecto con la siguiente estructura:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=incidencias_db
DB_USER=admin
DB_PASSWORD=tu_clave
```

Reemplaza `tu_clave` por la contraseña configurada para PostgreSQL.

### 5. Preparar la base de datos

Crea una base de datos PostgreSQL llamada `incidencias_db`.

Conéctate a esa base de datos y ejecuta el siguiente SQL para crear la tabla:

```sql
CREATE TABLE incidencias (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    prioridad VARCHAR(20) NOT NULL,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

La tabla almacena el identificador, el título, la prioridad y la fecha de creación de cada incidencia.

### 6. Ejecutar la API

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

- **API:** http://127.0.0.1:8000/
- **Documentación interactiva:** http://127.0.0.1:8000/docs

## Endpoints disponibles

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Mensaje de bienvenida. |
| GET | `/incidencias` | Lista todas las incidencias. |
| GET | `/incidencias?prioridad=Alta` | Filtra incidencias por prioridad. |
| GET | `/incidencias/{id}` | Consulta una incidencia por ID. |
| POST | `/incidencias` | Crea una incidencia. |
| PUT | `/incidencias/{id}` | Actualiza una incidencia existente. |
| DELETE | `/incidencias/{id}` | Elimina una incidencia. |

### Ejemplo de creación

Solicitud `POST /incidencias`:

```json
{
    "titulo": "La impresora no funciona",
    "prioridad": "Alta"
}
```

La API devuelve la incidencia creada, incluyendo su identificador y fecha de creación.

### Prioridades permitidas

- `Alta`
- `Media`
- `Baja`

Los títulos no pueden estar vacíos ni superar los 200 caracteres. Las prioridades se validan mediante los modelos de datos de la API.

## Pruebas automatizadas

Para ejecutar las pruebas:

```bash
python -m pytest -v
```

Las pruebas de la API utilizan el entorno de pruebas configurado en el proyecto. Las pruebas de integración requieren que PostgreSQL esté disponible y que exista la base de datos de pruebas `incidencias_test`.

## Ejecución con Docker

### 1. Requisitos

- Docker Desktop instalado y en ejecución.
- PostgreSQL accesible desde el contenedor de la API.
- Archivo `.env` configurado con las credenciales de PostgreSQL.

La configuración actual ejecuta PostgreSQL por separado y utiliza `host.docker.internal` para que el contenedor de la API pueda conectarse a él.

### 2. Iniciar la API

Desde la raíz del proyecto:

```bash
docker compose up --build -d
```

Este comando construye la imagen y ejecuta el contenedor de la API en segundo plano.

### 3. Comprobar el estado

```bash
docker compose ps
```

### 4. Consultar los registros

```bash
docker compose logs -f api
```

Para salir de los registros, pulsa `Ctrl + C`. Esto no detiene el contenedor.

### 5. Detener la API

```bash
docker compose down
```

Este comando detiene y elimina el contenedor de la API, pero no elimina el contenedor de PostgreSQL ejecutado por separado.

### 6. Acceder a la API

- **API:** http://127.0.0.1:8000/
- **Documentación interactiva:** http://127.0.0.1:8000/docs

## Estado del proyecto

El proyecto cuenta con operaciones CRUD, conexión a PostgreSQL, validaciones de entrada, filtrado y ordenamiento de incidencias, pruebas automatizadas y ejecución de la API mediante Docker Compose.
