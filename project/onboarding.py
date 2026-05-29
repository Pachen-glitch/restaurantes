"""Wizard de onboarding gastronomico inmersivo (15 pasos, auto-avance)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from styles import COLORS, FONTS, ONBOARDING
from ui_widgets import OnboardingOptionGrid

_RAW_ONBOARDING_STEPS = [
    {
        "id": "base",
        "title": "Base de tus comidas",
        "subtitle": "¿Cuál prefieres como base de tus comidas?",
        "options": [
            {"text": "Carne", "weights": {"contundente": 5, "premium": 2}},
            {"text": "Mariscos", "weights": {"sabor_fresco": 5, "pref_mediterranea": 2}},
            {"text": "Verduras", "weights": {"saludable": 5, "sabor_fresco": 3}},
        ],
    },
    {
        "id": "grupos",
        "title": "Grupos de comida",
        "subtitle": "¿Prefieres comer dentro de alguno de estos grupos?",
        "card_layout": True,
        "options": [
            {"text": "Pasta", "emoji": "🍝", "weights": {"pref_italiana": 5, "slow_food": 3}},
            {"text": "BBQ", "emoji": "🔥", "weights": {"smoky": 5, "contundente": 4, "social_grupo": 2}},
            {"text": "Sushi", "emoji": "🍣", "weights": {"pref_japonesa": 5, "gourmet": 3}},
            {"text": "Restaurante casual", "emoji": "🍽️", "weights": {"casual": 5, "equilibrado": 3}},
            {"text": "Fast food", "emoji": "🍔", "weights": {"fast_food": 5, "comida_rapida": 4}},
        ],
    },
    {
        "id": "proteina",
        "title": "Tipo de proteína",
        "subtitle": "¿Prefieres comer carne de res, cerdo, pollo o mariscos?",
        "options": [
            {"text": "Res", "weights": {"contundente": 5, "premium": 3}},
            {"text": "Cerdo", "weights": {"contundente": 4, "comfort_food": 3}},
            {"text": "Pollo", "weights": {"equilibrado": 4, "saludable": 3, "casual": 2}},
            {"text": "Mariscos", "weights": {"sabor_fresco": 5, "pref_mediterranea": 3}},
        ],
    },
    {
        "id": "tierra_mar",
        "title": "Tierra o mar",
        "subtitle": "¿Prefieres comer carne o mariscos?",
        "options": [
            {"text": "Carne", "weights": {"contundente": 5, "smoky": 3}},
            {"text": "Mariscos", "weights": {"sabor_fresco": 5, "saludable": 2}},
            {"text": "Ambos por igual", "weights": {"equilibrado": 5, "explorador": 3}},
        ],
    },
    {
        "id": "coccion",
        "title": "Punto de la carne",
        "subtitle": "¿Prefieres la carne…?",
        "options": [
            {"text": "Bien cocida", "weights": {"tradicional": 4, "comfort_food": 3}},
            {"text": "Término medio", "weights": {"equilibrado": 5, "premium": 2}},
            {"text": "Jugosa / poco cocida", "weights": {"gourmet": 4, "premium": 4, "contundente": 2}},
        ],
    },
    {
        "id": "cocinas",
        "title": "Cocinas del mundo",
        "subtitle": "¿Qué tipo de comida prefieres?",
        "card_layout": True,
        "options": [
            {"text": "Italiana", "emoji": "🍝", "weights": {"pref_italiana": 5, "slow_food": 2}},
            {"text": "Japonesa", "emoji": "🍣", "weights": {"pref_japonesa": 5, "sabor_umami": 3}},
            {"text": "Mexicana", "emoji": "🌮", "weights": {"street_food": 4, "spicy": 4, "pref_guatemalteca": 2}},
            {"text": "Americana", "emoji": "🍔", "weights": {"comfort_food": 4, "fast_food": 3, "casual": 2}},
            {"text": "Coreana", "emoji": "🍜", "weights": {"pref_coreana": 5, "spicy": 3}},
            {"text": "Tailandesa", "emoji": "🌶️", "weights": {"spicy": 5, "explorador": 3, "sabor_fresco": 2}},
            {"text": "Mediterránea", "emoji": "🥗", "weights": {"pref_mediterranea": 5, "saludable": 3}},
            {"text": "Guatemalteca", "emoji": "🌽", "weights": {"pref_guatemalteca": 5, "tradicional": 4}},
            {"text": "Francesa", "emoji": "🥐", "weights": {"gourmet": 5, "elegant": 4, "premium": 2}},
        ],
    },
    {
        "id": "formato",
        "title": "Formato del menú",
        "subtitle": "¿Prefieres restaurantes con platos para compartir o con platos principales?",
        "options": [
            {"text": "Platos para compartir", "weights": {"social_grupo": 5, "lively": 3, "tapas_style": 4}},
            {"text": "Platos principales", "weights": {"main_dish_focus": 5, "elegant": 2}},
            {"text": "Me da igual", "weights": {"equilibrado": 4, "casual": 3}},
        ],
    },
    {
        "id": "ingredientes",
        "title": "Calidad de ingredientes",
        "subtitle": "¿Te importa la calidad de los ingredientes?",
        "options": [
            {"text": "Es lo más importante", "weights": {"gourmet": 5, "premium": 4, "ingredient_quality": 5}},
            {"text": "Importa, pero sin obsesión", "weights": {"equilibrado": 5, "ingredient_quality": 3}},
            {"text": "No es prioridad", "weights": {"ahorrador": 4, "fast_food": 3, "casual": 2}},
        ],
    },
    {
        "id": "ambiente",
        "title": "Ambiente del lugar",
        "subtitle": "¿Cómo prefieres que sea el ambiente del restaurante?",
        "options": [
            {"text": "Romántico", "weights": {"romantic": 5, "intimate": 4, "elegant": 2}},
            {"text": "Casual", "weights": {"casual": 5, "comfort_food": 3}},
            {"text": "Trendy", "weights": {"trendy": 5, "aesthetic": 4, "moderno": 3}},
            {"text": "Familiar", "weights": {"family_friendly": 5, "social_familia": 4}},
            {"text": "Exclusivo", "weights": {"exclusive": 5, "premium": 4, "gourmet": 2}},
        ],
    },
    {
        "id": "bebidas",
        "title": "Bebidas",
        "subtitle": "¿Prefieres acompañar tu comida con vino, cerveza o cócteles?",
        "options": [
            {"text": "Vino", "weights": {"wine_focus": 5, "elegant": 3, "gourmet": 2}},
            {"text": "Cerveza", "weights": {"craft_beer": 5, "casual": 3, "lively": 2}},
            {"text": "Cócteles", "weights": {"cocktail_focus": 5, "trendy": 3, "nightlife": 2}},
            {"text": "No me importa", "weights": {"equilibrado": 4, "casual": 2}},
        ],
    },
    {
        "id": "exploracion",
        "title": "Probar cosas nuevas",
        "subtitle": "¿Prefieres restaurantes donde puedas probar cosas nuevas?",
        "options": [
            {"text": "Siempre quiero novedad", "weights": {"explorador": 5, "aventurero": 5, "moderno": 3}},
            {"text": "A veces", "weights": {"equilibrado": 5, "explorador": 2}},
            {"text": "Prefiero lo conocido", "weights": {"rutinero": 5, "tradicional": 4, "comfort_food": 2}},
        ],
    },
    {
        "id": "presupuesto",
        "title": "Presupuesto",
        "subtitle": "¿Cuánto gastas normalmente por persona?",
        "options": [
            {"text": "Prefiero comer en casa", "rango": "en_casa", "weights": {"home_dining": 5, "ahorrador": 4}},
            {"text": "Q50 – Q150", "rango": "q50_150", "weights": {"ahorrador": 5, "street_food": 3, "casual": 2}},
            {"text": "Q150 – Q300", "rango": "q150_300", "weights": {"equilibrado": 5, "casual": 3}},
            {"text": "Q300 – Q600", "rango": "q300_600", "weights": {"equilibrado": 4, "indulgente": 3}},
            {"text": "Q600 – Q1000", "rango": "q600_1000", "weights": {"premium": 4, "gourmet": 3}},
            {"text": "Q1000 – Q2000", "rango": "q1000_2000", "weights": {"premium": 5, "exclusive": 3, "gourmet": 3}},
            {"text": "Más de Q2000", "rango": "mas_2000", "weights": {"exclusive": 5, "indulgente": 4, "premium": 4}},
        ],
    },
    {
        "id": "ubicacion",
        "title": "Ubicación",
        "subtitle": "¿Te importa la ubicación del restaurante?",
        "options": [
            {"text": "Muy importante", "weights": {"location_focus": 5, "fast_service": 2}},
            {"text": "Importante", "weights": {"location_focus": 3, "equilibrado": 3}},
            {"text": "No es prioridad", "weights": {"explorador": 3, "indulgente": 2, "equilibrado": 2}},
        ],
    },
    {
        "id": "proposito",
        "title": "Propósito de la salida",
        "subtitle": "¿Prefieres comer para socializar, trabajar o celebrar?",
        "options": [
            {"text": "Socializar", "weights": {"social_grupo": 5, "lively": 4, "casual": 2}},
            {"text": "Trabajar", "weights": {"business_dining": 5, "tranquil": 3, "fast_service": 2}},
            {"text": "Celebrar", "weights": {"celebrate": 5, "premium": 3, "elegant": 3, "social_grupo": 2}},
        ],
    },
    {
        "id": "prioridad",
        "title": "Tu prioridad",
        "subtitle": "¿Qué te importa más en tu experiencia gastronómica?",
        "options": [
            {"text": "Presentación", "weights": {"presentation_focus": 5, "aesthetic": 4, "gourmet": 2}},
            {"text": "Sabor", "weights": {"flavor_focus": 5, "intense_flavor": 4, "gourmet": 2}},
            {"text": "Servicio", "weights": {"service_focus": 5, "elegant": 3, "premium": 2}},
            {"text": "Precio", "weights": {"price_focus": 5, "ahorrador": 4, "equilibrado": 2}},
        ],
    },
]


def _sanitize_option(option: dict) -> dict | None:
    text = str(option.get("text") or "").strip()
    if not text:
        return None
    cleaned = dict(option)
    cleaned["text"] = text
    emoji = str(option.get("emoji") or "").strip()
    if emoji:
        cleaned["emoji"] = emoji
    else:
        cleaned.pop("emoji", None)
    weights = option.get("weights")
    if not isinstance(weights, dict) or not weights:
        return None
    return cleaned


def _sanitize_onboarding_steps(steps: list[dict]) -> list[dict]:
    sanitized: list[dict] = []
    for step in steps:
        options = []
        for option in step.get("options") or []:
            cleaned = _sanitize_option(option)
            if cleaned:
                options.append(cleaned)
        if not options:
            continue
        title = str(step.get("title") or "").strip() or "Pregunta"
        subtitle = str(step.get("subtitle") or "").strip() or title
        sanitized.append({**step, "title": title, "subtitle": subtitle, "options": options})
    return sanitized


ONBOARDING_STEPS = _sanitize_onboarding_steps(_RAW_ONBOARDING_STEPS)


def validate_onboarding_steps() -> dict:
    """Valida que cada paso tenga opciones renderizables."""
    issues: list[str] = []
    for i, step in enumerate(ONBOARDING_STEPS, start=1):
        if not step.get("options"):
            issues.append("Paso %d sin opciones validas" % i)
        for j, opt in enumerate(step.get("options") or [], start=1):
            if not str(opt.get("text") or "").strip():
                issues.append("Paso %d opcion %d sin texto" % (i, j))
    return {"valid": len(issues) == 0, "steps": len(ONBOARDING_STEPS), "issues": issues}


assert validate_onboarding_steps()["valid"], "Onboarding invalido: %s" % validate_onboarding_steps()["issues"]

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
    "spicy": "Mexicana",
    "street_food": "Mexicana",
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


class OnboardingWizard(tk.Frame):
    """Asistente inmersivo de 15 pasos con transiciones suaves."""

    AUTO_MS = 380
    FADE_MS = 120

    def __init__(self, master=None, on_step_change=None, on_complete=None, **kwargs):
        super().__init__(master, bg=COLORS["bg"], **kwargs)
        self._on_step_change = on_step_change
        self._on_complete = on_complete
        self._step_index = 0
        self._scores: dict[str, float] = {}
        self._presupuesto_rango: str | None = None
        self._selections: list[int | None] = [None] * len(ONBOARDING_STEPS)
        self._pending_after_id: str | None = None
        self._resize_after: str | None = None
        self._last_layout_width = 0
        self._rendering = False
        self._transitioning = False

        self.progress_var = tk.DoubleVar(value=(1 / len(ONBOARDING_STEPS)) * 100)
        self.step_label_var = tk.StringVar()

        header = tk.Frame(
            self,
            bg=COLORS["surface2"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1,
            padx=24,
            pady=18,
        )
        header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(
            header,
            textvariable=self.step_label_var,
            font=FONTS["subtitle"],
            fg=COLORS["accent"],
            bg=COLORS["surface2"],
        ).pack(anchor=tk.W)
        self._progress = ttk.Progressbar(
            header,
            variable=self.progress_var,
            maximum=100,
            style="Horizontal.TProgressbar",
            mode="determinate",
        )
        self._progress.pack(fill=tk.X, pady=(12, 0))

        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(fill=tk.BOTH, expand=True)

        self.question_var = tk.StringVar()
        self._question_label = tk.Label(
            self.content,
            textvariable=self.question_var,
            font=FONTS["question"],
            fg=COLORS["text"],
            bg=COLORS["bg"],
            wraplength=760,
            justify=tk.LEFT,
            anchor=tk.W,
        )
        self._question_label.pack(anchor=tk.W, padx=12, pady=(8, 20))

        self.options_frame = OnboardingOptionGrid(self.content)
        self.options_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
        self.options_frame.bind("<Configure>", self._on_options_resize)

        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(fill=tk.X, pady=(16, 0))
        self.btn_prev = ttk.Button(nav, text="← Anterior", style="Secondary.TButton", command=self._prev_step)
        self.btn_prev.pack(side=tk.LEFT)

        self._render_step(notify=False)

    def _on_options_resize(self, _event=None):
        width = self.options_frame.winfo_width()
        if width <= 1 or width == self._last_layout_width:
            return
        self._last_layout_width = width
        if hasattr(self, "_resize_after") and self._resize_after:
            self.after_cancel(self._resize_after)
        self._resize_after = self.after(150, lambda: self._render_step(notify=False, relayout=True))

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

    def _transition_to(self, callback) -> None:
        if self._transitioning:
            callback()
            return
        self._transitioning = True
        overlay = tk.Frame(self.content, bg=COLORS["accent_light"])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        def fade_out(step=0):
            if step >= 3:
                overlay.destroy()
                callback()
                self._transitioning = False
                return
            self.after(self.FADE_MS // 3, lambda: fade_out(step + 1))

        fade_out()

    def _render_step(self, notify: bool = True, relayout: bool = False) -> None:
        if self._rendering:
            return
        self._rendering = True
        try:
            if self._pending_after_id:
                self.after_cancel(self._pending_after_id)
                self._pending_after_id = None

            step = ONBOARDING_STEPS[self._step_index]
            n = len(ONBOARDING_STEPS)
            self.step_label_var.set("Paso %d de %d · %s" % (self._step_index + 1, n, step["title"]))
            self.progress_var.set(((self._step_index + 1) / n) * 100)
            self.question_var.set(step.get("subtitle") or step.get("title") or "")

            wrap = max(420, min(860, self.winfo_width() - 120))
            self._question_label.configure(wraplength=wrap)

            selected_idx = self._selections[self._step_index]
            card_layout = bool(step.get("card_layout"))
            self.options_frame.render(
                step.get("options") or [],
                selected_idx,
                card_layout,
                self._select_option,
            )

            self.btn_prev.state(["!disabled"] if self._step_index > 0 else ["disabled"])
            if notify and self._on_step_change:
                self._on_step_change()
        finally:
            self._rendering = False

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

            def advance():
                self._step_index += 1
                self._render_step()

            self._transition_to(advance)
            return
        if self._on_complete:
            self._on_complete()

    def _prev_step(self) -> None:
        if self._pending_after_id:
            self.after_cancel(self._pending_after_id)
            self._pending_after_id = None
        if self._step_index > 0:

            def back():
                self._step_index -= 1
                self._render_step()

            self._transition_to(back)
