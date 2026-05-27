"""Menu interactivo del sistema de recomendacion de restaurantes."""

import sys
import database
from recommendation import (
    imprimir_historial,
    imprimir_recomendaciones,
    imprimir_usuarios,
    obtener_historial_usuario,
    obtener_usuarios,
    recomendar_restaurantes,
    usuario_existe,
)
from seed_data import crear_base_datos

SEP = "=" * 60


def pedir_usuario():
    uid = input("\nIngresa ID de usuario (u1, u2, u3): ").strip()
    if uid not in ("u1", "u2", "u3"):
        print("ID invalido.")
        return None
    if not usuario_existe(uid):
        print(f"Usuario {uid} no existe. Ejecuta opcion 1 primero.")
        return None
    return uid


def menu():
    print(f"\n{SEP}\n  SISTEMA DE RECOMENDACION DE RESTAURANTES\n{SEP}")
    print("  1. Crear base de datos")
    print("  2. Ver usuarios")
    print("  3. Recomendar restaurantes")
    print("  4. Ver historial de usuario")
    print("  5. Salir")
    print(SEP)


def main():
    print("\nBienvenido al sistema de recomendacion de restaurantes.")
    try:
        if database.get_connection().verify_connection():
            print("Conexion con Neo4j AuraDB verificada.\n")
    except (ValueError, database.ConnectionError) as exc:
        print(f"Error de conexion: {exc}\n")
        sys.exit(1)

    while True:
        menu()
        op = input("Selecciona una opcion: ").strip()
        if op == "5":
            print("\nHasta luego!\n")
            break
        elif op == "1":
            try:
                crear_base_datos()
            except Exception as exc:
                print(f"Error: {exc}")
        elif op == "2":
            try:
                imprimir_usuarios(obtener_usuarios())
            except Exception as exc:
                print(f"Error: {exc}")
        elif op == "3":
            uid = pedir_usuario()
            if uid:
                try:
                    imprimir_recomendaciones(uid, recomendar_restaurantes(uid))
                except Exception as exc:
                    print(f"Error: {exc}")
        elif op == "4":
            uid = pedir_usuario()
            if uid:
                try:
                    imprimir_historial(uid, obtener_historial_usuario(uid))
                except Exception as exc:
                    print(f"Error: {exc}")
        else:
            print("Opcion no valida.")
    database.close()


if __name__ == "__main__":
    main()
