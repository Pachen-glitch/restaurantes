"""Tema visual moderno dark mode para la aplicacion Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

COLORS = {
    "bg": "#11111b",
    "surface": "#1e1e2e",
    "surface2": "#313244",
    "surface3": "#45475a",
    "text": "#cdd6f4",
    "subtext": "#a6adc8",
    "accent": "#89b4fa",
    "accent2": "#cba6f7",
    "success": "#a6e3a1",
    "warning": "#f9e2af",
    "danger": "#f38ba8",
    "user": "#4a9eff",
    "restaurant": "#4ade80",
    "cuisine": "#fb923c",
    "zone": "#f87171",
    "preference": "#c084fc",
    "card_hover": "#3b3f55",
    "card_border": "#585b70",
}

FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "card": ("Segoe UI", 11),
    "card_title": ("Segoe UI", 11, "bold"),
}


def apply_theme(root: tk.Misc) -> ttk.Style:
    style = ttk.Style(root)
    style.theme_use("clam")
    c = COLORS

    style.configure(".", background=c["surface"], foreground=c["text"], font=FONTS["body"])
    style.configure("TFrame", background=c["surface"])
    style.configure("Card.TFrame", background=c["surface2"], relief="flat")
    style.configure("TLabel", background=c["surface"], foreground=c["text"])
    style.configure("Title.TLabel", background=c["surface"], foreground=c["text"], font=FONTS["title"])
    style.configure("Subtitle.TLabel", background=c["surface"], foreground=c["subtext"], font=FONTS["subtitle"])
    style.configure("Muted.TLabel", background=c["surface2"], foreground=c["subtext"], font=FONTS["small"])
    style.configure("Card.TLabel", background=c["surface2"], foreground=c["text"], font=FONTS["card"])

    style.configure(
        "TButton", background=c["surface2"], foreground=c["text"], padding=(14, 8), font=FONTS["body"]
    )
    style.map(
        "TButton",
        background=[("active", c["card_hover"]), ("pressed", c["accent"])],
        relief=[("pressed", "sunken"), ("!pressed", "flat")],
    )

    style.configure(
        "Accent.TButton", background=c["accent"], foreground=c["bg"], padding=(16, 10), font=("Segoe UI", 10, "bold")
    )
    style.map("Accent.TButton", background=[("active", c["accent2"])])

    style.configure(
        "Option.TButton", background=c["surface2"], foreground=c["text"], padding=(12, 10), font=FONTS["card"]
    )
    style.map("Option.TButton", background=[("active", c["card_hover"])])
    style.configure("Selected.Option.TButton", background=c["accent"], foreground=c["bg"])

    style.configure(
        "OptionCard.TButton",
        background=c["surface2"],
        foreground=c["text"],
        padding=(16, 14),
        font=FONTS["card_title"],
        borderwidth=1,
    )
    style.map(
        "OptionCard.TButton",
        background=[("active", c["card_hover"]), ("pressed", c["surface3"])],
        relief=[("active", "raised")],
    )
    style.configure(
        "Selected.OptionCard.TButton",
        background=c["accent"],
        foreground=c["bg"],
        borderwidth=2,
    )
    style.map("Selected.OptionCard.TButton", background=[("active", c["accent2"])])

    style.configure("TEntry", fieldbackground=c["surface2"], foreground=c["text"], insertcolor=c["text"])
    style.configure("TCombobox", fieldbackground=c["surface2"], foreground=c["text"], background=c["surface2"])
    style.configure("TNotebook", background=c["surface"], borderwidth=0)
    style.configure("TNotebook.Tab", background=c["surface2"], foreground=c["text"], padding=[14, 8])
    style.map("TNotebook.Tab", background=[("selected", c["accent"])], foreground=[("selected", c["bg"])])
    style.configure(
        "Treeview", background=c["surface2"], foreground=c["text"], fieldbackground=c["surface2"], rowheight=28
    )
    style.configure("Treeview.Heading", background=c["surface3"], foreground=c["text"], font=("Segoe UI", 9, "bold"))
    style.configure("Horizontal.TProgressbar", troughcolor=c["surface2"], background=c["accent"], thickness=10)
    style.configure("Horizontal.TPanedwindow", background=c["surface"])
    style.configure("Vertical.TScrollbar", background=c["surface2"])
    root.configure(bg=c["surface"])
    return style