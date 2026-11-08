# ImpulsaData + Redis

Aplicación en Python que usa **Redis** junto con la base de datos **MySQL** de ImpulsaData, la plataforma que recomienda empleo y formación a personas desempleadas.

## Requisitos

Solo **Docker** y **Docker Compose**. Funciona igual en Windows, macOS y Linux.

## Puesta en marcha

```bash
git clone https://github.com/margaPs-090/impulsadata-redis.git
cd impulsadata-redis

# 1. Levanta MySQL (crea y rellena la BD) y Redis Stack
docker compose up -d --build

# 2. Ejercicios 1-20
docker compose run --rm app python tutorial_redis.py

# 3. Ejercicio 21 (MySQL -> Redis)
docker compose run --rm app python mysql_a_redis.py

# 4. Ejercicio 22 (Redis -> MySQL)
docker compose run --rm app python redis_a_mysql.py

# 5. Limpiar todo
docker compose run --rm app python limpiar_todo.py            # solo Redis
docker compose run --rm app python limpiar_todo.py --mysql    # Redis + usuarios importados en MySQL
```

Los scripts esperan a que MySQL y Redis estén listos.

Para volver a crear la base MySQL desde cero: `docker compose down -v && docker compose up -d --build`.
Para parar todo: `docker compose down`.

## Estructura

| Ruta | Contenido |
|---|---|
| `docker-compose.yml` | MySQL 8, Redis Stack y contenedor de la aplicación |
| `Dockerfile` | Imagen de la aplicación Python |
| `docker/mysql/Dockerfile` | MySQL con los scripts SQL incorporados |
| `docker/redis/Dockerfile` | Redis Stack (Redis + JSON + Search) |
| `sql/01_schema.sql` | Creación de las tablas de ImpulsaData |
| `sql/02_datos.sql` | Insertar datos en la base de datos |
| `app/comun.py` | Conexiones y utilidades de impresión |
| `app/tutorial_redis.py` | Ejercicios 1-20 |
| `app/mysql_a_redis.py` | Ejercicio 21 |
| `app/redis_a_mysql.py` | Ejercicio 22 |
| `app/limpiar_todo.py` | Elimina todo lo creado |

## Ejercicios 1-20 (`tutorial_redis.py`)

| Nº | Función | Qué hace |
|---|---|---|
| 1 | `ej01_crear_registros` | SET de ofertas, plazas de cursos y usuarios (con `ex`) |
| 2 | `ej02_contar_claves` | DBSIZE |
| 3 | `ej03_obtener_registro` | GET por clave |
| 4 | `ej04_actualizar_valor` | SET sobre clave existente |
| 5 | `ej05_eliminar_clave` | DEL mostrando clave y valor |
| 6 | `ej06_todas_las_claves` | KEYS |
| 7 | `ej07_todos_los_valores` | MGET |
| 8 | `ej08_patron_asterisco` | `oferta:*` |
| 9 | `ej09_patron_corchetes` | `oferta:[135]`, `plazas:curso:[1-3]` |
| 10 | `ej10_patron_interrogacion` | `oferta:?` |
| 11 | `ej11_filtrar_por_valor` | ofertas con valor `abierta` |
| 12 | `ej12_actualizar_con_filtro` | INCR a cursos con ≤15 plazas |
| 13 | `ej13_eliminar_con_filtro` | DEL de ofertas `cerrada` |
| 14 | `ej14_crear_json_array` | array JSON de ofertas |
| 15 | `ej15_filtro_por_atributo` | JSONPath por cada atributo |
| 16 | `ej16_crear_lista` | RPUSH de cursos recomendados |
| 17 | `ej17_filtrar_lista` | cursos de ≤40 h |
| 18 | `ej18_crear_indice_y_datos` | índice con 4 campos + 5 candidatos |
| 19 | `ej19_busqueda_con_indice` | búsqueda por tag, rango numérico y texto |
| 20 | `ej20_group_by_con_indice` | FT.AGGREGATE por municipio |

El script empieza vaciando Redis. Cada ejercicio imprime su cabecera (función, qué hace), los comandos, los resultados y el efecto producido; si uno falla, lo indica y continúa con los demás.

## Ejercicios 21 y 22

* **21 `mysql_a_redis.py`**: consultas SQL (con JOIN y GROUP BY) cuyo resultado se guarda en Redis como JSON (usuarios y ofertas), hashes (cursos) y listas (cursos recomendados por usuario según las competencias que exigen las ofertas abiertas y que el usuario no tiene). Claves con prefijo `mysql:`.
* **22 `redis_a_mysql.py`**: crea altas de usuarios en Redis (`registro:*`), las lee e inserta en MySQL (`municipios`, `usuarios`, `usuario_competencia`). Es repetible y los usuarios llevan el email `@redis.impulsadata.es`, para poder borrarlos con `limpiar_todo.py --mysql`.

## Ejecución sin Docker para la aplicación (opcional)

Con `docker compose up -d` activo, desde tu máquina:

```bash
python3 -m venv redis-env
source redis-env/bin/activate        # Windows: redis-env\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cd app && python tutorial_redis.py
```

Variables de entorno (valores por defecto entre paréntesis): `REDIS_HOST` (localhost), `REDIS_PORT` (6379), `MYSQL_HOST` (localhost), `MYSQL_PORT` (3307), `MYSQL_USER` (impulsa), `MYSQL_PASSWORD` (impulsa123), `MYSQL_DATABASE` (impulsadata).

## Herramientas

* RedisInsight (interfaz web): http://localhost:8001
* MySQL desde tu máquina: `localhost:3307`, usuario `impulsa`, contraseña `impulsa123`.
