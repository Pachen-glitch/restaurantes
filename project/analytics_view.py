"""Panel de analytics e insights gastronómicos."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from recommendation import PREF_LABELS_ES, obtener_insights_usuario
from styles import COLORS, FONTS


class AnalyticsPanel(tk.Frame):
    """Insights: zonas, cocinas, preferencias y heatmap."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=COLORS["bg"], **kwargs)
        self._user_id: str | None = None

        tk.Label(self, text="Insights", font=FONTS["hero"], fg=COLORS["text"], bg=COLORS["bg"]).pack(anchor=tk.W)
        tk.Label(
            self,
            text="Inteligencia gastronómica de tu perfil Savory",
            font=FONTS["body"],
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W, pady=(4, 16))

        top = tk.Frame(self, bg=COLORS["bg"])
        top.pack(fill=tk.X, pady=(0, 12))
        tk.Label(top, text="Usuario", font=FONTS["subtitle"], fg=COLORS["text"], bg=COLORS["bg"]).pack(side=tk.LEFT, padx=(0, 8))
        self.user_var = tk.StringVar()
        self.user_cb = ttk.Combobox(top, textvariable=self.user_var, state="readonly", width=36)
        self.user_cb.pack(side=tk.LEFT)
        self.user_cb.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        cards = tk.Frame(self, bg=COLORS["bg"])
        cards.pack(fill=tk.X, pady=(0, 12))
        self.stat_vars = {}
        for i, (key, title) in enumerate(
            (
                ("top_zona", "Zona favorita"),
                ("top_cocina", "Cocina top"),
                ("top_pref", "Preferencia #1"),
                ("compat_media", "Compatibilidad media"),
            )
        ):
            card = tk.Frame(
                cards,
                bg=COLORS["surface2"],
                highlightbackground=COLORS["card_border"],
                highlightthickness=1,
                padx=14,
                pady=12,
            )
            card.grid(row=0, column=i, sticky=tk.NSEW, padx=(0 if i == 0 else 6, 6 if i < 3 else 0))
            cards.columnconfigure(i, weight=1)
            tk.Label(card, text=title, font=FONTS["small"], fg=COLORS["muted"], bg=COLORS["surface2"]).pack(anchor=tk.W)
            var = tk.StringVar(value="—")
            self.stat_vars[key] = var
            tk.Label(card, textvariable=var, font=FONTS["card_title"], fg=COLORS["accent"], bg=COLORS["surface2"]).pack(anchor=tk.W, pady=(6, 0))

        charts = tk.Frame(self, bg=COLORS["bg"])
        charts.pack(fill=tk.BOTH, expand=True)
        charts.columnconfigure(0, weight=1)
        charts.columnconfigure(1, weight=1)
        charts.rowconfigure(0, weight=1)

        left = tk.Frame(charts, bg=COLORS["surface2"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        left.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 8))
        right = tk.Frame(charts, bg=COLORS["surface2"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        right.grid(row=0, column=1, sticky=tk.NSEW, padx=(8, 0))

        self.fig_left = plt.Figure(figsize=(4.5, 3.5), dpi=100, facecolor=COLORS["surface2"])
        self.ax_prefs = self.fig_left.add_subplot(111)
        self.canvas_left = FigureCanvasTkAgg(self.fig_left, master=left)
        self.canvas_left.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.fig_right = plt.Figure(figsize=(4.5, 3.5), dpi=100, facecolor=COLORS["surface2"])
        self.ax_heat = self.fig_right.add_subplot(111)
        self.canvas_right = FigureCanvasTkAgg(self.fig_right, master=right)
        self.canvas_right.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.list_box = tk.Frame(self, bg=COLORS["surface2"], highlightbackground=COLORS["card_border"], highlightthickness=1, padx=16, pady=12)
        self.list_box.pack(fill=tk.X, pady=(12, 0))
        tk.Label(self.list_box, text="Restaurantes más compatibles", font=FONTS["subtitle"], bg=COLORS["surface2"], fg=COLORS["text"]).pack(anchor=tk.W)
        self.top_list = tk.Label(self.list_box, text="Selecciona un usuario.", font=FONTS["body"], bg=COLORS["surface2"], fg=COLORS["muted"], justify=tk.LEFT, anchor=tk.W)
        self.top_list.pack(fill=tk.X, pady=(8, 0))

    def set_users(self, labels: list[str], ids: list[str]) -> None:
        self._user_labels = labels
        self._user_ids = ids
        self.user_cb["values"] = labels

    def refresh(self) -> None:
        idx = self.user_cb.current()
        if idx < 0 or idx >= len(getattr(self, "_user_ids", [])):
            return
        uid = self._user_ids[idx]
        self._user_id = uid
        data = obtener_insights_usuario(uid)
        self.stat_vars["top_zona"].set(data.get("top_zona") or "—")
        self.stat_vars["top_cocina"].set(data.get("top_cocina") or "—")
        self.stat_vars["top_pref"].set(data.get("top_pref_label") or "—")
        self.stat_vars["compat_media"].set(data.get("compat_media") or "—")
        self._draw_prefs(data.get("top_prefs") or [])
        self._draw_heatmap(data.get("heatmap") or {})
        lines = data.get("top_restaurants") or []
        if lines:
            self.top_list.configure(
                text="\n".join("• %s — %s%% compatible · %s" % (r["nombre"], r["pct"], r.get("zona", "")) for r in lines[:5]),
                fg=COLORS["text"],
            )
        else:
            self.top_list.configure(text="Sin datos suficientes.", fg=COLORS["muted"])

    def _draw_prefs(self, prefs: list[tuple[str, float]]) -> None:
        self.ax_prefs.clear()
        self.ax_prefs.set_facecolor(COLORS["surface2"])
        if not prefs:
            self.ax_prefs.text(0.5, 0.5, "Sin preferencias", ha="center", va="center", color=COLORS["muted"])
            self.canvas_left.draw_idle()
            return
        names = [PREF_LABELS_ES.get(p, p)[:16] for p, _ in prefs[:6]]
        vals = [v for _, v in prefs[:6]]
        colors = [COLORS["accent2"] if i == 0 else COLORS["accent"] for i in range(len(vals))]
        self.ax_prefs.barh(names[::-1], vals[::-1], color=colors[::-1], alpha=0.85)
        self.ax_prefs.set_xlabel("Intensidad", fontsize=8, color=COLORS["muted"])
        self.ax_prefs.tick_params(colors=COLORS["text"], labelsize=8)
        self.fig_left.tight_layout(pad=1.0)
        self.canvas_left.draw_idle()

    def _draw_heatmap(self, heatmap: dict[str, float]) -> None:
        self.ax_heat.clear()
        self.ax_heat.set_facecolor(COLORS["surface2"])
        keys = list(heatmap.keys())[:8]
        vals = [heatmap[k] for k in keys]
        if not keys:
            self.ax_heat.text(0.5, 0.5, "Sin heatmap", ha="center", va="center", color=COLORS["muted"])
            self.canvas_right.draw_idle()
            return
        labels = [PREF_LABELS_ES.get(k, k)[:12] for k in keys]
        self.ax_heat.bar(range(len(vals)), vals, color=COLORS["accent_warm"], alpha=0.9)
        self.ax_heat.set_xticks(range(len(vals)))
        self.ax_heat.set_xticklabels(labels, rotation=35, ha="right", fontsize=7, color=COLORS["text"])
        self.ax_heat.set_title("Heatmap gastronómico", fontsize=9, color=COLORS["subtext"])
        self.ax_heat.tick_params(axis="y", colors=COLORS["muted"], labelsize=7)
        self.fig_right.tight_layout(pad=1.2)
        self.canvas_right.draw_idle()
