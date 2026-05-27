"""Componentes visuales reutilizables para la UI gastronomica."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from styles import COLORS, FONTS


class ScrollableFrame(ttk.Frame):
    """Contenedor con scroll vertical para listas de cards."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Content.TFrame", **kwargs)
        self.canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas, style="Content.TFrame")

        self.inner.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_canvas_resize(self, event):
        self.canvas.itemconfigure(self._window, width=event.width)

    def _on_mousewheel(self, event):
        if not self.winfo_ismapped():
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()


class CompatibilityBar(tk.Frame):
    """Barra de compatibilidad con porcentaje."""

    def __init__(self, master, pct: float = 0, **kwargs):
        super().__init__(master, bg=COLORS["surface2"], **kwargs)
        self.pct = max(0.0, min(100.0, float(pct)))
        top = tk.Frame(self, bg=COLORS["surface2"])
        top.pack(fill=tk.X)
        tk.Label(
            top,
            text="Compatibilidad",
            font=FONTS["small"],
            fg=COLORS["muted"],
            bg=COLORS["surface2"],
        ).pack(side=tk.LEFT)
        tk.Label(
            top,
            text="%.0f%%" % self.pct,
            font=FONTS["badge"],
            fg=COLORS["accent"],
            bg=COLORS["surface2"],
        ).pack(side=tk.RIGHT)

        bar_bg = tk.Frame(self, bg=COLORS["progress_bg"], height=10)
        bar_bg.pack(fill=tk.X, pady=(4, 0))
        bar_bg.pack_propagate(False)
        fill_w = max(1, int(self.pct))
        self._fill = tk.Frame(bar_bg, bg=COLORS["progress_fill"], width=0, height=10)
        self._fill.place(relx=0, rely=0, relheight=1, relwidth=fill_w / 100.0)


class RestaurantCard(tk.Frame):
    """Tarjeta premium de restaurante recomendado."""

    CUISINE_EMOJI = {
        "Japonesa": "🍣",
        "Italiana": "🍝",
        "Guatemalteca": "🇬🇹",
        "Mexicana": "🌮",
        "Internacional": "🍽️",
        "Coreana": "🇰🇷",
        "Mediterranea": "🫒",
        "Steakhouse": "🥩",
        "Mariscos": "🦐",
        "Cafe": "☕",
    }

    def __init__(
        self,
        master,
        data: dict,
        pref_labels: dict | None = None,
        on_select=None,
        **kwargs,
    ):
        super().__init__(
            master,
            bg=COLORS["surface2"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1,
            padx=18,
            pady=16,
            **kwargs,
        )
        self._data = data
        self._on_select = on_select
        pref_labels = pref_labels or {}

        cocinas = data.get("cocinas") or []
        emoji = self.CUISINE_EMOJI.get(cocinas[0] if cocinas else "", "🍽️")
        precio = int(data.get("precio") or 0)
        tier = _price_tier(precio)
        compat = float(data.get("compatibilidad_pct") or data.get("score_total") or 0)

        header = tk.Frame(self, bg=COLORS["surface2"])
        header.pack(fill=tk.X)
        tk.Label(header, text=emoji, font=("Segoe UI", 28), bg=COLORS["surface2"]).pack(side=tk.LEFT, padx=(0, 12))
        title_box = tk.Frame(header, bg=COLORS["surface2"])
        title_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            title_box,
            text=data.get("nombre") or "Restaurante",
            font=FONTS["card_title"],
            fg=COLORS["text"],
            bg=COLORS["surface2"],
            anchor=tk.W,
        ).pack(fill=tk.X)
        meta = "📍 %s   ⭐ %.1f   💰 %s" % (
            data.get("zona") or "—",
            float(data.get("rating") or 0),
            tier,
        )
        tk.Label(
            title_box,
            text=meta,
            font=FONTS["small"],
            fg=COLORS["subtext"],
            bg=COLORS["surface2"],
            anchor=tk.W,
        ).pack(fill=tk.X, pady=(4, 0))

        badge = tk.Label(
            header,
            text="🔥 %.0f%%" % compat,
            font=FONTS["badge"],
            fg=COLORS["text_light"],
            bg=COLORS["accent"],
            padx=10,
            pady=4,
        )
        badge.pack(side=tk.RIGHT)

        CompatibilityBar(self, pct=compat).pack(fill=tk.X, pady=(12, 8))

        tags_frame = tk.Frame(self, bg=COLORS["surface2"])
        tags_frame.pack(fill=tk.X, pady=(0, 8))
        coincidencias = (data.get("coincidencias") or [])[:4]
        if coincidencias:
            for pref in coincidencias:
                label = pref_labels.get(pref, pref.replace("_", " "))
                tk.Label(
                    tags_frame,
                    text="  %s  " % label,
                    font=FONTS["badge"],
                    fg=COLORS["subtext"],
                    bg=COLORS["badge_soft"],
                    padx=4,
                    pady=2,
                ).pack(side=tk.LEFT, padx=(0, 6), pady=2)

        lines = data.get("explicacion") or []
        if len(lines) > 1:
            tk.Label(
                self,
                text=lines[0],
                font=FONTS["small"],
                fg=COLORS["accent"],
                bg=COLORS["surface2"],
                anchor=tk.W,
            ).pack(fill=tk.X, pady=(4, 2))
            for line in lines[1:4]:
                tk.Label(
                    self,
                    text="• " + line,
                    font=FONTS["small"],
                    fg=COLORS["muted"],
                    bg=COLORS["surface2"],
                    anchor=tk.W,
                    wraplength=520,
                    justify=tk.LEFT,
                ).pack(fill=tk.X, padx=(8, 0))

        self.bind("<Enter>", lambda _e: self.configure(bg=COLORS["card_hover"], highlightbackground=COLORS["accent2"]))
        self.bind("<Leave>", lambda _e: self.configure(bg=COLORS["surface2"], highlightbackground=COLORS["card_border"]))
        if on_select:
            self.bind("<Button-1>", lambda _e: on_select(data))
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda _e: on_select(data))


def _price_tier(precio: int) -> str:
    if precio <= 0:
        return "En casa"
    if precio < 150:
        return "Economico"
    if precio < 350:
        return "Casual"
    if precio < 700:
        return "Premium"
    if precio < 1200:
        return "Fine dining"
    return "Exclusivo"


class Sidebar(tk.Frame):
    """Barra lateral de navegacion."""

    NAV_ITEMS = [
        ("home", "🏠", "Inicio"),
        ("profile", "👤", "Perfil"),
        ("rec", "🍽️", "Recomendador"),
        ("onboarding", "🧠", "Onboarding"),
        ("graph", "📈", "Grafo"),
        ("settings", "⚙️", "Config"),
    ]

    def __init__(self, master, on_navigate, **kwargs):
        super().__init__(master, bg=COLORS["sidebar"], width=220, **kwargs)
        self.pack_propagate(False)
        self._on_navigate = on_navigate
        self._buttons: dict[str, tk.Button] = {}
        self._active = "home"

        tk.Label(
            self,
            text="🍷 Savory",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["text_light"],
            bg=COLORS["sidebar"],
            pady=24,
        ).pack(fill=tk.X)
        tk.Label(
            self,
            text="Guatemala City",
            font=FONTS["small"],
            fg=COLORS["muted"],
            bg=COLORS["sidebar"],
        ).pack(fill=tk.X, pady=(0, 20))

        for key, icon, label in self.NAV_ITEMS:
            btn = tk.Button(
                self,
                text="%s  %s" % (icon, label),
                font=FONTS["nav"],
                fg=COLORS["text_light"],
                bg=COLORS["sidebar"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["text_light"],
                relief=tk.FLAT,
                anchor=tk.W,
                padx=20,
                pady=12,
                borderwidth=0,
                cursor="hand2",
                command=lambda k=key: self.set_active(k),
            )
            btn.pack(fill=tk.X, padx=8, pady=2)
            btn.bind("<Enter>", lambda _e, b=btn, k=key: self._hover(b, k))
            btn.bind("<Leave>", lambda _e, b=btn, k=key: self._leave(b, k))
            self._buttons[key] = btn

        self.set_active("home")

    def _hover(self, btn, key):
        if key != self._active:
            btn.configure(bg=COLORS["sidebar_hover"])

    def _leave(self, btn, key):
        if key != self._active:
            btn.configure(bg=COLORS["sidebar"])

    def set_active(self, key: str):
        self._active = key
        for k, btn in self._buttons.items():
            if k == key:
                btn.configure(bg=COLORS["sidebar_active"], font=("Segoe UI", 11, "bold"))
            else:
                btn.configure(bg=COLORS["sidebar"], font=FONTS["nav"])
        self._on_navigate(key)
