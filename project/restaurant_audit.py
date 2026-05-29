"""
Auditoria semantica del catalogo gastronomico Savory.

Genera CSVs de revision manual sin tocar Neo4j, UI ni recommendation engine.

Uso:
    python restaurant_audit.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any, Callable

from restaurants_guatemala import (
    CANONICAL_OVERRIDES,
    KNOWN_RESTAURANT_LINKS,
    RESTAURANTS,
    SEMANTIC_ARCHETYPES,
    _build_semantic_prefs,
    _detect_semantic_archetype,
    _FAST_FOOD_NAMES,
    normalize_canonical_key,
    validate_restaurant_classification,
)

OUTPUT_DIR = Path(__file__).resolve().parent

# Marcas / restaurantes de alto impacto en recomendaciones y percepcion del usuario.
HIGH_IMPACT_NAMES = {
    "burger_king",
    "wendys",
    "mcdonald_s",
    "china_wok",
    "tre_fratelli",
    "hacienda_real",
    "mercado_24",
    "saul",
    "kacao",
    "ambia",
    "tamarindos",
    "shiro",
    "pollo_campero",
    "starbucks",
    "hard_rock_cafe",
    "outback_steakhouse",
    "chili_s",
    "olive_garden",
    "wok_to_walk",
    "pecorino",
    "monoloco",
    "los_tres_tiempos",
    "frida_kahlo",
    "san_martin",
    "kaffeine",
}


class ContradictionRule:
    __slots__ = ("rule_id", "label", "severity", "check")

    def __init__(self, rule_id: str, label: str, severity: int, check: Callable[[dict], bool]):
        self.rule_id = rule_id
        self.label = label
        self.severity = severity
        self.check = check


def _prefs(r: dict) -> dict[str, int]:
    return dict(r.get("prefs") or {})


def _arch(r: dict) -> str:
    return str(r.get("semantic_archetype") or "")


def _is_burger_chain(r: dict) -> bool:
    name = (r.get("nombre") or "").lower()
    if _arch(r) in {"fast_food", "guatemalteca_fast"}:
        return True
    return any(token in name for token in _FAST_FOOD_NAMES)


def _is_coffee_shop(r: dict) -> bool:
    return r.get("cocina") == "Cafe" or _arch(r) == "cafe_brunch"


def _pref_at_least(r: dict, key: str, minimum: int) -> bool:
    return _prefs(r).get(key, 0) >= minimum


def _build_contradiction_rules() -> list[ContradictionRule]:
    return [
        ContradictionRule("fast_food_premium", "fast_food + premium", 18, lambda r: _pref_at_least(r, "fast_food", 6) and _pref_at_least(r, "premium", 4)),
        ContradictionRule("fast_food_gourmet", "fast_food + gourmet", 18, lambda r: _pref_at_least(r, "fast_food", 6) and _pref_at_least(r, "gourmet", 4)),
        ContradictionRule("burger_chain_italian", "burger_chain + italian", 20, lambda r: _is_burger_chain(r) and _pref_at_least(r, "pref_italiana", 3)),
        ContradictionRule("burger_chain_romantic", "burger_chain + romantic", 15, lambda r: _is_burger_chain(r) and _pref_at_least(r, "romantic", 4)),
        ContradictionRule("burger_chain_wine", "burger_chain + wine_focus", 12, lambda r: _is_burger_chain(r) and _pref_at_least(r, "wine_focus", 4)),
        ContradictionRule("asian_fast_premium", "asian_fast_casual + premium", 16, lambda r: _arch(r) == "asian_fast_casual" and _pref_at_least(r, "premium", 4)),
        ContradictionRule("asian_fast_gourmet", "asian_fast_casual + gourmet", 16, lambda r: _arch(r) == "asian_fast_casual" and _pref_at_least(r, "gourmet", 4)),
        ContradictionRule("asian_fast_italian", "asian_fast + italian", 18, lambda r: _arch(r) == "asian_fast_casual" and _pref_at_least(r, "pref_italiana", 3)),
        ContradictionRule("coffee_nightlife", "coffee_shop + nightlife", 14, lambda r: _is_coffee_shop(r) and _pref_at_least(r, "nightlife", 5)),
        ContradictionRule("brunch_luxury", "brunch + luxury/exclusive", 14, lambda r: _pref_at_least(r, "brunch", 6) and (_pref_at_least(r, "exclusive", 6) or _pref_at_least(r, "gourmet", 7))),
        ContradictionRule("family_exclusive", "family_friendly + exclusive", 12, lambda r: _pref_at_least(r, "family_friendly", 7) and _pref_at_least(r, "exclusive", 6)),
        ContradictionRule("quick_meal_premium", "quick_meal + premium", 15, lambda r: _pref_at_least(r, "quick_meal", 6) and _pref_at_least(r, "premium", 5)),
        ContradictionRule("quick_meal_gourmet", "quick_meal + gourmet", 15, lambda r: _pref_at_least(r, "quick_meal", 6) and _pref_at_least(r, "gourmet", 5)),
        ContradictionRule("economico_exclusive", "price_tier economico + exclusive", 12, lambda r: r.get("price_tier") == "economico" and _pref_at_least(r, "exclusive", 5)),
        ContradictionRule("fast_food_business", "fast_food + business_dining", 12, lambda r: _pref_at_least(r, "fast_food", 6) and _pref_at_least(r, "business_dining", 6)),
        ContradictionRule("italian_premium_fast", "italian_premium + fast_food", 18, lambda r: _arch(r) == "italian_premium" and _pref_at_least(r, "fast_food", 5)),
        ContradictionRule("archetype_price_mismatch_fine", "fine/luxury tier vs casual archetype", 10, lambda r: r.get("price_tier") in {"fine", "luxury"} and _arch(r) in {"fast_food", "asian_fast_casual", "guatemalteca_fast"}),
        ContradictionRule("archetype_price_mismatch_economico", "economico tier vs premium_fine", 10, lambda r: r.get("price_tier") == "economico" and _arch(r) in {"premium_fine", "italian_premium", "steakhouse_premium"}),
    ]


CONTRADICTION_RULES = _build_contradiction_rules()


def _forbidden_pref_violations(r: dict) -> list[str]:
    arch = _arch(r)
    template = SEMANTIC_ARCHETYPES.get(arch, {})
    forbidden = template.get("forbidden", set())
    max_prefs = template.get("max_prefs", {})
    issues: list[str] = []
    prefs = _prefs(r)
    for key in forbidden:
        if prefs.get(key, 0) > 0:
            issues.append("forbidden:%s=%s" % (key, prefs[key]))
    for key, cap in max_prefs.items():
        val = prefs.get(key, 0)
        if val > cap:
            issues.append("cap_exceeded:%s=%s>%s" % (key, val, cap))
    return issues


def detect_inconsistencies(r: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for issue in validate_restaurant_classification(r):
        rows.append({"rule_id": "catalog_validator", "label": issue, "severity": "12"})
    for issue in _forbidden_pref_violations(r):
        rows.append({"rule_id": "archetype_template", "label": issue, "severity": "10"})
    for rule in CONTRADICTION_RULES:
        if rule.check(r):
            rows.append({"rule_id": rule.rule_id, "label": rule.label, "severity": str(rule.severity)})

    # Deriva arquetipo sin overrides curados (solo para comparacion manual).
    detected = _detected_archetype(r)
    canon = r.get("canonical_name") or normalize_canonical_key(r.get("nombre") or "")
    forced = (CANONICAL_OVERRIDES.get(canon) or {}).get("forced_archetype")
    if detected != _arch(r) and not forced:
        rows.append(
            {
                "rule_id": "archetype_drift",
                "label": "arquetipo asignado (%s) != detectado (%s)" % (_arch(r), detected),
                "severity": "5",
            }
        )

    return rows


def semantic_health_score(r: dict) -> tuple[float, list[str]]:
    """
    Puntuacion 0-100 de coherencia semantica.
    100 = totalmente coherente; valores bajos = revision urgente.
    """
    notes: list[str] = []
    score = 100.0

    inconsistencies = detect_inconsistencies(r)
    for inc in inconsistencies:
        if inc.get("rule_id") == "archetype_drift":
            continue
        penalty = float(inc.get("severity") or 10)
        score -= penalty
        notes.append(inc["label"])

    arch = _arch(r)
    template = SEMANTIC_ARCHETYPES.get(arch)
    if not template:
        score -= 25
        notes.append("arquetipo desconocido: %s" % arch)

    # Coherencia arquetipo vs price_tier (suave)
    tier = r.get("price_tier") or ""
    if arch in {"fast_food", "guatemalteca_fast", "asian_fast_casual"} and tier in {"fine", "luxury"}:
        score -= 8
        notes.append("arquetipo rapido con price_tier alto")

    if arch in {"premium_fine", "steakhouse_premium"} and tier == "economico":
        score -= 8
        notes.append("arquetipo premium con price_tier economico")

    # Bonus si coincide con override curado y sin issues duros
    canon = r.get("canonical_name") or normalize_canonical_key(r.get("nombre") or "")
    hard = _hard_issues(inconsistencies)
    if canon in CANONICAL_OVERRIDES and not hard:
        score += 2
        notes.append("override curado aplicado")

    score = max(0.0, min(100.0, round(score, 1)))
    if score >= 90 and not [i for i in inconsistencies if i.get("rule_id") != "archetype_drift"]:
        notes.insert(0, "coherente")
    return score, notes


def _hard_issues(issues: list[dict[str, str]]) -> list[dict[str, str]]:
    return [i for i in issues if i.get("rule_id") != "archetype_drift"]


def _simulate_restaurant_with_archetype(r: dict, archetype: str) -> dict:
    nombre = r.get("nombre") or ""
    cocina = r.get("cocina") or ""
    tipo = r.get("tipo") or ""
    ambiente = r.get("ambiente") or ""
    price_tier = r.get("price_tier") or "casual"
    profile = r.get("price_tier") or "casual"
    if price_tier in {"fine", "luxury"}:
        profile = "luxury" if price_tier == "luxury" else "premium"

    canon = r.get("canonical_name") or normalize_canonical_key(nombre)
    boost = dict(CANONICAL_OVERRIDES.get(canon, {}).get("pref_boost") or {})
    new_arch, _scores, new_prefs = _build_semantic_prefs(
        nombre, cocina, tipo, ambiente, price_tier, profile, boost or None, forced_archetype=archetype
    )
    simulated = dict(r)
    simulated["semantic_archetype"] = new_arch
    simulated["prefs"] = new_prefs
    return simulated


def suggest_archetype(r: dict) -> tuple[str, str]:
    """Devuelve (arquetipo_sugerido, razon). Vacio si no hay cambio recomendado."""
    current = _arch(r)
    nombre = r.get("nombre") or ""
    canon = r.get("canonical_name") or normalize_canonical_key(nombre)

    candidates: list[tuple[str, str]] = []

    if canon in CANONICAL_OVERRIDES:
        forced = CANONICAL_OVERRIDES[canon].get("forced_archetype")
        if forced and forced != current:
            candidates.append((forced, "override curado CANONICAL_OVERRIDES"))

    detected = _detect_semantic_archetype(
        nombre,
        r.get("cocina") or "",
        r.get("tipo") or "",
        r.get("ambiente") or "",
        r.get("price_tier") or "casual",
        "premium" if r.get("price_tier") in {"fine", "luxury"} else "casual",
    )
    if detected != current:
        candidates.append((detected, "deteccion automatica por nombre/tipo/cocina"))

    # Heuristicas de nombre
    name_l = nombre.lower()
    if any(t in name_l for t in _FAST_FOOD_NAMES):
        candidates.insert(0, ("fast_food", "cadena fast food conocida"))
    if "china wok" in name_l or "wok to walk" in name_l:
        candidates.insert(0, ("asian_fast_casual", "cadena asiatica rapida"))
    if r.get("cocina") == "Cafe" and r.get("ambiente") in {"brunch", "cozy"}:
        candidates.append(("cafe_brunch", "cocina cafe + ambiente brunch/cozy"))
    if "bistro" in (r.get("tipo") or "").lower() and r.get("ambiente") == "trendy":
        candidates.append(("fusion_premium", "bistro trendy (alternativa a premium_fine)"))

    # Elegir candidato que maximice health score
    best_arch = ""
    best_reason = ""
    best_score = semantic_health_score(r)[0]

    seen: set[str] = set()
    for arch, reason in candidates:
        if arch in seen or arch == current:
            continue
        seen.add(arch)
        if arch not in SEMANTIC_ARCHETYPES:
            continue
        simulated = _simulate_restaurant_with_archetype(r, arch)
        sc, _ = semantic_health_score(simulated)
        if sc > best_score + 0.5:
            best_score = sc
            best_arch = arch
            best_reason = reason

    # Si health bajo pero ningun candidato, probar detected anyway
    if not best_arch and semantic_health_score(r)[0] < 75 and detected != current:
        return detected, "health bajo; deteccion automatica"

    return best_arch, best_reason


def _format_prefs(prefs: dict[str, int]) -> str:
    if not prefs:
        return ""
    ordered = sorted(prefs.items(), key=lambda x: (-x[1], x[0]))
    return "\n".join("%s=%s" % (k, v) for k, v in ordered)


def _detected_archetype(r: dict) -> str:
    profile = "premium" if r.get("price_tier") in {"fine", "luxury", "premium"} else "casual"
    return _detect_semantic_archetype(
        r.get("nombre") or "",
        r.get("cocina") or "",
        r.get("tipo") or "",
        r.get("ambiente") or "",
        r.get("price_tier") or "casual",
        profile,
    )


def _derive_tags(r: dict) -> str:
    """Tags de display derivados del arquetipo y prefs (solo lectura del catalogo)."""
    prefs = _prefs(r)
    arch = _arch(r)
    tags: list[str] = []

    ranked = sorted(prefs.items(), key=lambda x: -x[1])[:6]
    tag_map = {
        "fast_food": "fastfood",
        "comida_rapida": "quickmeal",
        "quick_meal": "quickmeal",
        "comfort_food": "comfortfood",
        "casual": "casual",
        "pref_italiana": "italiana",
        "asian_fusion": "asiatico",
        "premium": "premium",
        "gourmet": "gourmet",
        "trendy": "trendy",
        "nightlife": "nightlife",
        "pref_guatemalteca": "guatemalteca",
        "pref_japonesa": "japonesa",
        "pref_mexicana": "mexicana",
        "brunch": "brunch",
        "coffee_culture": "coffee",
    }
    template = SEMANTIC_ARCHETYPES.get(arch, {})
    forbidden = template.get("forbidden", set())

    for key, val in ranked:
        if key in forbidden:
            continue
        if arch in {"fast_food", "guatemalteca_fast"} and key in {
            "premium", "gourmet", "pref_italiana", "romantic", "wine_focus", "exclusive"
        }:
            continue
        if arch == "asian_fast_casual" and key in {"premium", "gourmet", "pref_italiana", "romantic"}:
            continue
        tag = tag_map.get(key, key.replace("_", ""))
        if tag not in tags:
            tags.append(tag)

    if arch in {"fast_food", "guatemalteca_fast"}:
        for extra in ("americana", "quickmeal"):
            if extra not in tags:
                tags.insert(min(2, len(tags)), extra)
    if arch == "asian_fast_casual" and "china" not in tags:
        tags.append("china")

    return " | ".join(tags[:8])


def _explanation_preview(r: dict) -> str:
    """Vista previa textual de como se explicaria el restaurante (sin motor de recomendaciones)."""
    arch = _arch(r)
    nombre = r.get("nombre") or "Restaurante"
    prefs = _prefs(r)

    if arch == "fast_food":
        return (
            "%s encaja con perfiles fast food/casual: comida rapida, comfort food, "
            "sin premium ni gourmet." % nombre
        )
    if arch == "asian_fast_casual":
        return (
            "%s encaja con perfiles asiatico rapido/casual: quick meal, asian fusion, "
            "sin premium ni italiano." % nombre
        )
    if arch == "italian_premium":
        return "%s encaja con perfiles italianos premium: cocina italiana, cenas especiales." % nombre
    if arch == "fusion_premium":
        return "%s encaja con perfiles exploradores/trendy: fusion, social, aventura." % nombre
    if arch == "cafe_brunch":
        return "%s encaja con perfiles cafe/brunch: coffee culture, ambiente casual." % nombre

    top = sorted(prefs.items(), key=lambda x: -x[1])[:3]
    if top:
        tops = ", ".join(k.replace("_", " ") for k, _ in top)
        return "%s destacaria por: %s." % (nombre, tops)
    return "%s sin prefs dominantes claras." % nombre


def _impact_priority(r: dict, health: float, issue_count: int) -> float:
    """Mayor = revisar antes."""
    canon = r.get("canonical_name") or normalize_canonical_key(r.get("nombre") or "")
    priority = 0.0
    if canon in HIGH_IMPACT_NAMES:
        priority += 40
    if (r.get("nombre") or "") in KNOWN_RESTAURANT_LINKS:
        priority += 15
    priority += float(r.get("rating") or 0) * 4
    priority += int(r.get("sucursales") or 1) * 3
    priority += len(_prefs(r)) * 1.5
    priority += issue_count * 8
    priority += max(0.0, 100 - health) * 0.6
    return round(priority, 2)


def audit_restaurant(r: dict) -> dict[str, Any]:
    health, health_notes = semantic_health_score(r)
    inconsistencies = detect_inconsistencies(r)
    hard = _hard_issues(inconsistencies)
    suggested_arch, suggest_reason = suggest_archetype(r)
    website = r.get("website_url") or KNOWN_RESTAURANT_LINKS.get(r.get("nombre") or "", {}).get("website_url", "")

    detected = _detected_archetype(r)
    canon = r.get("canonical_name") or normalize_canonical_key(r.get("nombre") or "")
    override_forced = (CANONICAL_OVERRIDES.get(canon) or {}).get("forced_archetype")

    return {
        "id": r.get("id") or "",
        "nombre": r.get("nombre") or "",
        "canonical_name": canon,
        "archetype": _arch(r),
        "detected_archetype": detected,
        "archetype_override": override_forced or "",
        "cocina": r.get("cocina") or "",
        "price_tier": r.get("price_tier") or "",
        "rating": r.get("rating") or "",
        "precio": r.get("precio") or "",
        "zonas_disponibles": ", ".join(r.get("zonas_disponibles") or [r.get("zona") or ""]),
        "sucursales": r.get("sucursales") or 1,
        "prefs": _format_prefs(_prefs(r)),
        "tags": _derive_tags(r),
        "descripcion": (r.get("descripcion") or "").replace("\n", " ")[:500],
        "website": website,
        "health_score": health,
        "health_notes": " | ".join(health_notes[:8]),
        "issue_count": len(hard),
        "review_flags": " | ".join(i["label"] for i in inconsistencies if i.get("rule_id") == "archetype_drift"),
        "inconsistencies": " | ".join(i["label"] for i in hard),
        "explicacion_preview": _explanation_preview(r),
        "suggested_archetype": suggested_arch,
        "suggest_reason": suggest_reason,
        "review_priority": _impact_priority(r, health, len(hard)),
    }


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_audit(output_dir: Path | None = None) -> dict[str, Any]:
    out = output_dir or OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    audits = [audit_restaurant(r) for r in RESTAURANTS]
    inconsistent = [a for a in audits if a["issue_count"] > 0 or a["health_score"] < 90]
    consistent = [a for a in audits if a not in inconsistent]

    # audit_restaurants.csv
    main_fields = [
        "id",
        "nombre",
        "archetype",
        "detected_archetype",
        "archetype_override",
        "cocina",
        "price_tier",
        "zonas_disponibles",
        "prefs",
        "tags",
        "descripcion",
        "website",
        "health_score",
        "explicacion_preview",
    ]
    _write_csv(out / "audit_restaurants.csv", audits, main_fields)

    # audit_inconsistencies.csv
    inc_rows: list[dict] = []
    for a in audits:
        r = next(x for x in RESTAURANTS if x.get("id") == a["id"])
        for inc in detect_inconsistencies(r):
            inc_rows.append(
                {
                    "id": a["id"],
                    "nombre": a["nombre"],
                    "archetype": a["archetype"],
                    "rule_id": inc["rule_id"],
                    "inconsistency": inc["label"],
                    "severity": inc["severity"],
                    "health_score": a["health_score"],
                }
            )
    _write_csv(
        out / "audit_inconsistencies.csv",
        inc_rows,
        ["id", "nombre", "archetype", "rule_id", "inconsistency", "severity", "health_score"],
    )

    # audit_top50.csv
    top50 = sorted(audits, key=lambda x: (-x["review_priority"], x["health_score"]))[:50]
    top_fields = [
        "nombre",
        "archetype",
        "detected_archetype",
        "health_score",
        "issue_count",
        "review_priority",
        "inconsistencies",
        "review_flags",
        "prefs",
        "tags",
        "explicacion_preview",
        "suggested_archetype",
        "suggest_reason",
    ]
    _write_csv(out / "audit_top50.csv", top50, top_fields)

    # recommended_fixes.csv
    fixes = [
        {
            "nombre": a["nombre"],
            "id": a["id"],
            "actual_archetype": a["archetype"],
            "suggested_archetype": a["suggested_archetype"],
            "reason": a["suggest_reason"],
            "health_score_actual": a["health_score"],
            "health_score_if_applied": semantic_health_score(
                _simulate_restaurant_with_archetype(
                    next(x for x in RESTAURANTS if x.get("id") == a["id"]),
                    a["suggested_archetype"],
                )
            )[0]
            if a["suggested_archetype"]
            else a["health_score"],
            "top_issues": a["inconsistencies"],
        }
        for a in audits
        if a["suggested_archetype"] or a["health_score"] < 85
    ]
    fixes.sort(key=lambda x: (x["health_score_actual"], -len(x.get("top_issues") or "")))
    _write_csv(
        out / "recommended_fixes.csv",
        fixes,
        [
            "nombre",
            "id",
            "actual_archetype",
            "suggested_archetype",
            "reason",
            "health_score_actual",
            "health_score_if_applied",
            "top_issues",
        ],
    )

    # Resumen errores por tipo
    error_counts: dict[str, int] = {}
    for row in inc_rows:
        key = row["inconsistency"]
        error_counts[key] = error_counts.get(key, 0) + 1
    top_errors = sorted(error_counts.items(), key=lambda x: -x[1])[:15]

    summary = {
        "total": len(audits),
        "consistent": len(consistent),
        "inconsistent": len(inconsistent),
        "needs_fix_suggestion": len(fixes),
        "top_errors": top_errors,
        "output_dir": str(out),
        "files": [
            "audit_restaurants.csv",
            "audit_inconsistencies.csv",
            "audit_top50.csv",
            "recommended_fixes.csv",
        ],
    }
    return summary


def _print_report(summary: dict[str, Any]) -> None:
    print("")
    print("=" * 60)
    print("  AUDITORIA SEMANTICA - Savory Catalog")
    print("=" * 60)
    print("")
    print("Total restaurantes:     %d" % summary["total"])
    print("Consistentes (>=90):    %d" % summary["consistent"])
    print("Inconsistentes:         %d" % summary["inconsistent"])
    print("Con fix sugerido:       %d" % summary["needs_fix_suggestion"])
    print("")
    print("Archivos generados en:")
    print("  %s" % summary["output_dir"])
    for fname in summary["files"]:
        print("  - %s" % fname)
    print("")
    if summary["top_errors"]:
        print("Top errores semanticos:")
        for label, count in summary["top_errors"]:
            print("  - [%d] %s" % (count, label))
    else:
        print("Top errores semanticos: ninguno detectado")
    print("")
    print("=" * 60)


def main() -> int:
    try:
        summary = run_audit()
        _print_report(summary)
        return 0
    except Exception as exc:
        print("Error en auditoria: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
