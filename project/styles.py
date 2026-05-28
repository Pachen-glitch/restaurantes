"""Tema visual gastronomico premium para la aplicacion Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

COLORS = {
    "bg": "#FDF2E9",
    "surface": "#FFFAF5",
    "surface2": "#FFFFFF",
    "surface3": "#F5E6D8",
    "sidebar": "#2C2C2C",
    "sidebar_hover": "#3D3D3D",
    "sidebar_active": "#C0392B",
    "header": "#FFFFFF",
    "header_border": "#E8D5C4",
    "text": "#2C2C2C",
    "text_light": "#FFFAF5",
    "subtext": "#8B4513",
    "muted": "#A0826D",
    "accent": "#C0392B",
    "accent2": "#E67E22",
    "accent_light": "#FADBD8",
    "accent_warm": "#F5B041",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#C0392B",
    "user": "#7B241C",
    "restaurant": "#D4AC0D",
    "cuisine": "#E67E22",
    "zone": "#6E2C00",
    "preference": "#7D3C98",
    "compat_gold": "#D4AC0D",
    "compat_orange": "#E67E22",
    "compat_soft": "#E59866",
    "hero_overlay": "#FFFAF5",
    "glow": "#F5B041",
    "card_hover": "#FFF5EB",
    "card_border": "#E8D5C4",
    "card_shadow": "#D7C4B0",
    "badge": "#E67E22",
    "badge_soft": "#FDEBD0",
    "progress_bg": "#E8D5C4",
    "progress_fill": "#C0392B",
    "graph_bg": "#1A120B",
    "graph_edge": "#C49A6C",
}

def compat_color(pct: float) -> str:
    if pct >= 90:
        return COLORS["compat_gold"]
    if pct >= 70:
        return COLORS["compat_orange"]
    return COLORS["compat_soft"]


FONTS = {
    "title": ("Segoe UI", 22, "bold"),
    "subtitle": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 11),
    "small": ("Segoe UI", 9),
    "card": ("Segoe UI", 12),
    "card_title": ("Segoe UI", 16, "bold"),
    "hero": ("Segoe UI", 28, "bold"),
    "question": ("Segoe UI", 17),
    "nav": ("Segoe UI", 11),
    "badge": ("Segoe UI", 9, "bold"),
    "header_tag": ("Segoe UI", 10),
}


def apply_theme(root: tk.Misc) -> ttk.Style:
    style = ttk.Style(root)
    style.theme_use("clam")
    c = COLORS

    style.configure(".", background=c["bg"], foreground=c["text"], font=FONTS["body"])
    style.configure("TFrame", background=c["bg"])
    style.configure("Surface.TFrame", background=c["surface"])
    style.configure("Card.TFrame", background=c["surface2"], relief="flat")
    style.configure("Content.TFrame", background=c["bg"])

    style.configure("TLabel", background=c["bg"], foreground=c["text"])
    style.configure("Surface.TLabel", background=c["surface"], foreground=c["text"])
    style.configure("Card.TLabel", background=c["surface2"], foreground=c["text"], font=FONTS["card"])
    style.configure("Title.TLabel", background=c["header"], foreground=c["accent"], font=FONTS["title"])
    style.configure("Subtitle.TLabel", background=c["bg"], foreground=c["subtext"], font=FONTS["subtitle"])
    style.configure("Muted.TLabel", background=c["surface2"], foreground=c["muted"], font=FONTS["small"])
    style.configure("Hero.TLabel", background=c["bg"], foreground=c["text"], font=FONTS["hero"])
    style.configure("Question.TLabel", background=c["bg"], foreground=c["text"], font=FONTS["question"])
    style.configure("Step.TLabel", background=c["surface2"], foreground=c["accent"], font=FONTS["subtitle"])

    style.configure(
        "TButton",
        background=c["surface2"],
        foreground=c["text"],
        padding=(16, 10),
        font=FONTS["body"],
        borderwidth=1,
    )
    style.map(
        "TButton",
        background=[("active", c["card_hover"]), ("pressed", c["surface3"])],
        relief=[("pressed", "sunken"), ("!pressed", "flat")],
    )

    style.configure(
        "Accent.TButton",
        background=c["accent"],
        foreground=c["text_light"],
        padding=(18, 12),
        font=("Segoe UI", 11, "bold"),
    )
    style.map("Accent.TButton", background=[("active", c["accent2"])])

    style.configure(
        "Secondary.TButton",
        background=c["surface3"],
        foreground=c["text"],
        padding=(14, 10),
    )
    style.map("Secondary.TButton", background=[("active", c["card_hover"])])

    style.configure(
        "OptionCard.TButton",
        background=c["surface2"],
        foreground=c["text"],
        padding=(22, 18),
        font=FONTS["card"],
        borderwidth=1,
    )
    style.map(
        "OptionCard.TButton",
        background=[("active", c["card_hover"]), ("pressed", c["accent_light"])],
    )
    style.configure(
        "Selected.OptionCard.TButton",
        background=c["accent"],
        foreground=c["text_light"],
        font=("Segoe UI", 12, "bold"),
    )
    style.map("Selected.OptionCard.TButton", background=[("active", c["accent2"])])

    style.configure("TEntry", fieldbackground=c["surface2"], foreground=c["text"], insertcolor=c["text"])
    style.configure(
        "TCombobox",
        fieldbackground=c["surface2"],
        foreground=c["text"],
        background=c["surface2"],
        arrowcolor=c["accent"],
    )

    style.configure(
        "Treeview",
        background=c["surface2"],
        foreground=c["text"],
        fieldbackground=c["surface2"],
        rowheight=32,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=c["surface3"],
        foreground=c["subtext"],
        font=("Segoe UI", 10, "bold"),
    )

    style.configure(
        "Horizontal.TProgressbar",
        troughcolor=c["progress_bg"],
        background=c["progress_fill"],
        thickness=12,
        borderwidth=0,
    )
    style.configure("Vertical.TScrollbar", background=c["surface3"], troughcolor=c["bg"])
    style.configure("Horizontal.TPanedwindow", background=c["bg"])

    root.configure(bg=c["bg"])
    return style
