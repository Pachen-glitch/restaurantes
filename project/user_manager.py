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
]

RESTAURANT_PREFERENCE_MAP = {
    "r1": {
        "gourmet": 0.9,
        "aventurero": 0.7,
        "explorador": 0.6,
        "indulgente": 0.8,
        "sabor_umami": 0.95,
        "pref_japonesa": 1.0,
        "slow_food": 0.75,
        "social_pareja": 0.5,
    },
    "r2": {
        "gourmet": 0.65,
        "tradicional": 0.55,
        "equilibrado": 0.7,
        "pref_italiana": 1.0,
        "slow_food": 0.6,
        "social_pareja": 0.6,
        "social_grupo": 0.5,
    },
    "r3": {
        "casual": 0.8,
        "tradicional": 0.85,
        "ahorrador": 0.75,
        "contundente": 0.9,
        "pref_guatemalteca": 1.0,
        "social_familia": 0.7,
        "comida_rapida": 0.4,
    },
    "r4": {
        "equilibrado": 0.8,
        "gourmet": 0.55,
        "pref_italiana": 1.0,
        "social_pareja": 0.75,
        "slow_food": 0.5,
        "tradicional": 0.45,
    },
}


def _usuario_existe(usuario_id: str) -> bool:
    with get_session() as session:
        rec = session.run("MATCH (u:User {id: $id}) RETURN count(u) AS n", id=usuario_id).single()
        return rec["n"] > 0


def ensure_preference_catalog() -> None:
    with get_session() as session:
        session.run(
            "UNWIND $names AS nombre MERGE (:Preference {nombre: nombre})",
            names=PREFERENCE_CATALOG,
        )
        for rest_id, prefs in RESTAURANT_PREFERENCE_MAP.items():
            for pref, weight in prefs.items():
                session.run(
                    """
                    MATCH (r:Restaurant {id: $rest_id})
                    MATCH (p:Preference {nombre: $pref})
                    MERGE (r)-[m:MATCHES_PREFERENCE]->(p)
                    SET m.weight = $weight
                    """,
                    rest_id=rest_id,
                    pref=pref,
                    weight=float(weight),
                )


def crear_usuario_base(user_id: str, nombre: str, presupuesto: int, zona: str) -> None:
    if _usuario_existe(user_id):
        raise ValueError(f"El usuario '{user_id}' ya existe.")
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
        raise ValueError(f"El usuario '{user_id}' no existe.")
    scores = {k: float(v) for k, v in (profile_scores or {}).items() if k in PREFERENCE_CATALOG}
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