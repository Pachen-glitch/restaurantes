"""Wizard de onboarding gastronomico (7 pasos, auto-avance)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from styles import COLORS, FONTS

ONBOARDING_STEPS = [
    {
        "id": "estilo",
        "title": "Estilo gastronomico",
        "subtitle": "Que buscas normalmente cuando sales a comer?",
        "options": [
            {"text": "Comfort food", "weights": {"comfort_food": 5, "casual": 3, "slow_food": 2}},
            {"text": "Experiencia gourmet", "weights": {"gourmet": 5, "premium": 4, "elegant": 3}},
            {"text": "Algo rapido", "weights": {"comida_rapida": 5, "fast_service": 4, "fast_food": 3}},
            {"text": "Algo trendy", "weights": {"trendy": 5, "moderno": 4, "aesthetic": 3}},
            {"text": "Lugar para conversar", "weights": {"tranquil": 5, "intimate": 4, "slow_food": 3}},
            {"text": "Lugar aesthetic", "weights": {"aesthetic": 5, "trendy": 4, "brunch": 2}},
            {"text": "Algo para compartir", "weights": {"social_grupo": 5, "comfort_food": 3, "lively": 2}},
            {"text": "Algo practico", "weights": {"fast_service": 5, "comida_rapida": 4, "equilibrado": 2}},
        ],
    },
    {
        "id": "exploracion",
        "title": "Exploracion",
        "subtitle": "Que tan dispuesto estas a probar lugares nuevos?",
        "options": [
            {"text": "Voy siempre a los mismos lugares", "weights": {"rutinero": 5, "tradicional": 4}},
            {"text": "A veces pruebo algo nuevo", "weights": {"equilibrado": 5, "explorador": 2}},
            {"text": "Me gusta descubrir restaurantes", "weights": {"explorador": 5, "aventurero": 4, "trendy": 2}},
            {"text": "Busco constantemente experiencias nuevas", "weights": {"explorador": 5, "aventurero": 5, "moderno": 4}},
        ],
    },
    {
        "id": "social",
        "title": "Contexto social",
        "subtitle": "Como suelen ser tus salidas?",
        "options": [
            {"text": "Solo", "weights": {"social_solo": 5, "tranquil": 3, "intimate": 2}},
            {"text": "Pareja", "weights": {"social_pareja": 5, "romantic": 4, "intimate": 3}},
            {"text": "Amigos", "weights": {"social_grupo": 5, "lively": 4, "nightlife": 2}},
            {"text": "Familia", "weights": {"social_familia": 5, "family_friendly": 4, "comfort_food": 2}},
            {"text": "Trabajo / reuniones", "weights": {"business_dining": 5, "elegant": 3, "fast_service": 2}},
        ],
    },
    {
        "id": "energia",
        "title": "Energia del lugar",
        "subtitle": "Que ambiente disfrutas mas?",
        "options": [
            {"text": "Tranquilo", "weights": {"tranquil": 5, "slow_food": 3, "intimate": 2}},
            {"text": "Elegante", "weights": {"elegant": 5, "gourmet": 3, "premium": 3}},
            {"text": "Casual", "weights": {"casual": 5, "comfort_food": 3, "equilibrado": 2}},
            {"text": "Ruidoso / social", "weights": {"lively": 5, "social_grupo": 4, "nightlife": 3}},
            {"text": "Moderno", "weights": {"moderno": 5, "trendy": 4, "aesthetic": 2}},
            {"text": "Exclusivo", "weights": {"exclusive": 5, "premium": 4, "gourmet": 3}},
        ],
    },
    {
        "id": "sabores",
        "title": "Intensidad de sabores",
        "subtitle": "Que perfil de sabor te representa mejor?",
        "options": [
            {"text": "Suave", "weights": {"sabor_fresco": 5, "balanced_flavor": 4, "saludable": 2}},
            {"text": "Balanceado", "weights": {"equilibrado": 5, "balanced_flavor": 4}},
            {"text": "Intenso", "weights": {"intense_flavor": 5, "sabor_umami": 4, "contundente": 2}},
            {"text": "Picante", "weights": {"sabor_picante": 5, "spicy": 5}},
            {"text": "Ahumado", "weights": {"smoky": 5, "contundente": 4, "premium": 2}},
            {"text": "Dulce / salado", "weights": {"sabor_dulce": 4, "sabor_salado": 4, "dessert_focus": 3}},
        ],
    },
    {
        "id": "presupuesto",
        "title": "Presupuesto",
        "subtitle": "Cuanto sueles invertir por persona en una salida?",
        "options": [
            {"text": "Prefiero comer en casa", "rango": "en_casa", "weights": {"home_dining": 5, "comfort_food": 3, "ahorrador": 4}},
            {"text": "Q50 - Q150", "rango": "q50_150", "weights": {"ahorrador": 5, "casual": 3, "street_food": 2}},
            {"text": "Q150 - Q300", "rango": "q150_300", "weights": {"equilibrado": 5, "casual": 2}},
            {"text": "Q300 - Q600", "rango": "q300_600", "weights": {"equilibrado": 4, "indulgente": 3}},
            {"text": "Q600 - Q1000", "rango": "q600_1000", "weights": {"premium": 4, "gourmet": 3}},
            {"text": "Q1000 - Q2000", "rango": "q1000_2000", "weights": {"premium": 5, "exclusive": 4, "gourmet": 3}},
            {"text": "Mas de Q2000", "rango": "mas_2000", "weights": {"exclusive": 5, "indulgente": 4, "premium": 4}},
        ],
    },
    {
        "id": "comida",
        "title": "Preferencias reales",
        "subtitle": "Que escogerias AHORA MISMO?",
        "card_layout": True,
        "options": [
            {"text": "Sushi premium", "emoji": "🍣", "weights": {"pref_japonesa": 5, "gourmet": 4, "premium": 3}},
            {"text": "Ramen", "emoji": "🍜", "weights": {"pref_japonesa": 5, "sabor_umami": 4, "comfort_food": 2}},
            {"text": "Tacos callejeros", "emoji": "🌮", "weights": {"street_food": 5, "pref_guatemalteca": 4}},
            {"text": "Pizza artesanal", "emoji": "🍕", "weights": {"pref_italiana": 5, "casual": 3}},
            {"text": "Steakhouse", "emoji": "🥩", "weights": {"contundente": 5, "premium": 4, "smoky": 3}},
            {"text": "Cafe & brunch", "emoji": "☕", "weights": {"brunch": 5, "aesthetic": 4, "trendy": 2}},
            {"text": "Burgers gourmet", "emoji": "🍔", "weights": {"comfort_food": 4, "moderno": 3, "casual": 3}},
            {"text": "Parrillada", "emoji": "🔥", "weights": {"contundente": 5, "smoky": 4, "social_grupo": 2}},
            {"text": "Pasta cremosa", "emoji": "🍝", "weights": {"pref_italiana": 5, "slow_food": 3, "comfort_food": 2}},
            {"text": "Poke bowl", "emoji": "🥙", "weights": {"saludable": 5, "sabor_fresco": 4, "pref_japonesa": 2}},
            {"text": "Comida coreana", "emoji": "🇰🇷", "weights": {"pref_coreana": 5, "spicy": 3, "explorador": 2}},
            {"text": "Comida mediterranea", "emoji": "🫒", "weights": {"pref_mediterranea": 5, "sabor_fresco": 3, "saludable": 2}},
        ],
    },
]

FOOD_TO_CUISINE = {
    "pref_japonesa": "Japonesa",
    "pref_italiana": "Italiana",
    "pref_guatemalteca": "Guatemalteca",
    "pref_coreana": "Coreana",
    "pref_mediterranea": "Mediterranea",
    "sabor_umami": "Japonesa",
    "sabor_dulce": "Italiana",
    "sabor_salado": "Italiana",
    "contundente": "Guatemalteca",
}


def map_food_to_cuisines(profile_scores: dict[str, float]) -> list[str]:
    threshold = 6.0
    out: list[str] = []
    seen: set[str] = set()
    for key, score in profile_scores.items():
        if score < threshold:
            continue
        cuisine = FOOD_TO_CUISINE.get(key)
        if cuisine and cuisine not in seen:
            seen.add(cuisine)
            out.append(cuisine)
    return out


def _merge_weights(target: dict[str, float], weights: dict[str, int | float]) -> None:
    for k, v in weights.items():
        target[k] = target.get(k, 0.0) + float(v)


class OnboardingWizard(ttk.Frame):
    """Asistente de 7 pasos con tarjetas y auto-avance."""

    AUTO_MS = 400

    def __init__(self, master=None, on_step_change=None, on_complete=None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_step_change = on_step_change
        self._on_complete = on_complete
        self._step_index = 0
        self._scores: dict[str, float] = {}
        self._presupuesto_rango: str | None = None
        self._selections: list[int | None] = [None] * len(ONBOARDING_STEPS)
        self._pending_after_id: str | None = None

        self.progress_var = tk.DoubleVar(value=(1 / len(ONBOARDING_STEPS)) * 100)
        self.step_label_var = tk.StringVar()

        header = ttk.Frame(self, style="Card.TFrame", padding=12)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, textvariable=self.step_label_var, style="Subtitle.TLabel").pack(anchor=tk.W)
        self._progress = ttk.Progressbar(
            header,
            variable=self.progress_var,
            maximum=100,
            style="Horizontal.TProgressbar",
            mode="determinate",
        )
        self._progress.pack(fill=tk.X, pady=(8, 0))

        self.question_var = tk.StringVar()
        ttk.Label(self, textvariable=self.question_var, wraplength=560, style="Card.TLabel").pack(
            anchor=tk.W, padx=4, pady=(0, 10)
        )

        self.options_frame = ttk.Frame(self)
        self.options_frame.pack(fill=tk.BOTH, expand=True)

        nav = ttk.Frame(self)
        nav.pack(fill=tk.X, pady=12)
        self.btn_prev = ttk.Button(nav, text="Anterior", command=self._prev_step)
        self.btn_prev.pack(side=tk.LEFT)

        self._render_step()

    def get_final_profile(self) -> dict[str, float]:
        return dict(sorted(self._scores.items(), key=lambda x: (-x[1], x[0])))

    def get_presupuesto_sugerido(self) -> int:
        from user_manager import presupuesto_desde_rango

        if self._presupuesto_rango:
            return presupuesto_desde_rango(self._presupuesto_rango)
        return 150

    def reset(self) -> None:
        if self._pending_after_id:
            self.after_cancel(self._pending_after_id)
            self._pending_after_id = None
        self._step_index = 0
        self._scores.clear()
        self._presupuesto_rango = None
        self._selections = [None] * len(ONBOARDING_STEPS)
        self._render_step()

    def load_profile(self, profile: dict[str, float]) -> None:
        self.reset()
        self._scores = {k: float(v) for k, v in (profile or {}).items()}

    def _render_step(self) -> None:
        if self._pending_after_id:
            self.after_cancel(self._pending_after_id)
            self._pending_after_id = None

        step = ONBOARDING_STEPS[self._step_index]
        n = len(ONBOARDING_STEPS)
        self.step_label_var.set("Paso %d de %d: %s" % (self._step_index + 1, n, step["title"]))
        self.progress_var.set(((self._step_index + 1) / n) * 100)
        self.question_var.set(step.get("subtitle") or step.get("title") or "")

        for w in self.options_frame.winfo_children():
            w.destroy()

        selected_idx = self._selections[self._step_index]
        card_layout = bool(step.get("card_layout"))
        cols = 3 if card_layout else 2

        for i, opt in enumerate(step["options"]):
            label = opt.get("text", "")
            if card_layout:
                label = "%s\n%s" % (opt.get("emoji", ""), label)
            style = "Selected.OptionCard.TButton" if selected_idx == i else "OptionCard.TButton"
            btn = ttk.Button(
                self.options_frame,
                text=label,
                style=style,
                command=lambda idx=i, o=opt: self._select_option(idx, o),
            )
            btn.grid(row=i // cols, column=i % cols, sticky=tk.NSEW, padx=6, pady=6)
        for c in range(cols):
            self.options_frame.columnconfigure(c, weight=1)

        self.btn_prev.state(["!disabled"] if self._step_index > 0 else ["disabled"])
        if self._on_step_change:
            self._on_step_change()

    def _select_option(self, index: int, option: dict) -> None:
        prev = self._selections[self._step_index]
        if prev is not None:
            old = ONBOARDING_STEPS[self._step_index]["options"][prev]
            for k, v in old.get("weights", {}).items():
                self._scores[k] = self._scores.get(k, 0.0) - float(v)
                if self._scores.get(k, 0) <= 0:
                    self._scores.pop(k, None)
            if ONBOARDING_STEPS[self._step_index]["id"] == "presupuesto":
                self._presupuesto_rango = None

        self._selections[self._step_index] = index
        _merge_weights(self._scores, option.get("weights", {}))
        if option.get("rango"):
            self._presupuesto_rango = option["rango"]
        self._render_step()

        if self._pending_after_id:
            self.after_cancel(self._pending_after_id)
        self._pending_after_id = self.after(self.AUTO_MS, self._auto_next)

    def _auto_next(self) -> None:
        self._pending_after_id = None
        if self._selections[self._step_index] is None:
            return
        if self._step_index < len(ONBOARDING_STEPS) - 1:
            self._step_index += 1
            self._render_step()
            return
        if self._on_complete:
            self._on_complete()

    def _prev_step(self) -> None:
        if self._pending_after_id:
            self.after_cancel(self._pending_after_id)
            self._pending_after_id = None
        if self._step_index > 0:
            self._step_index -= 1
            self._render_step()