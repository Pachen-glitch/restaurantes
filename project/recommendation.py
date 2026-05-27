"""Motor de recomendaciones basado en grafos."""

from neo4j.exceptions import Neo4jError
from database import get_session

SEP = "=" * 60


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
    MATCH (u)-[:LIKES_CUISINE]->(c:Cuisine)<-[:LIKES_CUISINE]-(similar:User)
    WHERE similar <> u
    WITH u, visitados, similar, count(DISTINCT c) AS cocinas_compartidas
    WHERE cocinas_compartidas > 0
    MATCH (similar)-[:VISITED]->(r:Restaurant)
    WHERE NOT r.id IN visitados AND r.precio <= u.presupuesto
    OPTIONAL MATCH (u)-[:LIVES_IN]->(zu:Zone)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(zr:Zone)
    WITH r, count(DISTINCT similar) AS usuarios_similares, r.rating AS rating,
         CASE WHEN zu IS NOT NULL AND zr = zu THEN 1 ELSE 0 END AS misma_zona
    RETURN r.id AS id, r.nombre AS nombre, r.rating AS rating, r.precio AS precio,
           usuarios_similares, misma_zona
    ORDER BY usuarios_similares DESC, misma_zona DESC, rating DESC
    LIMIT 5
    """
    try:
        with get_session() as session:
            return [dict(r) for r in session.run(query, usuario_id=usuario_id)]
    except Neo4jError as exc:
        raise RuntimeError(f"Error al recomendar: {exc}") from exc


def obtener_historial_usuario(usuario_id):
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
    except Neo4jError as exc:
        raise RuntimeError(f"Error al obtener historial: {exc}") from exc


def usuario_existe(usuario_id):
    with get_session() as session:
        rec = session.run("MATCH (u:User {id: $id}) RETURN count(u) AS n", id=usuario_id).single()
        return rec["n"] > 0


def imprimir_usuarios(usuarios):
    print(f"\n{SEP}\n  USUARIOS\n{SEP}")
    if not usuarios:
        print("  No hay usuarios. Ejecuta opcion 1.\n")
        return
    for u in usuarios:
        print(f"  {u['id']} | {u['nombre']} | Zona: {u.get('zona','N/A')} | Q{u['presupuesto']}")
    print()


def imprimir_recomendaciones(usuario_id, recs):
    print(f"\n{SEP}\n  RECOMENDACIONES PARA {usuario_id.upper()}\n{SEP}")
    if not recs:
        print("  Sin recomendaciones disponibles.\n")
        return
    for i, r in enumerate(recs, 1):
        print(f"  #{i} {r['nombre']} ({r['id']})")
        print(f"     Rating: {r['rating']} | Precio: Q{r['precio']}")
        print(f"     Usuarios similares: {r['usuarios_similares']} | Misma zona: {'Si' if r['misma_zona'] else 'No'}")
    print()


def imprimir_historial(usuario_id, visitas):
    print(f"\n{SEP}\n  HISTORIAL DE {usuario_id.upper()}\n{SEP}")
    if not visitas:
        print("  Sin visitas registradas.\n")
        return
    for v in visitas:
        cocinas = ", ".join(v.get("cocinas") or []) or "N/A"
        print(f"  {v['nombre']} ({v['id']}) | {v['fecha']} | nota {v['calificacion_personal']}")
        print(f"     Rating: {v['rating']} | Q{v['precio']} | Zona: {v.get('zona','N/A')} | {cocinas}")
    print()
