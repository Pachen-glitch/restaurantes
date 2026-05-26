"""Menu interactivo del sistema de recomendacion."""

import sys
import database
import recommendation
import seed_data


def mostrar_menu():
    print("\n" + "=" * 60)
    print(" SISTEMA DE RECOMENDACION DE RESTAURANTES (Neo4j)")
    print("=" * 60)
    print("  1. Cargar datos")
    print("  2. Ver usuarios")
    print("  3. Recomendar restaurantes")
    print("  4. Ver restaurantes visitados por un usuario")
    print("  5. Salir")
    print("=" * 60)


def solicitar_usuario_id():
    usuario_id = input("\nIngresa el ID del usuario (ej: u1): ").strip()
    if not usuario_id:
        print("Debes ingresar un ID de usuario.")
        return None
    if not recommendation.usuario_existe(usuario_id):
        print(f"El usuario '{usuario_id}' no existe.")
        return None
    return usuario_id


def main():
    print("\nBienvenido al sistema de recomendacion de restaurantes.")
    try:
        if not database.verify_connection():
            print("No se pudo verificar la conexion con Neo4j.")
            sys.exit(1)
        print("Conexion con Neo4j establecida correctamente.")
    except Exception as error:
        print(f"\nError de conexion: {error}")
        print("Configura NEO4J_URI, NEO4J_USER y NEO4J_PASSWORD.\n")
        sys.exit(1)

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opcion: ").strip()

        if opcion == "5":
            print("\nHasta luego!\n")
            break
        if opcion == "1":
            try:
                seed_data.cargar_datos()
            except Exception as error:
                print(f"Error al cargar datos: {error}")
        elif opcion == "2":
            try:
                recommendation.imprimir_usuarios(recommendation.obtener_usuarios())
            except Exception as error:
                print(f"Error al obtener usuarios: {error}")
        elif opcion == "3":
            usuario_id = solicitar_usuario_id()
            if usuario_id:
                try:
                    recs = recommendation.recomendar_restaurantes(usuario_id)
                    recommendation.imprimir_recomendaciones(usuario_id, recs)
                except Exception as error:
                    print(f"Error al recomendar: {error}")
        elif opcion == "4":
            usuario_id = solicitar_usuario_id()
            if usuario_id:
                try:
                    visitas = recommendation.obtener_restaurantes_visitados(usuario_id)
                    recommendation.imprimir_visitas(usuario_id, visitas)
                except Exception as error:
                    print(f"Error al consultar visitas: {error}")
        else:
            print("Opcion no valida.")

    database.close()


if __name__ == "__main__":
    main()
