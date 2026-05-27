"""
Script de prueba de conexion a Neo4j AuraDB.
Uso:
    python test_connection.py
    python test_connection.py --debug
    set DEBUG_NEO4J=1 && python test_connection.py
"""

from __future__ import annotations

import sys
import traceback

import database


def main() -> int:
    print("=" * 60)
    print(" TEST DE CONEXION NEO4J AURADB")
    print("=" * 60)

    if database.LOADED_ENV_PATH:
        print(f"Archivo .env: {database.LOADED_ENV_PATH}")
    else:
        print("ADVERTENCIA: No se cargo ningun .env al importar database.py")

    print("-" * 60)

    try:
        conn = database.get_connection()
        ok = conn.verify_connection()

        if ok:
            print("-" * 60)
            print("RESULTADO: Conexion exitosa")
            print("=" * 60)
            return 0

        print("-" * 60)
        print("RESULTADO: Conexion fallida (verify_connection retorno False)")
        print("=" * 60)
        return 1

    except database.ConnectionError as exc:
        print("-" * 60)
        print("RESULTADO: Error de conexion")
        print(str(exc))
        print("=" * 60)
        return 1

    except ValueError as exc:
        print("-" * 60)
        print("RESULTADO: Error de configuracion (.env)")
        print(str(exc))
        print("=" * 60)
        return 1

    except FileNotFoundError as exc:
        print("-" * 60)
        print("RESULTADO: Archivo .env no encontrado")
        print(str(exc))
        print("=" * 60)
        return 1

    except Exception as exc:
        print("-" * 60)
        print("RESULTADO: Error inesperado")
        print(f"Tipo: {type(exc).__name__}")
        print(f"Mensaje: {exc}")
        print("-" * 60)
        print("Traceback completo:")
        traceback.print_exc()
        print("=" * 60)
        return 1

    finally:
        database.close()


if __name__ == "__main__":
    sys.exit(main())
