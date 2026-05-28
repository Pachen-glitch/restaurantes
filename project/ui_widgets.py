"""Componentes visuales reutilizables para la UI gastronomica."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from styles import COLORS, FONTS, compat_color
from ui_animations import bind_hover_glow


class ShadowCard(tk.Frame):
    """Contenedor con sombra suave y borde redondeado simulado."""

    def __init__(self, master, padx=24, pady=20, shadow=3, **kwargs):
        bg = kwargs.pop("bg", COLORS["surface2"])
        super().__init__(master, bg=COLORS["card_shadow"], **kwargs)
        self.inner = tk.Frame(
            self,
            bg=bg,
            highlightbackground=COLORS["card_border"],
            highlightthickness=1,
            padx=padx,
            pady=pady,
        )
        self.inner.pack(fill=tk.BOTH, expand=True, padx=shadow, pady=shadow)

    def content(self) -> tk.Frame:
        return self.inner


class HomeCard(tk.Frame):
    """Tarjeta de accion rapida para la pantalla de inicio."""

    def __init__(self, master, icon: str, title: str, description: str, action: str, command, **kwargs):
        super().__init__(master, bg=COLORS["bg"], **kwargs)
        self._shadow = ShadowCard(self, padx=22, pady=20, shadow=4)
        self._shadow.pack(fill=tk.BOTH, expand=True)

        card = self._shadow.content()
        tk.Label(card, text=icon, font=("Segoe UI", 30), bg=COLORS["surface2"]).pack(anchor=tk.W)
        tk.Label(
            card,
            text=title,
            font=FONTS["card_title"],
            fg=COLORS["text"],
            bg=COLORS["surface2"],
        ).pack(anchor=tk.W, pady=(10, 6))
        tk.Label(
            card,
            text=description,
            font=FONTS["small"],
            fg=COLORS["muted"],
            bg=COLORS["surface2"],
            wraplength=260,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(0, 16))
        ttk.Button(card, text=action, style="Accent.TButton", command=command).pack(anchor=tk.W)

        for widget in (self, card):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event=None):
        self._shadow.inner.configure(highlightbackground=COLORS["accent2"])

    def _on_leave(self, _event=None):
        self._shadow.inner.configure(highlightbackground=COLORS["card_border"])


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


class CompatRing(tk.Canvas):
    """Anillo de compatibilidad premium."""

    def __init__(self, master, pct: float = 0, size: int = 72, **kwargs):
        super().__init__(master, width=size, height=size, bg=COLORS["surface2"], highlightthickness=0, **kwargs)
        self.pct = max(0.0, min(100.0, float(pct)))
        color = compat_color(self.pct)
        pad = 6
        self.create_oval(pad, pad, size - pad, size - pad, outline=COLORS["progress_bg"], width=8)
        extent = max(1, int(360 * self.pct / 100))
        self.create_arc(pad, pad, size - pad, size - pad, start=90, extent=-extent, outline=color, width=8, style=tk.ARC)
        self.create_text(size // 2, size // 2, text="%.0f%%" % self.pct, fill=color, font=("Segoe UI", 11, "bold"))


class RestaurantCard(tk.Frame):
    """Tarjeta premium estilo app foodie."""

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
        "Francesa": "🥐",
        "Peruana": "🌶️",
        "Saludable": "🥗",
        "Fusion": "✨",
        "Asiatica": "🥢",
    }

    GRADIENT_BANDS = ("#922B21", "#C0392B", "#E67E22", "#F5B041", "#FDEBD0")

    def __init__(self, master, data: dict, pref_labels: dict | None = None, on_select=None, **kwargs):
        super().__init__(master, bg=COLORS["bg"], **kwargs)
        pref_labels = pref_labels or {}
        shadow = ShadowCard(self, padx=0, pady=0, shadow=4)
        shadow.pack(fill=tk.BOTH, expand=True)
        card = shadow.content()
        bind_hover_glow(card, COLORS["card_border"], COLORS["glow"])

        cocinas = data.get("cocinas") or []
        emoji = self.CUISINE_EMOJI.get(cocinas[0] if cocinas else "", "🍽️")
        precio = int(data.get("precio") or 0)
        tier = _price_tier(precio)
        compat = float(data.get("compatibilidad_pct") or data.get("score_total") or 0)
        compat_c = compat_color(compat)

        hero = tk.Canvas(card, height=96, highlightthickness=0, bd=0, bg=COLORS["surface2"])
        hero.pack(fill=tk.X)
        hero.bind("<Configure>", lambda e, c=hero, em=emoji: self._draw_hero(c, em))

        body = tk.Frame(card, bg=COLORS["surface2"], padx=18, pady=14)
        body.pack(fill=tk.X)

        top = tk.Frame(body, bg=COLORS["surface2"])
        top.pack(fill=tk.X)
        info = tk.Frame(top, bg=COLORS["surface2"])
        info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(info, text=data.get("nombre") or "Restaurante", font=FONTS["card_title"], fg=COLORS["text"], bg=COLORS["surface2"], anchor=tk.W).pack(fill=tk.X)
        tk.Label(
            info,
            text="📍 %s   ⭐ %.1f   💎 %s" % (data.get("zona") or "—", float(data.get("rating") or 0), tier),
            font=FONTS["small"],
            fg=COLORS["subtext"],
            bg=COLORS["surface2"],
            anchor=tk.W,
        ).pack(fill=tk.X, pady=(4, 0))
        CompatRing(top, pct=compat).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Label(
            body,
            text="🔥 %.0f%% compatible" % compat,
            font=FONTS["badge"],
            fg=COLORS["text_light"],
            bg=compat_c,
            padx=10,
            pady=3,
        ).pack(anchor=tk.W, pady=(10, 8))

        CompatibilityBar(body, pct=compat).pack(fill=tk.X, pady=(0, 10))

        desc = (data.get("descripcion") or "").strip()
        lines = data.get("explicacion") or []
        quote = ""
        if len(lines) > 1:
            quote = lines[1]
        elif desc:
            quote = desc
        if quote:
            tk.Label(
                body,
                text="“%s”" % quote[:160],
                font=FONTS["body"],
                fg=COLORS["text"],
                bg=COLORS["surface2"],
                wraplength=620,
                justify=tk.LEFT,
            ).pack(fill=tk.X, pady=(0, 8))

        tags = tk.Frame(body, bg=COLORS["surface2"])
        tags.pack(fill=tk.X)
        coincidencias = (data.get("coincidencias") or [])[:5]
        for pref in coincidencias:
            label = pref_labels.get(pref, pref.replace("_", " ").title())
            tk.Label(
                tags,
                text="#%s" % label.replace(" ", ""),
                font=FONTS["badge"],
                fg=COLORS["subtext"],
                bg=COLORS["badge_soft"],
                padx=6,
                pady=2,
            ).pack(side=tk.LEFT, padx=(0, 6), pady=2)
        if cocinas:
            tk.Label(tags, text="#%s" % cocinas[0], font=FONTS["badge"], fg=COLORS["accent"], bg=COLORS["accent_light"], padx=6, pady=2).pack(
                side=tk.LEFT, padx=(0, 6)
            )

        if on_select:
            card.bind("<Button-1>", lambda _e: on_select(data))

    def _draw_hero(self, canvas: tk.Canvas, emoji: str) -> None:
        canvas.delete("all")
        w = max(canvas.winfo_width(), 200)
        h = max(canvas.winfo_height(), 80)
        steps = len(self.GRADIENT_BANDS)
        band = max(1, w // steps)
        for i, color in enumerate(self.GRADIENT_BANDS):
            canvas.create_rectangle(i * band, 0, (i + 1) * band + 1, h, fill=color, outline=color)
        canvas.create_text(w // 2, h // 2, text=emoji, font=("Segoe UI", 36))
        canvas.create_rectangle(0, h - 28, w, h, fill=COLORS["surface2"], outline=COLORS["surface2"])


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
    """Barra lateral de navegacion premium."""

    NAV_ITEMS = [
        ("home", "🏠", "Inicio"),
        ("rec", "✨", "Recomendador"),
        ("profile", "🧬", "ADN Gastronómico"),
        ("insights", "📊", "Insights"),
        ("onboarding", "🧠", "Onboarding"),
        ("graph", "🌐", "Grafo"),
        ("settings", "⚙️", "Config"),
    ]

    def __init__(self, master, on_navigate, **kwargs):
        super().__init__(master, bg=COLORS["sidebar"], width=232, **kwargs)
        self.pack_propagate(False)
        self._on_navigate = on_navigate
        self._buttons: dict[str, tk.Button] = {}
        self._active = "home"

        brand = tk.Frame(self, bg=COLORS["sidebar"], pady=28)
        brand.pack(fill=tk.X, padx=20)
        tk.Label(
            brand,
            text="🍷 Savory",
            font=("Segoe UI", 20, "bold"),
            fg=COLORS["text_light"],
            bg=COLORS["sidebar"],
        ).pack(anchor=tk.W)
        tk.Label(
            brand,
            text="Guatemala City",
            font=FONTS["small"],
            fg=COLORS["muted"],
            bg=COLORS["sidebar"],
        ).pack(anchor=tk.W, pady=(4, 0))

        tk.Frame(self, bg=COLORS["sidebar_hover"], height=1).pack(fill=tk.X, padx=16, pady=(0, 12))

        nav_box = tk.Frame(self, bg=COLORS["sidebar"])
        nav_box.pack(fill=tk.BOTH, expand=True, padx=10)

        for key, icon, label in self.NAV_ITEMS:
            btn = tk.Button(
                nav_box,
                text="%s   %s" % (icon, label),
                font=FONTS["nav"],
                fg=COLORS["text_light"],
                bg=COLORS["sidebar"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["text_light"],
                relief=tk.FLAT,
                anchor=tk.W,
                padx=18,
                pady=13,
                borderwidth=0,
                cursor="hand2",
                command=lambda k=key: self.set_active(k),
            )
            btn.pack(fill=tk.X, pady=3)
            btn.bind("<Enter>", lambda _e, b=btn, k=key: self._hover(b, k))
            btn.bind("<Leave>", lambda _e, b=btn, k=key: self._leave(b, k))
            self._buttons[key] = btn

        self.set_active("home", navigate=False)


    def _hover(self, btn, key):
        if key != self._active:
            btn.configure(bg=COLORS["sidebar_hover"])

    def _leave(self, btn, key):
        if key != self._active:
            btn.configure(bg=COLORS["sidebar"])

    def set_active(self, key: str, navigate: bool = True):
        self._active = key
        for k, btn in self._buttons.items():
            if k == key:
                btn.configure(bg=COLORS["sidebar_active"], font=("Segoe UI", 11, "bold"))
            else:
                btn.configure(bg=COLORS["sidebar"], font=FONTS["nav"])
        if navigate:
            self._on_navigate(key)
