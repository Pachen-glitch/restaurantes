"""Visualización del ADN gastronómico del usuario."""

from __future__ import annotations

import math
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from recommendation import PREF_LABELS_ES
from styles import COLORS, FONTS

RADAR_AXES = [
    ("premium", "Premium"),
    ("social_grupo", "Social"),
    ("explorador", "Explorador"),
    ("casual", "Casual"),
    ("gourmet", "Gourmet"),
    ("comfort_food", "Comfort"),
    ("nightlife", "Nightlife"),
]


class ProfileVisualizer(tk.Frame):
    """Barras animadas + radar chart del perfil gastronómico."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=COLORS["bg"], **kwargs)
        self._profile: dict[str, float] = {}

        tk.Label(
            self,
            text="Tu ADN Gastronómico",
            font=FONTS["hero"],
            fg=COLORS["text"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W)
        tk.Label(
            self,
            text="Mapa visual de tus afinidades culinarias",
            font=FONTS["body"],
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W, pady=(4, 16))

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self.bars_frame = tk.Frame(
            body,
            bg=COLORS["surface2"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        self.bars_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 8))

        radar_wrap = tk.Frame(
            body,
            bg=COLORS["surface2"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1,
        )
        radar_wrap.grid(row=0, column=1, sticky=tk.NSEW, padx=(8, 0))

        self.figure = plt.Figure(figsize=(4.2, 3.8), dpi=100, facecolor=COLORS["surface2"])
        self.ax = self.figure.add_subplot(111, polar=True)
        self.canvas = FigureCanvasTkAgg(self.figure, master=radar_wrap)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._empty_label = tk.Label(
            self.bars_frame,
            text="Selecciona un usuario para ver su ADN gastronómico.",
            font=FONTS["body"],
            fg=COLORS["muted"],
            bg=COLORS["surface2"],
            wraplength=320,
            justify=tk.LEFT,
        )
        self._empty_label.pack(pady=40)

    def render(self, profile: dict[str, float]) -> None:
        self._profile = profile or {}
        for w in self.bars_frame.winfo_children():
            w.destroy()
        if not self._profile:
            tk.Label(
                self.bars_frame,
                text="Sin preferencias registradas.\nCompleta el onboarding primero.",
                font=FONTS["body"],
                fg=COLORS["muted"],
                bg=COLORS["surface2"],
                justify=tk.LEFT,
            ).pack(pady=40)
            self._draw_radar({})
            return

        top = sorted(self._profile.items(), key=lambda x: -x[1])[:8]
        max_score = max(v for _, v in top) or 1.0
        for pref, score in top:
            label = PREF_LABELS_ES.get(pref, pref.replace("_", " ").title())
            row = tk.Frame(self.bars_frame, bg=COLORS["surface2"])
            row.pack(fill=tk.X, pady=6)
            tk.Label(row, text=label[:22], font=FONTS["small"], fg=COLORS["text"], bg=COLORS["surface2"], width=18, anchor=tk.W).pack(
                side=tk.LEFT
            )
            bar_bg = tk.Frame(row, bg=COLORS["progress_bg"], height=12)
            bar_bg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))
            bar_bg.pack_propagate(False)
            fill = tk.Frame(bar_bg, bg=COLORS["accent"], height=12)
            pct = min(1.0, score / max_score)
            fill.place(relx=0, rely=0, relheight=1, relwidth=0.01)
            self._animate_bar(fill, pct)
            tk.Label(row, text="%d" % int(score), font=FONTS["badge"], fg=COLORS["accent"], bg=COLORS["surface2"], width=4).pack(side=tk.RIGHT)

        self._draw_radar(self._profile)

    def _animate_bar(self, widget: tk.Frame, target: float, step: int = 0) -> None:
        if not widget.winfo_exists():
            return
        current = 0.01 + step * (target / 12)
        if current >= target:
            widget.place(relx=0, rely=0, relheight=1, relwidth=target)
            return
        widget.place(relx=0, rely=0, relheight=1, relwidth=current)
        widget.after(30, lambda: self._animate_bar(widget, target, step + 1))

    def _draw_radar(self, profile: dict[str, float]) -> None:
        self.ax.clear()
        self.ax.set_facecolor(COLORS["surface2"])
        labels = [label for _, label in RADAR_AXES]
        values = []
        for key, _ in RADAR_AXES:
            values.append(min(10.0, profile.get(key, 0) / 3.0))
        if not any(values):
            values = [0.1] * len(RADAR_AXES)
        angles = [n / float(len(labels)) * 2 * math.pi for n in range(len(labels))]
        values_cycle = values + values[:1]
        angles_cycle = angles + angles[:1]
        self.ax.plot(angles_cycle, values_cycle, color=COLORS["accent"], linewidth=2)
        self.ax.fill(angles_cycle, values_cycle, color=COLORS["accent2"], alpha=0.25)
        self.ax.set_xticks(angles)
        self.ax.set_xticklabels(labels, fontsize=8, color=COLORS["text"])
        self.ax.set_yticks([2, 4, 6, 8, 10])
        self.ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=7, color=COLORS["muted"])
        self.ax.spines["polar"].set_color(COLORS["card_border"])
        self.ax.grid(color=COLORS["card_border"], alpha=0.5)
        self.figure.tight_layout(pad=1.0)
        self.canvas.draw_idle()
