"""
ImpulsaData + Redis  ->  Ejercicios 1 a 20

Ejecuta los ejercicios del 1 al 20. Al empezar dejar Redis limpio.

Uso:  python tutorial_redis.py
"""
import json
import sys

from redis.commands.json.path import Path
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers

from comun import (cabecera, comando, conectar_redis, efecto, limpiar_redis,
                   resultado, titulo)

# ----------------------------------------------------------------------------
# Datos del negocio ImpulsaData
# ----------------------------------------------------------------------------
# Estado de las ofertas de empleo (clave: oferta:<id>)
OFERTAS_ESTADO = {
    "oferta:1": "abierta",
    "oferta:2": "cerrada",
    "oferta:3": "abierta",
    "oferta:4": "cerrada",
    "oferta:5": "abierta",
    "oferta:10": "abierta",   # id de dos cifras: lo usamos para distinguir * de ?
}
# Plazas libres de cada curso (clave: plazas:curso:<id>)
PLAZAS_CURSO = {
    "plazas:curso:1": 20,   # Python desde cero
    "plazas:curso:2": 15,   # SQL para análisis
    "plazas:curso:3": 30,   # Excel intermedio
    "plazas:curso:4": 10,   # Big Data con Spark
}
# Usuarios registrados (clave: usuario:<id>)
USUARIOS = {
    "usuario:1": "Jorge Guerra",
    "usuario:2": "Lucía Benítez",
    "usuario:3": "Pepe García",
}

# Estructura JSON de tipo array con ofertas de empleo
OFERTAS_JSON = [
    {"id_oferta": 1, "titulo": "Analista de datos junior", "empresa": "DataSur",
     "salario": 24000, "estado": "abierta", "municipio": "Sevilla"},
    {"id_oferta": 2, "titulo": "Técnico de soporte TI", "empresa": "TecnoVega",
     "salario": 20000, "estado": "cerrada", "municipio": "Madrid"},
    {"id_oferta": 3, "titulo": "Desarrollador Python", "empresa": "TecnoVega",
     "salario": 30000, "estado": "abierta", "municipio": "Madrid"},
    {"id_oferta": 4, "titulo": "Administrativo/a", "empresa": "Logística Norte",
     "salario": 18500, "estado": "abierta", "municipio": "Zaragoza"},
    {"id_oferta": 5, "titulo": "Ingeniero/a de datos", "empresa": "DataSur",
     "salario": 36000, "estado": "abierta", "municipio": "Sevilla"},
]

# Lista de cursos recomendados a un usuario (formato "nombre:horas")
CURSOS_RECOMENDADOS = [
    "Python desde cero:40",
    "SQL para análisis:60",
    "Excel intermedio:30",
    "Big Data con Spark:80",
    "Comunicación efectiva:20",
]

# Documentos JSON indexados (clave: candidato:<id>)
CANDIDATOS = {
    "candidato:1": {"nombre": "Jorge Guerra", "email": "jorge.guerra@example.com",
                    "edad": 38, "municipio": "Madrid", "competencia": "Python"},
    "candidato:2": {"nombre": "Lucía Benítez", "email": "lucia.benitez@example.com",
                    "edad": 24, "municipio": "Sevilla", "competencia": "Excel"},
    "candidato:3": {"nombre": "Pepe García", "email": "pepe.garcia@example.com",
                    "edad": 33, "municipio": "Madrid", "competencia": "SQL"},
    "candidato:4": {"nombre": "Elena Gómez", "email": "elena.gomez@example.com",
                    "edad": 29, "municipio": "Valencia", "competencia": "SQL"},
    "candidato:5": {"nombre": "Calisto Melibea", "email": "calisto.melibea@example.com",
                    "edad": 67, "municipio": "Toledo", "competencia": "Excel"},
}
INDICE = "indice:candidatos"


def mostrar_json(objeto):
    return json.dumps(objeto, ensure_ascii=False)


def doc_a_dict(doc):
    """Convierte un documento devuelto por RediSearch (índice JSON) en diccionario."""
    crudo = getattr(doc, "json", None)
    return json.loads(crudo) if crudo else dict(doc.__dict__)


# ----------------------------------------------------------------------------
# 1 - 7: operaciones básicas clave-valor
# ----------------------------------------------------------------------------
def ej01_crear_registros(r):
    cabecera(1, "Crear registros clave-valor",
             "Guarda con SET el estado de las ofertas, las plazas de los cursos y los "
             "usuarios. También crea una clave con tiempo de vida (ex).")
    for datos in (OFERTAS_ESTADO, PLAZAS_CURSO, USUARIOS):
        for clave, valor in datos.items():
            r.set(clave, valor)
            comando(f"SET {clave} {valor!r}")
    r.set("sesion:usuario:1", "token-abc123", ex=3600)
    comando("SET sesion:usuario:1 'token-abc123' ex=3600")
    resultado(f"TTL de sesion:usuario:1 = {r.ttl('sesion:usuario:1')} segundos")
    efecto("Se han creado 14 claves en Redis. La clave 'sesion:usuario:1' caducará "
           "sola dentro de 1 hora (3600 s).")


def ej02_contar_claves(r):
    cabecera(2, "Obtener y mostrar el número de claves",
             "Cuenta las claves de la base de datos con DBSIZE y comprueba con KEYS.")
    comando("DBSIZE")
    resultado(f"Número de claves (dbsize) = {r.dbsize()}")
    resultado(f"Número de claves (len(keys)) = {len(r.keys('*'))}")
    efecto("Solo se ha leído información: Redis no ha cambiado.")


def ej03_obtener_registro(r):
    cabecera(3, "Obtener y mostrar un registro por clave",
             "Lee con GET el valor de la clave 'usuario:1'.")
    comando("GET usuario:1")
    resultado(f"usuario:1 = {r.get('usuario:1')!r}")
    comando("GET clave_que_no_existe")
    resultado(f"clave_que_no_existe = {r.get('clave_que_no_existe')!r} (None: no existe)")
    efecto("GET devuelve el valor como texto (decode_responses=True) o None si la clave no existe.")


def ej04_actualizar_valor(r):
    cabecera(4, "Actualizar el valor de una clave",
             "Lanza SET de nuevo sobre una clave existente con un valor distinto.")
    resultado(f"Valor ANTES : usuario:1 = {r.get('usuario:1')!r}")
    r.set("usuario:1", "Jorge Guerra Fuentes")
    comando("SET usuario:1 'Jorge Guerra Fuentes'")
    resultado(f"Valor NUEVO : usuario:1 = {r.get('usuario:1')!r}")
    efecto("SET sobrescribe el valor anterior; el número de claves no cambia.")


def ej05_eliminar_clave(r):
    cabecera(5, "Eliminar una clave-valor",
             "Lee el valor de 'usuario:3', lo elimina con DEL y comprueba que ya no existe.")
    valor = r.get("usuario:3")
    borradas = r.delete("usuario:3")
    comando("DEL usuario:3")
    resultado(f"Clave eliminada: 'usuario:3' | Valor eliminado: {valor!r} | DEL devolvió {borradas}")
    resultado(f"Comprobación: GET usuario:3 = {r.get('usuario:3')!r}")
    efecto(f"La base de datos pasa a tener {r.dbsize()} claves (una menos).")


def ej06_todas_las_claves(r):
    cabecera(6, "Obtener y mostrar todas las claves",
             "Usa KEYS * para listar todas las claves guardadas.")
    claves = sorted(r.keys("*"))
    comando("KEYS *")
    for clave in claves:
        resultado(clave)
    efecto(f"Se han listado {len(claves)} claves. (KEYS recorre toda la BD: en producción "
           "se prefiere SCAN, que es lo que usamos en los ejercicios siguientes.)")


def ej07_todos_los_valores(r):
    cabecera(7, "Obtener y mostrar todos los valores",
             "Obtiene todas las claves y pide sus valores de una vez con MGET.")
    claves = sorted(r.keys("*"))
    valores = r.mget(claves)
    comando(f"MGET <{len(claves)} claves>")
    for valor in valores:
        resultado(repr(valor))
    efecto(f"Se han leído {len(valores)} valores con una sola petición a Redis.")


# ----------------------------------------------------------------------------
# 8 - 13: patrones y filtros
# ----------------------------------------------------------------------------
def _buscar_patron(r, patron):
    claves = sorted(r.scan_iter(match=patron))
    comando(f"SCAN MATCH {patron!r}")
    for clave in claves:
        resultado(f"{clave} = {r.get(clave)!r}")
    return claves


def ej08_patron_asterisco(r):
    cabecera(8, "Patrón con * (cualquier número de caracteres)",
             "Busca con scan_iter las claves que empiezan por 'oferta:'.")
    claves = _buscar_patron(r, "oferta:*")
    efecto(f"'*' sustituye a cualquier texto: encontradas {len(claves)} ofertas, "
           "incluida 'oferta:10'.")


def ej09_patron_corchetes(r):
    cabecera(9, "Patrón con [] (uno de los caracteres indicados)",
             "Busca las ofertas cuyo id sea 1, 3 o 5 y los cursos con id entre 1 y 3.")
    c1 = _buscar_patron(r, "oferta:[135]")
    c2 = _buscar_patron(r, "plazas:curso:[1-3]")
    efecto(f"'[135]' acepta un único carácter de esa lista ({len(c1)} claves) y "
           f"'[1-3]' un rango ({len(c2)} claves). 'oferta:10' no coincide porque "
           "[] solo admite un carácter.")


def ej10_patron_interrogacion(r):
    cabecera(10, "Patrón con ? (exactamente un carácter)",
             "Busca las ofertas con un id de una sola cifra.")
    claves = _buscar_patron(r, "oferta:?")
    efecto(f"'?' sustituye exactamente un carácter: {len(claves)} claves, y 'oferta:10' "
           "queda fuera (tiene dos cifras).")


def ej11_filtrar_por_valor(r):
    cabecera(11, "Obtener registros y filtrarlos por un valor",
             "Recorre las claves 'oferta:*' y se queda solo con las de valor 'abierta'.")
    abiertas = []
    for clave in sorted(r.scan_iter(match="oferta:*")):
        if r.get(clave) == "abierta":
            abiertas.append(clave)
            resultado(f"{clave} = 'abierta'")
    efecto(f"Redis no filtra por valor, así que se filtra en Python: {len(abiertas)} "
           "ofertas abiertas.")


def ej12_actualizar_con_filtro(r):
    cabecera(12, "Actualizar una serie de registros según un filtro",
             "A los cursos con 15 plazas o menos les añade 1 plaza con INCR.")
    for clave in sorted(r.scan_iter(match="plazas:curso:*")):
        antes = int(r.get(clave))
        if antes <= 15:
            r.incr(clave)
            comando(f"INCR {clave}")
            resultado(f"{clave}: {antes} -> {r.get(clave)}")
        else:
            resultado(f"{clave}: {antes} (no cumple el filtro, sin cambios)")
    efecto("Solo se han modificado los cursos que cumplían la condición; INCR suma 1 de forma atómica.")


def ej13_eliminar_con_filtro(r):
    cabecera(13, "Eliminar una serie de registros según un filtro",
             "Borra las ofertas cuyo valor es 'cerrada'.")
    for clave in sorted(r.scan_iter(match="oferta:*")):
        if r.get(clave) == "cerrada":
            r.delete(clave)
            comando(f"DEL {clave}")
            resultado(f"Eliminada {clave}")
    restantes = sorted(r.scan_iter(match="oferta:*"))
    resultado(f"Ofertas restantes: {restantes}")
    efecto("Las ofertas cerradas ya no existen en Redis; quedan solo las abiertas.")


# ----------------------------------------------------------------------------
# 14 - 15: JSON
# ----------------------------------------------------------------------------
def ej14_crear_json_array(r):
    cabecera(14, "Crear una estructura JSON de tipo array",
             "Crea con JSON.SET un array vacío y le añade las ofertas con JSON.ARRAPPEND.")
    r.json().set("ofertas_array", "$", [])
    comando("JSON.SET ofertas_array $ []")
    for oferta in OFERTAS_JSON:
        r.json().arrappend("ofertas_array", "$", oferta)
        comando(f"JSON.ARRAPPEND ofertas_array $ {mostrar_json(oferta)}")
    resultado(f"Elementos en el array: {r.json().arrlen('ofertas_array', '$')[0]}")
    efecto("Existe la clave 'ofertas_array' con un array JSON de 5 ofertas.")


def ej15_filtro_por_atributo(r):
    cabecera(15, "Filtro por cada atributo de la estructura JSON",
             "Usa JSONPath ($[?(...)]) para filtrar por id_oferta, titulo, empresa, "
             "salario, estado y municipio.")
    filtros = [
        ("id_oferta", '$[?(@.id_oferta == 3)]'),
        ("titulo", '$[?(@.titulo == "Ingeniero/a de datos")]'),
        ("empresa", '$[?(@.empresa == "TecnoVega")]'),
        ("salario", '$[?(@.salario > 25000)]'),
        ("estado", '$[?(@.estado == "cerrada")]'),
        ("municipio", '$[?(@.municipio == "Sevilla")]'),
    ]
    for atributo, ruta in filtros:
        encontrados = r.json().get("ofertas_array", ruta)
        comando(f"JSON.GET ofertas_array '{ruta}'")
        resultado(f"Filtro por '{atributo}': {len(encontrados)} oferta(s)")
        for oferta in encontrados:
            print(f"                 - {mostrar_json(oferta)}")
    efecto("Cada filtro devuelve solo los elementos del array que cumplen la condición.")


# ----------------------------------------------------------------------------
# 16 - 17: listas
# ----------------------------------------------------------------------------
def ej16_crear_lista(r):
    cabecera(16, "Crear una lista en Redis",
             "Crea la lista 'usuario:1:cursos_recomendados' con RPUSH (formato nombre:horas).")
    clave = "usuario:1:cursos_recomendados"
    for curso in CURSOS_RECOMENDADOS:
        r.rpush(clave, curso)
        comando(f"RPUSH {clave} {curso!r}")
    resultado(f"LLEN = {r.llen(clave)}")
    resultado(f"LRANGE 0 -1 = {r.lrange(clave, 0, -1)}")
    efecto("La lista conserva el orden de inserción (RPUSH añade por el final).")


def ej17_filtrar_lista(r):
    cabecera(17, "Obtener elementos de una lista con un filtro",
             "Lee la lista con LRANGE y se queda con los cursos de 40 horas o menos.")
    clave = "usuario:1:cursos_recomendados"
    cursos = r.lrange(clave, 0, -1)
    comando(f"LRANGE {clave} 0 -1")
    cortos = [c for c in cursos if int(c.rsplit(":", 1)[1]) <= 40]
    for curso in cortos:
        resultado(curso)
    efecto(f"De {len(cursos)} cursos, {len(cortos)} duran 40 horas o menos.")


# ----------------------------------------------------------------------------
# 18 - 20: índices (RediSearch)
# ----------------------------------------------------------------------------
def ej18_crear_indice_y_datos(r):
    cabecera(18, "Crear datos con índices (esquema de 4 campos)",
             "Crea el índice 'indice:candidatos' sobre documentos JSON 'candidato:*' con "
             "los campos nombre (texto), municipio (tag), competencia (tag) y edad "
             "(numérico) y luego inserta 5 candidatos.")
    esquema = (
        TextField("$.nombre", as_name="nombre"),
        TagField("$.municipio", as_name="municipio", sortable=True),
        TagField("$.competencia", as_name="competencia"),
        NumericField("$.edad", as_name="edad", sortable=True),
    )
    r.ft(INDICE).create_index(
        esquema,
        definition=IndexDefinition(prefix=["candidato:"], index_type=IndexType.JSON),
    )
    comando(f"FT.CREATE {INDICE} ON JSON PREFIX 1 candidato: SCHEMA nombre, municipio, competencia, edad")
    for clave, candidato in CANDIDATOS.items():
        r.json().set(clave, Path.root_path(), candidato)
        comando(f"JSON.SET {clave} $ {mostrar_json(candidato)}")
    info = r.ft(INDICE).info()
    resultado(f"Documentos indexados: {info.get('num_docs')}")
    efecto("El índice indexa automáticamente cada JSON 'candidato:*' que se guarde.")


def _mostrar_busqueda(r, texto_query, descripcion):
    res = r.ft(INDICE).search(Query(texto_query))
    comando(f"FT.SEARCH {INDICE} '{texto_query}'")
    resultado(f"{descripcion}: {res.total} resultado(s)")
    for doc in res.docs:
        print(f"                 - {doc.id}: {mostrar_json(doc_a_dict(doc))}")


def ej19_busqueda_con_indice(r):
    cabecera(19, "Búsqueda con índices en base a un campo",
             "Busca candidatos por municipio (tag), por rango de edad (numérico) y "
             "por nombre (texto).")
    _mostrar_busqueda(r, "@municipio:{Madrid}", "Candidatos del municipio Madrid")
    _mostrar_busqueda(r, "@edad:[30 40]", "Candidatos con edad entre 30 y 40")
    _mostrar_busqueda(r, "@nombre:Elena", "Candidatos cuyo nombre contiene 'Elena'")
    efecto("El índice permite buscar por campo sin recorrer las claves una a una.")


def ej20_group_by_con_indice(r):
    cabecera(20, "Group by usando los índices",
             "Agrupa los candidatos por municipio contando cuántos hay y calculando su "
             "edad media (FT.AGGREGATE).")
    peticion = aggregations.AggregateRequest("*").group_by(
        "@municipio",
        reducers.count().alias("total"),
        reducers.avg("@edad").alias("edad_media"),
    )
    filas = r.ft(INDICE).aggregate(peticion).rows
    comando("FT.AGGREGATE indice:candidatos * GROUPBY 1 @municipio REDUCE COUNT ... REDUCE AVG @edad")
    for fila in sorted(filas, key=lambda f: f[1]):
        d = dict(zip(fila[::2], fila[1::2]))
        resultado(f"municipio={d['municipio']:<10} total={d['total']}  edad_media={float(d['edad_media']):.1f}")
    efecto("Equivale a un GROUP BY de SQL: una fila por municipio con su recuento y media.")


EJERCICIOS = [
    ej01_crear_registros, ej02_contar_claves, ej03_obtener_registro,
    ej04_actualizar_valor, ej05_eliminar_clave, ej06_todas_las_claves,
    ej07_todos_los_valores, ej08_patron_asterisco, ej09_patron_corchetes,
    ej10_patron_interrogacion, ej11_filtrar_por_valor, ej12_actualizar_con_filtro,
    ej13_eliminar_con_filtro, ej14_crear_json_array, ej15_filtro_por_atributo,
    ej16_crear_lista, ej17_filtrar_lista, ej18_crear_indice_y_datos,
    ej19_busqueda_con_indice, ej20_group_by_con_indice,
]


def main():
    titulo("IMPULSADATA + REDIS - EJERCICIOS 1 A 20")
    r = conectar_redis()

    indices, n = limpiar_redis(r)
    print(f"Preparación: Redis limpiado ({n} claves y {len(indices)} índices eliminados) "
          "para partir de cero.")

    fallos = []
    for funcion in EJERCICIOS:
        try:
            funcion(r)
        except Exception as e:  # un fallo no debe impedir ver el resto
            fallos.append(funcion.__name__)
            print(f"  !! ERROR en {funcion.__name__}: {type(e).__name__}: {e}")

    titulo("RESUMEN")
    print(f"Ejercicios correctos: {len(EJERCICIOS) - len(fallos)}/{len(EJERCICIOS)}")
    if fallos:
        print("Con errores:", ", ".join(fallos))
        sys.exit(1)
    print("Todo correcto. Para limpiar Redis: python limpiar_todo.py")


if __name__ == "__main__":
    main()
