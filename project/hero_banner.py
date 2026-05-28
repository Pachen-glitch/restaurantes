"""Hero banner premium para la pantalla de inicio."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from styles import COLORS, FONTS
from ui_animations import fade_in


class HeroBanner(tk.Frame):
    """Banner hero con gradiente cálido, tagline y CTA principal."""

    GRADIENT = ("#922B21", "#C0392B", "#D35400", "#E67E22", "#F5B041", "#FDEBD0")

    def __init__(self, master, on_explore=None, **kwargs):
        super().__init__(master, bg=COLORS["bg"], height=240, **kwargs)
        self.pack_propagate(False)
        self._on_explore = on_explore

        self.canvas = tk.Canvas(self, height=220, highlightthickness=0, bd=0, bg=COLORS["bg"])
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.canvas.bind("<Configure>", self._draw_gradient)

        self.overlay = tk.Frame(self.canvas, bg="#FFFFFF")
        self._overlay_id = self.canvas.create_window(0, 0, window=self.overlay, anchor=tk.NW)
        self.canvas.bind("<Configure>", self._resize_overlay, add="+")

        inner = tk.Frame(self.overlay, bg="#FFFFFF")
        inner.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        tk.Label(
            inner,
            text="Descubre tu próxima experiencia gastronómica",
            font=("Segoe UI", 24, "bold"),
            fg=COLORS["text"],
            bg="#FFFFFF",
            anchor=tk.W,
        ).pack(anchor=tk.W)
        tk.Label(
            inner,
            text="IA culinaria personalizada para Ciudad de Guatemala",
            font=FONTS["body"],
            fg=COLORS["subtext"],
            bg="#FFFFFF",
            anchor=tk.W,
        ).pack(anchor=tk.W, pady=(8, 18))

        row = tk.Frame(inner, bg="#FFFFFF")
        row.pack(anchor=tk.W)
        cta = ttk.Button(row, text="✨  Explorar recomendaciones", style="Accent.TButton", command=self._explore)
        cta.pack(side=tk.LEFT)
        tk.Label(
            row,
            text="220+ restaurantes curados · Perfil IA · Mood del día",
            font=FONTS["small"],
            fg=COLORS["muted"],
            bg="#FFFFFF",
        ).pack(side=tk.LEFT, padx=(18, 0))

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

    def _explore(self):
        if self._on_explore:
            self._on_explore()
