"""Catalogo de restaurantes REALES de Ciudad de Guatemala para Neo4j."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

CUISINES = [
    "Japonesa",
    "Italiana",
    "Mexicana",
    "Guatemalteca",
    "Mediterranea",
    "Francesa",
    "Peruana",
    "Steakhouse",
    "Cafe",
    "Coreana",
    "Asiatica",
    "Internacional",
    "Mariscos",
    "Saludable",
    "Fusion",
]

ZONAS = ["Zona 10", "Zona 14", "Zona 15", "Zona 16", "Zona 11", "Zona 5"]

LEGACY_RESTAURANT_ID_PREFIXES = ("gt", "r")

_PRICE_TIER_RANGE = {
    "economico": (45, 90),
    "casual": (90, 180),
    "premium": (180, 340),
    "fine": (340, 560),
    "luxury": (560, 900),
}

_PREF_KEYS = [
    "gourmet",
    "premium",
    "romantic",
    "brunch",
    "nightlife",
    "aesthetic",
    "comfort_food",
    "trendy",
    "social_grupo",
    "business_dining",
    "family_friendly",
    "saludable",
    "aventurero",
    "casual",
    "exclusive",
    "fast_service",
    "rooftop",
    "coffee_culture",
    "asian_fusion",
    "pref_japonesa",
    "pref_italiana",
    "pref_mexicana",
    "pref_coreana",
    "pref_mediterranea",
    "pref_guatemalteca",
    "wine_focus",
    "craft_beer",
    "street_food",
    "slow_food",
    "elegant",
    "lively",
    "intimate",
    "fast_food",
    "comida_rapida",
]

# Perfiles semanticos: prefs coherentes + caps + prefs prohibidas por arquetipo.
SEMANTIC_ARCHETYPES: dict[str, dict[str, Any]] = {
    "fast_food": {
        "scores": {
            "nightlife_score": 3,
            "social_score": 7,
            "premium_score": 2,
            "comfort_score": 8,
            "aesthetic_score": 4,
            "romantic_score": 2,
            "fast_service_score": 10,
        },
        "prefs": {
            "fast_food": 10,
            "comida_rapida": 10,
            "fast_service": 10,
            "casual": 9,
            "comfort_food": 8,
            "family_friendly": 7,
            "social_grupo": 6,
        },
        "forbidden": {
            "pref_italiana",
            "pref_japonesa",
            "pref_coreana",
            "pref_mediterranea",
            "gourmet",
            "exclusive",
            "romantic",
            "intimate",
            "wine_focus",
            "slow_food",
            "business_dining",
            "elegant",
        },
        "max_prefs": {"premium": 2, "aesthetic": 4, "trendy": 4},
    },
    "guatemalteca_fast": {
        "scores": {
            "nightlife_score": 3,
            "social_score": 8,
            "premium_score": 2,
            "comfort_score": 9,
            "aesthetic_score": 4,
            "romantic_score": 2,
            "fast_service_score": 10,
        },
        "prefs": {
            "pref_guatemalteca": 10,
            "fast_food": 8,
            "comida_rapida": 8,
            "fast_service": 9,
            "comfort_food": 8,
            "family_friendly": 9,
            "casual": 8,
        },
        "forbidden": {
            "pref_italiana",
            "gourmet",
            "exclusive",
            "romantic",
            "wine_focus",
            "business_dining",
            "elegant",
        },
        "max_prefs": {"premium": 3, "trendy": 4},
    },
    "italian_premium": {
        "scores": {
            "nightlife_score": 5,
            "social_score": 7,
            "premium_score": 8,
            "comfort_score": 6,
            "aesthetic_score": 8,
            "romantic_score": 8,
            "fast_service_score": 5,
        },
        "prefs": {
            "pref_italiana": 10,
            "slow_food": 8,
            "wine_focus": 8,
            "romantic": 7,
            "business_dining": 7,
            "premium": 7,
            "elegant": 6,
        },
        "forbidden": {"fast_food", "comida_rapida", "street_food"},
        "max_prefs": {"fast_service": 6},
    },
    "italian_casual": {
        "scores": {
            "nightlife_score": 4,
            "social_score": 8,
            "premium_score": 4,
            "comfort_score": 8,
            "aesthetic_score": 5,
            "romantic_score": 5,
            "fast_service_score": 7,
        },
        "prefs": {
            "pref_italiana": 9,
            "casual": 8,
            "family_friendly": 8,
            "comfort_food": 7,
            "fast_service": 7,
        },
        "forbidden": {"gourmet", "exclusive", "fast_food", "business_dining"},
        "max_prefs": {"premium": 4, "romantic": 5},
    },
    "steakhouse_premium": {
        "scores": {
            "nightlife_score": 5,
            "social_score": 7,
            "premium_score": 9,
            "comfort_score": 6,
            "aesthetic_score": 7,
            "romantic_score": 6,
            "fast_service_score": 5,
        },
        "prefs": {
            "premium": 9,
            "gourmet": 8,
            "business_dining": 8,
            "contundente": 8,
            "wine_focus": 6,
            "elegant": 6,
        },
        "forbidden": {"fast_food", "comida_rapida", "street_food"},
        "max_prefs": {"fast_service": 6},
    },
    "cafe_brunch": {
        "scores": {
            "nightlife_score": 3,
            "social_score": 7,
            "premium_score": 4,
            "comfort_score": 8,
            "aesthetic_score": 8,
            "romantic_score": 5,
            "fast_service_score": 7,
        },
        "prefs": {
            "coffee_culture": 10,
            "brunch": 8,
            "aesthetic": 7,
            "casual": 8,
            "saludable": 6,
        },
        "forbidden": {"gourmet", "exclusive", "nightlife", "business_dining"},
        "max_prefs": {"premium": 4, "romantic": 5},
    },
    "fusion_premium": {
        "scores": {
            "nightlife_score": 7,
            "social_score": 8,
            "premium_score": 8,
            "comfort_score": 5,
            "aesthetic_score": 9,
            "romantic_score": 7,
            "fast_service_score": 5,
        },
        "prefs": {
            "gourmet": 9,
            "trendy": 9,
            "aventurero": 8,
            "aesthetic": 8,
            "social_grupo": 8,
            "premium": 7,
        },
        "forbidden": {"fast_food", "comida_rapida"},
        "max_prefs": {"fast_service": 6},
    },
    "nightlife_social": {
        "scores": {
            "nightlife_score": 9,
            "social_score": 9,
            "premium_score": 6,
            "comfort_score": 5,
            "aesthetic_score": 8,
            "romantic_score": 4,
            "fast_service_score": 6,
        },
        "prefs": {
            "nightlife": 9,
            "lively": 8,
            "social_grupo": 9,
            "craft_beer": 7,
            "trendy": 7,
        },
        "forbidden": {"family_friendly", "slow_food", "romantic"},
        "max_prefs": {"premium": 6},
    },
    "healthy_casual": {
        "scores": {
            "nightlife_score": 2,
            "social_score": 6,
            "premium_score": 3,
            "comfort_score": 6,
            "aesthetic_score": 7,
            "romantic_score": 3,
            "fast_service_score": 8,
        },
        "prefs": {
            "saludable": 10,
            "fast_service": 8,
            "casual": 7,
            "aesthetic": 6,
        },
        "forbidden": {"gourmet", "exclusive", "nightlife", "premium"},
        "max_prefs": {"premium": 3},
    },
    "casual_dining": {
        "scores": {
            "nightlife_score": 4,
            "social_score": 7,
            "premium_score": 4,
            "comfort_score": 8,
            "aesthetic_score": 5,
            "romantic_score": 4,
            "fast_service_score": 7,
        },
        "prefs": {
            "casual": 8,
            "comfort_food": 7,
            "family_friendly": 7,
            "fast_service": 7,
            "social_grupo": 6,
        },
        "forbidden": set(),
        "max_prefs": {"premium": 5, "gourmet": 5},
    },
    "premium_fine": {
        "scores": {
            "nightlife_score": 6,
            "social_score": 7,
            "premium_score": 9,
            "comfort_score": 6,
            "aesthetic_score": 9,
            "romantic_score": 8,
            "fast_service_score": 5,
        },
        "prefs": {
            "premium": 9,
            "gourmet": 9,
            "exclusive": 8,
            "elegant": 8,
            "romantic": 7,
            "wine_focus": 7,
        },
        "forbidden": {"fast_food", "comida_rapida", "street_food", "fast_service"},
        "max_prefs": {"fast_service": 6},
    },
}

_FAST_FOOD_NAMES = (
    "mcdonald",
    "burger king",
    "kfc",
    "wendy",
    "taco bell",
    "subway",
    "domino",
    "pizza hut",
    "little caesar",
    "papa john",
)

_CUISINE_PREF_HINTS = {
    "Japonesa": {"pref_japonesa": 9, "asian_fusion": 7, "gourmet": 6},
    "Italiana": {"pref_italiana": 9, "wine_focus": 6, "slow_food": 6},
    "Mexicana": {"pref_mexicana": 9, "street_food": 6, "lively": 6},
    "Guatemalteca": {"pref_guatemalteca": 9, "comfort_food": 7, "family_friendly": 6},
    "Mediterranea": {"pref_mediterranea": 9, "saludable": 7, "romantic": 5},
    "Cafe": {"coffee_culture": 9, "brunch": 7, "aesthetic": 6},
    "Coreana": {"pref_coreana": 9, "asian_fusion": 7, "aventurero": 6},
    "Asiatica": {"asian_fusion": 8, "aventurero": 6},
    "Steakhouse": {"gourmet": 7, "premium": 7, "business_dining": 6},
    "Mariscos": {"gourmet": 6, "romantic": 5, "slow_food": 6},
    "Francesa": {"gourmet": 8, "elegant": 7, "wine_focus": 6},
    "Peruana": {"aventurero": 7, "gourmet": 6, "asian_fusion": 5},
    "Saludable": {"saludable": 9, "brunch": 6, "aesthetic": 6},
    "Fusion": {"asian_fusion": 7, "trendy": 7, "aventurero": 6},
    "Internacional": {"business_dining": 6, "premium": 5},
}

_AMBIENTE_PREFS = {
    "elegante": {"elegant": 8, "gourmet": 6, "business_dining": 6},
    "romantico": {"romantic": 8, "intimate": 7, "slow_food": 6},
    "trendy": {"trendy": 8, "aesthetic": 8, "social_grupo": 6},
    "familiar": {"family_friendly": 8, "comfort_food": 7, "casual": 5},
    "casual": {"casual": 8, "fast_service": 6, "lively": 5},
    "nocturno": {"nightlife": 8, "lively": 7, "social_grupo": 7},
    "brunch": {"brunch": 9, "aesthetic": 7, "coffee_culture": 6},
    "cozy": {"intimate": 6, "comfort_food": 6, "romantic": 5},
}

_SCORE_PROFILES = {
    "luxury": {
        "nightlife_score": 7,
        "social_score": 8,
        "premium_score": 10,
        "comfort_score": 6,
        "aesthetic_score": 9,
        "romantic_score": 8,
        "fast_service_score": 6,
    },
    "premium": {
        "nightlife_score": 6,
        "social_score": 7,
        "premium_score": 8,
        "comfort_score": 6,
        "aesthetic_score": 8,
        "romantic_score": 7,
        "fast_service_score": 6,
    },
    "cafe": {
        "nightlife_score": 4,
        "social_score": 7,
        "premium_score": 5,
        "comfort_score": 8,
        "aesthetic_score": 8,
        "romantic_score": 6,
        "fast_service_score": 7,
    },
    "casual": {
        "nightlife_score": 5,
        "social_score": 8,
        "premium_score": 4,
        "comfort_score": 8,
        "aesthetic_score": 5,
        "romantic_score": 4,
        "fast_service_score": 8,
    },
}


def _detect_semantic_archetype(
    nombre: str,
    cocina: str,
    tipo: str,
    ambiente: str,
    price_tier: str,
    profile: str,
) -> str:
    name_l = (nombre or "").lower()
    tipo_l = (tipo or "").lower()
    ambiente_l = (ambiente or "").lower()

    if any(token in name_l for token in _FAST_FOOD_NAMES) or "comida rapida" in tipo_l:
        return "fast_food"
    if "pollo campero" in name_l or name_l.strip() == "tip top":
        return "guatemalteca_fast"
    if cocina == "Saludable" or "healthy" in tipo_l or "ensalada" in tipo_l:
        return "healthy_casual"
    if cocina == "Cafe" or "cafe" in tipo_l or "coffee" in tipo_l or "brunch" in tipo_l or "bakery" in tipo_l:
        return "cafe_brunch"
    if "food hall" in tipo_l or "mercado" in tipo_l:
        return "fusion_premium"
    if ambiente_l == "nocturno" or "gastrobar" in tipo_l or "cantina" in tipo_l or "cerveceria" in tipo_l:
        return "nightlife_social"
    if cocina == "Steakhouse" or "steakhouse" in tipo_l or "parrilla" in tipo_l:
        return "steakhouse_premium"
    if cocina == "Italiana":
        if price_tier in {"fine", "luxury"} or any(k in tipo_l for k in ("ristorante", "trattoria", "fine", "steakhouse")):
            return "italian_premium"
        return "italian_casual"
    if profile == "luxury" or price_tier in {"fine", "luxury"}:
        return "premium_fine"
    if cocina == "Fusion" and price_tier in {"premium", "fine", "luxury"}:
        return "fusion_premium"
    if price_tier == "economico" or profile == "casual":
        return "casual_dining"
    return "premium_fine" if price_tier in {"fine", "luxury"} else "casual_dining"


def _merge_pref_dict(base: dict[str, int], extra: dict[str, int] | None) -> dict[str, int]:
    merged = dict(base)
    for key, value in (extra or {}).items():
        if key not in _PREF_KEYS:
            continue
        merged[key] = max(merged.get(key, 0), max(0, min(10, int(value))))
    return merged


def _apply_cuisine_ambiente_hints(
    prefs: dict[str, int],
    cocina: str,
    ambiente: str,
    archetype: str,
) -> dict[str, int]:
    """Refuerzos suaves solo cuando no contradicen el arquetipo."""
    if archetype in {"fast_food", "guatemalteca_fast"}:
        return prefs
    for key, value in _CUISINE_PREF_HINTS.get(cocina, {}).items():
        if key in prefs:
            prefs[key] = max(prefs[key], min(value, prefs.get(key, 0) + 2))
        elif value >= 7:
            prefs[key] = min(value, 8)
    for key, value in _AMBIENTE_PREFS.get(ambiente, {}).items():
        if key in SEMANTIC_ARCHETYPES[archetype].get("forbidden", set()):
            continue
        prefs[key] = max(prefs.get(key, 0), min(value, 7))
    return prefs


def _sanitize_restaurant_prefs(prefs: dict[str, int], archetype: str) -> dict[str, int]:
    template = SEMANTIC_ARCHETYPES[archetype]
    forbidden = template.get("forbidden", set())
    max_prefs = template.get("max_prefs", {})
    clean = {k: v for k, v in prefs.items() if v > 0 and k not in forbidden}
    for key, cap in max_prefs.items():
        if key in clean:
            clean[key] = min(clean[key], cap)
    return clean


def _build_semantic_prefs(
    nombre: str,
    cocina: str,
    tipo: str,
    ambiente: str,
    price_tier: str,
    profile: str,
    pref_boost: dict[str, int] | None = None,
) -> tuple[str, dict[str, int], dict[str, int]]:
    archetype = _detect_semantic_archetype(nombre, cocina, tipo, ambiente, price_tier, profile)
    template = SEMANTIC_ARCHETYPES[archetype]
    scores = dict(template["scores"])
    prefs = _merge_pref_dict(template["prefs"], pref_boost)
    prefs = _apply_cuisine_ambiente_hints(prefs, cocina, ambiente, archetype)
    prefs = _sanitize_restaurant_prefs(prefs, archetype)
    return archetype, scores, prefs


def validate_restaurant_classification(restaurant: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    prefs = restaurant.get("prefs") or {}
    archetype = restaurant.get("semantic_archetype") or ""
    nombre = restaurant.get("nombre") or ""

    if archetype in {"fast_food", "guatemalteca_fast"}:
        if prefs.get("pref_italiana", 0) >= 3:
            issues.append("fast food con afinidad italiana")
        if prefs.get("gourmet", 0) >= 5:
            issues.append("fast food marcado como gourmet")
        if prefs.get("premium", 0) >= 5:
            issues.append("fast food marcado como premium")
        if prefs.get("romantic", 0) >= 5:
            issues.append("fast food marcado como romantico")
    if archetype == "italian_premium" and prefs.get("fast_food", 0) >= 5:
        issues.append("italiano premium con fast food")
    if prefs.get("fast_food", 0) >= 7 and prefs.get("exclusive", 0) >= 6:
        issues.append("fast food + luxury incompatible")
    if prefs.get("pref_italiana", 0) >= 7 and archetype == "fast_food":
        issues.append("%s clasificado como italiano" % nombre)
    return issues


def _google_maps_url(nombre: str, zona: str) -> str:
    query = quote_plus("%s %s Guatemala City restaurante" % (nombre, zona))
    return "https://www.google.com/maps/search/?api=1&query=%s" % query


def _google_search_url(nombre: str, zona: str) -> str:
    query = quote_plus("%s %s Guatemala restaurante" % (nombre, zona))
    return "https://www.google.com/search?q=%s" % query


# URLs curadas por nombre (cadenas comparten link entre zonas).
KNOWN_RESTAURANT_LINKS: dict[str, dict[str, str]] = {
    "Hacienda Real": {
        "website_url": "https://www.haciendareal.com.gt/",
        "instagram_url": "https://www.instagram.com/haciendarealgt/",
        "facebook_url": "https://www.facebook.com/haciendarealgt/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Hacienda+Real+Guatemala",
    },
    "Tre Fratelli": {
        "website_url": "https://www.trefratelli.com.gt/",
        "instagram_url": "https://www.instagram.com/trefratelli.gt/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Tre+Fratelli+Zona+10+Guatemala",
    },
    "Kacao": {
        "website_url": "https://www.kacao.com.gt/",
        "instagram_url": "https://www.instagram.com/kacaogt/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Kacao+Restaurante+Guatemala",
    },
    "Tamarindos": {
        "website_url": "https://www.tamarindos.com.gt/",
        "instagram_url": "https://www.instagram.com/tamarindosgt/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Tamarindos+Guatemala",
    },
    "Saúl": {
        "website_url": "https://www.restaurantesaul.com/",
        "instagram_url": "https://www.instagram.com/restaurantesaul/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Restaurante+Saul+Zona+10+Guatemala",
    },
    "Mercado 24": {
        "website_url": "https://www.mercado24.gt/",
        "instagram_url": "https://www.instagram.com/mercado24gt/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Mercado+24+Zona+10+Guatemala",
    },
    "Ambia": {
        "website_url": "https://www.ambia.com.gt/",
        "instagram_url": "https://www.instagram.com/ambiagt/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Ambia+Restaurante+Guatemala",
    },
    "Shiro": {
        "website_url": "https://www.shiro.com.gt/",
        "instagram_url": "https://www.instagram.com/shirogt/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Shiro+Sushi+Guatemala",
    },
    "Pecorino": {
        "website_url": "https://www.pecorino.com.gt/",
        "instagram_url": "https://www.instagram.com/pecorinogt/",
    },
    "Porcino": {
        "website_url": "https://www.porcino.com.gt/",
        "instagram_url": "https://www.instagram.com/porcinogt/",
    },
    "Monoloco": {
        "website_url": "https://www.monoloco.com/",
        "instagram_url": "https://www.instagram.com/monolocogt/",
    },
    "Sublime": {
        "website_url": "https://www.sublime.gt/",
        "instagram_url": "https://www.instagram.com/sublimegt/",
    },
    "Gracia Cocina de Autor": {
        "website_url": "https://www.gracia.gt/",
        "instagram_url": "https://www.instagram.com/graciacocinadeautor/",
    },
    "Los Tres Tiempos": {
        "website_url": "https://www.lostrestiempos.com/",
        "instagram_url": "https://www.instagram.com/lostrestiempos/",
    },
    "Frida Kahlo": {
        "website_url": "https://www.fridakahlo.com.gt/",
        "instagram_url": "https://www.instagram.com/fridakahlogt/",
    },
    "Atempo": {
        "website_url": "https://www.atempo.gt/",
        "instagram_url": "https://www.instagram.com/atempogt/",
    },
    "Marena": {
        "website_url": "https://www.marena.gt/",
        "instagram_url": "https://www.instagram.com/marenagt/",
    },
    "Kaffeine": {
        "website_url": "https://www.kaffeine.com.gt/",
        "instagram_url": "https://www.instagram.com/kaffeinegt/",
    },
    "Hard Rock Cafe": {
        "website_url": "https://www.hardrockcafe.com/location/guatemala-city/",
        "instagram_url": "https://www.instagram.com/hardrockcafeguatemala/",
    },
    "Burger King": {
        "website_url": "https://www.burgerking.com.gt/",
        "instagram_url": "https://www.instagram.com/burgerkinggt/",
        "facebook_url": "https://www.facebook.com/BurgerKingGuatemala/",
    },
    "McDonald's": {
        "website_url": "https://www.mcdonalds.com.gt/",
        "instagram_url": "https://www.instagram.com/mcdonalds_guatemala/",
    },
    "Wendy's": {
        "website_url": "https://www.wendys.com.gt/",
        "instagram_url": "https://www.instagram.com/wendysguatemala/",
    },
    "Starbucks": {
        "website_url": "https://www.starbucks.com.gt/",
        "instagram_url": "https://www.instagram.com/starbucksgt/",
    },
    "Pollo Campero": {
        "website_url": "https://www.campero.com/",
        "instagram_url": "https://www.instagram.com/pollocampero/",
    },
    "Chili's": {
        "website_url": "https://www.chilis.com/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Chili%27s+Guatemala",
    },
    "Outback Steakhouse": {
        "website_url": "https://www.outback.com/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Outback+Steakhouse+Guatemala",
    },
    "P.F. Chang's": {
        "website_url": "https://www.pfchangs.com/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=P.F.+Chang%27s+Guatemala",
    },
    "Olive Garden": {
        "website_url": "https://www.olivegarden.com/",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=Olive+Garden+Guatemala",
    },
}


def build_restaurant_links(
    nombre: str,
    zona: str,
    overrides: dict[str, str] | None = None,
) -> dict[str, str]:
    """Resuelve URLs del restaurante con fallback a Google Maps / busqueda."""
    links = dict(KNOWN_RESTAURANT_LINKS.get(nombre, {}))
    if overrides:
        links.update({k: v for k, v in overrides.items() if v})
    links.setdefault("website_url", "")
    links.setdefault("instagram_url", "")
    links.setdefault("facebook_url", "")
    if not links.get("maps_url"):
        links["maps_url"] = _google_maps_url(nombre, zona)
    links["search_url"] = _google_search_url(nombre, zona)
    return links


def get_restaurant_links(nombre: str, zona: str) -> dict[str, str]:
    return build_restaurant_links(nombre, zona)


def validate_restaurant_catalog(restaurants: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = restaurants if restaurants is not None else RESTAURANTS
    flagged: list[dict[str, Any]] = []
    for row in rows:
        issues = validate_restaurant_classification(row)
        if issues:
            flagged.append({"id": row.get("id"), "nombre": row.get("nombre"), "issues": issues})
    return {"valid": len(flagged) == 0, "checked": len(rows), "issues": flagged}


def _curated_entry(
    nombre: str,
    zona: str,
    cocina: str,
    tipo: str,
    ambiente: str,
    rating: float,
    price_tier: str,
    precio: int,
    descripcion: str,
    profile: str,
    pref_boost: dict[str, int] | None = None,
    link_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    archetype, score_map, prefs = _build_semantic_prefs(
        nombre, cocina, tipo, ambiente, price_tier, profile, pref_boost
    )
    links = build_restaurant_links(nombre, zona, link_overrides)
    return {
        "id": "",
        "nombre": nombre,
        "zona": zona,
        "rating": rating,
        "price_tier": price_tier,
        "precio": precio,
        "cocina": cocina,
        "tipo": tipo,
        "ambiente": ambiente,
        "descripcion": descripcion,
        "semantic_archetype": archetype,
        "nightlife_score": score_map["nightlife_score"],
        "social_score": score_map["social_score"],
        "premium_score": score_map["premium_score"],
        "comfort_score": score_map["comfort_score"],
        "aesthetic_score": score_map["aesthetic_score"],
        "romantic_score": score_map["romantic_score"],
        "fast_service_score": score_map["fast_service_score"],
        "prefs": prefs,
        "website_url": links["website_url"],
        "instagram_url": links["instagram_url"],
        "facebook_url": links["facebook_url"],
        "maps_url": links["maps_url"],
        "search_url": links["search_url"],
    }



def _real_entry(
    nombre,
    zona,
    cocina,
    tipo,
    ambiente,
    rating,
    tier,
    precio,
    descripcion,
    profile,
    boost=None,
    links=None,
):
    return _curated_entry(
        nombre,
        zona,
        cocina,
        tipo,
        ambiente,
        rating,
        tier,
        precio,
        descripcion,
        profile,
        boost or {},
        link_overrides=links,
    )


def build_catalog() -> list[dict[str, Any]]:
    rows = [
        _real_entry('Hacienda Real', 'Zona 10', 'Steakhouse', 'Steakhouse', 'elegante', 4.7, 'fine', 420, 'Parrilla guatemalteca iconica con cortes premium y arquitectura latinoamericana.', 'premium', {'business_dining': 9, 'premium': 9}),
        _real_entry('Tre Fratelli', 'Zona 10', 'Italiana', 'Trattoria', 'elegante', 4.6, 'premium', 285, 'Recetas italianas clasicas con servicio cuidado en Zona 10.', 'premium', {'pref_italiana': 10, 'wine_focus': 8, 'romantic': 7}),
        _real_entry('Kacao', 'Zona 10', 'Guatemalteca', 'Cocina Guatemalteca', 'elegante', 4.7, 'premium', 310, 'Alta cocina guatemalteca con ingredientes locales y presentacion contemporanea.', 'premium', {'pref_guatemalteca': 10, 'gourmet': 9}),
        _real_entry('Tamarindos', 'Zona 10', 'Fusion', 'Fine Dining', 'romantico', 4.8, 'fine', 455, 'Cocina de autor con ingredientes locales y montaje elegante.', 'luxury', {'romantic': 9, 'gourmet': 10, 'exclusive': 8}),
        _real_entry('Hibachi', 'Zona 10', 'Japonesa', 'Teppanyaki', 'elegante', 4.7, 'premium', 295, 'Plancha japonesa y show culinario en ambiente sofisticado.', 'premium', {'pref_japonesa': 9, 'business_dining': 8}),
        _real_entry('Pecorino', 'Zona 10', 'Italiana', 'Ristorante', 'romantico', 4.7, 'premium', 315, 'Pastas artesanales y carta de vinos para cenas largas.', 'premium', {'pref_italiana': 10, 'wine_focus': 8, 'slow_food': 8}),
        _real_entry('Porcino', 'Zona 10', 'Italiana', 'Steakhouse', 'elegante', 4.7, 'fine', 440, 'Cortes premium y especialidades italianas en salon moderno.', 'luxury', {'business_dining': 9, 'premium': 9}),
        _real_entry('Portal del Angel', 'Zona 10', 'Internacional', 'Fine Dining', 'elegante', 4.6, 'fine', 380, 'Restaurante reconocido en Fontabella con propuesta internacional refinada.', 'premium', {'elegant': 9, 'business_dining': 8}),
        _real_entry('Saúl', 'Zona 10', 'Internacional', 'Bistro', 'trendy', 4.6, 'premium', 270, 'Bistro creativo con identidad propia en el corazon de Zona 10.', 'premium', {'trendy': 9, 'aesthetic': 8}),
        _real_entry('Casa Escobar', 'Zona 10', 'Steakhouse', 'Steakhouse', 'elegante', 4.6, 'fine', 400, 'Carnes a la parrilla y tradicion steakhouse en Guatemala.', 'premium', {'premium': 9, 'business_dining': 8}),
        _real_entry('El Adobe', 'Zona 10', 'Guatemalteca', 'Cocina Guatemalteca', 'familiar', 4.5, 'premium', 250, 'Sabores guatemaltecos en ambiente rustico y acogedor.', 'premium', {'pref_guatemalteca': 10, 'comfort_food': 8}),
        _real_entry('La Estancia', 'Zona 10', 'Steakhouse', 'Steakhouse', 'elegante', 4.5, 'premium', 320, 'Cortes selectos y ambiente clasico para ocasiones especiales.', 'premium', {'business_dining': 8, 'premium': 8}),
        _real_entry('Diaca', 'Zona 10', 'Fusion', 'Cocina de Autor', 'trendy', 4.6, 'fine', 390, 'Cocina contemporanea con identidad guatemalteca y toques globales.', 'premium', {'gourmet': 9, 'trendy': 8}),
        _real_entry('Sublime', 'Zona 10', 'Fusion', 'Fine Dining', 'romantico', 4.7, 'fine', 430, 'Experiencia gastronomica de autor con maridaje cuidado.', 'luxury', {'gourmet': 10, 'romantic': 8}),
        _real_entry("Jake's", 'Zona 10', 'Internacional', 'Gastrobar', 'nocturno', 4.5, 'premium', 260, 'Gastrobar con cocteleria y platos para compartir.', 'premium', {'nightlife': 8, 'social_grupo': 8, 'craft_beer': 7}),
        _real_entry('Monoloco', 'Zona 10', 'Internacional', 'Gastrobar', 'nocturno', 4.5, 'premium', 240, 'Bar restaurante iconico con ambiente social y musica en vivo.', 'premium', {'nightlife': 9, 'lively': 9, 'social_grupo': 9}),
        _real_entry('Mercado 24', 'Zona 10', 'Internacional', 'Food Hall', 'trendy', 4.5, 'premium', 220, 'Mercado gastronomico con multiples conceptos y ambiente vibrante.', 'premium', {'trendy': 9, 'social_grupo': 9, 'aventurero': 8}),
        _real_entry('Del Griego', 'Zona 10', 'Mediterranea', 'Mediterraneo', 'elegante', 4.5, 'premium', 280, 'Sabores mediterraneos con fuerte identidad griega.', 'premium', {'pref_mediterranea': 10, 'saludable': 7}),
        _real_entry('Gracia Cocina de Autor', 'Zona 10', 'Fusion', 'Cocina de Autor', 'elegante', 4.7, 'fine', 410, 'Alta cocina guatemalteca con tecnicas modernas y producto local.', 'luxury', {'gourmet': 10, 'exclusive': 8}),
        _real_entry('La Finka', 'Zona 10', 'Guatemalteca', 'Comedor Contemporaneo', 'trendy', 4.6, 'premium', 265, 'Cocina guatemalteca contemporanea en ambiente urbano.', 'premium', {'pref_guatemalteca': 9, 'trendy': 8}),
        _real_entry('Ambia', 'Zona 10', 'Peruana', 'Nikkei', 'trendy', 4.6, 'premium', 330, 'Propuesta nikkei peruana con sabores audaces y presentacion moderna.', 'premium', {'asian_fusion': 9, 'aventurero': 8}),
        _real_entry('Bottega Foresto', 'Zona 10', 'Italiana', 'Bistro', 'trendy', 4.7, 'fine', 410, 'Concepto contemporaneo italiano con barra de vinos.', 'premium', {'aesthetic': 9, 'trendy': 9, 'wine_focus': 8}),
        _real_entry("L'Oliveto", 'Zona 10', 'Italiana', 'Ristorante', 'romantico', 4.6, 'premium', 300, 'Cocina italiana tradicional con aceite de oliva y pastas frescas.', 'premium', {'pref_italiana': 10, 'slow_food': 8}),
        _real_entry('Mantarraya', 'Zona 10', 'Mariscos', 'Seafood Grill', 'elegante', 4.6, 'premium', 310, 'Mariscos frescos y ceviches en ambiente sofisticado.', 'premium', {'gourmet': 8, 'romantic': 6}),
        _real_entry('Shiro', 'Zona 10', 'Japonesa', 'Sushi', 'elegante', 4.7, 'fine', 480, 'Sushi y cocina japonesa de alta calidad.', 'luxury', {'pref_japonesa': 10, 'gourmet': 9}),
        _real_entry('Estacion Santo Domingo', 'Zona 10', 'Internacional', 'Bistro', 'elegante', 4.5, 'premium', 275, 'Bistro internacional en entorno historico y elegante.', 'premium', {'elegant': 8, 'wine_focus': 7}),
        _real_entry('Tablon del 8', 'Zona 10', 'Steakhouse', 'Steakhouse', 'elegante', 4.6, 'fine', 450, 'Cortes premium y ambiente de parrilla de alto nivel.', 'premium', {'premium': 9, 'business_dining': 9}),
        _real_entry('La Veinte', 'Zona 10', 'Mexicana', 'Cocina Mexicana', 'trendy', 4.6, 'premium', 290, 'Cocina mexicana contemporanea con ambiente festivo.', 'premium', {'pref_mexicana': 10, 'lively': 8, 'nightlife': 7}),
        _real_entry("P.F. Chang's", 'Zona 10', 'Asiatica', 'Cadena Asiatica', 'elegante', 4.4, 'premium', 250, 'Cocina asiatica contemporanea en cadena reconocida.', 'premium', {'asian_fusion': 8, 'business_dining': 7}),
        _real_entry('El Arte Steak House', 'Zona 10', 'Steakhouse', 'Steakhouse', 'elegante', 4.5, 'fine', 420, 'Steakhouse con cortes selectos y servicio formal.', 'premium', {'premium': 9, 'business_dining': 8}),
        _real_entry('Rincon del Steak', 'Zona 10', 'Steakhouse', 'Steakhouse', 'elegante', 4.5, 'premium', 340, 'Parrilla reconocida para amantes de la carne.', 'premium', {'premium': 8, 'business_dining': 8}),
        _real_entry('Il Forno', 'Zona 10', 'Italiana', 'Pizzeria', 'familiar', 4.4, 'casual', 180, 'Pizza al horno de lena y pastas caseras.', 'casual', {'pref_italiana': 8, 'family_friendly': 8}),
        _real_entry('Paisano', 'Zona 10', 'Italiana', 'Trattoria', 'familiar', 4.4, 'casual', 170, 'Trattoria italiana accesible con ambiente familiar.', 'casual', {'pref_italiana': 8, 'comfort_food': 7}),
        _real_entry('45 Grados', 'Zona 10', 'Steakhouse', 'Steakhouse', 'elegante', 4.5, 'premium', 360, 'Cortes a la parrilla con tecnicas de coccion precisas.', 'premium', {'premium': 8, 'gourmet': 7}),
        _real_entry('Animal Gastro Bar', 'Zona 10', 'Internacional', 'Gastrobar', 'nocturno', 4.4, 'premium', 255, 'Gastrobar con propuesta creativa y cocteleria.', 'premium', {'nightlife': 8, 'trendy': 8}),
        _real_entry('Anadi2', 'Zona 10', 'Fusion', 'Bistro', 'trendy', 4.5, 'premium', 245, 'Bistro fusion con platos para compartir y ambiente moderno.', 'premium', {'trendy': 8, 'social_grupo': 8}),
        _real_entry('Bisque', 'Zona 10', 'Francesa', 'Bistro', 'elegante', 4.5, 'fine', 370, 'Cocina francesa con sopas, pescados y postres clasicos.', 'premium', {'gourmet': 8, 'elegant': 8}),
        _real_entry('Dumbo', 'Zona 10', 'Internacional', 'Bistro', 'trendy', 4.4, 'premium', 230, 'Propuesta internacional con ambiente relajado y moderno.', 'premium', {'trendy': 8, 'aesthetic': 7}),
        _real_entry('Gusta', 'Zona 10', 'Saludable', 'Healthy Kitchen', 'brunch', 4.4, 'casual', 165, 'Opciones saludables y bowls frescos.', 'cafe', {'saludable': 9, 'brunch': 7}),
        _real_entry('Nifu Nifa', 'Zona 10', 'Asiatica', 'Dim Sum', 'casual', 4.4, 'casual', 190, 'Dim sum y cocina cantonesa en ambiente casual.', 'casual', {'asian_fusion': 8, 'pref_japonesa': 6}),
        _real_entry('Saint Honore', 'Zona 10', 'Francesa', 'Pasteleria Restaurante', 'elegante', 4.5, 'premium', 220, 'Pasteleria francesa y platos ligeros de alta calidad.', 'premium', {'elegant': 8, 'aesthetic': 8}),
        _real_entry('Tul y Tul', 'Zona 10', 'Internacional', 'Bistro', 'romantico', 4.5, 'premium', 260, 'Bistro con terraza y propuesta internacional refinada.', 'premium', {'romantic': 8, 'intimate': 7}),
        _real_entry('Zest', 'Zona 10', 'Internacional', 'Bistro', 'trendy', 4.4, 'premium', 240, 'Cocina internacional con toques citricos y ambiente urbano.', 'premium', {'trendy': 8, 'aesthetic': 7}),
        _real_entry('Fiorellino', 'Zona 10', 'Italiana', 'Trattoria', 'cozy', 4.4, 'casual', 175, 'Pastas y pizzas en ambiente acogedor.', 'casual', {'pref_italiana': 8, 'comfort_food': 7}),
        _real_entry('Le Crepe', 'Zona 10', 'Francesa', 'Creperie', 'cozy', 4.3, 'casual', 150, 'Crepes dulces y salados en ambiente parisino.', 'cafe', {'romantic': 6, 'brunch': 7}),
        _real_entry('Paligo', 'Zona 10', 'Internacional', 'Bistro', 'elegante', 4.4, 'premium', 265, 'Bistro internacional con carta variada y servicio formal.', 'premium', {'business_dining': 7, 'elegant': 7}),
        _real_entry('Outback Steakhouse', 'Zona 10', 'Steakhouse', 'Cadena Steakhouse', 'familiar', 4.3, 'premium', 280, 'Steakhouse de cadena con cortes generosos y ambiente casual.', 'premium', {'family_friendly': 7, 'premium': 7}),
        _real_entry("Chili's", 'Zona 10', 'Internacional', 'Cadena Americana', 'familiar', 4.2, 'casual', 195, 'Cadena americana con burgers, ribs y ambiente familiar.', 'casual', {'family_friendly': 8, 'casual': 8}),
        _real_entry("TGI Friday's", 'Zona 10', 'Internacional', 'Cadena Americana', 'nocturno', 4.2, 'casual', 200, 'Restaurante bar americano con ambiente festivo.', 'casual', {'nightlife': 7, 'lively': 8}),
        _real_entry("Applebee's", 'Zona 10', 'Internacional', 'Cadena Americana', 'familiar', 4.1, 'casual', 185, 'Comida americana casual para grupos y familias.', 'casual', {'family_friendly': 8, 'casual': 8}),
        _real_entry('Olive Garden', 'Zona 10', 'Italiana', 'Cadena Italiana', 'familiar', 4.2, 'casual', 210, 'Cadena italiana con pastas y pan de ajo iconico.', 'casual', {'pref_italiana': 7, 'family_friendly': 8}),
        _real_entry("Tony Roma's", 'Zona 10', 'Internacional', 'Ribs House', 'familiar', 4.2, 'casual', 220, 'Costillas BBQ y platos americanos en cadena reconocida.', 'casual', {'comfort_food': 8, 'family_friendly': 7}),
        _real_entry('IHOP', 'Zona 10', 'Internacional', 'Desayunos', 'familiar', 4.1, 'casual', 160, 'Desayunos y pancakes todo el dia.', 'casual', {'brunch': 8, 'family_friendly': 8}),
        _real_entry("Denny's", 'Zona 10', 'Internacional', 'Diner', 'familiar', 4.0, 'casual', 155, 'Diner americano abierto 24 horas.', 'casual', {'comfort_food': 8, 'fast_service': 8}),
        _real_entry('Wok to Walk', 'Zona 10', 'Asiatica', 'Wok Rapido', 'casual', 4.2, 'economico', 95, 'Wok personalizable de servicio rapido.', 'casual', {'fast_service': 9, 'asian_fusion': 7}),
        _real_entry('Hard Rock Cafe', 'Zona 10', 'Internacional', 'Cadena Americana', 'nocturno', 4.3, 'premium', 250, 'Cadena iconica con musica en vivo y burgers.', 'premium', {'nightlife': 8, 'lively': 8}),
        _real_entry('Frida Kahlo', 'Zona 14', 'Mexicana', 'Cocina Mexicana', 'trendy', 4.6, 'premium', 295, 'Sabores mexicanos autenticos con diseno vibrante.', 'premium', {'pref_mexicana': 10, 'lively': 8}),
        _real_entry('Los Tres Tiempos', 'Zona 14', 'Guatemalteca', 'Cocina Guatemalteca', 'familiar', 4.7, 'premium', 265, 'Recetas guatemaltecas con enfoque moderno y porciones generosas.', 'premium', {'pref_guatemalteca': 10, 'comfort_food': 8}),
        _real_entry('Marena', 'Zona 14', 'Mediterranea', 'Mediterraneo', 'elegante', 4.7, 'fine', 420, 'Pescados, aceite de oliva y vegetales de temporada.', 'premium', {'pref_mediterranea': 10, 'saludable': 8}),
        _real_entry('Atempo', 'Zona 14', 'Fusion', 'Cocina de Autor', 'elegante', 4.7, 'fine', 485, 'Menu de temporada con tecnica moderna latinoeuropea.', 'luxury', {'exclusive': 9, 'gourmet': 9}),
        _real_entry('Hacienda Real', 'Zona 14', 'Steakhouse', 'Steakhouse', 'elegante', 4.7, 'fine', 420, 'Sucursal Zona 14 del steakhouse iconico de Guatemala.', 'premium', {'business_dining': 9, 'premium': 9}),
        _real_entry('Del Principe', 'Zona 14', 'Italiana', 'Ristorante', 'elegante', 4.5, 'premium', 300, 'Cocina italiana clasica con ambiente refinado.', 'premium', {'pref_italiana': 9, 'wine_focus': 7}),
        _real_entry("P.F. Chang's", 'Zona 14', 'Asiatica', 'Cadena Asiatica', 'elegante', 4.4, 'premium', 250, 'Cocina asiatica contemporanea en Zona 14.', 'premium', {'asian_fusion': 8}),
        _real_entry('Outback Steakhouse', 'Zona 14', 'Steakhouse', 'Cadena Steakhouse', 'familiar', 4.3, 'premium', 280, 'Steakhouse de cadena en Zona 14.', 'premium', {'family_friendly': 7}),
        _real_entry('IHOP', 'Zona 14', 'Internacional', 'Desayunos', 'familiar', 4.1, 'casual', 160, 'Desayunos y pancakes en Zona 14.', 'casual', {'brunch': 8}),
        _real_entry("Chili's", 'Zona 14', 'Internacional', 'Cadena Americana', 'familiar', 4.2, 'casual', 195, 'Cadena americana en Zona 14.', 'casual', {'family_friendly': 8}),
        _real_entry('Kaffeine', 'Zona 15', 'Cafe', 'Cafe de Especialidad', 'brunch', 4.6, 'casual', 145, 'Cafe de especialidad, reposteria y brunch todo el dia.', 'cafe', {'coffee_culture': 10, 'brunch': 9}),
        _real_entry('Cafe Leon', 'Zona 15', 'Cafe', 'Cafe', 'cozy', 4.4, 'casual', 120, 'Cafe guatemalteco con tradicion y panes frescos.', 'cafe', {'coffee_culture': 9, 'comfort_food': 7}),
        _real_entry('San Martin', 'Zona 16', 'Cafe', 'Bakery Cafe', 'familiar', 4.6, 'casual', 140, 'Panaderia iconica con menu amplio para toda la familia en Cayala.', 'cafe', {'family_friendly': 9, 'coffee_culture': 8}),
        _real_entry('Tre Fratelli', 'Zona 16', 'Italiana', 'Trattoria', 'elegante', 4.6, 'premium', 285, 'Sucursal Cayala de la trattoria italiana reconocida.', 'premium', {'pref_italiana': 10, 'romantic': 7}),
        _real_entry('Pecorino', 'Zona 16', 'Italiana', 'Ristorante', 'romantico', 4.7, 'premium', 315, 'Pastas artesanales en el corazon de Cayala.', 'premium', {'pref_italiana': 10, 'wine_focus': 8}),
        _real_entry('Porcino', 'Zona 16', 'Italiana', 'Steakhouse', 'elegante', 4.7, 'fine', 440, 'Cortes premium en Cayala.', 'luxury', {'premium': 9, 'business_dining': 9}),
        _real_entry('Tablon del 8', 'Zona 16', 'Steakhouse', 'Steakhouse', 'elegante', 4.6, 'fine', 450, 'Parrilla premium en Cayala.', 'premium', {'premium': 9, 'business_dining': 9}),
        _real_entry('Le Crepe', 'Zona 16', 'Francesa', 'Creperie', 'cozy', 4.3, 'casual', 150, 'Crepes en ambiente parisino en Cayala.', 'cafe', {'romantic': 6, 'brunch': 7}),
        _real_entry('Hacienda Real', 'Zona 16', 'Steakhouse', 'Steakhouse', 'elegante', 4.7, 'fine', 420, 'Sucursal Cayala del iconico steakhouse guatemalteco.', 'premium', {'business_dining': 9, 'premium': 9}),
        _real_entry('Rincon del Steak', 'Zona 16', 'Steakhouse', 'Steakhouse', 'elegante', 4.5, 'premium', 340, 'Parrilla reconocida en Cayala.', 'premium', {'premium': 8}),
        _real_entry('Casa Chapina', 'Zona 16', 'Guatemalteca', 'Cocina Guatemalteca', 'familiar', 4.5, 'premium', 230, 'Comida guatemalteca tradicional en Cayala.', 'premium', {'pref_guatemalteca': 10, 'family_friendly': 8}),
        _real_entry('Wok to Walk', 'Zona 16', 'Asiatica', 'Wok Rapido', 'casual', 4.2, 'economico', 95, 'Wok rapido en Cayala.', 'casual', {'fast_service': 9}),
        _real_entry("Chili's", 'Zona 16', 'Internacional', 'Cadena Americana', 'familiar', 4.2, 'casual', 195, 'Cadena americana en Cayala.', 'casual', {'family_friendly': 8}),
        _real_entry('Hacienda Real', 'Zona 11', 'Steakhouse', 'Steakhouse', 'familiar', 4.6, 'premium', 350, 'Sucursal Zona 11 del steakhouse nacional.', 'premium', {'family_friendly': 8, 'premium': 8}),
        _real_entry('Pollo Campero', 'Zona 11', 'Guatemalteca', 'Pollo Frito', 'familiar', 4.3, 'economico', 75, 'Cadena guatemalteca de pollo frito, icono nacional.', 'casual', {'pref_guatemalteca': 8, 'fast_service': 9, 'family_friendly': 9}),
        _real_entry('Pollo Campero', 'Zona 5', 'Guatemalteca', 'Pollo Frito', 'familiar', 4.3, 'economico', 75, 'Sucursal en Zona 5 de la cadena guatemalteca.', 'casual', {'pref_guatemalteca': 8, 'fast_service': 9}),
        _real_entry('Pollo Campero', 'Zona 10', 'Guatemalteca', 'Pollo Frito', 'familiar', 4.3, 'economico', 80, 'Sucursal Zona 10 de Pollo Campero.', 'casual', {'pref_guatemalteca': 8, 'fast_service': 9}),
        _real_entry('Pollo Campero', 'Zona 14', 'Guatemalteca', 'Pollo Frito', 'familiar', 4.3, 'economico', 80, 'Sucursal Zona 14 de Pollo Campero.', 'casual', {'pref_guatemalteca': 8, 'fast_service': 9}),
        _real_entry('Pollo Campero', 'Zona 15', 'Guatemalteca', 'Pollo Frito', 'familiar', 4.3, 'economico', 75, 'Sucursal Zona 15 de Pollo Campero.', 'casual', {'pref_guatemalteca': 8, 'fast_service': 9}),
        _real_entry('Pollo Campero', 'Zona 16', 'Guatemalteca', 'Pollo Frito', 'familiar', 4.3, 'economico', 80, 'Sucursal Cayala de Pollo Campero.', 'casual', {'pref_guatemalteca': 8, 'fast_service': 9}),
        _real_entry('Mansión del Río', 'Zona 10', 'Internacional', 'Hotel Restaurante', 'elegante', 4.5, 'fine', 400, 'Restaurante de hotel con vista y cocina internacional.', 'luxury', {'elegant': 9, 'romantic': 8}),
        _real_entry('Caffe Milano', 'Zona 10', 'Italiana', 'Cafe Restaurante', 'elegante', 4.4, 'premium', 240, 'Cafe italiano con pastas y ambiente europeo.', 'premium', {'pref_italiana': 8, 'coffee_culture': 7}),
        _real_entry('La Pampa', 'Zona 10', 'Steakhouse', 'Parrilla Argentina', 'elegante', 4.5, 'premium', 330, 'Parrilla argentina con cortes y empanadas.', 'premium', {'premium': 8, 'gourmet': 7}),
        _real_entry('Nuestra Cerveceria', 'Zona 10', 'Internacional', 'Cerveceria', 'nocturno', 4.4, 'casual', 180, 'Cerveza artesanal guatemalteca y platos para compartir.', 'casual', {'craft_beer': 9, 'nightlife': 7, 'social_grupo': 8}),
        _real_entry('Cerveceria 14', 'Zona 14', 'Internacional', 'Cerveceria', 'nocturno', 4.3, 'casual', 175, 'Cerveceria con ambiente social en Zona 14.', 'casual', {'craft_beer': 8, 'social_grupo': 8}),
        _real_entry('Rustica', 'Zona 10', 'Italiana', 'Pizzeria', 'familiar', 4.3, 'casual', 165, 'Pizza rustica al horno de lena.', 'casual', {'pref_italiana': 8, 'family_friendly': 7}),
        _real_entry('Milagrito', 'Zona 10', 'Mexicana', 'Cantina', 'nocturno', 4.3, 'casual', 170, 'Cantina mexicana con ambiente festivo.', 'casual', {'pref_mexicana': 8, 'nightlife': 7}),
        _real_entry('Punto Mediterraneo', 'Zona 10', 'Mediterranea', 'Mediterraneo', 'elegante', 4.4, 'premium', 260, 'Cocina mediterranea con pescados y pastas.', 'premium', {'pref_mediterranea': 9}),
        _real_entry('Gramo', 'Zona 10', 'Internacional', 'Bistro', 'trendy', 4.3, 'premium', 230, 'Bistro contemporaneo con platos de autor accesibles.', 'premium', {'trendy': 8}),
        _real_entry('El Invernadero', 'Zona 10', 'Saludable', 'Healthy Kitchen', 'trendy', 4.4, 'casual', 175, 'Cocina vegetal y organica en ambiente luminoso.', 'cafe', {'saludable': 9, 'aesthetic': 8}),
        _real_entry('Cielito Lindo', 'Zona 10', 'Mexicana', 'Cocina Mexicana', 'familiar', 4.3, 'casual', 160, 'Comida mexicana tradicional en ambiente colorido.', 'casual', {'pref_mexicana': 8, 'family_friendly': 7}),
        _real_entry('Isabelle', 'Zona 10', 'Francesa', 'Bistro', 'romantico', 4.4, 'premium', 270, 'Bistro frances con postres y vinos selectos.', 'premium', {'elegant': 8, 'romantic': 7}),
        _real_entry('Fiore Pasta Bar', 'Zona 10', 'Italiana', 'Pasta Bar', 'trendy', 4.3, 'casual', 185, 'Pastas frescas en barra abierta.', 'casual', {'pref_italiana': 8, 'trendy': 7}),
        _real_entry('Renata', 'Zona 16', 'Cafe', 'Pasteleria', 'familiar', 4.5, 'casual', 130, 'Pasteleria y reposteria reconocida en Cayala.', 'cafe', {'coffee_culture': 8, 'family_friendly': 8}),
        _real_entry('Cinnabon', 'Zona 16', 'Cafe', 'Reposteria', 'casual', 4.2, 'economico', 80, 'Rollos de canela y cafe en Cayala.', 'casual', {'comfort_food': 7, 'fast_service': 8}),
        _real_entry('Sarita', 'Zona 10', 'Cafe', 'Heladeria', 'familiar', 4.4, 'economico', 60, 'Helados Sarita, marca guatemalteca iconica.', 'casual', {'family_friendly': 9, 'comfort_food': 7}),
        _real_entry('Sarita', 'Zona 11', 'Cafe', 'Heladeria', 'familiar', 4.4, 'economico', 55, 'Helados Sarita en Zona 11.', 'casual', {'family_friendly': 9}),
        _real_entry('Sarita', 'Zona 16', 'Cafe', 'Heladeria', 'familiar', 4.4, 'economico', 60, 'Helados Sarita en Cayala.', 'casual', {'family_friendly': 9}),
        _real_entry('Eskimo', 'Zona 10', 'Cafe', 'Heladeria', 'familiar', 4.3, 'economico', 55, 'Helados Eskimo, tradicion guatemalteca.', 'casual', {'family_friendly': 8}),
        _real_entry('Eskimo', 'Zona 5', 'Cafe', 'Heladeria', 'familiar', 4.3, 'economico', 50, 'Helados Eskimo en Zona 5.', 'casual', {'family_friendly': 8}),
        _real_entry('China Wok', 'Zona 10', 'Asiatica', 'Comida China', 'casual', 4.1, 'economico', 100, 'Comida china rapida y accesible.', 'casual', {'asian_fusion': 7, 'fast_service': 8}),
        _real_entry('China Wok', 'Zona 11', 'Asiatica', 'Comida China', 'casual', 4.1, 'economico', 95, 'Comida china en Zona 11.', 'casual', {'asian_fusion': 7, 'fast_service': 8}),
        _real_entry('Bento Box', 'Zona 10', 'Japonesa', 'Bento', 'casual', 4.2, 'economico', 110, 'Bentos y comida japonesa rapida.', 'casual', {'pref_japonesa': 7, 'fast_service': 8}),
        _real_entry('Bento Box', 'Zona 16', 'Japonesa', 'Bento', 'casual', 4.2, 'economico', 110, 'Bentos japoneses en Cayala.', 'casual', {'pref_japonesa': 7, 'fast_service': 8}),
        _real_entry('Nuestra Cerveceria', 'Zona 16', 'Internacional', 'Cerveceria', 'nocturno', 4.4, 'casual', 180, 'Cerveceria artesanal en Cayala.', 'casual', {'craft_beer': 9, 'social_grupo': 8}),
        _real_entry('Nikkei', 'Zona 10', 'Peruana', 'Nikkei', 'trendy', 4.5, 'premium', 320, 'Cocina nikkei peruano-japonesa reconocida en la ciudad.', 'premium', {'asian_fusion': 9, 'aventurero': 8}),
        _real_entry('Nikkei', 'Zona 14', 'Peruana', 'Nikkei', 'trendy', 4.5, 'premium', 320, 'Propuesta nikkei en Zona 14.', 'premium', {'asian_fusion': 9}),
        _real_entry('Comida China Moon', 'Zona 10', 'Asiatica', 'Comida China', 'casual', 4.2, 'economico', 105, 'Comida china buffet reconocida en Guatemala.', 'casual', {'asian_fusion': 7, 'family_friendly': 7}),
        _real_entry('Comida China Moon', 'Zona 11', 'Asiatica', 'Comida China', 'casual', 4.2, 'economico', 100, 'Buffet chino accesible en Zona 11.', 'casual', {'asian_fusion': 7}),
        _real_entry('Little Caesars', 'Zona 10', 'Internacional', 'Pizzeria', 'familiar', 4.0, 'economico', 90, 'Pizza rapida de cadena internacional.', 'casual', {'fast_service': 9}),
        _real_entry("Papa John's", 'Zona 10', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 115, 'Pizza a domicilio de cadena internacional.', 'casual', {'fast_service': 8}),
        _real_entry('Dunkin', 'Zona 10', 'Cafe', 'Cafe y Donas', 'casual', 4.1, 'economico', 75, 'Cafe y donas de cadena internacional.', 'casual', {'coffee_culture': 7, 'fast_service': 9}),
        _real_entry('Dunkin', 'Zona 16', 'Cafe', 'Cafe y Donas', 'casual', 4.1, 'economico', 75, 'Dunkin en Cayala.', 'casual', {'coffee_culture': 7, 'fast_service': 9}),
        _real_entry('De Cero', 'Zona 10', 'Saludable', 'Ensaladas', 'casual', 4.3, 'casual', 120, 'Cadena de ensaladas y bowls personalizables.', 'cafe', {'saludable': 9, 'fast_service': 8}),
        _real_entry('De Cero', 'Zona 14', 'Saludable', 'Ensaladas', 'casual', 4.3, 'casual', 120, 'Ensaladas frescas en Zona 14.', 'cafe', {'saludable': 9}),
        _real_entry('De Cero', 'Zona 15', 'Saludable', 'Ensaladas', 'casual', 4.3, 'casual', 115, 'Bowls saludables en Zona 15.', 'cafe', {'saludable': 9}),
        _real_entry('De Cero', 'Zona 16', 'Saludable', 'Ensaladas', 'casual', 4.3, 'casual', 120, 'Ensaladas en Cayala.', 'cafe', {'saludable': 9}),
        _real_entry('Los Cebollines', 'Zona 11', 'Mexicana', 'Cadena Mexicana', 'familiar', 4.3, 'economico', 85, 'Cadena mexicana guatemalteca con tacos, burritos y ambiente familiar.', 'casual', {'pref_mexicana': 9, 'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Los Cebollines', 'Zona 14', 'Mexicana', 'Cadena Mexicana', 'familiar', 4.3, 'economico', 85, 'Cadena mexicana guatemalteca con tacos, burritos y ambiente familiar.', 'casual', {'pref_mexicana': 9, 'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Los Cebollines', 'Zona 15', 'Mexicana', 'Cadena Mexicana', 'familiar', 4.3, 'economico', 85, 'Cadena mexicana guatemalteca con tacos, burritos y ambiente familiar.', 'casual', {'pref_mexicana': 9, 'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Los Cebollines', 'Zona 16', 'Mexicana', 'Cadena Mexicana', 'familiar', 4.3, 'economico', 85, 'Cadena mexicana guatemalteca con tacos, burritos y ambiente familiar.', 'casual', {'pref_mexicana': 9, 'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Los Cebollines', 'Zona 5', 'Mexicana', 'Cadena Mexicana', 'familiar', 4.3, 'economico', 85, 'Cadena mexicana guatemalteca con tacos, burritos y ambiente familiar.', 'casual', {'pref_mexicana': 9, 'family_friendly': 8, 'fast_service': 8}),
        _real_entry('San Martin', 'Zona 10', 'Cafe', 'Bakery Cafe', 'familiar', 4.5, 'casual', 135, 'Panaderia y cafe reconocida en Guatemala.', 'cafe', {'family_friendly': 9, 'coffee_culture': 8}),
        _real_entry('San Martin', 'Zona 11', 'Cafe', 'Bakery Cafe', 'familiar', 4.5, 'casual', 135, 'Panaderia y cafe reconocida en Guatemala.', 'cafe', {'family_friendly': 9, 'coffee_culture': 8}),
        _real_entry('San Martin', 'Zona 14', 'Cafe', 'Bakery Cafe', 'familiar', 4.5, 'casual', 135, 'Panaderia y cafe reconocida en Guatemala.', 'cafe', {'family_friendly': 9, 'coffee_culture': 8}),
        _real_entry('San Martin', 'Zona 15', 'Cafe', 'Bakery Cafe', 'familiar', 4.5, 'casual', 135, 'Panaderia y cafe reconocida en Guatemala.', 'cafe', {'family_friendly': 9, 'coffee_culture': 8}),
        _real_entry('San Martin', 'Zona 5', 'Cafe', 'Bakery Cafe', 'familiar', 4.5, 'casual', 135, 'Panaderia y cafe reconocida en Guatemala.', 'cafe', {'family_friendly': 9, 'coffee_culture': 8}),
        _real_entry('Cafe Leon', 'Zona 10', 'Cafe', 'Cafe', 'cozy', 4.3, 'economico', 95, 'Cafe tradicional guatemalteco con panes y desayunos.', 'cafe', {'coffee_culture': 9, 'comfort_food': 7}),
        _real_entry('Cafe Leon', 'Zona 11', 'Cafe', 'Cafe', 'cozy', 4.3, 'economico', 95, 'Cafe tradicional guatemalteco con panes y desayunos.', 'cafe', {'coffee_culture': 9, 'comfort_food': 7}),
        _real_entry('Cafe Leon', 'Zona 14', 'Cafe', 'Cafe', 'cozy', 4.3, 'economico', 95, 'Cafe tradicional guatemalteco con panes y desayunos.', 'cafe', {'coffee_culture': 9, 'comfort_food': 7}),
        _real_entry('Cafe Leon', 'Zona 16', 'Cafe', 'Cafe', 'cozy', 4.3, 'economico', 95, 'Cafe tradicional guatemalteco con panes y desayunos.', 'cafe', {'coffee_culture': 9, 'comfort_food': 7}),
        _real_entry('Cafe Leon', 'Zona 5', 'Cafe', 'Cafe', 'cozy', 4.3, 'economico', 95, 'Cafe tradicional guatemalteco con panes y desayunos.', 'cafe', {'coffee_culture': 9, 'comfort_food': 7}),
        _real_entry('Barista', 'Zona 10', 'Cafe', 'Cafe de Especialidad', 'trendy', 4.4, 'casual', 115, 'Cadena de cafe de especialidad en Guatemala.', 'cafe', {'coffee_culture': 9, 'aesthetic': 7}),
        _real_entry('Barista', 'Zona 11', 'Cafe', 'Cafe de Especialidad', 'trendy', 4.4, 'casual', 115, 'Cadena de cafe de especialidad en Guatemala.', 'cafe', {'coffee_culture': 9, 'aesthetic': 7}),
        _real_entry('Barista', 'Zona 14', 'Cafe', 'Cafe de Especialidad', 'trendy', 4.4, 'casual', 115, 'Cadena de cafe de especialidad en Guatemala.', 'cafe', {'coffee_culture': 9, 'aesthetic': 7}),
        _real_entry('Barista', 'Zona 15', 'Cafe', 'Cafe de Especialidad', 'trendy', 4.4, 'casual', 115, 'Cadena de cafe de especialidad en Guatemala.', 'cafe', {'coffee_culture': 9, 'aesthetic': 7}),
        _real_entry('Barista', 'Zona 16', 'Cafe', 'Cafe de Especialidad', 'trendy', 4.4, 'casual', 115, 'Cadena de cafe de especialidad en Guatemala.', 'cafe', {'coffee_culture': 9, 'aesthetic': 7}),
        _real_entry('Barista', 'Zona 5', 'Cafe', 'Cafe de Especialidad', 'trendy', 4.4, 'casual', 115, 'Cadena de cafe de especialidad en Guatemala.', 'cafe', {'coffee_culture': 9, 'aesthetic': 7}),
        _real_entry('Starbucks', 'Zona 10', 'Cafe', 'Cafe de Cadena', 'casual', 4.2, 'casual', 110, 'Cafe de cadena internacional con bebidas y reposteria.', 'cafe', {'coffee_culture': 8, 'fast_service': 8}),
        _real_entry('Starbucks', 'Zona 11', 'Cafe', 'Cafe de Cadena', 'casual', 4.2, 'casual', 110, 'Cafe de cadena internacional con bebidas y reposteria.', 'cafe', {'coffee_culture': 8, 'fast_service': 8}),
        _real_entry('Starbucks', 'Zona 14', 'Cafe', 'Cafe de Cadena', 'casual', 4.2, 'casual', 110, 'Cafe de cadena internacional con bebidas y reposteria.', 'cafe', {'coffee_culture': 8, 'fast_service': 8}),
        _real_entry('Starbucks', 'Zona 15', 'Cafe', 'Cafe de Cadena', 'casual', 4.2, 'casual', 110, 'Cafe de cadena internacional con bebidas y reposteria.', 'cafe', {'coffee_culture': 8, 'fast_service': 8}),
        _real_entry('Starbucks', 'Zona 16', 'Cafe', 'Cafe de Cadena', 'casual', 4.2, 'casual', 110, 'Cafe de cadena internacional con bebidas y reposteria.', 'cafe', {'coffee_culture': 8, 'fast_service': 8}),
        _real_entry('Starbucks', 'Zona 5', 'Cafe', 'Cafe de Cadena', 'casual', 4.2, 'casual', 110, 'Cafe de cadena internacional con bebidas y reposteria.', 'cafe', {'coffee_culture': 8, 'fast_service': 8}),
        _real_entry('Tip Top', 'Zona 10', 'Internacional', 'Cadena Guatemalteca', 'familiar', 4.2, 'economico', 90, 'Cadena guatemalteca de comida rapida y platos tradicionales.', 'casual', {'pref_guatemalteca': 7, 'fast_service': 9, 'family_friendly': 8}),
        _real_entry('Tip Top', 'Zona 11', 'Internacional', 'Cadena Guatemalteca', 'familiar', 4.2, 'economico', 90, 'Cadena guatemalteca de comida rapida y platos tradicionales.', 'casual', {'pref_guatemalteca': 7, 'fast_service': 9, 'family_friendly': 8}),
        _real_entry('Tip Top', 'Zona 14', 'Internacional', 'Cadena Guatemalteca', 'familiar', 4.2, 'economico', 90, 'Cadena guatemalteca de comida rapida y platos tradicionales.', 'casual', {'pref_guatemalteca': 7, 'fast_service': 9, 'family_friendly': 8}),
        _real_entry('Tip Top', 'Zona 15', 'Internacional', 'Cadena Guatemalteca', 'familiar', 4.2, 'economico', 90, 'Cadena guatemalteca de comida rapida y platos tradicionales.', 'casual', {'pref_guatemalteca': 7, 'fast_service': 9, 'family_friendly': 8}),
        _real_entry('Tip Top', 'Zona 16', 'Internacional', 'Cadena Guatemalteca', 'familiar', 4.2, 'economico', 90, 'Cadena guatemalteca de comida rapida y platos tradicionales.', 'casual', {'pref_guatemalteca': 7, 'fast_service': 9, 'family_friendly': 8}),
        _real_entry('Tip Top', 'Zona 5', 'Internacional', 'Cadena Guatemalteca', 'familiar', 4.2, 'economico', 90, 'Cadena guatemalteca de comida rapida y platos tradicionales.', 'casual', {'pref_guatemalteca': 7, 'fast_service': 9, 'family_friendly': 8}),
        _real_entry('Pizza Hut', 'Zona 10', 'Internacional', 'Pizzeria', 'familiar', 4.1, 'economico', 120, 'Pizzeria de cadena internacional.', 'casual', {'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Pizza Hut', 'Zona 11', 'Internacional', 'Pizzeria', 'familiar', 4.1, 'economico', 120, 'Pizzeria de cadena internacional.', 'casual', {'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Pizza Hut', 'Zona 14', 'Internacional', 'Pizzeria', 'familiar', 4.1, 'economico', 120, 'Pizzeria de cadena internacional.', 'casual', {'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Pizza Hut', 'Zona 15', 'Internacional', 'Pizzeria', 'familiar', 4.1, 'economico', 120, 'Pizzeria de cadena internacional.', 'casual', {'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Pizza Hut', 'Zona 16', 'Internacional', 'Pizzeria', 'familiar', 4.1, 'economico', 120, 'Pizzeria de cadena internacional.', 'casual', {'family_friendly': 8, 'fast_service': 8}),
        _real_entry('Pizza Hut', 'Zona 5', 'Internacional', 'Pizzeria', 'familiar', 4.1, 'economico', 120, 'Pizzeria de cadena internacional.', 'casual', {'family_friendly': 8, 'fast_service': 8}),
        _real_entry("Domino's Pizza", 'Zona 10', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 110, 'Pizza a domicilio y local de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry("Domino's Pizza", 'Zona 11', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 110, 'Pizza a domicilio y local de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry("Domino's Pizza", 'Zona 14', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 110, 'Pizza a domicilio y local de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry("Domino's Pizza", 'Zona 15', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 110, 'Pizza a domicilio y local de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry("Domino's Pizza", 'Zona 16', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 110, 'Pizza a domicilio y local de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry("Domino's Pizza", 'Zona 5', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 110, 'Pizza a domicilio y local de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry('Subway', 'Zona 10', 'Internacional', 'Sandwiches', 'casual', 4.0, 'economico', 70, 'Sandwiches personalizables de cadena global.', 'casual', {'fast_service': 9, 'saludable': 5}),
        _real_entry('Subway', 'Zona 11', 'Internacional', 'Sandwiches', 'casual', 4.0, 'economico', 70, 'Sandwiches personalizables de cadena global.', 'casual', {'fast_service': 9, 'saludable': 5}),
        _real_entry('Subway', 'Zona 14', 'Internacional', 'Sandwiches', 'casual', 4.0, 'economico', 70, 'Sandwiches personalizables de cadena global.', 'casual', {'fast_service': 9, 'saludable': 5}),
        _real_entry('Subway', 'Zona 15', 'Internacional', 'Sandwiches', 'casual', 4.0, 'economico', 70, 'Sandwiches personalizables de cadena global.', 'casual', {'fast_service': 9, 'saludable': 5}),
        _real_entry('Subway', 'Zona 16', 'Internacional', 'Sandwiches', 'casual', 4.0, 'economico', 70, 'Sandwiches personalizables de cadena global.', 'casual', {'fast_service': 9, 'saludable': 5}),
        _real_entry('Subway', 'Zona 5', 'Internacional', 'Sandwiches', 'casual', 4.0, 'economico', 70, 'Sandwiches personalizables de cadena global.', 'casual', {'fast_service': 9, 'saludable': 5}),
        _real_entry("McDonald's", 'Zona 10', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 65, 'Cadena global de comida rapida.', 'casual', {'fast_service': 10, 'family_friendly': 8}),
        _real_entry("McDonald's", 'Zona 11', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 65, 'Cadena global de comida rapida.', 'casual', {'fast_service': 10, 'family_friendly': 8}),
        _real_entry("McDonald's", 'Zona 14', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 65, 'Cadena global de comida rapida.', 'casual', {'fast_service': 10, 'family_friendly': 8}),
        _real_entry("McDonald's", 'Zona 15', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 65, 'Cadena global de comida rapida.', 'casual', {'fast_service': 10, 'family_friendly': 8}),
        _real_entry("McDonald's", 'Zona 16', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 65, 'Cadena global de comida rapida.', 'casual', {'fast_service': 10, 'family_friendly': 8}),
        _real_entry("McDonald's", 'Zona 5', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 65, 'Cadena global de comida rapida.', 'casual', {'fast_service': 10, 'family_friendly': 8}),
        _real_entry('Burger King', 'Zona 10', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Hamburguesas de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry('Burger King', 'Zona 11', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Hamburguesas de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry('Burger King', 'Zona 14', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Hamburguesas de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry('Burger King', 'Zona 15', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Hamburguesas de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry('Burger King', 'Zona 16', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Hamburguesas de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry('Burger King', 'Zona 5', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Hamburguesas de cadena internacional.', 'casual', {'fast_service': 9, 'comfort_food': 7}),
        _real_entry("Wendy's", 'Zona 10', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 75, 'Hamburguesas y frosty de cadena americana.', 'casual', {'fast_service': 9}),
        _real_entry("Wendy's", 'Zona 11', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 75, 'Hamburguesas y frosty de cadena americana.', 'casual', {'fast_service': 9}),
        _real_entry("Wendy's", 'Zona 14', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 75, 'Hamburguesas y frosty de cadena americana.', 'casual', {'fast_service': 9}),
        _real_entry("Wendy's", 'Zona 15', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 75, 'Hamburguesas y frosty de cadena americana.', 'casual', {'fast_service': 9}),
        _real_entry("Wendy's", 'Zona 16', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 75, 'Hamburguesas y frosty de cadena americana.', 'casual', {'fast_service': 9}),
        _real_entry("Wendy's", 'Zona 5', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 75, 'Hamburguesas y frosty de cadena americana.', 'casual', {'fast_service': 9}),
        _real_entry('Taco Bell', 'Zona 10', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Comida mexicana rapida de cadena internacional.', 'casual', {'pref_mexicana': 6, 'fast_service': 9}),
        _real_entry('Taco Bell', 'Zona 11', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Comida mexicana rapida de cadena internacional.', 'casual', {'pref_mexicana': 6, 'fast_service': 9}),
        _real_entry('Taco Bell', 'Zona 14', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Comida mexicana rapida de cadena internacional.', 'casual', {'pref_mexicana': 6, 'fast_service': 9}),
        _real_entry('Taco Bell', 'Zona 15', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Comida mexicana rapida de cadena internacional.', 'casual', {'pref_mexicana': 6, 'fast_service': 9}),
        _real_entry('Taco Bell', 'Zona 16', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Comida mexicana rapida de cadena internacional.', 'casual', {'pref_mexicana': 6, 'fast_service': 9}),
        _real_entry('Taco Bell', 'Zona 5', 'Internacional', 'Comida Rapida', 'casual', 4.0, 'economico', 70, 'Comida mexicana rapida de cadena internacional.', 'casual', {'pref_mexicana': 6, 'fast_service': 9}),
        _real_entry('KFC', 'Zona 10', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 75, 'Pollo frito de cadena internacional.', 'casual', {'fast_service': 9, 'family_friendly': 7}),
        _real_entry('KFC', 'Zona 11', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 75, 'Pollo frito de cadena internacional.', 'casual', {'fast_service': 9, 'family_friendly': 7}),
        _real_entry('KFC', 'Zona 14', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 75, 'Pollo frito de cadena internacional.', 'casual', {'fast_service': 9, 'family_friendly': 7}),
        _real_entry('KFC', 'Zona 15', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 75, 'Pollo frito de cadena internacional.', 'casual', {'fast_service': 9, 'family_friendly': 7}),
        _real_entry('KFC', 'Zona 16', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 75, 'Pollo frito de cadena internacional.', 'casual', {'fast_service': 9, 'family_friendly': 7}),
        _real_entry('KFC', 'Zona 5', 'Internacional', 'Comida Rapida', 'familiar', 4.0, 'economico', 75, 'Pollo frito de cadena internacional.', 'casual', {'fast_service': 9, 'family_friendly': 7}),
        _real_entry('Dunkin', 'Zona 11', 'Cafe', 'Cafe y Donas', 'casual', 4.1, 'economico', 75, 'Cafe y donas de cadena internacional.', 'casual', {'coffee_culture': 7, 'fast_service': 9}),
        _real_entry('Dunkin', 'Zona 14', 'Cafe', 'Cafe y Donas', 'casual', 4.1, 'economico', 75, 'Cafe y donas de cadena internacional.', 'casual', {'coffee_culture': 7, 'fast_service': 9}),
        _real_entry('Dunkin', 'Zona 15', 'Cafe', 'Cafe y Donas', 'casual', 4.1, 'economico', 75, 'Cafe y donas de cadena internacional.', 'casual', {'coffee_culture': 7, 'fast_service': 9}),
        _real_entry('Dunkin', 'Zona 5', 'Cafe', 'Cafe y Donas', 'casual', 4.1, 'economico', 75, 'Cafe y donas de cadena internacional.', 'casual', {'coffee_culture': 7, 'fast_service': 9}),
        _real_entry('De Cero', 'Zona 11', 'Saludable', 'Ensaladas', 'casual', 4.3, 'casual', 120, 'Cadena de ensaladas y bowls personalizables.', 'cafe', {'saludable': 9, 'fast_service': 8}),
        _real_entry('De Cero', 'Zona 5', 'Saludable', 'Ensaladas', 'casual', 4.3, 'casual', 120, 'Cadena de ensaladas y bowls personalizables.', 'cafe', {'saludable': 9, 'fast_service': 8}),
        _real_entry('Little Caesars', 'Zona 11', 'Internacional', 'Pizzeria', 'familiar', 4.0, 'economico', 90, 'Pizza rapida de cadena internacional.', 'casual', {'fast_service': 9}),
        _real_entry('Little Caesars', 'Zona 14', 'Internacional', 'Pizzeria', 'familiar', 4.0, 'economico', 90, 'Pizza rapida de cadena internacional.', 'casual', {'fast_service': 9}),
        _real_entry('Little Caesars', 'Zona 15', 'Internacional', 'Pizzeria', 'familiar', 4.0, 'economico', 90, 'Pizza rapida de cadena internacional.', 'casual', {'fast_service': 9}),
        _real_entry('Little Caesars', 'Zona 16', 'Internacional', 'Pizzeria', 'familiar', 4.0, 'economico', 90, 'Pizza rapida de cadena internacional.', 'casual', {'fast_service': 9}),
        _real_entry('Little Caesars', 'Zona 5', 'Internacional', 'Pizzeria', 'familiar', 4.0, 'economico', 90, 'Pizza rapida de cadena internacional.', 'casual', {'fast_service': 9}),
        _real_entry("Papa John's", 'Zona 11', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 115, 'Pizza a domicilio de cadena internacional.', 'casual', {'fast_service': 8}),
        _real_entry("Papa John's", 'Zona 14', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 115, 'Pizza a domicilio de cadena internacional.', 'casual', {'fast_service': 8}),
        _real_entry("Papa John's", 'Zona 15', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 115, 'Pizza a domicilio de cadena internacional.', 'casual', {'fast_service': 8}),
        _real_entry("Papa John's", 'Zona 16', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 115, 'Pizza a domicilio de cadena internacional.', 'casual', {'fast_service': 8}),
        _real_entry("Papa John's", 'Zona 5', 'Internacional', 'Pizzeria', 'casual', 4.0, 'economico', 115, 'Pizza a domicilio de cadena internacional.', 'casual', {'fast_service': 8}),
    ]
    for idx, restaurant in enumerate(rows, start=1):
        restaurant["id"] = f"gc_{idx:03d}"
    report = validate_restaurant_catalog(rows)
    if not report["valid"]:
        sample = report["issues"][:5]
        raise ValueError("Catalogo con clasificacion invalida: %s" % sample)
    return rows


RESTAURANTS = build_catalog()
RESTAURANT_COUNT = len(RESTAURANTS)

RESTAURANT_SEMANTIC_INDEX: dict[str, dict[str, Any]] = {
    r["id"]: {
        "archetype": r.get("semantic_archetype", ""),
        "prefs": {k: round(float(v) / 10.0, 2) for k, v in (r.get("prefs") or {}).items() if float(v) > 0},
        "nombre": r.get("nombre", ""),
        "cocina": r.get("cocina", ""),
        "tipo": r.get("tipo", ""),
        "price_tier": r.get("price_tier", ""),
        "website_url": r.get("website_url", ""),
        "instagram_url": r.get("instagram_url", ""),
        "facebook_url": r.get("facebook_url", ""),
        "maps_url": r.get("maps_url", ""),
        "search_url": r.get("search_url", ""),
    }
    for r in RESTAURANTS
}
