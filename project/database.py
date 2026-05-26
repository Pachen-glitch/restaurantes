"""
Conexion con Neo4j AuraDB usando GraphDatabase.driver.
"""

import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "neo4j+s://xxxxxxxx.databases.neo4j.io")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "tu_password_aqui")

_driver = None


def get_driver():
    global _driver
    if _driver is not None:
        return _driver
    if not URI or URI == "neo4j+s://xxxxxxxx.databases.neo4j.io":
        raise ValueError("Configura NEO4J_URI con la URI de tu instancia AuraDB.")
    if not PASSWORD or PASSWORD == "tu_password_aqui":
        raise ValueError("Configura NEO4J_PASSWORD con la contrasena de tu instancia AuraDB.")
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
