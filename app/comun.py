"""
Utilidades comunes de ImpulsaData: conexiones a Redis y MySQL y funciones
para imprimir la salida.

Las conexiones se configuran con variables de entorno (con valores por defecto para ejecutar los scripts).
"""
import inspect
import os
import sys
import time

import mysql.connector
import redis

try:  # evita problemas de codificación en terminales Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3307"))
MYSQL_USER = os.getenv("MYSQL_USER", "impulsa")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "impulsa123")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "impulsadata")

DOMINIO_REDIS = "@redis.impulsadata.es"  # email de los usuarios que vienen de Redis
ANCHO = 80


# ----------------------------------------------------------------------------
# Impresión
# ----------------------------------------------------------------------------
def titulo(texto):
    print("\n" + "=" * ANCHO)
    print(texto)
    print("=" * ANCHO)


def cabecera(num, nombre, que_hace):
    """Imprime el encabezado de un ejercicio con el nombre de la función que lo ejecuta."""
    funcion = inspect.stack()[1].function
    print("\n" + "#" * ANCHO)
    print(f"# EJERCICIO {num}: {nombre}")
    print("#" * ANCHO)
    print(f"FUNCIÓN QUE SE EJECUTA : {funcion}()")
    print(f"QUÉ HACE               : {que_hace}")
    print("-" * ANCHO)


def comando(texto):
    print(f"  [COMANDO]   {texto}")


def resultado(texto):
    print(f"  [RESULTADO] {texto}")


def efecto(texto):
    print(f"  >> EFECTO: {texto}")


# ----------------------------------------------------------------------------
# Conexiones
# ----------------------------------------------------------------------------
def conectar_redis(verificar_modulos=True):
    """Conexión con ConnectionPool (como en el tutorial) y decode_responses=True."""
    conexion = redis.ConnectionPool(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    )
    r = redis.Redis(connection_pool=conexion)

    for intento in range(30):
        try:
            r.ping()
            break
        except redis.exceptions.ConnectionError:
            print(f"Esperando a Redis en {REDIS_HOST}:{REDIS_PORT} ... ({intento + 1}/30)")
            time.sleep(1)
    else:
        print("ERROR: no se pudo conectar con Redis. ¿Está levantado 'docker compose up -d'?")
        sys.exit(1)

    if verificar_modulos:
        try:
            r.execute_command("FT._LIST")
            r.json().type("__clave_inexistente__")
        except redis.exceptions.ResponseError:
            print("ERROR: este Redis no tiene los módulos JSON/Search.")
            print("       Usa la imagen redis/redis-stack (ver docker-compose.yml).")
            sys.exit(1)
    return r


def conectar_mysql():
    """Conexión a MySQL con reintentos (el contenedor puede tardar en arrancar)."""
    ultimo_error = None
    for intento in range(30):
        try:
            return mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                charset="utf8mb4",
            )
        except mysql.connector.Error as e:
            ultimo_error = e
            print(f"Esperando a MySQL en {MYSQL_HOST}:{MYSQL_PORT} ... ({intento + 1}/30)")
            time.sleep(2)
    print(f"ERROR: no se pudo conectar con MySQL: {ultimo_error}")
    sys.exit(1)


# ----------------------------------------------------------------------------
# Limpieza
# ----------------------------------------------------------------------------
def borrar_indices(r):
    """Elimina todos los índices de RediSearch (y sus documentos)."""
    try:
        indices = r.execute_command("FT._LIST")
    except redis.exceptions.ResponseError:  # Redis sin módulo Search
        return []
    for indice in indices:
        r.ft(indice).dropindex(True)
    return indices


def limpiar_redis(r):
    """Borra índices y todas las claves de la base de datos 0."""
    indices = borrar_indices(r)
    n_claves = r.dbsize()
    r.flushdb()
    return indices, n_claves


def borrar_por_patron(r, patron):
    """Borra las claves que cumplen un patrón. Devuelve cuántas se borraron."""
    borradas = 0
    for clave in list(r.scan_iter(match=patron)):
        borradas += r.delete(clave)
    return borradas
