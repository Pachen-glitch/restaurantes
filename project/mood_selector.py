"""Selector emocional de mood antes de recomendar."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from styles import COLORS, FONTS
from ui_animations import bind_hover_glow

MOOD_OPTIONS = [
    ("comfort", "Comfort", "🍜"),
    ("explorar", "Explorar", "🌎"),
    ("premium", "Premium", "🍷"),
    ("social", "Social", "🍻"),
    ("chill", "Chill", "☕"),
    ("romantico", "Romántico", "🌙"),
    ("trabajo", "Trabajo", "💼"),
    ("familiar", "Familiar", "👨‍👩‍👧"),
]


class MoodSelector(tk.Frame):
    """Grid visual de moods; altera pesos temporalmente al recomendar."""

    def __init__(self, master, on_change=None, **kwargs):
        super().__init__(master, bg=COLORS["bg"], **kwargs)
        self._on_change = on_change
        self._selected: str | None = None
        self._buttons: dict[str, tk.Frame] = {}

        tk.Label(
            self,
            text="¿Qué mood tienes hoy?",
            font=FONTS["subtitle"],
            fg=COLORS["text"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W, pady=(0, 10))

        grid = tk.Frame(self, bg=COLORS["bg"])
        grid.pack(fill=tk.X)
        cols = 4
        for i, (key, label, emoji) in enumerate(MOOD_OPTIONS):
            card = tk.Frame(
                grid,
                bg=COLORS["surface2"],
                highlightbackground=COLORS["card_border"],
                highlightthickness=1,
                padx=12,
                pady=10,
                cursor="hand2",
            )
            card.grid(row=i // cols, column=i % cols, sticky=tk.NSEW, padx=6, pady=6)
            tk.Label(card, text=emoji, font=("Segoe UI", 22), bg=COLORS["surface2"]).pack()
            tk.Label(card, text=label, font=FONTS["small"], fg=COLORS["text"], bg=COLORS["surface2"]).pack(pady=(4, 0))
            card.bind("<Button-1>", lambda _e, k=key: self.set_mood(k))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda _e, k=key: self.set_mood(k))
            bind_hover_glow(card, COLORS["card_border"])
            self._buttons[key] = card
            grid.columnconfigure(i % cols, weight=1)

        tk.Label(
            self,
            text="El mood ajusta la recomendación sin cambiar tu perfil permanente.",
            font=FONTS["small"],
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W, pady=(8, 0))

    @property
    def selected_mood(self) -> str | None:
        return self._selected

    def set_mood(self, mood: str | None) -> None:
        self._selected = mood
        for key, card in self._buttons.items():
            if key == mood:
                card.configure(bg=COLORS["accent_light"], highlightbackground=COLORS["accent"])
                for child in card.winfo_children():
                    child.configure(bg=COLORS["accent_light"])
            else:
                card.configure(bg=COLORS["surface2"], highlightbackground=COLORS["card_border"])
                for child in card.winfo_children():
                    child.configure(bg=COLORS["surface2"])
        if self._on_change:
            self._on_change(mood)

    def clear(self) -> None:
        self.set_mood(None)
