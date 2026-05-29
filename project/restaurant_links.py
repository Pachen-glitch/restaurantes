"""Resolucion de URLs externas para restaurantes (web, maps, redes)."""

from __future__ import annotations

import webbrowser

LINK_PRIORITY = ("website_url", "instagram_url", "maps_url", "facebook_url", "search_url")


def pick_primary_restaurant_url(links: dict[str, str], nombre: str = "", zona: str = "") -> str:
    """Elige la mejor URL: web > Instagram > Maps > Facebook > busqueda Google."""
    for key in LINK_PRIORITY:
        url = (links.get(key) or "").strip()
        if url:
            return url
    try:
        from restaurants_guatemala import _google_search_url

        return _google_search_url(nombre, zona)
    except ImportError:
        return ""


def resolve_restaurant_links(nombre: str, zona: str, restaurant_id: str = "") -> dict[str, str]:
    """Obtiene URLs desde el catalogo semantico o genera fallbacks."""
    try:
        from restaurants_guatemala import RESTAURANT_SEMANTIC_INDEX, get_restaurant_links

        meta = RESTAURANT_SEMANTIC_INDEX.get(restaurant_id, {})
        if meta:
            return {
                "website_url": meta.get("website_url") or "",
                "instagram_url": meta.get("instagram_url") or "",
                "facebook_url": meta.get("facebook_url") or "",
                "maps_url": meta.get("maps_url") or "",
                "search_url": meta.get("search_url") or "",
            }
        return get_restaurant_links(nombre, zona)
    except ImportError:
        return {
            "website_url": "",
            "instagram_url": "",
            "facebook_url": "",
            "maps_url": "",
            "search_url": "",
        }


def enrich_restaurant_links(item: dict) -> dict:
    """Agrega URLs y link principal a un resultado de recomendacion."""
    links = resolve_restaurant_links(
        item.get("nombre") or "",
        item.get("zona") or "",
        item.get("id") or "",
    )
    item.update(links)
    item["primary_url"] = pick_primary_restaurant_url(
        links,
        item.get("nombre") or "",
        item.get("zona") or "",
    )
    return item


def open_restaurant_in_browser(item: dict, link_key: str | None = None) -> bool:
    """Abre el navegador con la URL del restaurante."""
    links = enrich_restaurant_links(dict(item))
    if link_key:
        url = (links.get(link_key) or "").strip()
    else:
        url = (links.get("primary_url") or "").strip()
    if not url:
        return False
    webbrowser.open(url)
    return True
