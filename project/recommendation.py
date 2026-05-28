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




MOOD_BOOSTS: dict[str, dict[str, float]] = {
    "comfort": {"comfort_food": 4.0, "casual": 3.0, "slow_food": 2.0},
    "explorar": {"explorador": 5.0, "aventurero": 4.0, "trendy": 2.5},
    "premium": {"premium": 5.0, "gourmet": 4.0, "exclusive": 3.5, "rooftop": 3.0},
    "social": {"social_grupo": 5.0, "lively": 3.5, "nightlife": 3.0},
    "chill": {"tranquil": 4.0, "coffee_culture": 3.5, "brunch": 3.0},
    "romantico": {"romantic": 5.0, "intimate": 4.0, "elegant": 2.5},
    "trabajo": {"business_dining": 5.0, "fast_service": 3.0, "elegant": 2.0},
    "familiar": {"family_friendly": 5.0, "comfort_food": 3.0, "casual": 2.5},
}


def apply_mood_boost(user_prefs: dict[str, float], mood: str | None) -> dict[str, float]:
    """Aplica boost temporal de mood sin modificar el perfil en Neo4j."""
    if not mood:
        return dict(user_prefs)
    boosts = MOOD_BOOSTS.get(mood, {})
    if not boosts:
        return dict(user_prefs)
    boosted = dict(user_prefs)
    for pref, delta in boosts.items():
        boosted[pref] = boosted.get(pref, 0.0) + float(delta)
    return boosted


def obtener_insights_usuario(usuario_id: str) -> dict:
    """Agrega insights visuales a partir de perfil y recomendaciones existentes."""
    perfil = obtener_preferencias_usuario(usuario_id)
    recs = recomendar_restaurantes_inteligente(usuario_id)
    detalle = obtener_usuario_detalle(usuario_id) or {}

    top_prefs = sorted(perfil.items(), key=lambda x: -x[1])[:8]
    top_pref_key = top_prefs[0][0] if top_prefs else ""
    top_pref_label = PREF_LABELS_ES.get(top_pref_key, top_pref_key.replace("_", " "))

    cocina_counts: dict[str, int] = {}
    zona_counts: dict[str, int] = {}
    for r in recs:
        for c in r.get("cocinas") or []:
            cocina_counts[c] = cocina_counts.get(c, 0) + 1
        z = r.get("zona")
        if z:
            zona_counts[z] = zona_counts.get(z, 0) + 1

    compat_vals = [float(r.get("compatibilidad_pct") or 0) for r in recs]
    compat_media = "%.0f%%" % (sum(compat_vals) / len(compat_vals)) if compat_vals else "—"

    heatmap = {k: min(10.0, v / 3.0) for k, v in top_prefs[:8]}

    return {
        "top_zona": detalle.get("zona") or (max(zona_counts, key=zona_counts.get) if zona_counts else "—"),
        "top_cocina": max(cocina_counts, key=cocina_counts.get) if cocina_counts else "—",
        "top_pref": top_pref_key,
        "top_pref_label": top_pref_label,
        "compat_media": compat_media,
        "top_prefs": top_prefs,
        "heatmap": heatmap,
        "top_restaurants": [
            {
                "nombre": r.get("nombre"),
                "pct": int(r.get("compatibilidad_pct") or 0),
                "zona": r.get("zona"),
            }
            for r in recs[:5]
        ],
    }


PREF_LABELS_ES = {
    "gourmet": "experiencias gourmet",
    "premium": "lugares premium",
    "casual": "ambientes casuales",
    "romantic": "cenas romanticas",
    "family_friendly": "salidas en familia",
    "street_food": "sabor callejero autentico",
    "pref_japonesa": "comida japonesa",
    "pref_italiana": "cocina italiana",
    "pref_guatemalteca": "sabores guatemaltecos",
    "pref_mexicana": "cocina mexicana",
    "pref_coreana": "cocina coreana",
    "pref_mediterranea": "cocina mediterranea",
    "sabor_umami": "perfil umami",
    "sabor_picante": "notas picantes",
    "tranquil": "ambientes tranquilos",
    "trendy": "lugares modernos y trendy",
    "brunch": "brunch de fin de semana",
    "exclusive": "experiencias exclusivas",
    "comfort_food": "comida reconfortante",
    "slow_food": "ritmo slow food",
    "explorador": "explorar experiencias nuevas",
    "aventurero": "descubrir sabores nuevos",
    "contundente": "platos contundentes",
    "aesthetic": "presentacion aesthetic",
    "nightlife": "ambiente nocturno",
    "elegant": "elegancia en el servicio",
    "smoky": "notas ahumadas",
    "saludable": "opciones saludables",
    "business_dining": "comidas de negocios",
    "fast_service": "servicio rapido",
    "home_dining": "comer en casa",
    "lively": "ambientes animados",
    "intimate": "espacios intimos",
    "rooftop": "terraza con vista",
    "coffee_culture": "cultura de cafe de especialidad",
    "asian_fusion": "fusion asiatica",
    "wine_focus": "maridaje con vino",
    "craft_beer": "cerveza artesanal",
    "social_grupo": "salidas sociales en grupo",
    "location_focus": "ubicacion conveniente",
    "presentation_focus": "presentacion impecable",
    "flavor_focus": "intensidad de sabor",
    "service_focus": "servicio destacado",
    "price_focus": "buena relacion precio-calidad",
}


def _restaurant_headline(nombre: str, tipo: str, rest_prefs: dict[str, float]) -> str:
    tipo_l = (tipo or "").lower()
    if rest_prefs.get("rooftop", 0) >= 0.7 and (
        rest_prefs.get("pref_japonesa", 0) >= 0.7 or "sushi" in tipo_l or "japon" in tipo_l
    ):
        return "Te recomendamos %s, un rooftop japones, porque:" % nombre
    if rest_prefs.get("rooftop", 0) >= 0.7:
        return "Te recomendamos %s, un rooftop con vista, porque:" % nombre
    if rest_prefs.get("pref_japonesa", 0) >= 0.8:
        return "Te recomendamos %s por su propuesta japonesa porque:" % nombre
    if rest_prefs.get("brunch", 0) >= 0.7 and rest_prefs.get("aesthetic", 0) >= 0.7:
        return "Te recomendamos %s para brunch aesthetic porque:" % nombre
    if rest_prefs.get("premium", 0) >= 0.8:
        return "Te recomendamos %s como experiencia premium porque:" % nombre
    return "Te recomendamos %s porque:" % nombre


def generar_explicacion(
    restaurant_nombre: str,
    user_prefs: dict[str, float],
    rest_prefs: dict[str, float],
    *,
    misma_zona: bool = False,
    explorador_score: float = 0.0,
    tipo: str = "",
    descripcion: str = "",
) -> list[str]:
    """Genera bullets en espanol tipo recomendacion hiper personalizada."""
    bullets: list[str] = []
    coincidencias: list[tuple[str, float]] = []
    for pref, u_score in user_prefs.items():
        w = rest_prefs.get(pref)
        if w is None or w < 0.45 or u_score < 4.0:
            continue
        coincidencias.append((pref, u_score * w))
    coincidencias.sort(key=lambda x: -x[1])

    for pref, _ in coincidencias[:4]:
        label = PREF_LABELS_ES.get(pref, pref.replace("_", " "))
        if pref.startswith("pref_"):
            bullets.append("tienes alta afinidad con %s" % label)
        elif pref in ("explorador", "aventurero"):
            bullets.append("te gusta %s" % label)
        elif pref in ("premium", "exclusive", "gourmet"):
            bullets.append("buscas %s" % label)
        elif pref in ("trendy", "aesthetic", "moderno"):
            bullets.append("disfrutas %s" % label)
        elif pref in ("romantic", "intimate"):
            bullets.append("valoras %s" % label)
        else:
            bullets.append("coincides en %s" % label)

    if rest_prefs.get("rooftop", 0) >= 0.7 and max(
        user_prefs.get("premium", 0),
        user_prefs.get("nightlife", 0),
        user_prefs.get("trendy", 0),
    ) >= 5:
        bullets.append("te atraen terrazas y ambientes con vista")
    if rest_prefs.get("pref_japonesa", 0) >= 0.7 and user_prefs.get("pref_japonesa", 0) >= 6:
        bullets.append("tienes alta afinidad con comida asiatica y japonesa")
    if rest_prefs.get("pref_italiana", 0) >= 0.7 and user_prefs.get("pref_italiana", 0) >= 6:
        bullets.append("te atrae la cocina italiana")
    if rest_prefs.get("premium", 0) >= 0.7 and user_prefs.get("premium", 0) >= 5:
        bullets.append("buscas experiencias premium")
    if rest_prefs.get("aesthetic", 0) >= 0.7 and user_prefs.get("aesthetic", 0) >= 5:
        bullets.append("disfrutas ambientes modernos y bien presentados")
    if rest_prefs.get("coffee_culture", 0) >= 0.7 and user_prefs.get("coffee_culture", 0) >= 5:
        bullets.append("valoras la cultura del cafe de especialidad")
    if explorador_score >= 6 and rest_prefs.get("trendy", 0) >= 0.6:
        bullets.append("te gusta explorar restaurantes nuevos")
    if rest_prefs.get("saludable", 0) >= 0.7 and user_prefs.get("saludable", 0) >= 5:
        bullets.append("priorizas opciones saludables y frescas")
    if rest_prefs.get("business_dining", 0) >= 0.7 and user_prefs.get("business_dining", 0) >= 5:
        bullets.append("necesitas un lugar ideal para reuniones de trabajo")

    if misma_zona:
        bullets.append("esta en tu zona habitual")

    seen: set[str] = set()
    unique: list[str] = []
    for b in bullets:
        if b not in seen:
            seen.add(b)
            unique.append(b)

    if not unique:
        if descripcion:
            unique.append(descripcion[:120])
        else:
            unique.append("tu perfil gastronomico encaja con el estilo de este lugar")

    headline = _restaurant_headline(restaurant_nombre, tipo, rest_prefs)
    return [headline] + unique[:5]


def _coincidencias_prefs(user_prefs: dict[str, float], rest_prefs: dict[str, float]) -> list[str]:
    out = []
    for pref, u_score in user_prefs.items():
        w = rest_prefs.get(pref)
        if w is not None and w >= 0.5 and u_score >= 4.0:
            out.append(pref)
    out.sort(key=lambda p: -(user_prefs.get(p, 0) * rest_prefs.get(p, 0)))
    return out[:8]

def recomendar_restaurantes_inteligente(usuario_id: str, mood: str | None = None) -> list[dict]:
    ensure_preference_catalog()
    user_prefs = apply_mood_boost(obtener_preferencias_usuario(usuario_id), mood)
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
           r.tipo AS tipo, r.descripcion AS descripcion,
           zr.nombre AS zona,
           CASE WHEN zu IS NOT NULL AND zr = zu THEN 1 ELSE 0 END AS misma_zona,
           collect(DISTINCT rc.nombre) AS cocinas
    """
    try:
        with get_session() as session:
            candidatos = [dict(r) for r in session.run(query, usuario_id=usuario_id)]
    except Neo4jError as exc:
        raise RuntimeError("Error al recomendar: %s" % exc) from exc

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
            0.5 * match_pct + 0.2 * sim_pct + 0.18 * rating_pct + 0.12 * zone_pct,
            1,
        )
        compatibilidad_pct = round(min(100.0, max(0.0, match_pref * 100)), 1)
        coincidencias = _coincidencias_prefs(user_prefs, rp)
        explorador = max(
            user_prefs.get("explorador", 0),
            user_prefs.get("aventurero", 0),
        )
        explicacion = generar_explicacion(
            row.get("nombre") or rid,
            user_prefs,
            rp,
            misma_zona=bool(misma_zona),
            explorador_score=explorador,
            tipo=row.get("tipo") or "",
            descripcion=row.get("descripcion") or "",
        )
        item = dict(row)
        item["cocinas"] = [c for c in (item.get("cocinas") or []) if c]
        item["match_pref"] = round(match_pref, 3)
        item["usuarios_similares"] = similares
        item["similares"] = similares
        item["score_total"] = min(100.0, max(0.0, score_total))
        item["compatibilidad_pct"] = compatibilidad_pct
        item["explicacion"] = explicacion
        item["coincidencias"] = coincidencias
        scored.append(item)

    scored.sort(
        key=lambda x: (
            x.get("score_total", 0),
            x.get("compatibilidad_pct", 0),
            x.get("usuarios_similares", 0),
            x.get("misma_zona", 0),
            x.get("rating", 0),
        ),
        reverse=True,
    )
    return scored[:8]



def recomendar_restaurantes(usuario_id):
    return recomendar_restaurantes_inteligente(usuario_id)


def _node_key(label, props):
    if label in ("User", "Restaurant"):
        return f"{label}:{props.get('id', '')}"
    return f"{label}:{props.get('nombre', '')}"


def obtener_datos_grafo(focus_user_id=None):
    nodes = {}
    edges = []

    if focus_user_id:
        node_query = """
        MATCH (u:User {id: $uid})
        OPTIONAL MATCH (u)-[r]-(n)
        WHERE n:Restaurant OR n:Cuisine OR n:Zone OR n:Preference
        WITH u, collect(DISTINCT n) AS neigh
        UNWIND neigh + [u] AS n
        RETURN labels(n)[0] AS label, properties(n) AS props
        """
        rel_query = """
        MATCH (u:User {id: $uid})
        MATCH (a)-[r]->(b)
        WHERE (a:User OR a:Restaurant OR a:Cuisine OR a:Zone OR a:Preference)
          AND (b:User OR b:Restaurant OR b:Cuisine OR b:Zone OR b:Preference)
          AND (a = u OR b = u)
        RETURN labels(a)[0] AS la, properties(a) AS pa,
               labels(b)[0] AS lb, properties(b) AS pb,
               type(r) AS rel, properties(r) AS rprops
        LIMIT 650
        """
        params = {"uid": focus_user_id}
    else:
        node_query = """
        MATCH (n)
        WHERE n:User OR n:Restaurant OR n:Cuisine OR n:Zone OR n:Preference
        RETURN labels(n)[0] AS label, properties(n) AS props
        LIMIT 220
        """
        rel_query = """
        MATCH (a)-[r]->(b)
        WHERE (a:User OR a:Restaurant OR a:Cuisine OR a:Zone OR a:Preference)
          AND (b:User OR b:Restaurant OR b:Cuisine OR b:Zone OR b:Preference)
        RETURN labels(a)[0] AS la, properties(a) AS pa,
               labels(b)[0] AS lb, properties(b) AS pb,
               type(r) AS rel, properties(r) AS rprops
        LIMIT 520
        """
        params = {}

    with get_session() as session:
        for rec in session.run(node_query, **params):
            label = rec["label"]
            props = dict(rec["props"])
            nid = _node_key(label, props)
            name = props.get("nombre") or props.get("id") or nid
            nodes[nid] = {"id": nid, "label": label, "name": name}

        for rec in session.run(rel_query, **params):
            la, pa = rec["la"], dict(rec["pa"])
            lb, pb = rec["lb"], dict(rec["pb"])
            rprops = dict(rec["rprops"] or {})
            source = _node_key(la, pa)
            target = _node_key(lb, pb)
            if source == target:
                continue
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