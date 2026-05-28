"""Importacion del catalogo gastronomico Guatemala a Neo4j (reemplazo seguro)."""

from __future__ import annotations

from database import get_session
from restaurants_guatemala import (
    CUISINES,
    LEGACY_RESTAURANT_ID_PREFIXES,
    RESTAURANTS,
    ZONAS,
)

BATCH_SIZE = 40


def _is_legacy_restaurant_id(restaurant_id: str) -> bool:
    rid = str(restaurant_id or "")
    if rid.startswith("gt"):
        return True
    if rid.startswith("r") and rid[1:].isdigit():
        return True
    return False


def purge_legacy_restaurants() -> dict[str, int]:
    """
    Elimina restaurantes del catalogo antiguo (gt*, r1, r2...).
    Conserva usuarios, perfiles, preferencias y visitas:
    - Solo borra restaurantes legacy SIN relaciones VISITED.
    """
    stats = {"removed": 0, "kept_with_visits": 0}

    with get_session() as session:
        kept = session.run(
            """
            MATCH (r:Restaurant)
            WHERE (r.id STARTS WITH 'gt' OR (r.id STARTS WITH 'r' AND r.id =~ 'r[0-9]+'))
              AND (r)<-[:VISITED]-()
            RETURN count(r) AS n
            """
        ).single()
        stats["kept_with_visits"] = int((kept or {}).get("n") or 0)

        result = session.run(
            """
            MATCH (r:Restaurant)
            WHERE (r.id STARTS WITH 'gt' OR (r.id STARTS WITH 'r' AND r.id =~ 'r[0-9]+'))
              AND NOT (r)<-[:VISITED]-()
            WITH r
            DETACH DELETE r
            RETURN count(*) AS removed
            """
        ).single()
        stats["removed"] = int((result or {}).get("removed") or 0)

    return stats


def _normalize_pref_weight(value: float) -> float:
    """Convierte pesos 0-10 del dataset a escala 0-1 para MATCHES_PREFERENCE."""
    return round(max(0.0, min(10.0, float(value))) / 10.0, 2)


def _collect_pref_edges() -> tuple[set[str], list[dict]]:
    all_prefs: set[str] = set()
    pref_edges: list[dict] = []
    for restaurant in RESTAURANTS:
        for pref, weight in (restaurant.get("prefs") or {}).items():
            if not pref or float(weight) <= 0:
                continue
            all_prefs.add(pref)
            pref_edges.append(
                {
                    "rest_id": restaurant["id"],
                    "pref": pref,
                    "weight": _normalize_pref_weight(weight),
                }
            )
    return all_prefs, pref_edges


def _restaurant_payload(restaurant: dict) -> dict:
    return {
        "id": restaurant["id"],
        "nombre": restaurant["nombre"],
        "rating": float(restaurant["rating"]),
        "precio": int(restaurant["precio"]),
        "zona": restaurant["zona"],
        "cocina": restaurant["cocina"],
        "tipo": restaurant.get("tipo", ""),
        "ambiente": restaurant.get("ambiente", "casual"),
        "price_tier": restaurant.get("price_tier", "casual"),
        "descripcion": restaurant.get("descripcion", ""),
        "nightlife_score": int(restaurant.get("nightlife_score") or 0),
        "social_score": int(restaurant.get("social_score") or 0),
        "premium_score": int(restaurant.get("premium_score") or 0),
        "comfort_score": int(restaurant.get("comfort_score") or 0),
        "aesthetic_score": int(restaurant.get("aesthetic_score") or 0),
        "romantic_score": int(restaurant.get("romantic_score") or 0),
        "fast_service_score": int(restaurant.get("fast_service_score") or 0),
    }


def _batch_import_restaurants(session, batch: list[dict]) -> None:
    session.run(
        """
        UNWIND $restaurantes AS r
        MERGE (rest:Restaurant {id: r.id})
        SET rest.nombre = r.nombre,
            rest.rating = r.rating,
            rest.precio = r.precio,
            rest.ambiente = r.ambiente,
            rest.tipo = r.tipo,
            rest.price_tier = r.price_tier,
            rest.descripcion = r.descripcion,
            rest.nightlife_score = r.nightlife_score,
            rest.social_score = r.social_score,
            rest.premium_score = r.premium_score,
            rest.comfort_score = r.comfort_score,
            rest.aesthetic_score = r.aesthetic_score,
            rest.romantic_score = r.romantic_score,
            rest.fast_service_score = r.fast_service_score
        WITH rest, r
        MATCH (z:Zone {nombre: r.zona})
        MERGE (rest)-[:LOCATED_IN]->(z)
        WITH rest, r
        MATCH (c:Cuisine {nombre: r.cocina})
        MERGE (rest)-[:HAS_CUISINE]->(c)
        """,
        restaurantes=batch,
    )


def _batch_import_pref_edges(session, batch: list[dict]) -> None:
    session.run(
        """
        UNWIND $edges AS e
        MATCH (rest:Restaurant {id: e.rest_id})
        MATCH (p:Preference {nombre: e.pref})
        MERGE (rest)-[m:MATCHES_PREFERENCE]->(p)
        SET m.weight = e.weight
        """,
        edges=batch,
    )


def import_guatemala_restaurants(replace_legacy: bool = True) -> int:
    """
    Reemplaza el catalogo antiguo e importa el nuevo dataset Guatemala.
    Usa MERGE y lotes para mantener rendimiento en AuraDB.
    """
    if replace_legacy:
        purge_legacy_restaurants()

    all_prefs, pref_edges = _collect_pref_edges()
    restaurantes = [_restaurant_payload(r) for r in RESTAURANTS]

    with get_session() as session:
        session.run("UNWIND $zonas AS nombre MERGE (:Zone {nombre: nombre})", zonas=ZONAS)
        session.run("UNWIND $cocinas AS nombre MERGE (:Cuisine {nombre: nombre})", cocinas=CUISINES)
        session.run(
            "UNWIND $names AS nombre MERGE (:Preference {nombre: nombre})",
            names=sorted(all_prefs),
        )

        for i in range(0, len(restaurantes), BATCH_SIZE):
            _batch_import_restaurants(session, restaurantes[i : i + BATCH_SIZE])

        for i in range(0, len(pref_edges), BATCH_SIZE * 3):
            _batch_import_pref_edges(session, pref_edges[i : i + BATCH_SIZE * 3])

    return len(RESTAURANTS)


def legacy_id_prefixes() -> tuple[str, ...]:
    return LEGACY_RESTAURANT_ID_PREFIXES
