"""Clasificacion gastronomica experta — identidad multicategoria por restaurante canonico."""

from __future__ import annotations

from typing import Any


def _I(
    primary: str,
    secondary: list[str],
    personality: str,
    experience: str,
    premium: int,
    social: int,
    comfort: int,
    exploration: int,
    romantic: int,
    nightlife: int,
    *,
    cocina: str = "",
    ambiente: str = "",
    pref_boost: dict[str, int] | None = None,
    aesthetic: int = 0,
) -> dict[str, Any]:
    return {
        "primary_archetype": primary,
        "secondary_categories": secondary,
        "personality": personality,
        "experience_style": experience,
        "cocina_principal": cocina,
        "ambiente": ambiente,
        "dimensions": {
            "premium": premium,
            "social": social,
            "comfort": comfort,
            "exploration": exploration,
            "romantic": romantic,
            "nightlife": nightlife,
        },
        "pref_boost": pref_boost or {},
        "aesthetic_level": aesthetic,
    }


GASTRONOMIC_IDENTITIES: dict[str, dict[str, Any]] = {
    # --- Prioritarios (revision experta) ---
    "tre_fratelli": _I(
        "italian_premium",
        ["pref_italiana", "wine_focus", "slow_food", "romantic", "business_dining"],
        "Trattoria italiana elegante con alma de casa",
        "Cena italiana clasicamente premium con vino y servicio cuidado",
        8, 7, 6, 5, 8, 4,
        cocina="Italiana", ambiente="elegante",
        pref_boost={"pref_italiana": 10, "wine_focus": 8, "romantic": 8},
    ),
    "pecorino": _I(
        "italian_premium",
        ["pref_italiana", "wine_focus", "slow_food", "romantic", "dinner_experience"],
        "Ristorante de pastas artesanales y cenas largas",
        "Experiencia italiana premium para compartir y disfrutar sin prisa",
        8, 6, 6, 5, 8, 3,
        cocina="Italiana", ambiente="romantico",
        pref_boost={"pref_italiana": 10, "slow_food": 8, "wine_focus": 8},
    ),
    "ambia": _I(
        "asian_fusion_premium",
        ["trendy", "social", "premium", "adventurous", "dinner_experience"],
        "Nikkei peruano audaz con presentacion de autor",
        "Cena social premium con sabores cruzados y propuesta moderna",
        8, 8, 5, 9, 6, 5,
        cocina="Peruana", ambiente="trendy",
        pref_boost={"asian_fusion": 10, "aventurero": 9, "trendy": 9},
    ),
    "tamarindos": _I(
        "premium_fine",
        ["gourmet", "romantic", "exclusive", "elegant", "slow_food"],
        "Fine dining de autor con identidad guatemalteca",
        "Experiencia gastronomica de lujo para ocasiones especiales",
        10, 6, 5, 8, 9, 4,
        cocina="Fusion", ambiente="romantico",
        pref_boost={"gourmet": 10, "exclusive": 8, "romantic": 9},
    ),
    "kacao": _I(
        "guatemalteca_signature",
        ["cultural", "comfort_food", "family_friendly", "traditional", "premium_local"],
        "Alta cocina guatemalteca con orgullo local",
        "Experiencia premium que celebra sabores y tradicion nacional",
        8, 7, 8, 6, 6, 3,
        cocina="Guatemalteca", ambiente="elegante",
        pref_boost={"pref_guatemalteca": 10, "gourmet": 9, "premium": 8},
    ),
    "mercado_24": _I(
        "fusion_premium",
        ["trendy", "social", "nightlife", "adventurous", "foodie"],
        "Food hall vibrante con multiples conceptos",
        "Salida social para probar de todo en ambiente urbano y dinamico",
        7, 9, 6, 9, 4, 8,
        cocina="Internacional", ambiente="trendy",
        pref_boost={"trendy": 10, "social_grupo": 9, "aventurero": 9, "nightlife": 8},
    ),
    "saul": _I(
        "cafe_brunch",
        ["coffee_culture", "aesthetic", "casual", "brunch", "social"],
        "Bistro creativo con alma de cafe y brunch urbano",
        "Brunch aesthetic, cafe de calidad y platos de autor relajados",
        7, 8, 7, 7, 5, 3,
        cocina="Internacional", ambiente="trendy",
        pref_boost={"coffee_culture": 9, "brunch": 9, "aesthetic": 9, "trendy": 8},
        aesthetic=8,
    ),
    "kaffeine": _I(
        "cafe_brunch",
        ["coffee_culture", "aesthetic", "brunch", "casual", "social"],
        "Cafe de especialidad con reposteria cuidada",
        "Brunch y cafe de autor en ambiente luminoso",
        5, 7, 8, 7, 4, 2,
        cocina="Cafe", ambiente="brunch",
        pref_boost={"coffee_culture": 10, "brunch": 9, "aesthetic": 8},
        aesthetic=8,
    ),
    "san_martin": _I(
        "cafe_brunch",
        ["family_friendly", "coffee_culture", "comfort_food", "casual", "bakery"],
        "Panaderia-cafe iconica para toda la familia",
        "Desayuno, pan fresco y comida reconfortante sin pretensiones",
        4, 8, 9, 4, 4, 2,
        cocina="Cafe", ambiente="familiar",
        pref_boost={"family_friendly": 9, "coffee_culture": 8, "comfort_food": 8},
    ),
    "hibachi": _I(
        "japanese_premium",
        ["pref_japonesa", "show_dining", "premium", "social", "business_dining"],
        "Teppanyaki con show en vivo y ambiente sofisticado",
        "Cena japonesa premium con experiencia en plancha",
        8, 8, 5, 6, 5, 4,
        cocina="Japonesa", ambiente="elegante",
        pref_boost={"pref_japonesa": 10, "premium": 8, "business_dining": 8},
    ),
    "bottega_foresto": _I(
        "italian_premium",
        ["trendy", "aesthetic", "wine_focus", "premium", "dinner_experience"],
        "Bistro italiano contemporaneo con barra de vinos",
        "Cena italiana moderna, estetica y maridaje",
        9, 7, 6, 8, 7, 5,
        cocina="Italiana", ambiente="trendy",
        pref_boost={"aesthetic": 9, "trendy": 9, "wine_focus": 8},
        aesthetic=9,
    ),
    "marena": _I(
        "mediterranean_premium",
        ["pref_mediterranea", "saludable", "premium", "elegant", "slow_food"],
        "Mediterraneo refinado con pescado y producto de temporada",
        "Cena elegante con aceite de oliva, mar y vegetales",
        9, 6, 6, 6, 7, 3,
        cocina="Mediterranea", ambiente="elegante",
        pref_boost={"pref_mediterranea": 10, "saludable": 8, "gourmet": 8},
    ),
    "gracia_cocina_de_autor": _I(
        "premium_fine",
        ["gourmet", "exclusive", "cultural", "traditional", "slow_food"],
        "Alta cocina guatemalteca de autor",
        "Experiencia exclusiva con tecnica moderna y raices locales",
        10, 5, 5, 8, 7, 2,
        cocina="Fusion", ambiente="elegante",
        pref_boost={"gourmet": 10, "exclusive": 9, "pref_guatemalteca": 9},
    ),
    "diaca": _I(
        "fusion_premium",
        ["gourmet", "trendy", "cultural", "premium", "dinner_experience"],
        "Cocina de autor guatemalteca con mirada global",
        "Cena creativa premium con identidad local",
        9, 6, 5, 8, 6, 4,
        cocina="Fusion", ambiente="trendy",
        pref_boost={"gourmet": 9, "trendy": 8, "pref_guatemalteca": 8},
    ),
    "atempo": _I(
        "premium_fine",
        ["gourmet", "exclusive", "romantic", "slow_food", "elegant"],
        "Fine dining latinoeuropeo de temporada",
        "Experiencia de lujo con menu degustacion y maridaje",
        10, 5, 5, 7, 9, 3,
        cocina="Fusion", ambiente="elegante",
        pref_boost={"gourmet": 10, "exclusive": 9, "romantic": 8},
    ),
    "shiro": _I(
        "japanese_premium",
        ["pref_japonesa", "gourmet", "premium", "exclusive", "elegant"],
        "Sushi y cocina japonesa de maximo nivel",
        "Experiencia japonesa premium para paladares exigentes",
        10, 5, 4, 7, 7, 3,
        cocina="Japonesa", ambiente="elegante",
        pref_boost={"pref_japonesa": 10, "gourmet": 9, "exclusive": 8},
    ),
    "portal_del_angel": _I(
        "premium_fine",
        ["elegant", "business_dining", "gourmet", "romantic", "wine_focus"],
        "Fine dining internacional en Fontabella",
        "Cena refinada para negocios o ocasion especial",
        9, 6, 5, 5, 8, 4,
        cocina="Internacional", ambiente="elegante",
        pref_boost={"elegant": 9, "business_dining": 8, "gourmet": 8},
    ),
    "los_cebollines": _I(
        "mexican_casual_chain",
        ["pref_mexicana", "family_friendly", "comfort_food", "quick_meal", "casual"],
        "Cadena mexicana guatemalteca accesible y familiar",
        "Comida mexicana rapida para compartir en familia",
        2, 7, 8, 3, 3, 2,
        cocina="Mexicana", ambiente="familiar",
        pref_boost={"pref_mexicana": 10, "family_friendly": 8, "fast_service": 8},
    ),
    "frida_kahlo": _I(
        "mexican_signature",
        ["pref_mexicana", "trendy", "aesthetic", "social", "lively"],
        "Mexicana autentica con diseno vibrante",
        "Cena mexicana premium-festiva con identidad fuerte",
        7, 8, 7, 7, 5, 6,
        cocina="Mexicana", ambiente="trendy",
        pref_boost={"pref_mexicana": 10, "lively": 8, "aesthetic": 8},
        aesthetic=8,
    ),
    "monoloco": _I(
        "nightlife_social",
        ["nightlife", "social", "lively", "craft_beer", "americana"],
        "Bar-restaurante iconico con musica en vivo",
        "Salida nocturna social con comida y ambiente festivo",
        6, 9, 6, 6, 4, 9,
        cocina="Internacional", ambiente="nocturno",
        pref_boost={"nightlife": 9, "lively": 9, "social_grupo": 9},
    ),
    "hard_rock_cafe": _I(
        "nightlife_social",
        ["nightlife", "americana", "social", "lively", "comfort_food"],
        "Cadena rockera con musica en vivo y burgers",
        "Experiencia americana social y nocturna",
        6, 9, 7, 5, 3, 8,
        cocina="Internacional", ambiente="nocturno",
        pref_boost={"nightlife": 8, "lively": 8, "comfort_food": 7},
    ),
    "p_f_chang_s": _I(
        "asian_fusion_premium",
        ["asian_fusion", "business_dining", "premium", "social", "casual"],
        "Cadena asiatica contemporanea premium",
        "Cena asiatica accesible-premium para grupos y negocios",
        7, 7, 6, 6, 4, 4,
        cocina="Asiatica", ambiente="elegante",
        pref_boost={"asian_fusion": 9, "business_dining": 7},
    ),
    "outback_steakhouse": _I(
        "steakhouse_premium",
        ["steakhouse", "family_friendly", "premium", "comfort_food", "casual"],
        "Steakhouse de cadena con cortes generosos",
        "Parrilla americana premium-casual para familia o grupos",
        7, 7, 8, 4, 4, 3,
        cocina="Steakhouse", ambiente="familiar",
        pref_boost={"premium": 8, "family_friendly": 7},
    ),
    "hacienda_real": _I(
        "steakhouse_premium",
        ["steakhouse", "premium", "business_dining", "gourmet", "traditional"],
        "Icono steakhouse guatemalteco con cortes premium",
        "Parrilla de referencia nacional para ocasiones importantes",
        9, 7, 6, 4, 5, 4,
        cocina="Steakhouse", ambiente="elegante",
        pref_boost={"premium": 9, "business_dining": 9, "gourmet": 8},
    ),
    "olive_garden": _I(
        "italian_casual",
        ["pref_italiana", "family_friendly", "comfort_food", "casual", "americana"],
        "Cadena italiana familiar con pastas reconfortantes",
        "Comida italiana casual para salidas en familia",
        4, 7, 8, 3, 4, 2,
        cocina="Italiana", ambiente="familiar",
        pref_boost={"pref_italiana": 8, "family_friendly": 8, "comfort_food": 7},
    ),
    "china_wok": _I(
        "asian_fast_casual",
        ["asian_fusion", "quick_meal", "comfort_food", "casual", "fast_food"],
        "Comida china rapida y accesible",
        "Wok rapido para comer bien sin complicaciones",
        2, 6, 7, 3, 2, 2,
        cocina="Asiatica", ambiente="casual",
        pref_boost={"asian_fusion": 10, "quick_meal": 10},
    ),
    "wok_to_walk": _I(
        "asian_fast_casual",
        ["asian_fusion", "quick_meal", "casual", "street_food", "fast_food"],
        "Wok personalizable de servicio rapido",
        "Comida asiatica walk-and-eat",
        2, 5, 6, 4, 2, 2,
        cocina="Asiatica", ambiente="casual",
        pref_boost={"quick_meal": 10, "fast_service": 10},
    ),
    "burger_king": _I(
        "fast_food",
        ["fast_food", "quick_meal", "comfort_food", "casual", "americana"],
        "Cadena global de hamburguesas",
        "Comida rapida americana sin pretensiones",
        1, 6, 8, 2, 2, 2,
        cocina="Internacional", ambiente="casual",
        pref_boost={"fast_food": 10, "quick_meal": 10, "comfort_food": 9},
    ),
    "wendy_s": _I(
        "fast_food",
        ["fast_food", "quick_meal", "comfort_food", "casual", "americana"],
        "Hamburguesas y frosty de cadena americana",
        "Fast food clasico para comer rapido",
        1, 6, 8, 2, 2, 2,
        cocina="Internacional", ambiente="casual",
        pref_boost={"fast_food": 10, "quick_meal": 10},
    ),
    "mcdonald_s": _I(
        "fast_food",
        ["fast_food", "quick_meal", "family_friendly", "comfort_food", "casual"],
        "Icono global de comida rapida",
        "Opcion rapida universal para cualquier momento",
        1, 7, 8, 2, 2, 2,
        cocina="Internacional", ambiente="familiar",
        pref_boost={"fast_food": 10, "fast_service": 10, "family_friendly": 8},
    ),
    "pollo_campero": _I(
        "guatemalteca_fast",
        ["pref_guatemalteca", "family_friendly", "comfort_food", "quick_meal", "casual"],
        "Icono nacional de pollo frito guatemalteco",
        "Comida rapida con orgullo guatemalteco",
        2, 8, 9, 3, 3, 2,
        cocina="Guatemalteca", ambiente="familiar",
        pref_boost={"pref_guatemalteca": 10, "family_friendly": 9},
    ),
    "taco_bell": _I(
        "fast_food",
        ["pref_mexicana", "quick_meal", "fast_food", "casual", "comfort_food"],
        "Mexicana rapida de cadena internacional",
        "Tacos y burritos fast food",
        1, 6, 7, 3, 2, 2,
        cocina="Internacional", ambiente="casual",
        pref_boost={"fast_food": 10, "quick_meal": 9},
    ),
    "subway": _I(
        "fast_food",
        ["quick_meal", "saludable", "fast_food", "casual", "comfort_food"],
        "Sandwiches personalizables rapidos",
        "Opcion rapida percibida como mas ligera",
        1, 5, 6, 3, 2, 1,
        cocina="Internacional", ambiente="casual",
        pref_boost={"fast_service": 10, "quick_meal": 9},
    ),
    "pizza_hut": _I(
        "fast_food",
        ["comfort_food", "family_friendly", "quick_meal", "casual", "americana"],
        "Pizzeria de cadena internacional",
        "Pizza familiar rapida",
        2, 7, 8, 2, 3, 2,
        cocina="Internacional", ambiente="familiar",
        pref_boost={"comfort_food": 8, "family_friendly": 8, "fast_service": 8},
    ),
    "domino_s_pizza": _I(
        "fast_food",
        ["quick_meal", "comfort_food", "fast_food", "casual", "family_friendly"],
        "Pizza a domicilio y local rapido",
        "Pizza comoda para compartir en casa o local",
        2, 6, 8, 2, 3, 2,
        cocina="Internacional", ambiente="casual",
        pref_boost={"fast_service": 10, "quick_meal": 9},
    ),
    "papa_john_s": _I(
        "fast_food",
        ["quick_meal", "comfort_food", "casual", "family_friendly", "americana"],
        "Pizza delivery de cadena",
        "Pizza americana para compartir",
        2, 6, 8, 2, 3, 2,
        cocina="Internacional", ambiente="casual",
        pref_boost={"fast_service": 9, "comfort_food": 7},
    ),
    "little_caesars": _I(
        "fast_food",
        ["quick_meal", "fast_food", "comfort_food", "family_friendly", "casual"],
        "Pizza rapida economica",
        "Pizza lista para llevar sin espera",
        1, 6, 7, 2, 2, 2,
        cocina="Internacional", ambiente="familiar",
        pref_boost={"fast_service": 10, "quick_meal": 9},
    ),
    "starbucks": _I(
        "cafe_brunch",
        ["coffee_culture", "casual", "aesthetic", "social", "comfort_food"],
        "Cafe de cadena global con ritual diario",
        "Cafe, reposteria y pausa social",
        4, 7, 7, 5, 3, 3,
        cocina="Cafe", ambiente="casual",
        pref_boost={"coffee_culture": 9, "casual": 8},
    ),
    "barista": _I(
        "cafe_brunch",
        ["coffee_culture", "aesthetic", "casual", "social", "trendy"],
        "Cafe de especialidad guatemalteco",
        "Espresso de calidad en ambiente urbano",
        5, 7, 7, 6, 3, 2,
        cocina="Cafe", ambiente="trendy",
        pref_boost={"coffee_culture": 10, "aesthetic": 7},
        aesthetic=7,
    ),
    "cafe_leon": _I(
        "cafe_brunch",
        ["coffee_culture", "comfort_food", "casual", "traditional", "family_friendly"],
        "Cafe tradicional guatemalteco con panes frescos",
        "Desayuno hogareño y cafe de barrio",
        3, 6, 9, 3, 4, 2,
        cocina="Cafe", ambiente="cozy",
        pref_boost={"coffee_culture": 9, "comfort_food": 8},
    ),
    "dunkin": _I(
        "cafe_brunch",
        ["coffee_culture", "quick_meal", "casual", "comfort_food", "dessert"],
        "Cafe y donas rapidas de cadena",
        "Pausa dulce y cafe sin complicaciones",
        2, 5, 7, 2, 2, 2,
        cocina="Cafe", ambiente="casual",
        pref_boost={"coffee_culture": 7, "fast_service": 9},
    ),
    "sarita": _I(
        "cafe_brunch",
        ["dessert", "family_friendly", "comfort_food", "casual", "traditional"],
        "Heladeria iconica guatemalteca",
        "Postre familiar y tradicion dulce local",
        2, 7, 8, 2, 3, 2,
        cocina="Cafe", ambiente="familiar",
        pref_boost={"family_friendly": 9, "comfort_food": 7},
    ),
    "de_cero": _I(
        "healthy_casual",
        ["saludable", "healthy_fast", "quick_meal", "casual", "aesthetic"],
        "Ensaladas y bowls personalizables frescos",
        "Comida saludable rapida y customizable",
        4, 5, 6, 5, 2, 1,
        cocina="Saludable", ambiente="casual",
        pref_boost={"saludable": 10, "fast_service": 8},
    ),
    # --- Resto del catalogo ---
    "45_grados": _I(
        "steakhouse_premium", ["steakhouse", "premium", "gourmet", "business_dining", "elegant"],
        "Parrilla con tecnicas de coccion precisas", "Steakhouse premium para carnivoros exigentes",
        8, 6, 5, 4, 5, 3, cocina="Steakhouse", ambiente="elegante",
    ),
    "anadi2": _I(
        "fusion_premium", ["trendy", "social", "adventurous", "casual", "foodie"],
        "Bistro fusion para compartir", "Platos creativos en ambiente moderno",
        7, 8, 6, 8, 4, 5, cocina="Fusion", ambiente="trendy",
    ),
    "animal_gastro_bar": _I(
        "nightlife_social", ["nightlife", "trendy", "craft_beer", "social", "foodie"],
        "Gastrobar creativo con cocteleria", "Salida nocturna con propuesta gastronomica",
        6, 8, 5, 7, 3, 8, cocina="Internacional", ambiente="nocturno",
    ),
    "applebee_s": _I(
        "american_casual_chain", ["family_friendly", "comfort_food", "casual", "americana", "social"],
        "Cadena americana casual para grupos", "Comida americana reconfortante en familia",
        3, 7, 8, 3, 3, 4, cocina="Internacional", ambiente="familiar",
    ),
    "bento_box": _I(
        "asian_fast_casual", ["pref_japonesa", "quick_meal", "casual", "comfort_food", "fast_food"],
        "Bento japones rapido", "Comida japonesa accesible para llevar",
        2, 5, 6, 4, 2, 2, cocina="Japonesa", ambiente="casual",
    ),
    "bisque": _I(
        "french_bistro", ["gourmet", "elegant", "slow_food", "romantic", "wine_focus"],
        "Bistro frances con sopas y pescados clasicos", "Cena francesa refinada",
        8, 5, 5, 5, 7, 3, cocina="Francesa", ambiente="elegante",
    ),
    "caffe_milano": _I(
        "cafe_brunch", ["coffee_culture", "pref_italiana", "casual", "aesthetic", "social"],
        "Cafe italiano con pastas ligeras", "Espresso y cocina italiana casual",
        6, 6, 7, 5, 5, 3, cocina="Italiana", ambiente="elegante",
    ),
    "casa_chapina": _I(
        "guatemalteca_signature", ["pref_guatemalteca", "traditional", "family_friendly", "comfort_food", "cultural"],
        "Comida guatemalteca tradicional en Cayala", "Sabores chapinos en ambiente acogedor",
        6, 7, 8, 4, 4, 2, cocina="Guatemalteca", ambiente="familiar",
    ),
    "casa_escobar": _I(
        "steakhouse_premium", ["steakhouse", "premium", "traditional", "business_dining", "gourmet"],
        "Tradicion steakhouse guatemalteca", "Parrilla clasica con cortes premium",
        8, 6, 6, 3, 5, 3, cocina="Steakhouse", ambiente="elegante",
    ),
    "cerveceria_14": _I(
        "nightlife_social", ["craft_beer", "nightlife", "social", "casual", "lively"],
        "Cerveceria social en Zona 14", "Cerveza artesanal y ambiente relajado",
        4, 8, 6, 5, 3, 7, cocina="Internacional", ambiente="nocturno",
    ),
    "chili_s": _I(
        "american_casual_chain", ["family_friendly", "comfort_food", "casual", "americana", "social"],
        "Cadena americana de burgers y ribs", "Comida americana casual para grupos",
        4, 7, 8, 3, 3, 4, cocina="Internacional", ambiente="familiar",
    ),
    "cielito_lindo": _I(
        "mexican_casual_chain", ["pref_mexicana", "family_friendly", "comfort_food", "casual", "traditional"],
        "Mexicana tradicional colorida", "Comida mexicana accesible y festiva",
        3, 7, 8, 4, 3, 3, cocina="Mexicana", ambiente="familiar",
    ),
    "cinnabon": _I(
        "cafe_brunch", ["dessert", "comfort_food", "casual", "quick_meal", "family_friendly"],
        "Reposteria dulce de mall", "Rollos de canela y cafe dulce",
        2, 5, 7, 2, 2, 2, cocina="Cafe", ambiente="casual",
    ),
    "comida_china_moon": _I(
        "asian_fast_casual", ["asian_fusion", "family_friendly", "comfort_food", "casual", "quick_meal"],
        "Buffet chino accesible", "Comida china abundante para compartir",
        2, 7, 7, 3, 2, 2, cocina="Asiatica", ambiente="familiar",
    ),
    "del_griego": _I(
        "mediterranean_premium", ["pref_mediterranea", "saludable", "premium", "elegant", "slow_food"],
        "Identidad griega mediterranea", "Sabores del Egeo con elegancia",
        7, 6, 6, 5, 6, 3, cocina="Mediterranea", ambiente="elegante",
    ),
    "del_principe": _I(
        "italian_premium", ["pref_italiana", "wine_focus", "elegant", "romantic", "slow_food"],
        "Italiana clasica refinada", "Cena italiana con servicio formal",
        8, 5, 6, 4, 7, 3, cocina="Italiana", ambiente="elegante",
    ),
    "denny_s": _I(
        "american_casual_chain", ["comfort_food", "quick_meal", "family_friendly", "casual", "americana"],
        "Diner americano 24 horas", "Comida reconfortante a cualquier hora",
        2, 6, 8, 2, 3, 3, cocina="Internacional", ambiente="familiar",
    ),
    "dumbo": _I(
        "fusion_premium", ["trendy", "aesthetic", "casual", "social", "adventurous"],
        "Bistro internacional relajado", "Propuesta moderna sin formalidad",
        6, 7, 7, 7, 4, 4, cocina="Internacional", ambiente="trendy",
    ),
    "el_adobe": _I(
        "guatemalteca_signature", ["pref_guatemalteca", "traditional", "comfort_food", "family_friendly", "cultural"],
        "Sabores chapinos en ambiente rustico", "Guatemalteca acogedora y tradicional",
        6, 7, 9, 4, 5, 2, cocina="Guatemalteca", ambiente="familiar",
    ),
    "el_arte_steak_house": _I(
        "steakhouse_premium", ["steakhouse", "premium", "business_dining", "elegant", "gourmet"],
        "Steakhouse formal con cortes selectos", "Parrilla premium de servicio cuidado",
        9, 6, 5, 4, 5, 3, cocina="Steakhouse", ambiente="elegante",
    ),
    "el_invernadero": _I(
        "healthy_casual", ["saludable", "aesthetic", "trendy", "brunch", "casual"],
        "Cocina vegetal organica luminosa", "Saludable, fresca y fotogenica",
        5, 6, 6, 7, 3, 2, cocina="Saludable", ambiente="trendy", aesthetic=8,
    ),
    "eskimo": _I(
        "cafe_brunch", ["dessert", "family_friendly", "comfort_food", "traditional", "casual"],
        "Helados tradicion guatemalteca", "Postre familiar de siempre",
        2, 7, 8, 2, 3, 2, cocina="Cafe", ambiente="familiar",
    ),
    "estacion_santo_domingo": _I(
        "fusion_premium", ["elegant", "wine_focus", "premium", "romantic", "dinner_experience"],
        "Bistro internacional en entorno historico", "Cena elegante con contexto patrimonial",
        8, 6, 6, 5, 7, 4, cocina="Internacional", ambiente="elegante",
    ),
    "fiore_pasta_bar": _I(
        "italian_casual", ["pref_italiana", "trendy", "casual", "social", "aesthetic"],
        "Pastas frescas en barra abierta", "Italiana casual moderna",
        5, 7, 7, 6, 4, 3, cocina="Italiana", ambiente="trendy",
    ),
    "fiorellino": _I(
        "italian_casual", ["pref_italiana", "comfort_food", "casual", "family_friendly", "cozy"],
        "Pastas y pizzas acogedoras", "Italiana de barrio calida",
        4, 6, 8, 3, 5, 2, cocina="Italiana", ambiente="cozy",
    ),
    "gramo": _I(
        "fusion_premium", ["trendy", "casual", "adventurous", "social", "foodie"],
        "Bistro contemporaneo accesible", "Autor accesible con espiritu urbano",
        6, 7, 6, 7, 4, 4, cocina="Internacional", ambiente="trendy",
    ),
    "gusta": _I(
        "healthy_casual", ["saludable", "brunch", "casual", "aesthetic", "quick_meal"],
        "Bowls y opciones frescas", "Saludable rapido para el dia a dia",
        4, 5, 6, 5, 2, 1, cocina="Saludable", ambiente="brunch",
    ),
    "ihop": _I(
        "cafe_brunch", ["brunch", "family_friendly", "comfort_food", "casual", "americana"],
        "Desayunos y pancakes todo el dia", "Brunch americano familiar",
        3, 7, 8, 3, 3, 2, cocina="Internacional", ambiente="familiar",
    ),
    "il_forno": _I(
        "italian_casual", ["pref_italiana", "family_friendly", "comfort_food", "casual", "traditional"],
        "Pizza al horno de lena familiar", "Italiana rustica para compartir",
        4, 7, 8, 3, 4, 2, cocina="Italiana", ambiente="familiar",
    ),
    "isabelle": _I(
        "french_bistro", ["elegant", "romantic", "wine_focus", "gourmet", "dinner_experience"],
        "Bistro frances con postres y vinos", "Francesa romantica y refinada",
        8, 5, 6, 5, 8, 3, cocina="Francesa", ambiente="romantico",
    ),
    "jake_s": _I(
        "nightlife_social", ["nightlife", "craft_beer", "social", "trendy", "foodie"],
        "Gastrobar con cocteleria creativa", "Noche social con platos para compartir",
        6, 8, 5, 7, 3, 8, cocina="Internacional", ambiente="nocturno",
    ),
    "kfc": _I(
        "fast_food", ["fast_food", "quick_meal", "family_friendly", "comfort_food", "americana"],
        "Pollo frito de cadena global", "Fast food de pollo para todos",
        2, 7, 7, 2, 2, 2, cocina="Internacional", ambiente="familiar",
    ),
    "l_oliveto": _I(
        "italian_premium", ["pref_italiana", "slow_food", "romantic", "traditional", "wine_focus"],
        "Italiana tradicional con oliva y pasta fresca", "Cena italiana autentica y pausada",
        7, 5, 7, 4, 8, 3, cocina="Italiana", ambiente="romantico",
    ),
    "la_estancia": _I(
        "steakhouse_premium", ["steakhouse", "premium", "business_dining", "elegant", "traditional"],
        "Parrilla clasica para ocasiones especiales", "Steakhouse de referencia",
        8, 6, 5, 3, 5, 3, cocina="Steakhouse", ambiente="elegante",
    ),
    "la_finka": _I(
        "guatemalteca_signature", ["pref_guatemalteca", "trendy", "cultural", "comfort_food", "casual"],
        "Guatemalteca contemporanea urbana", "Tradicion chapina con mirada moderna",
        6, 7, 7, 6, 4, 3, cocina="Guatemalteca", ambiente="trendy",
    ),
    "la_pampa": _I(
        "steakhouse_premium", ["steakhouse", "premium", "gourmet", "traditional", "social"],
        "Parrilla argentina con empanadas", "Asado y carnes con espiritu porteno",
        8, 7, 6, 4, 4, 4, cocina="Steakhouse", ambiente="elegante",
    ),
    "la_veinte": _I(
        "mexican_signature", ["pref_mexicana", "lively", "trendy", "social", "nightlife"],
        "Mexicana contemporanea festiva", "Cena mexicana con energia y diseno",
        7, 8, 6, 6, 4, 7, cocina="Mexicana", ambiente="trendy",
    ),
    "le_crepe": _I(
        "cafe_brunch", ["brunch", "romantic", "comfort_food", "casual", "aesthetic"],
        "Creperie parisina acogedora", "Crepes dulces y salados en ambiente cozy",
        4, 5, 8, 5, 7, 2, cocina="Francesa", ambiente="cozy",
    ),
    "los_tres_tiempos": _I(
        "guatemalteca_signature", ["pref_guatemalteca", "traditional", "comfort_food", "family_friendly", "premium_local"],
        "Guatemalteca moderna con porciones generosas", "Tradicion chapina bien ejecutada",
        7, 7, 8, 5, 5, 3, cocina="Guatemalteca", ambiente="familiar",
    ),
    "mansion_del_rio": _I(
        "premium_fine", ["hotel_dining", "elegant", "romantic", "gourmet", "business_dining"],
        "Restaurante de hotel con vista", "Internacional refinada en contexto hotelero",
        9, 5, 5, 5, 8, 4, cocina="Internacional", ambiente="elegante",
    ),
    "mantarraya": _I(
        "mediterranean_premium", ["seafood", "gourmet", "romantic", "elegant", "slow_food"],
        "Mariscos frescos y ceviches", "Mar y pescado en ambiente sofisticado",
        8, 6, 5, 5, 7, 3, cocina="Mariscos", ambiente="elegante",
    ),
    "milagrito": _I(
        "nightlife_social", ["pref_mexicana", "nightlife", "lively", "social", "casual"],
        "Cantina mexicana festiva", "Noche mexicana con tequila y ambiente",
        4, 8, 6, 5, 3, 8, cocina="Mexicana", ambiente="nocturno",
    ),
    "nifu_nifa": _I(
        "asian_fast_casual", ["asian_fusion", "casual", "comfort_food", "family_friendly", "quick_meal"],
        "Dim sum cantones casual", "Comida china para compartir sin formalidad",
        3, 7, 7, 4, 2, 2, cocina="Asiatica", ambiente="casual",
    ),
    "nikkei": _I(
        "asian_fusion_premium", ["asian_fusion", "adventurous", "trendy", "premium", "dinner_experience"],
        "Nikkei peruano-japones reconocido", "Fusion audaz de alto nivel",
        8, 7, 5, 9, 5, 5, cocina="Peruana", ambiente="trendy",
    ),
    "nuestra_cerveceria": _I(
        "nightlife_social", ["craft_beer", "social", "nightlife", "casual", "foodie"],
        "Cerveza artesanal guatemalteca", "Brewpub local con platos para compartir",
        4, 9, 6, 6, 3, 7, cocina="Internacional", ambiente="nocturno",
    ),
    "paisano": _I(
        "italian_casual", ["pref_italiana", "comfort_food", "family_friendly", "casual", "traditional"],
        "Trattoria italiana accesible", "Italiana de barrio para toda la familia",
        4, 7, 8, 3, 4, 2, cocina="Italiana", ambiente="familiar",
    ),
    "paligo": _I(
        "fusion_premium", ["business_dining", "elegant", "premium", "wine_focus", "dinner_experience"],
        "Bistro internacional formal", "Carta variada con servicio cuidado",
        7, 6, 5, 4, 5, 4, cocina="Internacional", ambiente="elegante",
    ),
    "porcino": _I(
        "steakhouse_premium", ["steakhouse", "premium", "gourmet", "business_dining", "elegant"],
        "Cortes premium con alma italiana", "Steakhouse de lujo en Cayala",
        9, 6, 5, 4, 5, 3, cocina="Italiana", ambiente="elegante",
    ),
    "punto_mediterraneo": _I(
        "mediterranean_premium", ["pref_mediterranea", "seafood", "saludable", "elegant", "slow_food"],
        "Mediterraneo con pescados y pastas", "Mar, oliva y sabores del sur",
        7, 6, 6, 5, 6, 3, cocina="Mediterranea", ambiente="elegante",
    ),
    "renata": _I(
        "cafe_brunch", ["dessert", "coffee_culture", "family_friendly", "aesthetic", "comfort_food"],
        "Pasteleria fina en Cayala", "Reposteria artesanal y cafe",
        5, 7, 8, 5, 4, 2, cocina="Cafe", ambiente="familiar",
    ),
    "rincon_del_steak": _I(
        "steakhouse_premium", ["steakhouse", "premium", "business_dining", "comfort_food", "traditional"],
        "Parrilla reconocida para carnivoros", "Carne como protagonista",
        7, 6, 6, 3, 4, 3, cocina="Steakhouse", ambiente="elegante",
    ),
    "rustica": _I(
        "italian_casual", ["pref_italiana", "comfort_food", "family_friendly", "casual", "traditional"],
        "Pizza rustica al lena", "Italiana sencilla y honesta",
        4, 6, 8, 3, 3, 2, cocina="Italiana", ambiente="familiar",
    ),
    "saint_honore": _I(
        "french_bistro", ["aesthetic", "elegant", "dessert", "premium", "slow_food"],
        "Pasteleria francesa y platos ligeros", "Francesa dulce y refinada",
        6, 6, 7, 6, 5, 3, cocina="Francesa", ambiente="elegante", aesthetic=8,
    ),
    "sublime": _I(
        "premium_fine", ["gourmet", "romantic", "exclusive", "slow_food", "wine_focus"],
        "Experiencia de autor con maridaje", "Fine dining para paladares exigentes",
        10, 5, 5, 7, 9, 3, cocina="Fusion", ambiente="romantico",
    ),
    "tablon_del_8": _I(
        "steakhouse_premium", ["steakhouse", "premium", "business_dining", "gourmet", "elegant"],
        "Parrilla de alto nivel", "Steakhouse premium de referencia",
        9, 6, 5, 4, 5, 3, cocina="Steakhouse", ambiente="elegante",
    ),
    "tgi_friday_s": _I(
        "nightlife_social", ["nightlife", "lively", "americana", "social", "casual"],
        "Bar-restaurante americano festivo", "Noche americana con ambiente animado",
        4, 8, 7, 4, 3, 7, cocina="Internacional", ambiente="nocturno",
    ),
    "tip_top": _I(
        "guatemalteca_fast", ["pref_guatemalteca", "comfort_food", "family_friendly", "quick_meal", "casual"],
        "Cadena guatemalteca de comida rapida tradicional", "Rapido con sabor local",
        2, 7, 8, 3, 3, 2, cocina="Internacional", ambiente="familiar",
    ),
    "tony_roma_s": _I(
        "american_casual_chain", ["comfort_food", "family_friendly", "americana", "casual", "social"],
        "Costillas BBQ iconicas", "Americana reconfortante de cadena",
        4, 7, 8, 3, 3, 4, cocina="Internacional", ambiente="familiar",
    ),
    "tul_y_tul": _I(
        "fusion_premium", ["romantic", "elegant", "premium", "social", "dinner_experience"],
        "Bistro con terraza refinada", "Internacional romantica al aire libre",
        8, 6, 6, 5, 8, 4, cocina="Internacional", ambiente="romantico",
    ),
    "zest": _I(
        "fusion_premium", ["trendy", "aesthetic", "adventurous", "casual", "foodie"],
        "Internacional con toques citricos", "Bistro urbano fresco y moderno",
        6, 7, 6, 7, 4, 4, cocina="Internacional", ambiente="trendy",
    ),
}


def derive_identity_fallback(restaurant: dict) -> dict[str, Any]:
    """Fallback humanizado cuando no hay entrada experta explicita."""
    from restaurants_guatemala import _detect_semantic_archetype

    nombre = restaurant.get("nombre") or ""
    cocina = restaurant.get("cocina") or ""
    tipo = restaurant.get("tipo") or ""
    ambiente = restaurant.get("ambiente") or "casual"
    price_tier = restaurant.get("price_tier") or "casual"
    profile = "premium" if price_tier in {"fine", "luxury", "premium"} else "casual"
    primary = _detect_semantic_archetype(nombre, cocina, tipo, ambiente, price_tier, profile)

    secondary: list[str] = ["casual"]
    if ambiente == "trendy":
        secondary = ["trendy", "social", "aesthetic", "casual", "adventurous"]
    elif ambiente == "elegante":
        secondary = ["elegant", "premium", "dinner_experience", "slow_food", "business_dining"]
    elif ambiente == "romantico":
        secondary = ["romantic", "elegant", "slow_food", "premium", "dinner_experience"]
    elif ambiente == "nocturno":
        secondary = ["nightlife", "social", "lively", "craft_beer", "casual"]
    elif ambiente == "familiar":
        secondary = ["family_friendly", "comfort_food", "casual", "social", "traditional"]
    elif ambiente == "brunch":
        secondary = ["brunch", "coffee_culture", "aesthetic", "casual", "social"]
    elif ambiente == "cozy":
        secondary = ["comfort_food", "casual", "romantic", "traditional", "social"]

    cuisine_cat = {
        "Italiana": "pref_italiana",
        "Guatemalteca": "pref_guatemalteca",
        "Mexicana": "pref_mexicana",
        "Japonesa": "pref_japonesa",
        "Mediterranea": "pref_mediterranea",
        "Asiatica": "asian_fusion",
        "Francesa": "gourmet",
        "Steakhouse": "steakhouse",
        "Cafe": "coffee_culture",
        "Saludable": "saludable",
        "Peruana": "asian_fusion",
    }.get(cocina)
    if cuisine_cat and cuisine_cat not in secondary:
        secondary.insert(0, cuisine_cat)

    dims = {
        "premium": {"economico": 2, "casual": 4, "premium": 7, "fine": 9, "luxury": 10}.get(price_tier, 5),
        "social": 6,
        "comfort": 7 if ambiente in {"familiar", "cozy", "casual"} else 5,
        "exploration": 6 if ambiente == "trendy" else 4,
        "romantic": 7 if ambiente == "romantico" else 4,
        "nightlife": 7 if ambiente == "nocturno" else 3,
    }

    return _I(
        primary,
        secondary[:5],
        "%s en Guatemala" % nombre,
        "Experiencia %s en ambiente %s" % (cocina.lower() or "gastronomica", ambiente),
        dims["premium"],
        dims["social"],
        dims["comfort"],
        dims["exploration"],
        dims["romantic"],
        dims["nightlife"],
        cocina=cocina,
        ambiente=ambiente,
    )
