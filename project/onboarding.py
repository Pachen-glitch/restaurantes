"""Wizard de onboarding gastronomico."""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk

from styles import COLORS, FONTS

_ONBOARDING_JSON = """
[
  {
    "id": "estilo",
    "title": "Estilo general",
    "subtitle": "Que buscas normalmente al salir a comer?",
    "options": [
      {
        "text": "Algo rapido",
        "weights": {
          "comida_rapida": 5,
          "fast_food": 4,
          "casual": 2
        }
      },
      {
        "text": "Una experiencia tranquila",
        "weights": {
          "slow_food": 5,
          "casual": 4,
          "gourmet": 2
        }
      },
      {
        "text": "Algo gourmet",
        "weights": {
          "gourmet": 5,
          "premium": 4,
          "indulgente": 3
        }
      },
      {
        "text": "Algo casual",
        "weights": {
          "casual": 5,
          "equilibrado": 3,
          "social_grupo": 2
        }
      },
      {
        "text": "Comida callejera",
        "weights": {
          "street_food": 5,
          "contundente": 4,
          "pref_guatemalteca": 2
        }
      }
    ]
  },
  {
    "id": "exploracion",
    "title": "Exploracion",
    "subtitle": "Que tanto te gusta probar cosas nuevas?",
    "options": [
      {
        "text": "Nunca",
        "weights": {
          "rutinero": 5,
          "tradicional": 4
        }
      },
      {
        "text": "A veces",
        "weights": {
          "equilibrado": 4,
          "explorador": 2
        }
      },
      {
        "text": "Frecuentemente",
        "weights": {
          "explorador": 5,
          "aventurero": 3
        }
      },
      {
        "text": "Siempre",
        "weights": {
          "explorador": 5,
          "aventurero": 5,
          "moderno": 3
        }
      }
    ]
  },
  {
    "id": "presupuesto",
    "title": "Presupuesto emocional",
    "subtitle": "Cuanto gastarias en una salida especial?",
    "options": [
      {
        "text": "Q50",
        "weights": {
          "ahorrador": 5,
          "casual": 3
        }
      },
      {
        "text": "Q100",
        "weights": {
          "equilibrado": 5,
          "casual": 2
        }
      },
      {
        "text": "Q200+",
        "weights": {
          "premium": 5,
          "gourmet": 4,
          "indulgente": 3
        }
      },
      {
        "text": "Depende del lugar",
        "weights": {
          "equilibrado": 4,
          "explorador": 3,
          "indulgente": 2
        }
      }
    ]
  },
  {
    "id": "social",
    "title": "Contexto social",
    "subtitle": "Con quien sales normalmente?",
    "options": [
      {
        "text": "Solo",
        "weights": {
          "social_solo": 5,
          "comida_rapida": 2
        }
      },
      {
        "text": "Pareja",
        "weights": {
          "social_pareja": 5,
          "gourmet": 2,
          "slow_food": 2
        }
      },
      {
        "text": "Amigos",
        "weights": {
          "social_grupo": 5,
          "casual": 3,
          "aventurero": 2
        }
      },
      {
        "text": "Familia",
        "weights": {
          "social_familia": 5,
          "tradicional": 3,
          "contundente": 2
        }
      }
    ]
  },
  {
    "id": "sabores",
    "title": "Sabores",
    "subtitle": "Que tipo de sabores prefieres?",
    "options": [
      {
        "text": "Suaves",
        "weights": {
          "sabor_fresco": 5,
          "balanced_flavor": 4
        }
      },
      {
        "text": "Balanceados",
        "weights": {
          "equilibrado": 5,
          "balanced_flavor": 4
        }
      },
      {
        "text": "Picantes",
        "weights": {
          "sabor_picante": 5,
          "spicy": 5
        }
      },
      {
        "text": "Intensos",
        "weights": {
          "sabor_umami": 5,
          "intense_flavor": 4,
          "gourmet": 2
        }
      }
    ]
  },
  {
    "id": "comida",
    "title": "Comida real",
    "subtitle": "Que escogerias AHORA MISMO?",
    "options": [
      {
        "text": "Sushi",
        "weights": {
          "pref_japonesa": 5,
          "gourmet": 3,
          "sabor_umami": 4
        }
      },
      {
        "text": "Hamburguesa artesanal",
        "weights": {
          "casual": 4,
          "contundente": 3,
          "moderno": 2
        }
      },
      {
        "text": "Pasta cremosa",
        "weights": {
          "pref_italiana": 5,
          "slow_food": 3,
          "indulgente": 2
        }
      },
      {
        "text": "Tacos",
        "weights": {
          "street_food": 4,
          "pref_guatemalteca": 5,
          "contundente": 3
        }
      },
      {
        "text": "Parrillada",
        "weights": {
          "contundente": 5,
          "social_grupo": 3,
          "premium": 2
        }
      },
      {
        "text": "Cafe + postre",
        "weights": {
          "casual": 4,
          "social_pareja": 3,
          "slow_food": 2
        }
      },
      {
        "text": "Ramen",
        "weights": {
          "pref_japonesa": 5,
          "sabor_umami": 4,
          "explorador": 2
        }
      },
      {
        "text": "Pizza",
        "weights": {
          "pref_italiana": 4,
          "casual": 4,
          "social_grupo": 2
        }
      }
    ]
  }
]
"""

ONBOARDING_STEPS = json.loads(_ONBOARDING_JSON)

FOOD_TO_CUISINE = {
    "pref_japonesa": "Japonesa",
    "pref_italiana": "Italiana",
    "pref_guatemalteca": "Guatemalteca",
    "sabor_umami": "Japonesa",
    "sabor_dulce": "Italiana",
    "sabor_salado": "Italiana",
    "contundente": "Guatemalteca",
}


def map_food_to_cuisines(profile_scores: dict[str, float]) -> list[str]:
    """Devuelve cocinas a sincronizar con LIKES_CUISINE segun prefs altas."""
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
    """Asistente de 6 pasos con tarjetas de opcion."""

    def __init__(self, master=None, on_step_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_step_change = on_step_change
        self._step_index = 0
        self._scores: dict[str, float] = {}
        self._selections: list[int | None] = [None] * len(ONBOARDING_STEPS)
        self._option_buttons: list[ttk.Button] = []

        self.progress_var = tk.DoubleVar(value=(1 / len(ONBOARDING_STEPS)) * 100)
        self.step_label_var = tk.StringVar()

        header = ttk.Frame(self, style="Card.TFrame", padding=12)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, textvariable=self.step_label_var, style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Progressbar(header, variable=self.progress_var, maximum=100, style="Horizontal.TProgressbar").pack(
            fill=tk.X, pady=(8, 0)
        )

        self.question_var = tk.StringVar()
        ttk.Label(self, textvariable=self.question_var, wraplength=520, style="Card.TLabel").pack(
            anchor=tk.W, padx=4, pady=(0, 10)
        )

        self.options_frame = ttk.Frame(self)
        self.options_frame.pack(fill=tk.BOTH, expand=True)

        nav = ttk.Frame(self)
        nav.pack(fill=tk.X, pady=12)
        self.btn_prev = ttk.Button(nav, text="Anterior", command=self._prev_step)
        self.btn_prev.pack(side=tk.LEFT)
        self.btn_next = ttk.Button(nav, text="Siguiente", style="Accent.TButton", command=self._next_step)
        self.btn_next.pack(side=tk.RIGHT)

        self._render_step()

    def get_final_profile(self) -> dict[str, float]:
        return dict(sorted(self._scores.items(), key=lambda x: (-x[1], x[0])))

    def reset(self) -> None:
        self._step_index = 0
        self._scores.clear()
        self._selections = [None] * len(ONBOARDING_STEPS)
        self._render_step()

    def load_profile(self, profile: dict[str, float]) -> None:
        self._scores = {k: float(v) for k, v in (profile or {}).items()}
        self._step_index = 0
        self._selections = [None] * len(ONBOARDING_STEPS)
        self._render_step()

    def _render_step(self) -> None:
        step = ONBOARDING_STEPS[self._step_index]
        n = len(ONBOARDING_STEPS)
        self.step_label_var.set(f"Paso {self._step_index + 1} de {n}: {step['title']}")
        self.progress_var.set(((self._step_index + 1) / n) * 100)
        self.question_var.set(step.get("subtitle") or step.get("title") or "")

        for w in self.options_frame.winfo_children():
            w.destroy()
        self._option_buttons.clear()

        selected_idx = self._selections[self._step_index]
        for i, opt in enumerate(step["options"]):
            style = "Selected.Option.TButton" if selected_idx == i else "Option.TButton"
            btn = ttk.Button(
                self.options_frame,
                text=opt["text"],
                style=style,
                command=lambda idx=i, o=opt: self._select_option(idx, o),
            )
            btn.grid(row=i // 2, column=i % 2, sticky=tk.EW, padx=6, pady=6)
            self._option_buttons.append(btn)
        self.options_frame.columnconfigure(0, weight=1)
        self.options_frame.columnconfigure(1, weight=1)

        self.btn_prev.state(["!disabled"] if self._step_index > 0 else ["disabled"])
        self.btn_next.configure(text="Finalizar" if self._step_index >= n - 1 else "Siguiente")
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
        self._selections[self._step_index] = index
        _merge_weights(self._scores, option.get("weights", {}))
        self._render_step()

    def _prev_step(self) -> None:
        if self._step_index > 0:
            self._step_index -= 1
            self._render_step()

    def _next_step(self) -> None:
        if self._selections[self._step_index] is None:
            return
        if self._step_index < len(ONBOARDING_STEPS) - 1:
            self._step_index += 1
            self._render_step()
        elif self._on_step_change:
            self._on_step_change()