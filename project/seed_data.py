"""
Carga inicial de datos en Neo4j.
"""

from database import get_session


def limpiar_base(session):
    session.run("MATCH (n) DETACH DELETE n")


def crear_zonas(session):
    session.run(
        "UNWIND $zonas AS zona MERGE (z:Zone {nombre: zona})",
        zonas=["Zona 10", "Zona 4", "Zona 1"],
    )


def crear_cocinas(session):
    session.run(
        "UNWIND $cocinas AS cocina MERGE (c:Cuisine {nombre: cocina})",
        cocinas=["Italiana", "Japonesa", "Guatemalteca"],
    )


def crear_restaurantes(session):
    query = """
    UNWIND $restaurantes AS r
    MERGE (rest:Restaurant {id: r.id})
    SET rest.nombre = r.nombre, rest.rating = r.rating, rest.precio = r.precio
    WITH rest, r
    MATCH (z:Zone {nombre: r.zona})
    MERGE (rest)-[:LOCATED_IN]->(z)
    WITH rest, r
    MATCH (c:Cuisine {nombre: r.cocina})
    MERGE (rest)-[:HAS_CUISINE]->(c)
    """
    restaurantes = [
        {"id": "r1", "nombre": "Sushi Ito", "rating": 4.8, "precio": 120, "zona": "Zona 10", "cocina": "Japonesa"},
        {"id": "r2", "nombre": "La Trattoria", "rating": 4.5, "precio": 80, "zona": "Zona 10", "cocina": "Italiana"},
        {"id": "r3", "nombre": "El Fogón", "rating": 4.3, "precio": 60, "zona": "Zona 4", "cocina": "Guatemalteca"},
        {"id": "r4", "nombre": "Casa Mia", "rating": 4.6, "precio": 95, "zona": "Zona 1", "cocina": "Italiana"},
    ]
    session.run(query, restaurantes=restaurantes)


def crear_usuarios(session):
    query = """
    UNWIND $usuarios AS u
    MERGE (user:User {id: u.id})
    SET user.nombre = u.nombre, user.presupuesto = u.presupuesto
    WITH user, u
    MATCH (z:Zone {nombre: u.zona})
    MERGE (user)-[:LIVES_IN]->(z)
    WITH user, u
    UNWIND u.cocinas AS cocina
    MATCH (c:Cuisine {nombre: cocina})
    MERGE (user)-[:LIKES_CUISINE]->(c)
    """
    usuarios = [
        {"id": "u1", "nombre": "Ana G.", "zona": "Zona 10", "presupuesto": 150, "cocinas": ["Japonesa", "Italiana"]},
        {"id": "u2", "nombre": "Carlos M.", "zona": "Zona 10", "presupuesto": 120, "cocinas": ["Italiana", "Guatemalteca"]},
        {"id": "u3", "nombre": "Sofia R.", "zona": "Zona 4", "presupuesto": 80, "cocinas": ["Guatemalteca", "Japonesa"]},
    ]
    session.run(query, usuarios=usuarios)


def crear_visitas(session):
    query = """
    UNWIND $visitas AS v
    MATCH (u:User {id: v.usuario_id})
    MATCH (r:Restaurant {id: v.restaurante_id})
    MERGE (u)-[vis:VISITED]->(r)
    SET vis.fecha = v.fecha, vis.calificacion_personal = v.calificacion_personal
    """
    visitas = [
        {"usuario_id": "u1", "restaurante_id": "r1", "fecha": "2025-01-15", "calificacion_personal": 5.0},
        {"usuario_id": "u1", "restaurante_id": "r2", "fecha": "2025-02-20", "calificacion_personal": 4.5},
        {"usuario_id": "u2", "restaurante_id": "r2", "fecha": "2025-01-10", "calificacion_personal": 4.0},
        {"usuario_id": "u2", "restaurante_id": "r3", "fecha": "2025-03-05", "calificacion_personal": 4.2},
        {"usuario_id": "u3", "restaurante_id": "r3", "fecha": "2025-02-01", "calificacion_personal": 4.8},
        {"usuario_id": "u3", "restaurante_id": "r4", "fecha": "2025-03-18", "calificacion_personal": 4.6},
    ]
    session.run(query, visitas=visitas)


def cargar_datos():
    with get_session() as session:
        limpiar_base(session)
        crear_zonas(session)
        crear_cocinas(session)
        crear_restaurantes(session)
        crear_usuarios(session)
        crear_visitas(session)
    print("Datos cargados correctamente en Neo4j.")
