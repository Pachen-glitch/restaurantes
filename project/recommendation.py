"""Motor de recomendaciones basado en grafos."""

from __future__ import annotations

import math
from collections import defaultdict

from neo4j.exceptions import Neo4jError
from database import get_session
from user_manager import ensure_preference_catalog

SEP = "=" * 60


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(k, 0.0) * vec_b.get(k, 0.0) for k in keys)
    na = math.sqrt(sum(vec_a.get(k, 0.0) ** 2 for k in keys))
    nb = math.sqrt(sum(vec_b.get(k, 0.0) ** 2 for k in keys))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


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


def obtener_preferencias_usuario(usuario_id: str) -> dict[str, float]:
    query = """
    MATCH (u:User {id: $id})-[r:HAS_PREFERENCE]->(p:Preference)
    RETURN p.nombre AS pref, r.score AS score
    """
    with get_session() as session:
        return {row["pref"]: float(row["score"]) for row in session.run(query, id=usuario_id)}


def _restaurant_preference_vectors() -> dict[str, dict[str, float]]:
    query = """
    MATCH (r:Restaurant)-[m:MATCHES_PREFERENCE]->(p:Preference)
    RETURN r.id AS id, p.nombre AS pref, m.weight AS weight
    """
    out: dict[str, dict[str, float]] = defaultdict(dict)
    with get_session() as session:
        for row in session.run(query):
            out[row["id"]][row["pref"]] = float(row["weight"])
    return dict(out)


def _similar_users_visits(usuario_id: str) -> dict[str, int]:
    query = """
    MATCH (u:User {id: $usuario_id})
    OPTIONAL MATCH (u)-[:VISITED]->(visitado:Restaurant)
    WITH u, collect(DISTINCT visitado.id) AS visitados
    MATCH (u)-[:LIKES_CUISINE]->(c:Cuisine)<-[:LIKES_CUISINE]-(similar:User)
    WHERE similar <> u
    WITH visitados, similar, count(DISTINCT c) AS shared
    WHERE shared > 0
    MATCH (similar)-[:VISITED]->(r:Restaurant)
    WHERE NOT r.id IN visitados
    RETURN r.id AS restaurante_id, count(DISTINCT similar) AS similares
    """
    with get_session() as session:
        return {r["restaurante_id"]: int(r["similares"]) for r in session.run(query, usuario_id=usuario_id)}


def recomendar_restaurantes_inteligente(usuario_id: str) -> list[dict]:
    ensure_preference_catalog()
    user_prefs = obtener_preferencias_usuario(usuario_id)
    rest_prefs = _restaurant_preference_vectors()
    similares_map = _similar_users_visits(usuario_id)

    query = """
    MATCH (u:User {id: $usuario_id})
    OPTIONAL MATCH (u)-[:VISITED]->(vr:Restaurant)
    WITH u, collect(DISTINCT vr.id) AS visitados
    MATCH (r:Restaurant)
    WHERE NOT r.id IN visitados AND r.precio <= u.presupuesto
    OPTIONAL MATCH (u)-[:LIVES_IN]->(zu:Zone)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(zr:Zone)
    OPTIONAL MATCH (r)-[:HAS_CUISINE]->(rc:Cuisine)
    RETURN r.id AS id, r.nombre AS nombre, r.rating AS rating, r.precio AS precio,
           zr.nombre AS zona,
           CASE WHEN zu IS NOT NULL AND zr = zu THEN 1 ELSE 0 END AS misma_zona,
           collect(DISTINCT rc.nombre) AS cocinas
    """
    try:
        with get_session() as session:
            candidatos = [dict(r) for r in session.run(query, usuario_id=usuario_id)]
    except Neo4jError as exc:
        raise RuntimeError(f"Error al recomendar: {exc}") from exc

    max_sim = max(similares_map.values(), default=1) or 1
    scored: list[dict] = []
    for row in candidatos:
        rid = row["id"]
        rp = rest_prefs.get(rid, {})
        match_pref = cosine_similarity(user_prefs, rp) if user_prefs else 0.0
        similares = similares_map.get(rid, 0)
        rating = float(row.get("rating") or 0)
        misma_zona = int(row.get("misma_zona") or 0)
        match_pct = match_pref * 100
        sim_pct = (similares / max_sim) * 100 if similares else 0
        rating_pct = (rating / 5.0) * 100
        zone_pct = 100 if misma_zona else 0
        score_total = round(
            0.45 * match_pct + 0.25 * sim_pct + 0.2 * rating_pct + 0.1 * zone_pct,
            1,
        )
        item = dict(row)
        item["cocinas"] = [c for c in (item.get("cocinas") or []) if c]
        item["match_pref"] = round(match_pref, 3)
        item["usuarios_similares"] = similares
        item["similares"] = similares
        item["score_total"] = min(100.0, max(0.0, score_total))
        scored.append(item)

    scored.sort(
        key=lambda x: (
            x.get("score_total", 0),
            x.get("usuarios_similares", 0),
            x.get("misma_zona", 0),
            x.get("rating", 0),
        ),
        reverse=True,
    )
    return scored[:5]


def recomendar_restaurantes(usuario_id):
    return recomendar_restaurantes_inteligente(usuario_id)


def _node_key(label, props):
    if label in ("User", "Restaurant"):
        return f"{label}:{props.get('id', '')}"
    return f"{label}:{props.get('nombre', '')}"


def obtener_datos_grafo():
    nodes = {}
    edges = []

    node_query = """
    MATCH (n)
    WHERE n:User OR n:Restaurant OR n:Cuisine OR n:Zone OR n:Preference
    RETURN labels(n)[0] AS label, properties(n) AS props
    """
    rel_query = """
    MATCH (a)-[r]->(b)
    WHERE (a:User OR a:Restaurant OR a:Cuisine OR a:Zone OR a:Preference)
      AND (b:User OR b:Restaurant OR b:Cuisine OR b:Zone OR b:Preference)
    RETURN labels(a)[0] AS la, properties(a) AS pa,
           labels(b)[0] AS lb, properties(b) AS pb,
           type(r) AS rel, properties(r) AS rprops
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
            rprops = dict(rec["rprops"] or {})
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
            edge = {"source": source, "target": target, "rel": rec["rel"]}
            if rec["rel"] == "HAS_PREFERENCE" and "score" in rprops:
                edge["score"] = rprops["score"]
            if rec["rel"] == "MATCHES_PREFERENCE" and "weight" in rprops:
                edge["weight"] = rprops["weight"]
            edges.append(edge)

    return {"nodes": list(nodes.values()), "edges": edges}


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
        print(f"     Score IA: {r.get('score_total', 'N/A')} | Match pref: {r.get('match_pref', 'N/A')}")
        print(f"     Rating: {r['rating']} | Precio: Q{r['precio']} | Zona: {r.get('zona','N/A')}")
        print(f"     Cocinas: {cocinas}")
        print(f"     Usuarios similares: {r.get('usuarios_similares', r.get('similares', 0))} | Misma zona: {'Si' if r.get('misma_zona') else 'No'}")
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