"""Catalogo realista de restaurantes de Ciudad de Guatemala para Neo4j."""

from __future__ import annotations

import random
from typing import Any

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
]

_CUISINE_PREFS = {
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


def _price_from_tier(tier: str) -> int:
    low, high = _PRICE_TIER_RANGE[tier]
    return int(round(random.randint(low, high) / 5) * 5)


def _scores_to_prefs(scores: dict[str, Any], archetype_prefs: dict[str, int]) -> dict[str, int]:
    prefs = {key: 0 for key in _PREF_KEYS}
    for key, value in archetype_prefs.items():
        if key in prefs:
            prefs[key] = max(0, min(10, int(value)))

    cocina = str(scores.get("cocina", ""))
    ambiente = str(scores.get("ambiente", ""))
    for key, value in _CUISINE_PREFS.get(cocina, {}).items():
        prefs[key] = max(prefs[key], value)
    for key, value in _AMBIENTE_PREFS.get(ambiente, {}).items():
        prefs[key] = max(prefs[key], value)

    nightlife = int(scores.get("nightlife_score", 5))
    social = int(scores.get("social_score", 5))
    premium = int(scores.get("premium_score", 5))
    comfort = int(scores.get("comfort_score", 5))
    aesthetic = int(scores.get("aesthetic_score", 5))
    romantic = int(scores.get("romantic_score", 5))
    fast_service = int(scores.get("fast_service_score", 5))
    rating = float(scores.get("rating", 4.3))

    prefs["nightlife"] = max(prefs["nightlife"], nightlife)
    prefs["social_grupo"] = max(prefs["social_grupo"], social)
    prefs["premium"] = max(prefs["premium"], premium)
    prefs["exclusive"] = max(prefs["exclusive"], max(1, premium - 1))
    prefs["business_dining"] = max(prefs["business_dining"], max(1, premium - 2))
    prefs["comfort_food"] = max(prefs["comfort_food"], comfort)
    prefs["aesthetic"] = max(prefs["aesthetic"], aesthetic)
    prefs["trendy"] = max(prefs["trendy"], max(1, social - 1))
    prefs["romantic"] = max(prefs["romantic"], romantic)
    prefs["intimate"] = max(prefs["intimate"], max(1, romantic - 1))
    prefs["fast_service"] = max(prefs["fast_service"], fast_service)
    prefs["lively"] = max(prefs["lively"], max(1, nightlife - 1))
    prefs["gourmet"] = max(prefs["gourmet"], max(1, int(round((premium + rating) / 2))))

    if fast_service >= 8:
        prefs["street_food"] = max(prefs["street_food"], 7)
    if premium >= 8:
        prefs["wine_focus"] = max(prefs["wine_focus"], 6)
        prefs["elegant"] = max(prefs["elegant"], 7)
    if aesthetic >= 8:
        prefs["coffee_culture"] = max(prefs["coffee_culture"], 6)
    if comfort >= 8:
        prefs["family_friendly"] = max(prefs["family_friendly"], 7)
        prefs["casual"] = max(prefs["casual"], 6)

    return prefs


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
) -> dict[str, Any]:
    score_map = dict(_SCORE_PROFILES[profile])
    score_map.update({"cocina": cocina, "ambiente": ambiente, "rating": rating})
    prefs = _scores_to_prefs(score_map, pref_boost or {})
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
        "nightlife_score": score_map["nightlife_score"],
        "social_score": score_map["social_score"],
        "premium_score": score_map["premium_score"],
        "comfort_score": score_map["comfort_score"],
        "aesthetic_score": score_map["aesthetic_score"],
        "romantic_score": score_map["romantic_score"],
        "fast_service_score": score_map["fast_service_score"],
        "prefs": prefs,
    }


CURATED = [
    _curated_entry("Hibachi", "Zona 10", "Japonesa", "Teppanyaki", "elegante", 4.7, "premium", 295, "Plancha japonesa y show culinario en ambiente sofisticado.", "premium", {"business_dining": 8, "social_grupo": 7}),
    _curated_entry("Tamarindos", "Zona 10", "Fusion", "Fine Dining", "romantico", 4.8, "fine", 455, "Cocina de autor con ingredientes locales y montaje elegante.", "luxury", {"romantic": 9, "gourmet": 10}),
    _curated_entry("Pecorino", "Zona 10", "Italiana", "Ristorante", "romantico", 4.7, "premium", 315, "Pastas artesanales y carta de vinos para cenas largas.", "premium", {"wine_focus": 8, "slow_food": 8}),
    _curated_entry("Tre Fratelli", "Zona 10", "Italiana", "Trattoria", "elegante", 4.6, "premium", 285, "Recetas italianas clasicas con servicio cuidado.", "premium", {"family_friendly": 7}),
    _curated_entry("Bottega Foresto", "Zona 10", "Italiana", "Bistro", "trendy", 4.7, "fine", 410, "Concepto contemporaneo italiano con barra de vinos.", "premium", {"aesthetic": 9, "trendy": 9}),
    _curated_entry("Viu Bistro", "Zona 10", "Internacional", "Bistro", "trendy", 4.6, "premium", 275, "Bistro urbano de platos cortos y cocteleria cuidada.", "premium", {"nightlife": 7}),
    _curated_entry("Porcino", "Zona 10", "Italiana", "Steakhouse", "elegante", 4.7, "fine", 440, "Cortes premium y especialidades italianas en salon moderno.", "luxury", {"business_dining": 9}),
    _curated_entry("El Cielo", "Zona 10", "Fusion", "Fine Dining", "romantico", 4.8, "luxury", 640, "Menu degustacion con tecnica moderna y atencion personalizada.", "luxury", {"exclusive": 10, "romantic": 9}),
    _curated_entry("Casa del Angel", "Zona 10", "Francesa", "Fine Dining", "romantico", 4.7, "luxury", 690, "Cocina francesa contemporanea en casa restaurada.", "luxury", {"intimate": 9, "wine_focus": 9}),
    _curated_entry("Sake Atelier", "Zona 10", "Japonesa", "Omakase", "elegante", 4.9, "luxury", 790, "Barra omakase con pescados importados y maridaje.", "luxury", {"pref_japonesa": 10, "gourmet": 10}),
    _curated_entry("Brasa Capital", "Zona 10", "Steakhouse", "Steakhouse", "elegante", 4.6, "fine", 470, "Madurados en seco y carta amplia de cortes.", "premium", {"business_dining": 8, "premium": 9}),
    _curated_entry("Nikkei 10", "Zona 10", "Peruana", "Nikkei", "trendy", 4.6, "premium", 335, "Finos toques peruanos y japoneses para compartir.", "premium", {"asian_fusion": 9, "aventurero": 8}),
    _curated_entry("La Barra del Patio", "Zona 10", "Mexicana", "Cantina Gourmet", "nocturno", 4.4, "casual", 170, "Tacos de autor y mixologia para grupos grandes.", "casual", {"craft_beer": 7, "nightlife": 8}),
    _curated_entry("Rooftop Diez", "Zona 10", "Internacional", "Rooftop", "nocturno", 4.5, "premium", 320, "Terraza con vista, tapas y ambiente de noche.", "premium", {"rooftop": 10, "nightlife": 9}),
    _curated_entry("Marea Urbana", "Zona 10", "Mariscos", "Seafood Grill", "elegante", 4.5, "premium", 305, "Mariscos frescos y ceviches en formato urbano.", "premium", {"romantic": 6, "gourmet": 8}),

    _curated_entry("Frida Kahlo", "Zona 14", "Mexicana", "Cocina Mexicana", "trendy", 4.6, "premium", 295, "Sabores mexicanos autenticos con diseno vibrante.", "premium", {"pref_mexicana": 10, "lively": 8}),
    _curated_entry("Los Tres Tiempos", "Zona 14", "Guatemalteca", "Cocina Guatemalteca", "familiar", 4.7, "premium", 265, "Recetas guatemaltecas con enfoque moderno y porciones generosas.", "premium", {"pref_guatemalteca": 10, "comfort_food": 8}),
    _curated_entry("Marena", "Zona 14", "Mediterranea", "Mediterraneo", "elegante", 4.7, "fine", 420, "Pescados, aceite de oliva y vegetales de temporada.", "premium", {"pref_mediterranea": 10, "saludable": 8}),
    _curated_entry("Corte Nativo", "Zona 14", "Steakhouse", "Steakhouse", "elegante", 4.6, "fine", 460, "Parrilla premium para almuerzos corporativos y cenas.", "premium", {"business_dining": 9}),
    _curated_entry("Osteria Primitivo", "Zona 14", "Italiana", "Osteria", "romantico", 4.7, "premium", 330, "Pasta fresca, vino y ambiente calido.", "premium", {"wine_focus": 8, "intimate": 8}),
    _curated_entry("Sora Sushi", "Zona 14", "Japonesa", "Sushi", "elegante", 4.8, "fine", 515, "Nigiris delicados y servicio de alta precision.", "luxury", {"pref_japonesa": 10, "gourmet": 9}),
    _curated_entry("El Portico 14", "Zona 14", "Francesa", "Bistro", "romantico", 4.5, "premium", 310, "Bistro frances de porciones balanceadas y postres clasicos.", "premium", {"romantic": 8}),
    _curated_entry("Atempo", "Zona 14", "Fusion", "Cocina de Autor", "elegante", 4.7, "fine", 485, "Menu de temporada con tecnica moderna latinoeuropea.", "luxury", {"exclusive": 9, "gourmet": 9}),
    _curated_entry("Luna Rooftop", "Zona 14", "Internacional", "Rooftop", "nocturno", 4.5, "premium", 295, "Cocteles de autor y platos pequenos para after office.", "premium", {"rooftop": 10, "nightlife": 9}),
    _curated_entry("Brasa 14", "Zona 14", "Steakhouse", "Grill House", "elegante", 4.5, "premium", 320, "Carnes al carbon y selecciones para compartir.", "premium", {"business_dining": 8}),
    _curated_entry("Mikuna", "Zona 14", "Peruana", "Nikkei", "trendy", 4.6, "premium", 345, "Cebiches y tiraditos con enfoque contemporaneo.", "premium", {"asian_fusion": 8, "aventurero": 8}),
    _curated_entry("Casa Amapola", "Zona 14", "Mediterranea", "Bistro", "cozy", 4.4, "casual", 180, "Cocina mediterranea ligera en ambiente acogedor.", "cafe", {"saludable": 8, "aesthetic": 7}),
    _curated_entry("Siena Mercato", "Zona 14", "Italiana", "Wine Bar", "trendy", 4.5, "premium", 260, "Platos italianos cortos y buena seleccion de vino por copa.", "premium", {"wine_focus": 8, "trendy": 8}),
    _curated_entry("Paladar 14", "Zona 14", "Internacional", "Bistro", "elegante", 4.5, "premium", 275, "Menu ejecutivo de alto nivel y cena con musica suave.", "premium", {"business_dining": 8, "social_grupo": 7}),
    _curated_entry("Ceviche de Barrio Alto", "Zona 14", "Mariscos", "Cevicheria", "casual", 4.3, "casual", 165, "Ceviches clasicos y tostadas frescas para almuerzos rapidos.", "casual", {"fast_service": 8}),

    _curated_entry("Kaffeine", "Zona 15", "Cafe", "Cafe de Especialidad", "brunch", 4.6, "casual", 145, "Cafe de especialidad, reposteria y brunch todo el dia.", "cafe", {"coffee_culture": 10, "brunch": 9}),
    _curated_entry("Nido Verde", "Zona 15", "Saludable", "Healthy Kitchen", "brunch", 4.5, "casual", 160, "Bowls, ensaladas y smoothies para rutina saludable.", "cafe", {"saludable": 10, "aesthetic": 8}),
    _curated_entry("Masa Madre 15", "Zona 15", "Cafe", "Bakery Cafe", "cozy", 4.5, "casual", 135, "Pan de fermentacion natural y desayunos bien presentados.", "cafe", {"coffee_culture": 8, "comfort_food": 7}),
    _curated_entry("Avena Casa", "Zona 15", "Saludable", "Brunch", "brunch", 4.4, "casual", 140, "Opciones de brunch saludable y cafe filtrado.", "cafe", {"brunch": 9, "saludable": 9}),
    _curated_entry("Lumen Coffee Lab", "Zona 15", "Cafe", "Coffee Lab", "trendy", 4.5, "casual", 150, "Extracciones de especialidad con menu ligero.", "cafe", {"coffee_culture": 10, "aesthetic": 9}),
    _curated_entry("Basilico Verde", "Zona 15", "Mediterranea", "Bistro", "trendy", 4.5, "premium", 220, "Mediterraneo fresco con enfoque plant-forward.", "cafe", {"pref_mediterranea": 9, "saludable": 8}),
    _curated_entry("Miel Taller", "Zona 15", "Cafe", "Brunch House", "brunch", 4.4, "casual", 130, "Huevos, waffles y panaderia artesanal para fines de semana.", "cafe", {"brunch": 9, "family_friendly": 7}),
    _curated_entry("Aguacate Social", "Zona 15", "Saludable", "Brunch", "trendy", 4.3, "casual", 155, "Tostadas, bowls y cafe de origen en ambiente luminoso.", "cafe", {"trendy": 8, "social_grupo": 8}),
    _curated_entry("Verde y Limon", "Zona 15", "Saludable", "Healthy Bar", "casual", 4.3, "economico", 90, "Jugos prensados y wraps para ritmo de oficina.", "casual", {"fast_service": 9, "saludable": 8}),
    _curated_entry("Giardino 15", "Zona 15", "Italiana", "Trattoria", "romantico", 4.6, "premium", 245, "Pastas caseras y terraza verde para cenas tranquilas.", "premium", {"intimate": 8, "aesthetic": 8}),
    _curated_entry("Moki Poke", "Zona 15", "Asiatica", "Poke", "casual", 4.2, "economico", 100, "Poke bowls rapidos con ingredientes frescos.", "casual", {"asian_fusion": 7, "fast_service": 9}),
    _curated_entry("Yuzu Bowl", "Zona 15", "Japonesa", "Ramen", "cozy", 4.4, "casual", 175, "Ramen y donburi en un espacio pequeno y moderno.", "cafe", {"pref_japonesa": 8, "comfort_food": 7}),
    _curated_entry("Andino Fit", "Zona 15", "Peruana", "Healthy Bistro", "trendy", 4.3, "casual", 165, "Cocina peruana ligera con bowls y ceviche.", "cafe", {"saludable": 8, "aventurero": 7}),
    _curated_entry("Aroma Taller", "Zona 15", "Cafe", "Cafe de Especialidad", "brunch", 4.4, "casual", 120, "Cafe de origen guatemalteco y pasteleria simple.", "cafe", {"coffee_culture": 9}),
    _curated_entry("Cosecha 15", "Zona 15", "Guatemalteca", "Comedor Contemporaneo", "familiar", 4.4, "casual", 170, "Ingredientes locales en platos caseros de temporada.", "cafe", {"pref_guatemalteca": 8, "family_friendly": 8}),

    _curated_entry("San Martin", "Zona 16", "Cafe", "Bakery Cafe", "familiar", 4.6, "casual", 140, "Panaderia iconica con menu amplio para toda la familia.", "cafe", {"family_friendly": 9, "coffee_culture": 8}),
    _curated_entry("Cayala Brunch Co", "Zona 16", "Cafe", "Brunch", "brunch", 4.5, "casual", 155, "Brunch de fin de semana en entorno peatonal.", "cafe", {"brunch": 9, "aesthetic": 8}),
    _curated_entry("Bosco Verde", "Zona 16", "Saludable", "Healthy Kitchen", "trendy", 4.5, "casual", 170, "Opciones saludables con ingredientes de temporada.", "cafe", {"saludable": 10, "trendy": 8}),
    _curated_entry("Naranjo Bistro", "Zona 16", "Mediterranea", "Bistro", "elegante", 4.5, "premium", 235, "Mediterraneo ligero para comidas de negocios.", "premium", {"business_dining": 8, "pref_mediterranea": 9}),
    _curated_entry("Moka District", "Zona 16", "Cafe", "Coffee Bar", "trendy", 4.4, "casual", 135, "Barra de espresso y tostados locales en espacio moderno.", "cafe", {"coffee_culture": 10, "aesthetic": 8}),
    _curated_entry("Aurora House", "Zona 16", "Fusion", "Bistro", "romantico", 4.6, "premium", 260, "Cocina fusion y terraza intima para cita.", "premium", {"romantic": 9, "intimate": 8}),
    _curated_entry("Marea Cayala", "Zona 16", "Mariscos", "Cevicheria", "trendy", 4.4, "premium", 240, "Mariscos frescos y cocteleria ligera.", "premium", {"social_grupo": 8, "nightlife": 7}),
    _curated_entry("Casa Botanica", "Zona 16", "Saludable", "Brunch", "brunch", 4.5, "casual", 150, "Platos vegetales y ambiente natural para desayunos largos.", "cafe", {"saludable": 9, "aesthetic": 9}),
    _curated_entry("Gusto 16", "Zona 16", "Italiana", "Pizzeria", "familiar", 4.3, "casual", 165, "Pizza al horno y pastas para compartir.", "casual", {"family_friendly": 8, "comfort_food": 8}),
    _curated_entry("Cosecha Urbana", "Zona 16", "Guatemalteca", "Comedor", "familiar", 4.4, "casual", 150, "Comida guatemalteca moderna con ingredientes del altiplano.", "casual", {"pref_guatemalteca": 8, "comfort_food": 8}),
    _curated_entry("Koru Sushi", "Zona 16", "Japonesa", "Sushi", "elegante", 4.5, "premium", 295, "Sushi premium y platos calientes para cena social.", "premium", {"pref_japonesa": 9, "premium": 8}),
    _curated_entry("Piedra Alta", "Zona 16", "Steakhouse", "Steakhouse", "elegante", 4.6, "fine", 390, "Cortes madurados y barra de vinos robusta.", "premium", {"business_dining": 8, "wine_focus": 8}),
    _curated_entry("Casa Guayacan", "Zona 16", "Internacional", "Bistro", "cozy", 4.4, "casual", 180, "Platos internacionales en ambiente acogedor.", "cafe", {"comfort_food": 7, "intimate": 7}),
    _curated_entry("Ritual Matcha", "Zona 16", "Cafe", "Tea & Coffee", "trendy", 4.3, "casual", 120, "Bebidas de te y cafe con postres ligeros.", "cafe", {"coffee_culture": 8, "aesthetic": 8}),
    _curated_entry("Altura 16", "Zona 16", "Internacional", "Rooftop", "nocturno", 4.4, "premium", 270, "Vista panoramica con cocina ligera y dj set.", "premium", {"rooftop": 10, "nightlife": 8}),

    _curated_entry("La Cazuela 11", "Zona 11", "Guatemalteca", "Comedor", "familiar", 4.4, "economico", 85, "Comida casera guatemalteca para almuerzo diario.", "casual", {"pref_guatemalteca": 9, "comfort_food": 9}),
    _curated_entry("Taqueria El Naranjo", "Zona 11", "Mexicana", "Taqueria", "casual", 4.3, "economico", 80, "Tacos al pastor y gringas en servicio rapido.", "casual", {"street_food": 9, "fast_service": 9}),
    _curated_entry("Pollo y Lena", "Zona 11", "Guatemalteca", "Asados", "familiar", 4.2, "economico", 75, "Pollo asado y guarniciones tradicionales.", "casual", {"family_friendly": 8}),
    _curated_entry("Pupusas de Dona Tere", "Zona 11", "Guatemalteca", "Pupuseria", "casual", 4.3, "economico", 70, "Pupusas artesanales y curtido casero.", "casual", {"street_food": 8, "comfort_food": 8}),
    _curated_entry("El Chirmol", "Zona 11", "Guatemalteca", "Comedor", "familiar", 4.4, "economico", 85, "Platos tipicos y tortillas recien hechas.", "casual", {"pref_guatemalteca": 9}),
    _curated_entry("Chicharrones La Ceiba", "Zona 11", "Guatemalteca", "Antojitos", "casual", 4.1, "economico", 65, "Chicharrones, yuca y antojitos para compartir.", "casual", {"street_food": 8, "lively": 7}),
    _curated_entry("La Plancha Once", "Zona 11", "Mexicana", "Parrillada", "casual", 4.2, "casual", 110, "Parrillada mixta y tortillas de maiz al momento.", "casual", {"social_grupo": 8}),
    _curated_entry("Rincon Chapin", "Zona 11", "Guatemalteca", "Comedor", "familiar", 4.3, "economico", 90, "Desayunos chapines y caldos sustanciosos.", "casual", {"comfort_food": 9, "family_friendly": 9}),
    _curated_entry("Marisqueria Once", "Zona 11", "Mariscos", "Marisqueria", "casual", 4.2, "casual", 135, "Caldos de mariscos y ceviches clasicos.", "casual", {"fast_service": 7}),
    _curated_entry("Ramen Barrio 11", "Zona 11", "Japonesa", "Ramen", "cozy", 4.3, "casual", 170, "Ramen abundante en local pequeno y acogedor.", "casual", {"pref_japonesa": 7, "comfort_food": 8}),
    _curated_entry("Punto Coreano", "Zona 11", "Coreana", "Korean BBQ", "casual", 4.2, "casual", 180, "Coreano informal con parrilla y guarniciones.", "casual", {"pref_coreana": 8, "aventurero": 8}),
    _curated_entry("La Esquina 11", "Zona 11", "Internacional", "Bistro", "casual", 4.1, "economico", 95, "Menu variado y rapido para horario de oficina.", "casual", {"fast_service": 8, "casual": 8}),
    _curated_entry("Antojitos Montufar", "Zona 11", "Guatemalteca", "Street Food", "casual", 4.2, "economico", 70, "Shucos y garnachas para comer al paso.", "casual", {"street_food": 9, "fast_service": 9}),
    _curated_entry("Comal y Carbon", "Zona 11", "Guatemalteca", "Parrilla", "familiar", 4.3, "casual", 120, "Carnes al carbon y antojitos para grupos familiares.", "casual", {"family_friendly": 8, "social_grupo": 8}),
    _curated_entry("La Casa del Caldo", "Zona 11", "Guatemalteca", "Sopas", "cozy", 4.2, "economico", 80, "Caldos reconfortantes con sazon tradicional.", "casual", {"comfort_food": 9}),

    _curated_entry("Tortas Quinta", "Zona 5", "Mexicana", "Taqueria", "casual", 4.2, "economico", 75, "Tortas y tacos para servicio agil y sabroso.", "casual", {"street_food": 9, "fast_service": 9}),
    _curated_entry("Comedor La Estacion", "Zona 5", "Guatemalteca", "Comedor", "familiar", 4.3, "economico", 80, "Menues diarios con comida casera y buen precio.", "casual", {"comfort_food": 9, "family_friendly": 8}),
    _curated_entry("Shucos El Trebol", "Zona 5", "Guatemalteca", "Street Food", "casual", 4.1, "economico", 55, "Shucos de barrio con ingredientes al gusto.", "casual", {"street_food": 10, "fast_service": 9}),
    _curated_entry("Taqueria Reforma 5", "Zona 5", "Mexicana", "Taqueria", "casual", 4.2, "economico", 70, "Tacos y quesadillas con salsa de casa.", "casual", {"pref_mexicana": 8}),
    _curated_entry("Cafecito Obrero", "Zona 5", "Cafe", "Cafe", "cozy", 4.0, "economico", 60, "Cafe sencillo con panes y desayunos rapidos.", "casual", {"coffee_culture": 6, "comfort_food": 7}),
    _curated_entry("Doce Onzas", "Zona 5", "Cafe", "Cafe", "casual", 4.1, "economico", 70, "Cafe de origen local y sandwiches para llevar.", "casual", {"coffee_culture": 7, "fast_service": 8}),
    _curated_entry("El Sazon de Abuela", "Zona 5", "Guatemalteca", "Comedor", "familiar", 4.4, "economico", 85, "Recetas tradicionales y porciones abundantes.", "casual", {"pref_guatemalteca": 9, "comfort_food": 9}),
    _curated_entry("Casa Mixco", "Zona 5", "Guatemalteca", "Parrilla", "familiar", 4.2, "casual", 130, "Parrilla chapina y acompañamientos clasicos.", "casual", {"social_grupo": 8}),
    _curated_entry("Paches y Tamales Lupita", "Zona 5", "Guatemalteca", "Antojitos", "casual", 4.3, "economico", 65, "Paches, tamales y atol para desayunos y cenas.", "casual", {"street_food": 8, "comfort_food": 8}),
    _curated_entry("Marimba Food Hall", "Zona 5", "Internacional", "Food Hall", "casual", 4.2, "casual", 120, "Puestos variados ideales para grupos y oficina.", "casual", {"social_grupo": 9, "lively": 8}),
    _curated_entry("Burger del Barrio", "Zona 5", "Internacional", "Hamburguesas", "casual", 4.1, "economico", 90, "Hamburguesas clasicas con papas crujientes.", "casual", {"fast_service": 8, "comfort_food": 8}),
    _curated_entry("Ceviche Quinta", "Zona 5", "Mariscos", "Cevicheria", "casual", 4.1, "casual", 125, "Ceviches frescos para almuerzo rapido.", "casual", {"fast_service": 8, "street_food": 7}),
    _curated_entry("El Rincon Coreano", "Zona 5", "Coreana", "Korean BBQ", "casual", 4.0, "casual", 165, "Parrilla coreana accesible con buen ambiente.", "casual", {"pref_coreana": 8, "social_grupo": 8}),
    _curated_entry("Ramen de la Quinta", "Zona 5", "Japonesa", "Ramen", "cozy", 4.2, "casual", 155, "Ramen y gyozas para dias lluviosos.", "casual", {"pref_japonesa": 7, "comfort_food": 8}),
    _curated_entry("Plaza 5 Cantina", "Zona 5", "Mexicana", "Cantina", "nocturno", 4.1, "casual", 145, "Botanas, cerveza artesanal y musica en vivo.", "casual", {"craft_beer": 8, "nightlife": 7}),
]

ARCHETYPES = [
    {
        "name": "premium_urbano",
        "weight": 34,
        "zone_weights": {"Zona 10": 42, "Zona 14": 36, "Zona 15": 8, "Zona 16": 8, "Zona 11": 3, "Zona 5": 3},
        "tier_weights": {"premium": 40, "fine": 40, "luxury": 15, "casual": 5},
        "cuisines": ["Japonesa", "Italiana", "Steakhouse", "Francesa", "Fusion", "Mediterranea"],
        "tipos": ["Sushi", "Omakase", "Steakhouse", "Fine Dining", "Ristorante", "Bistro"],
        "ambientes": ["elegante", "romantico", "trendy"],
        "score_range": {
            "nightlife_score": (5, 8),
            "social_score": (6, 9),
            "premium_score": (7, 10),
            "comfort_score": (4, 7),
            "aesthetic_score": (7, 10),
            "romantic_score": (6, 9),
            "fast_service_score": (4, 7),
        },
        "prefs": {"gourmet": 8, "business_dining": 8, "elegant": 8, "wine_focus": 7},
        "description_patterns": [
            "Propuesta {cocina} con enfoque premium y servicio detallado.",
            "{tipo} de nivel alto ideal para cena especial.",
            "Cocina {cocina} refinada en ambiente {ambiente}.",
        ],
        "name_a": ["Atelier", "Casa", "Bistro", "Mesa", "Sello", "Corte", "Patio", "Aurum", "Brasa"],
        "name_b": ["Capital", "Reserva", "Norte", "Selecto", "Vanguardia", "Urbana", "Gran", "Prime", "Alta"],
    },
    {
        "name": "cafe_brunch_bonito",
        "weight": 31,
        "zone_weights": {"Zona 10": 8, "Zona 14": 10, "Zona 15": 36, "Zona 16": 36, "Zona 11": 5, "Zona 5": 5},
        "tier_weights": {"economico": 15, "casual": 60, "premium": 20, "fine": 5},
        "cuisines": ["Cafe", "Saludable", "Mediterranea", "Fusion"],
        "tipos": ["Cafe de Especialidad", "Brunch", "Healthy Kitchen", "Bistro", "Coffee Bar"],
        "ambientes": ["brunch", "trendy", "cozy", "familiar"],
        "score_range": {
            "nightlife_score": (2, 6),
            "social_score": (6, 9),
            "premium_score": (4, 7),
            "comfort_score": (6, 9),
            "aesthetic_score": (7, 10),
            "romantic_score": (4, 8),
            "fast_service_score": (6, 9),
        },
        "prefs": {"coffee_culture": 8, "brunch": 8, "aesthetic": 8, "saludable": 7},
        "description_patterns": [
            "Espacio {ambiente} con cafe y platos ligeros de estilo {cocina}.",
            "Brunch popular en {zona} con enfoque visual y sabor balanceado.",
            "Menu {cocina} pensado para desayunos largos y reuniones casuales.",
        ],
        "name_a": ["Lumen", "Moka", "Ritual", "Casa", "Aroma", "Huerto", "Nido", "Verde", "Masa"],
        "name_b": ["Coffee", "Brunch", "Garden", "Studio", "Bowl", "Taller", "Lab", "Cultura", "Patio"],
    },
    {
        "name": "barrio_casual",
        "weight": 25,
        "zone_weights": {"Zona 10": 6, "Zona 14": 7, "Zona 15": 10, "Zona 16": 10, "Zona 11": 34, "Zona 5": 33},
        "tier_weights": {"economico": 45, "casual": 45, "premium": 10},
        "cuisines": ["Guatemalteca", "Mexicana", "Internacional", "Coreana", "Japonesa"],
        "tipos": ["Comedor", "Taqueria", "Street Food", "Parrilla", "Ramen", "Cantina"],
        "ambientes": ["casual", "familiar", "cozy", "nocturno"],
        "score_range": {
            "nightlife_score": (3, 8),
            "social_score": (6, 9),
            "premium_score": (2, 6),
            "comfort_score": (7, 10),
            "aesthetic_score": (3, 7),
            "romantic_score": (2, 6),
            "fast_service_score": (7, 10),
        },
        "prefs": {"street_food": 8, "comfort_food": 8, "family_friendly": 7, "casual": 8},
        "description_patterns": [
            "Favorito de barrio con cocina {cocina} y servicio rapido.",
            "{tipo} de estilo local para grupos y familia.",
            "Opciones abundantes de {cocina} con ambiente {ambiente}.",
        ],
        "name_a": ["Rincon", "Sabor", "Comal", "Taqueria", "Casa", "Barrio", "Antojitos", "Plaza", "Parrilla"],
        "name_b": ["Chapin", "Popular", "Central", "de Barrio", "de la 5", "de la 11", "Tradicion", "Express", "del Mercado"],
    },
    {
        "name": "social_nocturno",
        "weight": 10,
        "zone_weights": {"Zona 10": 40, "Zona 14": 32, "Zona 15": 10, "Zona 16": 10, "Zona 11": 4, "Zona 5": 4},
        "tier_weights": {"casual": 25, "premium": 55, "fine": 20},
        "cuisines": ["Fusion", "Internacional", "Mexicana", "Asiatica", "Mariscos"],
        "tipos": ["Rooftop", "Gastrobar", "Bistro", "Tapas", "Cantina"],
        "ambientes": ["nocturno", "trendy", "elegante"],
        "score_range": {
            "nightlife_score": (7, 10),
            "social_score": (7, 10),
            "premium_score": (5, 8),
            "comfort_score": (4, 7),
            "aesthetic_score": (7, 10),
            "romantic_score": (4, 7),
            "fast_service_score": (5, 8),
        },
        "prefs": {"nightlife": 9, "rooftop": 8, "lively": 8, "social_grupo": 9},
        "description_patterns": [
            "Lugar {ambiente} para cocteles y platos para compartir.",
            "Concepto social en {zona} con energia nocturna.",
            "{tipo} con cocina {cocina} y ambiente vibrante.",
        ],
        "name_a": ["Luna", "Nube", "Rooftop", "Altura", "Cielo", "Distrito", "Nox", "Mirador", "Horizonte"],
        "name_b": ["Social", "Nights", "Bar", "Lounge", "Urbano", "Club", "Kitchen", "14", "10"],
    },
]


def _weighted_choice(weights: dict[str, int]) -> str:
    options = list(weights)
    values = [weights[item] for item in options]
    return random.choices(options, weights=values, k=1)[0]


def _generate_name(archetype: dict[str, Any], used_names: set[str], zona: str) -> str:
    for _ in range(40):
        a = random.choice(archetype["name_a"])
        b = random.choice(archetype["name_b"])
        maybe_zone = ""
        if random.random() < 0.22:
            maybe_zone = f" {zona.split()[-1]}"
        candidate = f"{a} {b}{maybe_zone}".replace("  ", " ").strip()
        if candidate not in used_names:
            return candidate
    return f"{archetype['name_a'][0]} {archetype['name_b'][0]} {len(used_names)}"


def _make_generated(archetype: dict[str, Any], used_names: set[str]) -> dict[str, Any]:
    zona = _weighted_choice(archetype["zone_weights"])
    price_tier = _weighted_choice(archetype["tier_weights"])
    cocina = random.choice(archetype["cuisines"])
    tipo = random.choice(archetype["tipos"])
    ambiente = random.choice(archetype["ambientes"])
    precio = _price_from_tier(price_tier)
    rating_low = 4.0 if price_tier in {"economico", "casual"} else 4.2
    rating_high = 4.7 if price_tier in {"economico", "casual"} else 4.9
    rating = round(random.uniform(rating_low, rating_high), 1)

    scores: dict[str, Any] = {"cocina": cocina, "ambiente": ambiente, "rating": rating}
    for key, value_range in archetype["score_range"].items():
        scores[key] = random.randint(value_range[0], value_range[1])

    name = _generate_name(archetype, used_names, zona)
    used_names.add(name)
    descripcion = random.choice(archetype["description_patterns"]).format(
        cocina=cocina, tipo=tipo, ambiente=ambiente, zona=zona
    )

    return {
        "id": "",
        "nombre": name,
        "zona": zona,
        "rating": rating,
        "price_tier": price_tier,
        "precio": precio,
        "cocina": cocina,
        "tipo": tipo,
        "ambiente": ambiente,
        "descripcion": descripcion,
        "nightlife_score": scores["nightlife_score"],
        "social_score": scores["social_score"],
        "premium_score": scores["premium_score"],
        "comfort_score": scores["comfort_score"],
        "aesthetic_score": scores["aesthetic_score"],
        "romantic_score": scores["romantic_score"],
        "fast_service_score": scores["fast_service_score"],
        "prefs": _scores_to_prefs(scores, archetype["prefs"]),
    }


def build_catalog(target_count: int = 220) -> list[dict[str, Any]]:
    random.seed(20260528)
    restaurants = [dict(item) for item in CURATED]
    used_names = {item["nombre"] for item in restaurants}

    while len(restaurants) < target_count:
        archetype = random.choices(
            ARCHETYPES, weights=[arch["weight"] for arch in ARCHETYPES], k=1
        )[0]
        restaurants.append(_make_generated(archetype, used_names))

    for idx, restaurant in enumerate(restaurants, start=1):
        restaurant["id"] = f"gc_{idx:03d}"

    return restaurants


RESTAURANTS = build_catalog()
RESTAURANT_COUNT = len(RESTAURANTS)