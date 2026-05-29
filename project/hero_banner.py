"""Hero banner premium para la pantalla de inicio."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from styles import COLORS, FONTS, SPACING
from ui_animations import fade_in


class HeroBanner(tk.Frame):
    """Banner hero con gradiente cálido, tagline y CTA principal."""

    GRADIENT = ("#922B21", "#C0392B", "#D35400", "#E67E22", "#F5B041", "#FDEBD0")

    def __init__(self, master, on_create_profile=None, on_explore=None, **kwargs):
        super().__init__(master, bg=COLORS["bg"], height=248, **kwargs)
        self.pack_propagate(False)
        self._on_create_profile = on_create_profile
        self._on_explore = on_explore

        self.canvas = tk.Canvas(self, height=212, highlightthickness=0, bd=0, bg=COLORS["bg"])
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.canvas.bind("<Configure>", self._draw_gradient)

        overlay_bg = COLORS["hero_overlay"]
        self.overlay = tk.Frame(self.canvas, bg=overlay_bg)
        self._overlay_id = self.canvas.create_window(0, 0, window=self.overlay, anchor=tk.NW)
        self.canvas.bind("<Configure>", self._resize_overlay, add="+")

        inner = tk.Frame(self.overlay, bg=overlay_bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=SPACING["hero_pad_x"], pady=SPACING["hero_pad_y"])

        tk.Label(
            inner,
            text="Descubre tu próxima experiencia gastronómica",
            font=FONTS["hero"],
            fg=COLORS["text"],
            bg=overlay_bg,
            anchor=tk.W,
        ).pack(anchor=tk.W)
        tk.Label(
            inner,
            text="Encuentra lugares que se adapten a tu estilo, mood y gustos.",
            font=FONTS["subtitle"],
            fg=COLORS["subtext"],
            bg=overlay_bg,
            anchor=tk.W,
            wraplength=620,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(10, 6))
        tk.Label(
            inner,
            text="Tu experiencia gastronómica comienza aquí — Ciudad de Guatemala.",
            font=FONTS["small"],
            fg=COLORS["muted"],
            bg=overlay_bg,
            anchor=tk.W,
        ).pack(anchor=tk.W, pady=(0, 22))

        cta_row = tk.Frame(inner, bg=overlay_bg)
        cta_row.pack(anchor=tk.W)
        ttk.Button(
            cta_row,
            text="Crear perfil gastronómico",
            style="Accent.TButton",
            command=self._create_profile,
        ).pack(side=tk.LEFT)
        ttk.Button(
            cta_row,
            text="Explorar recomendaciones",
            style="Secondary.TButton",
            command=self._explore,
        ).pack(side=tk.LEFT, padx=(12, 0))

        self.after(120, lambda: fade_in(inner))

    def _draw_gradient(self, event=None):
        self.canvas.delete("grad")
        w = max(self.canvas.winfo_width(), 400)
        h = max(self.canvas.winfo_height(), 200)
        steps = len(self.GRADIENT)
        band = max(1, w // steps)
        for i, color in enumerate(self.GRADIENT):
            self.canvas.create_rectangle(i * band, 0, (i + 1) * band + 2, h, fill=color, outline=color, tags="grad")
        self.canvas.tag_lower("grad")

    def _resize_overlay(self, event=None):
        w = max(self.canvas.winfo_width() - 16, 300)
        h = max(self.canvas.winfo_height() - 16, 160)
        self.canvas.coords(self._overlay_id, 8, 8)
        self.overlay.configure(width=w, height=h)

    def _create_profile(self):
        if self._on_create_profile:
            self._on_create_profile()

    def _explore(self):
        if self._on_explore:
            self._on_explore()
