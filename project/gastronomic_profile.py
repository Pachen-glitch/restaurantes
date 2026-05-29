"""
Perfil gastronomico multicategoria — aplica identidades expertas al catalogo.

Cada restaurante recibe:
- arquetipo principal
- categorias secundarias
- personalidad y estilo de experiencia
- dimensiones (premium, social, comfort, exploracion, romantic, nightlife)
- prefs derivadas de identidad (no solo reglas automaticas)
"""

from __future__ import annotations

from typing import Any

from gastronomic_identities import GASTRONOMIC_IDENTITIES, derive_identity_fallback
from restaurants_guatemala import (
    SEMANTIC_ARCHETYPES,
    _merge_pref_dict,
    _sanitize_restaurant_prefs,
    normalize_canonical_key,
)

# Categoria secundaria humana -> refuerzo de preferencias Savory.
CATEGORY_PREF_MAP: dict[str, dict[str, int]] = {
    "coffee_culture": {"coffee_culture": 9},
    "aesthetic": {"aesthetic": 8},
    "casual": {"casual": 8},
    "brunch": {"brunch": 9},
    "social": {"social_grupo": 8, "lively": 6},
    "trendy": {"trendy": 9},
    "nightlife": {"nightlife": 8, "lively": 7},
    "adventurous": {"aventurero": 9},
    "foodie": {"gourmet": 7, "aventurero": 7},
    "cultural": {"pref_guatemalteca": 8, "slow_food": 6},
    "comfort_food": {"comfort_food": 8},
    "family_friendly": {"family_friendly": 8},
    "traditional": {"slow_food": 7, "comfort_food": 7},
    "premium_local": {"premium": 8, "pref_guatemalteca": 9},
    "premium": {"premium": 8},
    "dinner_experience": {"slow_food": 7, "elegant": 7},
    "romantic": {"romantic": 8, "intimate": 7},
    "business_dining": {"business_dining": 8},
    "wine_focus": {"wine_focus": 8},
    "gourmet": {"gourmet": 9},
    "exclusive": {"exclusive": 8},
    "elegant": {"elegant": 8},
    "pref_italiana": {"pref_italiana": 10},
    "pref_japonesa": {"pref_japonesa": 9},
    "pref_mexicana": {"pref_mexicana": 9},
    "pref_guatemalteca": {"pref_guatemalteca": 10},
    "pref_mediterranea": {"pref_mediterranea": 9},
    "pref_coreana": {"pref_coreana": 9},
    "asian_fusion": {"asian_fusion": 9},
    "saludable": {"saludable": 9},
    "craft_beer": {"craft_beer": 8},
    "quick_meal": {"quick_meal": 9, "fast_service": 9},
    "fast_food": {"fast_food": 10, "comida_rapida": 9},
    "street_food": {"street_food": 7},
    "show_dining": {"social_grupo": 8, "lively": 7},
    "hotel_dining": {"elegant": 8, "business_dining": 7},
    "bakery": {"comfort_food": 7, "coffee_culture": 7},
    "dessert": {"comfort_food": 7, "family_friendly": 7},
    "healthy_fast": {"saludable": 9, "fast_service": 8},
    "americana": {"comfort_food": 7, "casual": 7},
    "steakhouse": {"premium": 8, "gourmet": 7},
    "seafood": {"gourmet": 7, "slow_food": 6},
    "rooftop": {"rooftop": 8, "aesthetic": 7},
}

# Categorias secundarias que refuerzan match con perfiles de usuario.
CATEGORY_USER_AFFINITY: dict[str, set[str]] = {
    "coffee_culture": {"brunch_user", "comfort_user"},
    "brunch": {"brunch_user"},
    "aesthetic": {"brunch_user", "explorer_user"},
    "trendy": {"explorer_user", "social_user", "nightlife_user"},
    "social": {"social_user", "nightlife_user"},
    "nightlife": {"nightlife_user", "social_user"},
    "adventurous": {"explorer_user"},
    "foodie": {"explorer_user", "premium_user"},
    "premium": {"premium_user", "romantic_user"},
    "premium_local": {"premium_user", "comfort_user"},
    "gourmet": {"premium_user", "romantic_user"},
    "romantic": {"romantic_user"},
    "family_friendly": {"comfort_user", "fast_food_user"},
    "comfort_food": {"comfort_user", "fast_food_user"},
    "fast_food": {"fast_food_user"},
    "quick_meal": {"fast_food_user", "comfort_user"},
    "pref_italiana": {"premium_user", "romantic_user"},
    "pref_guatemalteca": {"comfort_user", "premium_user"},
    "pref_mexicana": {"comfort_user", "social_user"},
    "pref_japonesa": {"premium_user", "explorer_user"},
    "asian_fusion": {"explorer_user", "premium_user"},
    "saludable": {"brunch_user", "comfort_user"},
    "craft_beer": {"nightlife_user", "social_user"},
    "steakhouse": {"premium_user", "romantic_user"},
    "business_dining": {"premium_user"},
    "traditional": {"comfort_user", "premium_user"},
    "cultural": {"comfort_user", "premium_user", "explorer_user"},
}


def _dims_to_pref_boosts(dims: dict[str, int]) -> dict[str, int]:
    boosts: dict[str, int] = {}
    mapping = {
        "premium": "premium",
        "social": "social_grupo",
        "comfort": "comfort_food",
        "exploration": "aventurero",
        "romantic": "romantic",
        "nightlife": "nightlife",
    }
    for dim_key, pref_key in mapping.items():
        val = int(dims.get(dim_key) or 0)
        if val >= 5:
            boosts[pref_key] = min(10, val)
    if dims.get("social", 0) >= 6:
        boosts["lively"] = min(10, max(boosts.get("lively", 0), dims["social"] - 1))
    if dims.get("exploration", 0) >= 6:
        boosts["trendy"] = min(10, max(boosts.get("trendy", 0), dims["exploration"] - 1))
    return boosts


def _build_prefs_from_identity(identity: dict[str, Any]) -> dict[str, int]:
    primary = identity["primary_archetype"]
    template = SEMANTIC_ARCHETYPES.get(primary)
    if not template:
        prefs: dict[str, int] = {}
    else:
        prefs = dict(template.get("prefs") or {})

    for category in identity.get("secondary_categories") or []:
        prefs = _merge_pref_dict(prefs, CATEGORY_PREF_MAP.get(category, {}))

    prefs = _merge_pref_dict(prefs, _dims_to_pref_boosts(identity.get("dimensions") or {}))
    prefs = _merge_pref_dict(prefs, identity.get("pref_boost") or {})
    return _sanitize_restaurant_prefs(prefs, primary)


def _scores_from_identity(identity: dict[str, Any], primary: str) -> dict[str, int]:
    dims = identity.get("dimensions") or {}
    template = SEMANTIC_ARCHETYPES.get(primary, {})
    base_scores = dict(template.get("scores") or {})
    return {
        "nightlife_score": int(dims.get("nightlife") or base_scores.get("nightlife_score") or 4),
        "social_score": int(dims.get("social") or base_scores.get("social_score") or 6),
        "premium_score": int(dims.get("premium") or base_scores.get("premium_score") or 5),
        "comfort_score": int(dims.get("comfort") or base_scores.get("comfort_score") or 6),
        "aesthetic_score": int(
            max(dims.get("exploration", 0), identity.get("aesthetic_level") or 0)
            or base_scores.get("aesthetic_score")
            or 5
        ),
        "romantic_score": int(dims.get("romantic") or base_scores.get("romantic_score") or 4),
        "fast_service_score": int(base_scores.get("fast_service_score") or 6),
    }


def apply_gastronomic_identity(restaurant: dict[str, Any]) -> dict[str, Any]:
    """Aplica clasificacion gastronomica experta sobre el registro canonico."""
    key = restaurant.get("canonical_name") or normalize_canonical_key(restaurant.get("nombre") or "")
    identity = GASTRONOMIC_IDENTITIES.get(key) or derive_identity_fallback(restaurant)

    primary = identity["primary_archetype"]
    dims = dict(identity.get("dimensions") or {})
    scores = _scores_from_identity(identity, primary)
    prefs = _build_prefs_from_identity(identity)

    out = dict(restaurant)
    out["semantic_archetype"] = primary
    out["primary_archetype"] = primary
    out["secondary_categories"] = list(identity.get("secondary_categories") or [])
    out["gastronomic_personality"] = identity.get("personality") or ""
    out["experience_style"] = identity.get("experience_style") or ""
    out["cocina_principal"] = identity.get("cocina_principal") or out.get("cocina") or ""
    out["ambiente_label"] = identity.get("ambiente") or out.get("ambiente") or ""
    out["dimension_premium"] = int(dims.get("premium") or 0)
    out["dimension_social"] = int(dims.get("social") or 0)
    out["dimension_comfort"] = int(dims.get("comfort") or 0)
    out["dimension_exploration"] = int(dims.get("exploration") or 0)
    out["dimension_romantic"] = int(dims.get("romantic") or 0)
    out["dimension_nightlife"] = int(dims.get("nightlife") or 0)
    out["prefs"] = prefs
    out.update(scores)
    if identity.get("cocina_principal"):
        out["cocina"] = identity["cocina_principal"]
    return out


def identity_match_boost(user_archetype: str, secondary_categories: list[str]) -> float:
    """Boost suave cuando categorias secundarias encajan con el perfil dominante del usuario."""
    if not secondary_categories:
        return 0.0
    hits = 0
    for cat in secondary_categories:
        if user_archetype in CATEGORY_USER_AFFINITY.get(cat, set()):
            hits += 1
    if hits == 0:
        return 0.0
    return min(12.0, 3.0 + hits * 2.5)


def categories_to_display_tags(categories: list[str], limit: int = 6) -> list[str]:
    """Convierte categorias secundarias a hashtags legibles."""
    label_map = {
        "coffee_culture": "coffee",
        "comfort_food": "comfortfood",
        "family_friendly": "family",
        "pref_italiana": "italiana",
        "pref_guatemalteca": "guatemalteca",
        "pref_mexicana": "mexicana",
        "pref_japonesa": "japonesa",
        "pref_mediterranea": "mediterranea",
        "pref_coreana": "coreana",
        "asian_fusion": "asiatico",
        "quick_meal": "quickmeal",
        "fast_food": "fastfood",
        "business_dining": "business",
        "premium_local": "premiumlocal",
        "dinner_experience": "dinner",
        "show_dining": "showdining",
        "healthy_fast": "healthy",
        "craft_beer": "craftbeer",
        "foodie": "foodie",
        "adventurous": "aventura",
    }
    tags: list[str] = []
    for cat in categories:
        tag = label_map.get(cat, cat.replace("_", ""))
        if tag not in tags:
            tags.append(tag)
    return tags[:limit]


def export_classification_csv(output_path: str | None = None) -> str:
    """Exporta la clasificacion gastronomica experta completa a CSV."""
    import csv
    from pathlib import Path

    from restaurants_guatemala import RESTAURANTS

    path = Path(output_path or Path(__file__).resolve().parent / "gastronomic_classification.csv")
    fields = [
        "nombre",
        "primary_archetype",
        "secondary_categories",
        "cocina_principal",
        "ambiente_label",
        "gastronomic_personality",
        "experience_style",
        "dimension_premium",
        "dimension_social",
        "dimension_comfort",
        "dimension_exploration",
        "dimension_romantic",
        "dimension_nightlife",
    ]
    rows = []
    for r in sorted(RESTAURANTS, key=lambda x: x.get("nombre", "").lower()):
        rows.append(
            {
                "nombre": r.get("nombre"),
                "primary_archetype": r.get("primary_archetype"),
                "secondary_categories": " | ".join(r.get("secondary_categories") or []),
                "cocina_principal": r.get("cocina_principal"),
                "ambiente_label": r.get("ambiente_label"),
                "gastronomic_personality": r.get("gastronomic_personality"),
                "experience_style": r.get("experience_style"),
                "dimension_premium": r.get("dimension_premium"),
                "dimension_social": r.get("dimension_social"),
                "dimension_comfort": r.get("dimension_comfort"),
                "dimension_exploration": r.get("dimension_exploration"),
                "dimension_romantic": r.get("dimension_romantic"),
                "dimension_nightlife": r.get("dimension_nightlife"),
            }
        )
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


if __name__ == "__main__":
    print("Clasificacion exportada:", export_classification_csv())
