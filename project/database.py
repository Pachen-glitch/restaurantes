"""
Conexion con Neo4j AuraDB usando GraphDatabase.driver.
Lee credenciales desde variables de entorno o archivo .env
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Cargar .env del directorio del proyecto
load_dotenv(Path(__file__).resolve().parent / ".env")

URI = os.getenv("NEO4J_URI", "")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "")

_driver = None


def get_driver():
    global _driver
    if _driver is not None:
        return _driver
    if not URI:
        raise ValueError(
            "NEO4J_URI no configurada. Ejecuta: python instalar.py"
        )
    if not PASSWORD:
        raise ValueError(
            "NEO4J_PASSWORD no configurada. Ejecuta: python instalar.py"
        )
    _driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    return _driver


def get_session():
    return get_driver().session()


def close():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def verify_connection():
    with get_session() as session:
        record = session.run("RETURN 1 AS ok").single()
        return record is not None and record["ok"] == 1
