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


def obtener_zonas():
    query = "MATCH (z:Zone) RETURN z.nombre AS nombre ORDER BY z.nombre"
    with get_session() as session:
        return [r["nombre"] for r in session.run(query)]


def obtener_cocinas():
    query = "MATCH (c:Cuisine) RETURN c.nombre AS nombre ORDER BY c.nombre"
    with get_session() as session:
        return [r["nombre"] for r in session.run(query)]


def obtener_usuario_detalle(usuario_id):
    query = """
    MATCH (u:User {id: $usuario_id})
    OPTIONAL MATCH (u)-[:LIVES_IN]->(z:Zone)
    OPTIONAL MATCH (u)-[:LIKES_CUISINE]->(c:Cuisine)
    RETURN u.id AS id, u.nombre AS nombre, u.presupuesto AS presupuesto,
           z.nombre AS zona, collect(DISTINCT c.nombre) AS cocinas
    """
    with get_session() as session:
        rec = session.run(query, usuario_id=usuario_id).single()
        if rec is None:
            return None
        data = dict(rec)
        data["cocinas"] = [c for c in (data.get("cocinas") or []) if c]
        return data


def crear_usuario(usuario_id, nombre, presupuesto, zona, cocinas):
    if usuario_existe(usuario_id):
        raise ValueError(f"El usuario '{usuario_id}' ya existe.")
    cocinas = list(cocinas or [])
    with get_session() as session:
        session.run(
            """
            MERGE (u:User {id: $id})
            SET u.nombre = $nombre, u.presupuesto = $presupuesto
            """,
            id=usuario_id,
            nombre=nombre,
            presupuesto=int(presupuesto),
        )
        session.run(
            """
            MATCH (u:User {id: $id})
            MATCH (z:Zone {nombre: $zona})
            MERGE (u)-[:LIVES_IN]->(z)
            """,
            id=usuario_id,
            zona=zona,
        )
        for cocina in cocinas:
            session.run(
                """
                MATCH (u:User {id: $id})
                MATCH (c:Cuisine {nombre: $cocina})
                MERGE (u)-[:LIKES_CUISINE]->(c)
                """,
                id=usuario_id,
                cocina=cocina,
            )


def actualizar_usuario(usuario_id, nombre, presupuesto, zona, cocinas):
    if not usuario_existe(usuario_id):
        raise ValueError(f"El usuario '{usuario_id}' no existe.")
    cocinas = list(cocinas or [])
    with get_session() as session:
        session.run(
            """
            MATCH (u:User {id: $id})
            SET u.nombre = $nombre, u.presupuesto = $presupuesto
            """,
            id=usuario_id,
            nombre=nombre,
            presupuesto=int(presupuesto),
        )
        session.run(
            "MATCH (u:User {id: $id})-[r:LIVES_IN]->() DELETE r",
            id=usuario_id,
        )
        session.run(
            "MATCH (u:User {id: $id})-[r:LIKES_CUISINE]->() DELETE r",
            id=usuario_id,
        )
        session.run(
            """
            MATCH (u:User {id: $id})
            MATCH (z:Zone {nombre: $zona})
            MERGE (u)-[:LIVES_IN]->(z)
            """,
            id=usuario_id,
            zona=zona,
        )
        for cocina in cocinas:
            session.run(
                """
                MATCH (u:User {id: $id})
                MATCH (c:Cuisine {nombre: $cocina})
                MERGE (u)-[:LIKES_CUISINE]->(c)
                """,
                id=usuario_id,
                cocina=cocina,
            )


def _node_key(label, props):
    if label in ("User", "Restaurant"):
        return f"{label}:{props.get('id', '')}"
    return f"{label}:{props.get('nombre', '')}"


def obtener_datos_grafo():
    nodes = {}
    edges = []

    node_query = """
    MATCH (n)
    WHERE n:User OR n:Restaurant OR n:Cuisine OR n:Zone
    RETURN labels(n)[0] AS label, properties(n) AS props
    """
    rel_query = """
    MATCH (a)-[r]->(b)
    WHERE (a:User OR a:Restaurant OR a:Cuisine OR a:Zone)
      AND (b:User OR b:Restaurant OR b:Cuisine OR b:Zone)
    RETURN labels(a)[0] AS la, properties(a) AS pa,
           labels(b)[0] AS lb, properties(b) AS pb,
           type(r) AS rel
    """

    with get_session() as session:
        for rec in session.run(node_query):
            label = rec["label"]
            props = dict(rec["props"])
            nid = _node_key(label, props)
            name = props.get("nombre") or props.get("id") or nid
            nodes[nid] = {"id": nid, "label": label, "name": name}

        for rec in session.run(rel_query):
            la, pa = rec["la"], dict(rec["pa"])
            lb, pb = rec["lb"], dict(rec["pb"])
            source = _node_key(la, pa)
            target = _node_key(lb, pb)
            if source not in nodes:
                nodes[source] = {
                    "id": source,
                    "label": la,
                    "name": pa.get("nombre") or pa.get("id") or source,
                }
            if target not in nodes:
                nodes[target] = {
                    "id": target,
                    "label": lb,
                    "name": pb.get("nombre") or pb.get("id") or target,
                }
            edges.append({"source": source, "target": target, "rel": rec["rel"]})

    return {"nodes": list(nodes.values()), "edges": edges}


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
    OPTIONAL MATCH (r)-[:HAS_CUISINE]->(rc:Cuisine)
    WITH r, count(DISTINCT similar) AS usuarios_similares, r.rating AS rating,
         CASE WHEN zu IS NOT NULL AND zr = zu THEN 1 ELSE 0 END AS misma_zona,
         zr.nombre AS zona, collect(DISTINCT rc.nombre) AS cocinas
    RETURN r.id AS id, r.nombre AS nombre, r.rating AS rating, r.precio AS precio,
           usuarios_similares, misma_zona, zona, cocinas
    ORDER BY usuarios_similares DESC, misma_zona DESC, rating DESC
    LIMIT 5
    """
    try:
        with get_session() as session:
            rows = []
            for r in session.run(query, usuario_id=usuario_id):
                row = dict(r)
                row["cocinas"] = [c for c in (row.get("cocinas") or []) if c]
                rows.append(row)
            return rows
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
        cocinas = ", ".join(r.get("cocinas") or []) or "N/A"
        print(f"  #{i} {r['nombre']} ({r['id']})")
        print(f"     Rating: {r['rating']} | Precio: Q{r['precio']} | Zona: {r.get('zona','N/A')}")
        print(f"     Cocinas: {cocinas}")
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