"""
Ejercicio 22: Redis -> MySQL

Simula que la web de ImpulsaData guarda en Redis (como búfer rápido) los
registros de nuevos usuarios. Este script:
  1. Crea esos registros de ejemplo en Redis (JSON 'registro:<id>').
  2. Los lee de Redis.
  3. Los inserta en MySQL: tabla municipios (si el municipio no existe), usuarios
     y usuario_competencia.

Los usuarios importados tienen email '...@redis.impulsadata.es' para poder
identificarlos y borrarlos después con 'python limpiar_todo.py --mysql'.
Es repetible: si el usuario ya existe se actualiza en lugar de duplicarse.

Uso:  python redis_a_mysql.py
"""
from datetime import date

from redis.commands.json.path import Path

from comun import (DOMINIO_REDIS, cabecera, comando, conectar_mysql,
                   conectar_redis, efecto, resultado, titulo)

REGISTROS = {
    "registro:1": {
        "nombre": "Raúl Ortega", "email": f"raul.ortega{DOMINIO_REDIS}", "telefono": "611000001",
        "municipio": "Getafe", "provincia": "Madrid",
        "competencias": [{"nombre": "Python", "nivel": "Básico"}, {"nombre": "SQL", "nivel": "Básico"}],
    },
    "registro:2": {
        "nombre": "Nuria Campos", "email": f"nuria.campos{DOMINIO_REDIS}", "telefono": "611000002",
        "municipio": "Sevilla", "provincia": "Sevilla",
        "competencias": [{"nombre": "Excel", "nivel": "Avanzado"}, {"nombre": "Comunicación", "nivel": "Intermedio"}],
    },
    "registro:3": {
        "nombre": "Iván Soto", "email": f"ivan.soto{DOMINIO_REDIS}", "telefono": "611000003",
        "municipio": "Valencia", "provincia": "Valencia",
        "competencias": [{"nombre": "Inglés", "nivel": "Intermedio"}, {"nombre": "Spark", "nivel": "Básico"}],
    },
}


def ej22a_crear_registros_en_redis(r):
    cabecera("22 (paso 1)", "Crear registros de nuevos usuarios en Redis",
             "Guarda 3 altas de usuarios como JSON en Redis (claves 'registro:<id>').")
    for clave, doc in REGISTROS.items():
        r.json().set(clave, Path.root_path(), doc)
        comando(f"JSON.SET {clave} $ <{doc['nombre']}>")
    efecto(f"Hay {len(REGISTROS)} registros pendientes de pasar a MySQL.")


def ej22b_leer_de_redis(r):
    cabecera("22 (paso 2)", "Leer los registros de Redis",
             "Busca las claves 'registro:*' con SCAN y lee cada JSON.")
    registros = []
    for clave in sorted(r.scan_iter(match="registro:*")):
        doc = r.json().get(clave)
        if doc:
            registros.append((clave, doc))
            resultado(f"{clave}: {doc['nombre']} - {doc['municipio']} - "
                      f"{[c['nombre'] for c in doc['competencias']]}")
    efecto(f"Leídos {len(registros)} registros de Redis.")
    return registros


def _id_municipio(cursor, nombre, provincia):
    cursor.execute("SELECT id_municipio FROM municipios WHERE nombre = %s LIMIT 1", (nombre,))
    fila = cursor.fetchone()
    if fila:
        return fila[0], False
    cursor.execute("INSERT INTO municipios (nombre, provincia) VALUES (%s, %s)", (nombre, provincia))
    return cursor.lastrowid, True


def ej22c_insertar_en_mysql(conexion, registros):
    cabecera("22 (paso 3)", "Insertar los registros en MySQL",
             "Por cada registro: crea el municipio si no existe, inserta (o actualiza) el "
             "usuario y reemplaza sus competencias en usuario_competencia.")
    cursor = conexion.cursor()
    try:
        for clave, doc in registros:
            id_mun, nuevo = _id_municipio(cursor, doc["municipio"], doc["provincia"])
            if nuevo:
                resultado(f"Municipio nuevo en MySQL: {doc['municipio']} (id {id_mun})")

            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (doc["email"],))
            fila = cursor.fetchone()
            if fila:
                id_usuario = fila[0]
                cursor.execute(
                    "UPDATE usuarios SET nombre=%s, telefono=%s, id_municipio=%s WHERE id_usuario=%s",
                    (doc["nombre"], doc["telefono"], id_mun, id_usuario))
                accion = "actualizado"
            else:
                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, telefono, fecha_registro, id_municipio) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (doc["nombre"], doc["email"], doc["telefono"], date.today(), id_mun))
                id_usuario = cursor.lastrowid
                accion = "insertado"

            cursor.execute("DELETE FROM usuario_competencia WHERE id_usuario = %s", (id_usuario,))
            n_comp = 0
            for comp in doc["competencias"]:
                cursor.execute("SELECT id_competencia FROM competencias WHERE nombre = %s", (comp["nombre"],))
                c = cursor.fetchone()
                if not c:
                    resultado(f"   Aviso: la competencia '{comp['nombre']}' no existe en MySQL, se omite")
                    continue
                cursor.execute(
                    "INSERT INTO usuario_competencia (id_usuario, id_competencia, nivel) VALUES (%s, %s, %s)",
                    (id_usuario, c[0], comp["nivel"]))
                n_comp += 1
            resultado(f"{clave} -> usuario {accion} (id {id_usuario}) con {n_comp} competencia(s)")
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
    efecto("Cambios confirmados (COMMIT) en MySQL.")


def ej22d_comprobar_en_mysql(conexion):
    cabecera("22 (paso 4)", "Comprobar el resultado en MySQL",
             "Consulta con SQL los usuarios importados desde Redis y sus competencias.")
    sql = """
        SELECT u.id_usuario, u.nombre, u.email, m.nombre AS municipio,
               GROUP_CONCAT(CONCAT(c.nombre, ' (', uc.nivel, ')') ORDER BY c.nombre SEPARATOR ', ') AS competencias
        FROM usuarios u
        LEFT JOIN municipios m ON m.id_municipio = u.id_municipio
        LEFT JOIN usuario_competencia uc ON uc.id_usuario = u.id_usuario
        LEFT JOIN competencias c ON c.id_competencia = uc.id_competencia
        WHERE u.email LIKE %s
        GROUP BY u.id_usuario, u.nombre, u.email, m.nombre
        ORDER BY u.id_usuario
    """
    cursor = conexion.cursor()
    cursor.execute(sql, (f"%{DOMINIO_REDIS}",))
    filas = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]
    cursor.close()
    for f in filas:
        resultado(f"id={f[0]} | {f[1]} | {f[2]} | {f[3]} | {f[4]}")
    efecto(f"MySQL contiene {len(filas)} usuarios procedentes de Redis (total de usuarios en la tabla: {total}).")


def main():
    titulo("EJERCICIO 22 - REDIS -> MySQL")
    r = conectar_redis()
    conexion = conectar_mysql()
    try:
        ej22a_crear_registros_en_redis(r)
        registros = ej22b_leer_de_redis(r)
        ej22c_insertar_en_mysql(conexion, registros)
        ej22d_comprobar_en_mysql(conexion)
    finally:
        conexion.close()
    titulo("FIN")
    print("Para deshacerlo: python limpiar_todo.py --mysql")


if __name__ == "__main__":
    main()
