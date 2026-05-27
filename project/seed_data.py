"""
Crea automaticamente la base de datos en Neo4j AuraDB.
"""

from database import get_session

SEP = "=" * 60


def _titulo(texto):
    print(f"\n{SEP}\n  {texto}\n{SEP}")


def limpiar_base(session):
    session.run("MATCH (n) DETACH DELETE n")
    print("  [OK] Base limpiada")


def crear_zonas(session):
    zonas = ["Zona 10", "Zona 4", "Zona 1"]
    session.run("UNWIND $zonas AS nombre MERGE (z:Zone {nombre: nombre})", zonas=zonas)
    for z in zonas:
        print(f"  [OK] Zone: {z}")


def crear_cocinas(session):
    cocinas = ["Italiana", "Japonesa", "Guatemalteca"]
    session.run("UNWIND $cocinas AS nombre MERGE (c:Cuisine {nombre: nombre})", cocinas=cocinas)
    for c in cocinas:
        print(f"  [OK] Cuisine: {c}")


def crear_restaurantes(session):
    query = """
    UNWIND $restaurantes AS r
    MERGE (rest:Restaurant {id: r.id})
    SET rest.nombre = r.nombre, rest.rating = r.rating, rest.precio = r.precio
    WITH rest, r MATCH (z:Zone {nombre: r.zona}) MERGE (rest)-[:LOCATED_IN]->(z)
    WITH rest, r MATCH (c:Cuisine {nombre: r.cocina}) MERGE (rest)-[:HAS_CUISINE]->(c)
    """
    restaurantes = [
        {"id": "r1", "nombre": "Sushi Ito", "rating": 4.8, "precio": 120, "zona": "Zona 10", "cocina": "Japonesa"},
        {"id": "r2", "nombre": "La Trattoria", "rating": 4.5, "precio": 80, "zona": "Zona 10", "cocina": "Italiana"},
        {"id": "r3", "nombre": "El Fogón", "rating": 4.3, "precio": 60, "zona": "Zona 4", "cocina": "Guatemalteca"},
        {"id": "r4", "nombre": "Casa Mia", "rating": 4.6, "precio": 95, "zona": "Zona 1", "cocina": "Italiana"},
    ]
    session.run(query, restaurantes=restaurantes)
    for r in restaurantes:
        print(f"  [OK] {r['id']} {r['nombre']} | rating {r['rating']} | Q{r['precio']}")


def crear_usuarios(session):
    q_user = """
    UNWIND $usuarios AS u
    MERGE (user:User {id: u.id}) SET user.nombre = u.nombre, user.presupuesto = u.presupuesto
    WITH user, u MATCH (z:Zone {nombre: u.zona}) MERGE (user)-[:LIVES_IN]->(z)
    """
    q_like = "MATCH (user:User {id: $id}) MATCH (c:Cuisine {nombre: $cocina}) MERGE (user)-[:LIKES_CUISINE]->(c)"
    usuarios = [
        {"id": "u1", "nombre": "Ana G.", "zona": "Zona 10", "presupuesto": 150, "cocinas": ["Japonesa", "Italiana"]},
        {"id": "u2", "nombre": "Carlos M.", "zona": "Zona 10", "presupuesto": 120, "cocinas": ["Italiana", "Guatemalteca"]},
        {"id": "u3", "nombre": "Sofia R.", "zona": "Zona 4", "presupuesto": 80, "cocinas": ["Guatemalteca", "Japonesa"]},
    ]
    session.run(q_user, usuarios=usuarios)
    for u in usuarios:
        for c in u["cocinas"]:
            session.run(q_like, id=u["id"], cocina=c)
        print(f"  [OK] {u['id']} {u['nombre']} | {u['zona']} | Q{u['presupuesto']}")


def crear_visitas(session):
    query = """
    UNWIND $visitas AS v
    MATCH (u:User {id: v.usuario_id}) MATCH (r:Restaurant {id: v.restaurante_id})
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
    for v in visitas:
        print(f"  [OK] {v['usuario_id']} -> {v['restaurante_id']} | {v['fecha']} | nota {v['calificacion_personal']}")


def crear_base_datos():
    _titulo("CREANDO BASE DE DATOS NEO4J AURADB")
    with get_session() as session:
        _titulo("1. Limpiando datos")
        limpiar_base(session)
        _titulo("2. Zonas")
        crear_zonas(session)
        _titulo("3. Cocinas")
        crear_cocinas(session)
        _titulo("4. Restaurantes")
        crear_restaurantes(session)
        _titulo("5. Usuarios")
        crear_usuarios(session)
        _titulo("6. Visitas")
        crear_visitas(session)
    print(f"\n{SEP}\n  BASE DE DATOS CREADA EXITOSAMENTE\n{SEP}\n")


if __name__ == "__main__":
    crear_base_datos()
