"""
Ejercicio 21: MySQL -> Redis

Obtiene datos de la base de datos MySQL de ImpulsaData mediante consultas SQL
y los carga en Redis:
  - usuarios con su municipio y competencias  -> JSON   (mysql:usuario:<id>)
  - ofertas de empleo con empresa y requisitos -> JSON   (mysql:oferta:<id>)
  - cursos                                     -> HASH   (mysql:curso:<id>)
  - cursos recomendados para cada usuario      -> LISTA  (mysql:recomendaciones:usuario:<id>)

Uso:  python mysql_a_redis.py
"""
import json
from datetime import date, datetime
from decimal import Decimal

from redis.commands.json.path import Path

from comun import (borrar_por_patron, cabecera, comando, conectar_mysql,
                   conectar_redis, efecto, resultado, titulo)

SQL_USUARIOS = """
SELECT u.id_usuario, u.nombre, u.email, u.telefono, u.fecha_registro,
       m.nombre AS municipio, m.provincia,
       GROUP_CONCAT(CONCAT(c.nombre, ':', uc.nivel) ORDER BY c.nombre SEPARATOR ';') AS competencias
FROM usuarios u
LEFT JOIN municipios m ON m.id_municipio = u.id_municipio
LEFT JOIN usuario_competencia uc ON uc.id_usuario = u.id_usuario
LEFT JOIN competencias c ON c.id_competencia = uc.id_competencia
GROUP BY u.id_usuario, u.nombre, u.email, u.telefono, u.fecha_registro, m.nombre, m.provincia
ORDER BY u.id_usuario
"""

SQL_OFERTAS = """
SELECT o.id_oferta, o.titulo, o.salario, o.estado, o.fecha_publicacion,
       e.nombre AS empresa, m.nombre AS municipio,
       GROUP_CONCAT(c.nombre ORDER BY c.nombre SEPARATOR ',') AS competencias_requeridas
FROM ofertas_empleo o
JOIN empresas e ON e.id_empresa = o.id_empresa
LEFT JOIN municipios m ON m.id_municipio = e.id_municipio
LEFT JOIN oferta_competencia oc ON oc.id_oferta = o.id_oferta
LEFT JOIN competencias c ON c.id_competencia = oc.id_competencia
GROUP BY o.id_oferta, o.titulo, o.salario, o.estado, o.fecha_publicacion, e.nombre, m.nombre
ORDER BY o.id_oferta
"""

SQL_CURSOS = "SELECT id_curso, nombre, horas, plazas FROM cursos ORDER BY id_curso"

# Para cada usuario: cursos que enseñan competencias exigidas por ofertas ABIERTAS
# que el usuario todavía no tiene (cuantas más ofertas desbloquea, mejor curso).
SQL_RECOMENDACIONES = """
SELECT u.id_usuario, c.nombre AS curso, c.horas,
       COUNT(DISTINCT o.id_oferta) AS ofertas_desbloqueadas
FROM usuarios u
JOIN ofertas_empleo o ON o.estado = 'abierta'
JOIN oferta_competencia oc ON oc.id_oferta = o.id_oferta
JOIN curso_competencia cc ON cc.id_competencia = oc.id_competencia
JOIN cursos c ON c.id_curso = cc.id_curso
LEFT JOIN usuario_competencia uc
       ON uc.id_usuario = u.id_usuario AND uc.id_competencia = oc.id_competencia
WHERE uc.id_usuario_competencia IS NULL
GROUP BY u.id_usuario, c.id_curso, c.nombre, c.horas
ORDER BY u.id_usuario, ofertas_desbloqueadas DESC, c.nombre
"""


def serializable(fila):
    """Convierte tipos de MySQL (Decimal, date) en tipos válidos para JSON."""
    limpia = {}
    for k, v in fila.items():
        if isinstance(v, Decimal):
            v = float(v)
        elif isinstance(v, (date, datetime)):
            v = v.isoformat()
        limpia[k] = v
    return limpia


def consultar(conexion, sql):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(sql)
    filas = [serializable(f) for f in cursor.fetchall()]
    cursor.close()
    return filas


def ej21a_limpiar_claves_previas(r):
    cabecera("21 (paso 1)", "Preparar Redis",
             "Borra las claves 'mysql:*' de ejecuciones anteriores para no duplicar listas.")
    borradas = borrar_por_patron(r, "mysql:*")
    resultado(f"Claves 'mysql:*' eliminadas: {borradas}")
    efecto("Solo se tocan las claves con prefijo 'mysql:'; el resto de Redis no se modifica.")


def ej21b_usuarios_a_json(r, conexion):
    cabecera("21 (paso 2)", "Usuarios MySQL -> JSON en Redis",
             "Ejecuta un SELECT con JOIN sobre usuarios, municipios y competencias y "
             "guarda cada fila como documento JSON.")
    comando("SQL: SELECT ... FROM usuarios JOIN municipios JOIN usuario_competencia JOIN competencias GROUP BY ...")
    filas = consultar(conexion, SQL_USUARIOS)
    for fila in filas:
        competencias = []
        if fila["competencias"]:
            for par in fila["competencias"].split(";"):
                nombre, nivel = par.rsplit(":", 1)
                competencias.append({"competencia": nombre, "nivel": nivel})
        fila["competencias"] = competencias
        clave = f"mysql:usuario:{fila['id_usuario']}"
        r.json().set(clave, Path.root_path(), fila)
    resultado(f"Filas leídas de MySQL: {len(filas)}")
    muestra = r.json().get("mysql:usuario:1")
    resultado(f"Ejemplo JSON.GET mysql:usuario:1 -> {json.dumps(muestra, ensure_ascii=False)}")
    efecto(f"Se han creado {len(filas)} documentos JSON 'mysql:usuario:<id>' en Redis.")


def ej21c_ofertas_a_json(r, conexion):
    cabecera("21 (paso 3)", "Ofertas MySQL -> JSON en Redis",
             "Ejecuta un SELECT con JOIN sobre ofertas, empresas, municipios y "
             "competencias requeridas y guarda cada oferta como JSON.")
    comando("SQL: SELECT ... FROM ofertas_empleo JOIN empresas ... JOIN competencias GROUP BY ...")
    filas = consultar(conexion, SQL_OFERTAS)
    for fila in filas:
        req = fila["competencias_requeridas"]
        fila["competencias_requeridas"] = req.split(",") if req else []
        r.json().set(f"mysql:oferta:{fila['id_oferta']}", Path.root_path(), fila)
    resultado(f"Filas leídas de MySQL: {len(filas)}")
    muestra = r.json().get("mysql:oferta:5")
    resultado(f"Ejemplo JSON.GET mysql:oferta:5 -> {json.dumps(muestra, ensure_ascii=False)}")
    efecto(f"Se han creado {len(filas)} documentos JSON 'mysql:oferta:<id>' en Redis.")


def ej21d_cursos_a_hash(r, conexion):
    cabecera("21 (paso 4)", "Cursos MySQL -> HASH en Redis",
             "Ejecuta un SELECT sobre cursos y guarda cada curso como hash (HSET).")
    comando(f"SQL: {SQL_CURSOS}")
    filas = consultar(conexion, SQL_CURSOS)
    for fila in filas:
        r.hset(f"mysql:curso:{fila['id_curso']}",
               mapping={"nombre": fila["nombre"], "horas": fila["horas"], "plazas": fila["plazas"]})
    resultado(f"Filas leídas de MySQL: {len(filas)}")
    resultado(f"Ejemplo HGETALL mysql:curso:4 -> {r.hgetall('mysql:curso:4')}")
    efecto(f"Se han creado {len(filas)} hashes 'mysql:curso:<id>' en Redis.")


def ej21e_recomendaciones_a_listas(r, conexion):
    cabecera("21 (paso 5)", "Recomendaciones de formación MySQL -> LISTAS en Redis",
             "Calcula con SQL qué cursos debería hacer cada usuario (competencias que "
             "piden las ofertas abiertas y que no tiene) y los guarda en una lista por usuario.")
    comando("SQL: usuarios x ofertas abiertas x competencias exigidas x cursos que las enseñan, "
            "excluyendo las competencias que el usuario ya tiene")
    filas = consultar(conexion, SQL_RECOMENDACIONES)
    for fila in filas:
        texto = f"{fila['curso']} ({fila['horas']}h) - desbloquea {fila['ofertas_desbloqueadas']} oferta(s) abierta(s)"
        r.rpush(f"mysql:recomendaciones:usuario:{fila['id_usuario']}", texto)
    claves = sorted(r.scan_iter(match="mysql:recomendaciones:usuario:*"))
    resultado(f"Filas leídas de MySQL: {len(filas)} | listas creadas: {len(claves)}")
    for clave in claves[:3]:
        resultado(f"{clave} -> {r.lrange(clave, 0, -1)}")
    efecto("Cada usuario tiene en Redis su lista personalizada de cursos recomendados, "
           "lista para consultarse con latencia mínima.")


def main():
    titulo("EJERCICIO 21 - MySQL -> REDIS")
    r = conectar_redis()
    conexion = conectar_mysql()
    try:
        ej21a_limpiar_claves_previas(r)
        ej21b_usuarios_a_json(r, conexion)
        ej21c_ofertas_a_json(r, conexion)
        ej21d_cursos_a_hash(r, conexion)
        ej21e_recomendaciones_a_listas(r, conexion)
    finally:
        conexion.close()
    titulo("RESUMEN")
    total = len(list(r.scan_iter(match="mysql:*")))
    print(f"Claves 'mysql:*' en Redis tras la carga: {total}")


if __name__ == "__main__":
    main()
