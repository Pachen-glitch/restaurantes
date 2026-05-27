"""Importacion segura del catalogo Guatemala a Neo4j (solo MERGE)."""

from __future__ import annotations

from database import get_session
from restaurants_guatemala import RESTAURANTS, ZONAS, CUISINES


def import_guatemala_restaurants() -> int:
    """Importa zonas, cocinas, restaurantes y MATCHES_PREFERENCE sin borrar datos."""
    all_prefs: set[str] = set()
    pref_edges: list[dict] = []
    for r in RESTAURANTS:
        for pref, weight in (r.get("prefs") or {}).items():
            all_prefs.add(pref)
            pref_edges.append(
                {"rest_id": r["id"], "pref": pref, "weight": float(weight)}
            )

    restaurantes = [
        {
            "id": r["id"],
            "nombre": r["nombre"],
            "rating": float(r["rating"]),
            "precio": int(r["precio"]),
            "zona": r["zona"],
            "cocina": r["cocina"],
            "ambiente": r.get("ambiente", "casual"),
        }
        for r in RESTAURANTS
    ]

    with get_session() as session:
        session.run("UNWIND $zonas AS nombre MERGE (:Zone {nombre: nombre})", zonas=ZONAS)
        session.run("UNWIND $cocinas AS nombre MERGE (:Cuisine {nombre: nombre})", cocinas=CUISINES)
        session.run(
            "UNWIND $names AS nombre MERGE (:Preference {nombre: nombre})",
            names=sorted(all_prefs),
        )
        session.run(
            """
            UNWIND $restaurantes AS r
            MERGE (rest:Restaurant {id: r.id})
            SET rest.nombre = r.nombre,
                rest.rating = r.rating,
                rest.precio = r.precio,
                rest.ambiente = r.ambiente
            WITH rest, r
            MATCH (z:Zone {nombre: r.zona})
            MERGE (rest)-[:LOCATED_IN]->(z)
            WITH rest, r
            MATCH (c:Cuisine {nombre: r.cocina})
            MERGE (rest)-[:HAS_CUISINE]->(c)
            """,
            restaurantes=restaurantes,
        )
        session.run(
            """
            UNWIND $edges AS e
            MATCH (rest:Restaurant {id: e.rest_id})
            MATCH (p:Preference {nombre: e.pref})
            MERGE (rest)-[m:MATCHES_PREFERENCE]->(p)
            SET m.weight = e.weight
            """,
            edges=pref_edges,
        )

    return len(RESTAURANTS)
