"""
Instala dependencias y configura la conexion con Neo4j AuraDB.
Ejecutar: python instalar.py
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"
REQUIREMENTS = PROJECT_DIR / "requirements.txt"


def instalar_dependencias():
    print("\n[1/3] Instalando dependencias...")
    resultado = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        print("Error al instalar dependencias:")
        print(resultado.stderr or resultado.stdout)
        sys.exit(1)
    print("Dependencias instaladas correctamente.")


def solicitar_credenciales():
    print("\n[2/3] Configuracion de Neo4j AuraDB")
    print("Obtén estos datos en: https://console.neo4j.io/\n")

    uri = input("NEO4J_URI (ej: neo4j+s://xxxxx.databases.neo4j.io): ").strip()
    user = input("NEO4J_USER [neo4j]: ").strip() or "neo4j"
    password = input("NEO4J_PASSWORD: ").strip()

    if not uri:
        print("La URI es obligatoria.")
        sys.exit(1)
    if not password:
        print("La contrasena es obligatoria.")
        sys.exit(1)

    return uri, user, password


def guardar_env(uri, user, password):
    contenido = (
        f"NEO4J_URI={uri}\n"
        f"NEO4J_USER={user}\n"
        f"NEO4J_PASSWORD={password}\n"
    )
    ENV_FILE.write_text(contenido, encoding="utf-8")
    print(f"\nCredenciales guardadas en: {ENV_FILE}")


def probar_conexion():
    print("\n[3/3] Probando conexion con Neo4j AuraDB...")

    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)

    from neo4j import GraphDatabase

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        with driver.session() as session:
            record = session.run("RETURN 'Conexion exitosa' AS mensaje").single()
            print(record["mensaje"])
        driver.close()
        return True
    except Exception as error:
        print(f"Error de conexion: {error}")
        return False


def main():
    print("=" * 60)
    print(" INSTALADOR - Sistema de Recomendacion de Restaurantes")
    print("=" * 60)

    if not REQUIREMENTS.exists():
        print(f"No se encontro {REQUIREMENTS}")
        sys.exit(1)

    instalar_dependencias()

    if ENV_FILE.exists():
        respuesta = input("\nYa existe un archivo .env. Deseas sobrescribirlo? (s/n): ").strip().lower()
        if respuesta != "s":
            print("Se conserva la configuracion actual.")
            if probar_conexion():
                print("\nTodo listo. Ejecuta: python main.py")
            else:
                print("\nRevisa tus credenciales en .env o vuelve a ejecutar este script.")
            return

    uri, user, password = solicitar_credenciales()
    guardar_env(uri, user, password)

    if probar_conexion():
        print("\n" + "=" * 60)
        print(" Instalacion completada.")
        print(" Ejecuta el proyecto con: python main.py")
        print("=" * 60 + "\n")
    else:
        print("\nLa instalacion termino pero la conexion fallo.")
        print("Verifica URI, usuario y contrasena en el archivo .env")
        sys.exit(1)


if __name__ == "__main__":
    main()
