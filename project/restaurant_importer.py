"""Importacion del catalogo gastronomico Guatemala a Neo4j (reemplazo seguro)."""

from __future__ import annotations

from database import get_session
from restaurants_guatemala import (
    BRANCH_TO_CANONICAL_ID,
    CUISINES,
    LEGACY_RESTAURANT_ID_PREFIXES,
    RESTAURANTS,
    ZONAS,
    validate_restaurant_catalog,
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


def migrate_visits_to_canonical(branch_map: dict[str, str]) -> dict[str, int]:
    """Reasigna VISITED de sucursales gc_* al restaurante canonico cn_*."""
    stats = {"migrated": 0, "skipped": 0}
    if not branch_map:
        return stats

    with get_session() as session:
        for old_id, new_id in branch_map.items():
            if old_id == new_id:
                stats["skipped"] += 1
                continue
            result = session.run(
                """
                MATCH (u:User)-[v:VISITED]->(old:Restaurant {id: $old_id})
                MATCH (new:Restaurant {id: $new_id})
                MERGE (u)-[nv:VISITED]->(new)
                SET nv.fecha = coalesce(v.fecha, nv.fecha),
                    nv.calificacion_personal = coalesce(v.calificacion_personal, nv.calificacion_personal)
                WITH v
                DELETE v
                RETURN count(*) AS n
                """,
                old_id=old_id,
                new_id=new_id,
            ).single()
            stats["migrated"] += int((result or {}).get("n") or 0)

    return stats


def purge_stale_restaurants(valid_ids: set[str]) -> dict[str, int]:
    """
    Elimina restaurantes que no pertenecen al catalogo actual.
    Conserva nodos con relaciones VISITED (historial de usuarios).
    """
    stats = {"removed": 0, "kept_with_visits": 0}
    ids = list(valid_ids)

    with get_session() as session:
        kept = session.run(
            """
            MATCH (r:Restaurant)
            WHERE NOT r.id IN $valid_ids AND (r)<-[:VISITED]-()
            RETURN count(r) AS n
            """,
            valid_ids=ids,
        ).single()
        stats["kept_with_visits"] = int((kept or {}).get("n") or 0)

        result = session.run(
            """
            MATCH (r:Restaurant)
            WHERE NOT r.id IN $valid_ids AND NOT (r)<-[:VISITED]-()
            DETACH DELETE r
            RETURN count(*) AS removed
            """,
            valid_ids=ids,
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
    zonas = list(restaurant.get("zonas_disponibles") or [])
    if not zonas and restaurant.get("zona"):
        zonas = [restaurant["zona"]]
    return {
        "id": restaurant["id"],
        "nombre": restaurant["nombre"],
        "canonical_name": restaurant.get("canonical_name", ""),
        "rating": float(restaurant["rating"]),
        "precio": int(restaurant["precio"]),
        "zona": restaurant.get("zona") or (zonas[0] if zonas else ""),
        "zonas_disponibles": zonas,
        "cocina": restaurant["cocina"],
        "tipo": restaurant.get("tipo", ""),
        "ambiente": restaurant.get("ambiente", "casual"),
        "price_tier": restaurant.get("price_tier", "casual"),
        "descripcion": restaurant.get("descripcion", ""),
        "semantic_archetype": restaurant.get("semantic_archetype", ""),
        "primary_archetype": restaurant.get("primary_archetype", restaurant.get("semantic_archetype", "")),
        "secondary_categories": list(restaurant.get("secondary_categories") or []),
        "gastronomic_personality": restaurant.get("gastronomic_personality", ""),
        "experience_style": restaurant.get("experience_style", ""),
        "cocina_principal": restaurant.get("cocina_principal", restaurant.get("cocina", "")),
        "ambiente_label": restaurant.get("ambiente_label", restaurant.get("ambiente", "")),
        "dimension_premium": int(restaurant.get("dimension_premium") or 0),
        "dimension_social": int(restaurant.get("dimension_social") or 0),
        "dimension_comfort": int(restaurant.get("dimension_comfort") or 0),
        "dimension_exploration": int(restaurant.get("dimension_exploration") or 0),
        "dimension_romantic": int(restaurant.get("dimension_romantic") or 0),
        "dimension_nightlife": int(restaurant.get("dimension_nightlife") or 0),
        "nightlife_score": int(restaurant.get("nightlife_score") or 0),
        "social_score": int(restaurant.get("social_score") or 0),
        "premium_score": int(restaurant.get("premium_score") or 0),
        "comfort_score": int(restaurant.get("comfort_score") or 0),
        "aesthetic_score": int(restaurant.get("aesthetic_score") or 0),
        "romantic_score": int(restaurant.get("romantic_score") or 0),
        "fast_service_score": int(restaurant.get("fast_service_score") or 0),
        "website_url": restaurant.get("website_url", ""),
        "instagram_url": restaurant.get("instagram_url", ""),
        "facebook_url": restaurant.get("facebook_url", ""),
        "maps_url": restaurant.get("maps_url", ""),
        "search_url": restaurant.get("search_url", ""),
    }


def _batch_import_restaurants(session, batch: list[dict]) -> None:
    session.run(
        """
        UNWIND $restaurantes AS r
        MERGE (rest:Restaurant {id: r.id})
        SET rest.nombre = r.nombre,
            rest.canonical_name = r.canonical_name,
            rest.rating = r.rating,
            rest.precio = r.precio,
            rest.ambiente = r.ambiente,
            rest.tipo = r.tipo,
            rest.price_tier = r.price_tier,
            rest.descripcion = r.descripcion,
            rest.semantic_archetype = r.semantic_archetype,
            rest.primary_archetype = r.primary_archetype,
            rest.secondary_categories = r.secondary_categories,
            rest.gastronomic_personality = r.gastronomic_personality,
            rest.experience_style = r.experience_style,
            rest.cocina_principal = r.cocina_principal,
            rest.ambiente_label = r.ambiente_label,
            rest.dimension_premium = r.dimension_premium,
            rest.dimension_social = r.dimension_social,
            rest.dimension_comfort = r.dimension_comfort,
            rest.dimension_exploration = r.dimension_exploration,
            rest.dimension_romantic = r.dimension_romantic,
            rest.dimension_nightlife = r.dimension_nightlife,
            rest.nightlife_score = r.nightlife_score,
            rest.social_score = r.social_score,
            rest.premium_score = r.premium_score,
            rest.comfort_score = r.comfort_score,
            rest.aesthetic_score = r.aesthetic_score,
            rest.romantic_score = r.romantic_score,
            rest.fast_service_score = r.fast_service_score,
            rest.website_url = r.website_url,
            rest.instagram_url = r.instagram_url,
            rest.facebook_url = r.facebook_url,
            rest.maps_url = r.maps_url,
            rest.search_url = r.search_url,
            rest.zonas_disponibles = r.zonas_disponibles,
            rest.zona = r.zona
        WITH rest, r
        MATCH (c:Cuisine {nombre: r.cocina})
        MERGE (rest)-[:HAS_CUISINE]->(c)
        WITH rest, r
        OPTIONAL MATCH (rest)-[old:LOCATED_IN]->(:Zone)
        DELETE old
        WITH rest, r
        UNWIND r.zonas_disponibles AS zona_nombre
        MATCH (z:Zone {nombre: zona_nombre})
        MERGE (rest)-[:LOCATED_IN]->(z)
        """,
        restaurantes=batch,
    )


def _purge_restaurant_pref_edges(session, restaurant_ids: list[str]) -> None:
    """Elimina MATCHES_PREFERENCE obsoletas antes de reimportar."""
    if not restaurant_ids:
        return
    session.run(
        """
        UNWIND $ids AS rid
        MATCH (r:Restaurant {id: rid})-[m:MATCHES_PREFERENCE]->()
        DELETE m
        """,
        ids=restaurant_ids,
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


def import_guatemala_restaurants(replace_legacy: bool = True) -> dict[str, int | str]:
    """
    Reemplaza catalogo antiguo/fake e importa restaurantes canonicos a Neo4j.
    Consolida sucursales y migra visitas de ids gc_* a cn_*.
    """
    valid_ids = {restaurant["id"] for restaurant in RESTAURANTS}
    purge_stats = {"legacy_removed": 0, "stale_removed": 0, "kept_with_visits": 0, "visits_migrated": 0}

    if replace_legacy:
        legacy = purge_legacy_restaurants()
        purge_stats["legacy_removed"] = legacy["removed"]
        purge_stats["kept_with_visits"] += legacy["kept_with_visits"]

    validation = validate_restaurant_catalog(RESTAURANTS)
    if not validation["valid"]:
        raise ValueError(
            "Catalogo con clasificacion incoherente (%d casos). Ejemplo: %s"
            % (len(validation["issues"]), validation["issues"][:2])
        )

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
            batch = restaurantes[i : i + BATCH_SIZE]
            _batch_import_restaurants(session, batch)
            _purge_restaurant_pref_edges(session, [r["id"] for r in batch])

        for i in range(0, len(pref_edges), BATCH_SIZE * 3):
            _batch_import_pref_edges(session, pref_edges[i : i + BATCH_SIZE * 3])

    if replace_legacy:
        migrate_stats = migrate_visits_to_canonical(BRANCH_TO_CANONICAL_ID)
        purge_stats["visits_migrated"] = migrate_stats["migrated"]
        stale = purge_stale_restaurants(valid_ids)
        purge_stats["stale_removed"] = stale["removed"]
        purge_stats["kept_with_visits"] += stale["kept_with_visits"]

    return {
        "imported": len(RESTAURANTS),
        "validation_ok": True,
        **purge_stats,
    }


def legacy_id_prefixes() -> tuple[str, ...]:
    return LEGACY_RESTAURANT_ID_PREFIXES
