"""
Elimina todo lo creado por los ejercicios.

  python limpiar_todo.py           -> vacía Redis (índices + todas las claves)
  python limpiar_todo.py --mysql   -> además borra de MySQL los usuarios importados
                                      desde Redis en el ejercicio 22 (email
                                      '...@redis.impulsadata.es') y el municipio
                                      'Getafe' creado por ese ejercicio
"""
import sys

from comun import (DOMINIO_REDIS, conectar_mysql, conectar_redis,
                   limpiar_redis, titulo)


def limpiar_mysql():
    conexion = conectar_mysql()
    cursor = conexion.cursor()
    patron = (f"%{DOMINIO_REDIS}",)
    try:
        for sql in (
            "DELETE uc FROM usuario_competencia uc JOIN usuarios u ON u.id_usuario = uc.id_usuario WHERE u.email LIKE %s",
            "DELETE c FROM candidaturas c JOIN usuarios u ON u.id_usuario = c.id_usuario WHERE u.email LIKE %s",
            "DELETE FROM usuarios WHERE email LIKE %s",
        ):
            cursor.execute(sql, patron)
            print(f"  MySQL: {cursor.rowcount} fila(s) -> {sql.split(' WHERE')[0][:60]}...")
        cursor.execute(
            "DELETE FROM municipios WHERE nombre = 'Getafe' "
            "AND id_municipio NOT IN (SELECT id_municipio FROM usuarios WHERE id_municipio IS NOT NULL) "
            "AND id_municipio NOT IN (SELECT id_municipio FROM empresas WHERE id_municipio IS NOT NULL)"
        )
        print(f"  MySQL: {cursor.rowcount} municipio(s) creados por Redis eliminados")
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


def main():
    titulo("LIMPIEZA")
    r = conectar_redis(verificar_modulos=False)
    indices, n_claves = limpiar_redis(r)
    print(f"  Redis: {len(indices)} índice(s) eliminado(s): {indices}")
    print(f"  Redis: {n_claves} clave(s) eliminada(s). Claves restantes: {r.dbsize()}")
    if "--mysql" in sys.argv:
        limpiar_mysql()
    else:
        print("  (MySQL no se ha tocado; usa --mysql para borrar los usuarios importados desde Redis)")
    print("Limpieza completada.")


if __name__ == "__main__":
    main()
