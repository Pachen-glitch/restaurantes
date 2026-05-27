from pathlib import Path

path = Path("recommendation.py")
src = path.read_text(encoding="utf-8")

insert = '''

PREF_LABELS_ES = {
    "gourmet": "experiencia gourmet",
    "premium": "nivel premium",
    "casual": "ambiente casual",
    "romantic": "ideal para pareja",
    "family_friendly": "apto para familia",
    "street_food": "sabor callejero",
    "pref_japonesa": "cocina japonesa",
    "pref_italiana": "cocina italiana",
    "pref_guatemalteca": "cocina guatemalteca",
    "sabor_umami": "perfil umami",
    "sabor_picante": "notas picantes",
    "tranquil": "ambiente tranquilo",
    "trendy": "lugar trendy",
    "brunch": "estilo brunch",
    "exclusive": "experiencia exclusiva",
    "comfort_food": "comida reconfortante",
    "slow_food": "ritmo slow food",
    "explorador": "espiritu explorador",
    "contundente": "platos contundentes",
    "aesthetic": "presentacion aesthetic",
    "nightlife": "vida nocturna",
    "elegant": "elegancia",
    "smoky": "notas ahumadas",
    "saludable": "opciones saludables",
}


def generar_explicacion(
    usuario_id: str,
    restaurant_id: str,
    user_prefs: dict[str, float],
    rest_prefs: dict[str, float],
) -> list[str]:
    bullets: list[str] = []
    coincidencias = []
    for pref, u_score in sorted(user_prefs.items(), key=lambda x: -x[1]):
        w = rest_prefs.get(pref)
        if w is None or w < 0.45:
            continue
        if u_score < 4.0:
            continue
        coincidencias.append(pref)
    if coincidencias:
        top = coincidencias[:3]
        labels = [PREF_LABELS_ES.get(p, p.replace("_", " ")) for p in top]
        bullets.append("Coincide con tus preferencias: " + ", ".join(labels) + ".")
    if rest_prefs.get("pref_japonesa", 0) >= 0.8 and user_prefs.get("pref_japonesa", 0) >= 6:
        bullets.append("Fuerte alineacion con tu gusto por cocina japonesa.")
    if rest_prefs.get("pref_italiana", 0) >= 0.8 and user_prefs.get("pref_italiana", 0) >= 6:
        bullets.append("Encaja con tu preferencia por cocina italiana.")
    if rest_prefs.get("pref_guatemalteca", 0) >= 0.8 and user_prefs.get("pref_guatemalteca", 0) >= 6:
        bullets.append("Conecta con sabores guatemaltecos que valoras.")
    if not bullets:
        bullets.append("Recomendado por afinidad global de perfil y datos del grafo.")
    bullets.append("Usuario %s vs restaurante %s." % (usuario_id, restaurant_id))
    return bullets[:5]


def _coincidencias_prefs(user_prefs: dict[str, float], rest_prefs: dict[str, float]) -> list[str]:
    out = []
    for pref, u_score in user_prefs.items():
        w = rest_prefs.get(pref)
        if w is not None and w >= 0.5 and u_score >= 4.0:
            out.append(pref)
    out.sort(key=lambda p: -(user_prefs.get(p, 0) * rest_prefs.get(p, 0)))
    return out[:8]

'''

marker = "def recomendar_restaurantes_inteligente"
if "def generar_explicacion" not in src:
    src = src.replace(marker, insert + marker)

new_intel = '''def recomendar_restaurantes_inteligente(usuario_id: str) -> list[dict]:
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
        explicacion = generar_explicacion(usuario_id, rid, user_prefs, rp)
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
'''

import re
src = re.sub(
    r"def recomendar_restaurantes_inteligente\(usuario_id: str\) -> list\[dict\]:.*?return scored\[:5\]",
    new_intel,
    src,
    count=1,
    flags=re.S,
)

new_grafo = '''def obtener_datos_grafo(focus_user_id=None):
    nodes = {}
    edges = []

    if focus_user_id:
        node_query = """
        MATCH (u:User {id: $uid})
        OPTIONAL MATCH (u)-[r1]->(n1)
        WHERE n1:Restaurant OR n1:Cuisine OR n1:Zone OR n1:Preference
        OPTIONAL MATCH (n2)-[r2]->(u)
        WHERE n2:Restaurant OR n2:Cuisine OR n2:Zone OR n2:Preference
        WITH collect(DISTINCT u) + collect(DISTINCT n1) + collect(DISTINCT n2) AS raw
        UNWIND raw AS n
        RETURN labels(n)[0] AS label, properties(n) AS props
        """
        rel_query = """
        MATCH (u:User {id: $uid})
        OPTIONAL MATCH (a)-[r]->(b)
        WHERE (a:User OR a:Restaurant OR a:Cuisine OR a:Zone OR a:Preference)
          AND (b:User OR b:Restaurant OR b:Cuisine OR b:Zone OR b:Preference)
          AND (a = u OR b = u OR (a)-[]-(u) OR (b)-[]-(u))
        RETURN labels(a)[0] AS la, properties(a) AS pa,
               labels(b)[0] AS lb, properties(b) AS pb,
               type(r) AS rel, properties(r) AS rprops
        LIMIT 400
        """
        params = {"uid": focus_user_id}
    else:
        node_query = """
        MATCH (n)
        WHERE n:User OR n:Restaurant OR n:Cuisine OR n:Zone OR n:Preference
        RETURN labels(n)[0] AS label, properties(n) AS props
        LIMIT 120
        """
        rel_query = """
        MATCH (a)-[r]->(b)
        WHERE (a:User OR a:Restaurant OR a:Cuisine OR a:Zone OR a:Preference)
          AND (b:User OR b:Restaurant OR b:Cuisine OR b:Zone OR b:Preference)
        RETURN labels(a)[0] AS la, properties(a) AS pa,
               labels(b)[0] AS lb, properties(b) AS pb,
               type(r) AS rel, properties(r) AS rprops
        LIMIT 250
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
'''

src = re.sub(
    r"def obtener_datos_grafo\(\):.*?return \{\"nodes\": list\(nodes\.values\(\)\), \"edges\": edges\}",
    new_grafo,
    src,
    count=1,
    flags=re.S,
)

path.write_text(src, encoding="utf-8")
print("patched", path)