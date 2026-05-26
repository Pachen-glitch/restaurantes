"""Motor de recomendaciones basado en grafos."""

from neo4j.exceptions import Neo4jError
from database import get_session


def obtener_usuarios():
    query = """
    MATCH (u:User)
    OPTIONAL MATCH (u)-[:LIVES_IN]->(z:Zone)
    RETURN u.id AS id, u.nombre AS nombre, u.presupuesto AS presupuesto, z.nombre AS zona
    ORDER BY u.id
    """
    with get_session() as session:
        return [dict(r) for r in session.run(query)]


def recomendar_restaurantes(usuario_id):
    query = """
    MATCH (u:User {id: $usuario_id})
    OPTIONAL MATCH (u)-[:VISITED]->(visitado:Restaurant)
    WITH u, collect(DISTINCT visitado.id) AS visitados
    MATCH (u)-[:LIKES_CUISINE]->(cocina:Cuisine)
    MATCH (similar:User)-[:LIKES_CUISINE]->(cocina)
    WHERE similar <> u
    WITH u, visitados, similar, count(DISTINCT cocina) AS cocinas_compartidas
    WHERE cocinas_compartidas > 0
    MATCH (similar)-[:VISITED]->(r:Restaurant)
    WHERE NOT r.id IN visitados AND r.precio <= u.presupuesto
    OPTIONAL MATCH (u)-[:LIVES_IN]->(zona_usuario:Zone)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(zona_rest:Zone)
    OPTIONAL MATCH (r)-[:HAS_CUISINE]->(cocina_rest:Cuisine)
    OPTIONAL MATCH (u)-[:LIKES_CUISINE]->(cocina_rest)
    WITH r,
         count(DISTINCT similar) AS usuarios_similares,
         r.rating AS rating,
         r.precio AS precio,
         collect(DISTINCT zona_rest.nombre) AS zonas,
         CASE WHEN zona_usuario IS NOT NULL AND zona_rest = zona_usuario THEN 1 ELSE 0 END AS misma_zona,
         count(DISTINCT cocina_rest) AS cocinas_afines
    RETURN r.id AS id, r.nombre AS nombre, r.rating AS rating, r.precio AS precio,
           usuarios_similares, misma_zona, cocinas_afines, zonas
    ORDER BY usuarios_similares DESC, misma_zona DESC, rating DESC, precio ASC
    LIMIT 5
    """
    try:
        with get_session() as session:
            return [dict(r) for r in session.run(query, usuario_id=usuario_id)]
    except Neo4jError as error:
        raise RuntimeError(f"Error al generar recomendaciones: {error}") from error


def obtener_restaurantes_visitados(usuario_id):
    query = """
    MATCH (u:User {id: $usuario_id})-[v:VISITED]->(r:Restaurant)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(z:Zone)
    OPTIONAL MATCH (r)-[:HAS_CUISINE]->(c:Cuisine)
    RETURN r.id AS id, r.nombre AS nombre, r.rating AS rating, r.precio AS precio,
           v.fecha AS fecha, v.calificacion_personal AS calificacion_personal,
           z.nombre AS zona, collect(DISTINCT c.nombre) AS cocinas
    ORDER BY v.fecha DESC
    """
    try:
        with get_session() as session:
            return [dict(r) for r in session.run(query, usuario_id=usuario_id)]
    except Neo4jError as error:
        raise RuntimeError(f"Error al consultar visitas: {error}") from error


def usuario_existe(usuario_id):
    with get_session() as session:
        record = session.run(
            "MATCH (u:User {id: $usuario_id}) RETURN count(u) AS total",
            usuario_id=usuario_id,
        ).single()
        return record["total"] > 0


def imprimir_usuarios(usuarios):
    if not usuarios:
        print("\nNo hay usuarios. Carga los datos primero (opcion 1).\n")
        return
    print("\n" + "=" * 60)
    print(" USUARIOS REGISTRADOS")
    print("=" * 60)
    for u in usuarios:
        print(f"  {u['id']} | {u['nombre']} | Zona: {u.get('zona', 'N/A')} | Presupuesto: Q{u['presupuesto']}")
    print("=" * 60 + "\n")


def imprimir_recomendaciones(usuario_id, recomendaciones):
    print("\n" + "=" * 60)
    print(f" RECOMENDACIONES PARA {usuario_id.upper()}")
    print("=" * 60)
    if not recomendaciones:
        print("  No se encontraron recomendaciones.")
    else:
        for i, rec in enumerate(recomendaciones, 1):
            zonas = ", ".join(rec.get("zonas") or []) or "N/A"
            print(f"\n  #{i} {rec['nombre']} ({rec['id']})")
            print(f"     Rating: {rec['rating']} | Precio: Q{rec['precio']}")
            print(f"     Usuarios similares: {rec['usuarios_similares']}")
            print(f"     Misma zona: {'Si' if rec['misma_zona'] else 'No'}")
            print(f"     Ubicacion: {zonas}")
    print("\n" + "=" * 60 + "\n")


def imprimir_visitas(usuario_id, visitas):
    print("\n" + "=" * 60)
    print(f" VISITAS DE {usuario_id.upper()}")
    print("=" * 60)
    if not visitas:
        print("  Sin visitas registradas.\n")
        return
    for v in visitas:
        cocinas = ", ".join(v.get("cocinas") or []) or "N/A"
        print(f"\n  {v['nombre']} ({v['id']})")
        print(f"     Fecha: {v['fecha']} | Tu nota: {v['calificacion_personal']}")
        print(f"     Rating: {v['rating']} | Precio: Q{v['precio']} | Zona: {v.get('zona', 'N/A')}")
        print(f"     Cocina: {cocinas}")
    print("\n" + "=" * 60 + "\n")
