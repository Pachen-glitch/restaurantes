"""Gestion de usuarios y preferencias gastronomicas en Neo4j."""

from __future__ import annotations

from database import get_session
from onboarding import map_food_to_cuisines

PREFERENCE_CATALOG = [
    "casual",
    "gourmet",
    "tradicional",
    "moderno",
    "aventurero",
    "explorador",
    "rutinero",
    "ahorrador",
    "equilibrado",
    "indulgente",
    "social_solo",
    "social_pareja",
    "social_familia",
    "social_grupo",
    "sabor_picante",
    "sabor_dulce",
    "sabor_salado",
    "sabor_umami",
    "sabor_fresco",
    "comida_rapida",
    "slow_food",
    "saludable",
    "contundente",
    "pref_japonesa",
    "pref_italiana",
    "pref_guatemalteca",
    "fast_food",
    "street_food",
    "premium",
    "spicy",
    "balanced_flavor",
    "intense_flavor",
    "comfort_food",
    "trendy",
    "aesthetic",
    "romantic",
    "family_friendly",
    "nightlife",
    "brunch",
    "exclusive",
    "fast_service",
    "tranquil",
    "elegant",
    "smoky",
    "home_dining",
    "lively",
    "intimate",
    "outdoor",
    "rooftop",
    "wine_focus",
    "craft_beer",
    "dessert_focus",
    "business_dining",
    "pref_coreana",
    "pref_mediterranea",
]

PRESUPUESTO_RANGOS = {
    "q50_150": 120,
    "q150_300": 225,
    "q300_600": 450,
    "q600_1000": 800,
    "q1000_2000": 1500,
    "mas_2000": 2500,
    "en_casa": 100,
}


def presupuesto_desde_rango(rango_key: str) -> int:
    return int(PRESUPUESTO_RANGOS.get(rango_key, 150))


def _catalog_from_restaurants() -> set[str]:
    try:
        from restaurants_guatemala import RESTAURANTS
    except ImportError:
        return set()
    names: set[str] = set(PREFERENCE_CATALOG)
    for r in RESTAURANTS:
        names.update((r.get("prefs") or {}).keys())
    return names


def generar_siguiente_user_id() -> str:
    query = "MATCH (u:User) WHERE u.id STARTS WITH 'u' RETURN u.id AS id"
    with get_session() as session:
        ids = [row["id"] for row in session.run(query)]
    max_n = 0
    for uid in ids:
        suffix = uid[1:] if uid.startswith("u") else ""
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return "u%d" % (max_n + 1)


def _usuario_existe(usuario_id: str) -> bool:
    with get_session() as session:
        rec = session.run("MATCH (u:User {id: $id}) RETURN count(u) AS n", id=usuario_id).single()
        return rec["n"] > 0


def ensure_preference_catalog() -> None:
    catalog = sorted(_catalog_from_restaurants())
    with get_session() as session:
        session.run(
            "UNWIND $names AS nombre MERGE (:Preference {nombre: nombre})",
            names=catalog,
        )


def crear_usuario_base(user_id: str, nombre: str, presupuesto: int, zona: str) -> None:
    if _usuario_existe(user_id):
        raise ValueError("El usuario '%s' ya existe." % user_id)
    with get_session() as session:
        session.run(
            """
            MERGE (u:User {id: $id})
            SET u.nombre = $nombre, u.presupuesto = $presupuesto
            """,
            id=user_id,
            nombre=nombre,
            presupuesto=int(presupuesto),
        )
        session.run(
            """
            MATCH (u:User {id: $id})
            MATCH (z:Zone {nombre: $zona})
            MERGE (u)-[:LIVES_IN]->(z)
            """,
            id=user_id,
            zona=zona,
        )


def guardar_perfil_gastronomico(user_id: str, profile_scores: dict[str, float]) -> None:
    if not _usuario_existe(user_id):
        raise ValueError("El usuario '%s' no existe." % user_id)
    allowed = _catalog_from_restaurants()
    scores = {k: float(v) for k, v in (profile_scores or {}).items() if k in allowed}
    with get_session() as session:
        for pref, score in scores.items():
            session.run(
                """
                MATCH (u:User {id: $id})
                MATCH (p:Preference {nombre: $pref})
                MERGE (u)-[r:HAS_PREFERENCE]->(p)
                SET r.score = $score
                """,
                id=user_id,
                pref=pref,
                score=score,
            )
        for cocina in map_food_to_cuisines(scores):
            session.run(
                """
                MATCH (u:User {id: $id})
                MATCH (c:Cuisine {nombre: $cocina})
                MERGE (u)-[:LIKES_CUISINE]->(c)
                """,
                id=user_id,
                cocina=cocina,
            )


def obtener_perfil_gastronomico(user_id: str) -> dict[str, float]:
    query = """
    MATCH (u:User {id: $id})-[r:HAS_PREFERENCE]->(p:Preference)
    RETURN p.nombre AS pref, r.score AS score
    ORDER BY score DESC
    """
    with get_session() as session:
        return {r["pref"]: float(r["score"]) for r in session.run(query, id=user_id)}


def actualizar_usuario(usuario_id, nombre, presupuesto, zona, cocinas=None):
    from recommendation import actualizar_usuario as legacy

    return legacy(usuario_id, nombre, presupuesto, zona, cocinas or [])