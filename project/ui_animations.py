"""Animaciones y microinteracciones simuladas para Tkinter."""

from __future__ import annotations

import tkinter as tk

from styles import COLORS, FONTS

LOADING_MESSAGES = [
    "Analizando afinidad gastronómica…",
    "Buscando experiencias compatibles…",
    "Calibrando tu mood culinario…",
    "Explorando sabores en Ciudad de Guatemala…",
]


def fade_in(widget: tk.Misc, steps: int = 6, delay_ms: int = 35, on_done=None) -> None:
    """Simula fade-in cambiando opacidad via color de fondo (widgets tk)."""
    if not widget.winfo_exists():
        return
    try:
        widget.update_idletasks()
    except tk.TclError:
        return

    try:
        bg = widget.cget("bg")
    except tk.TclError:
        if on_done:
            on_done()
        return
    palette = [COLORS["bg"], COLORS["surface"], bg]

    def step(i=0):
        if not widget.winfo_exists():
            return
        if i < len(palette):
            try:
                widget.configure(bg=palette[min(i, len(palette) - 1)])
            except tk.TclError:
                pass
            widget.after(delay_ms, lambda: step(i + 1))
        elif on_done:
            on_done()

    step(0)


def warm_flash(parent: tk.Misc, duration_ms: int = 220) -> None:
    """Destello cálido breve sobre un contenedor."""
    if not parent.winfo_exists():
        return
    overlay = tk.Frame(parent, bg=COLORS["accent_warm"])
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    def remove():
        if overlay.winfo_exists():
            overlay.destroy()

    parent.after(duration_ms, remove)


def slide_replace(hide_widget: tk.Misc, show_widget: tk.Misc, parent: tk.Misc) -> None:
    """Transición suave: oculta uno y muestra otro con flash cálido."""
    hide_widget.pack_forget()
    warm_flash(parent)
    show_widget.pack(fill=tk.BOTH, expand=True)
    fade_in(show_widget)


class LoadingOverlay(tk.Toplevel):
    """Overlay elegante de carga."""

    def __init__(self, master, message: str = LOADING_MESSAGES[0]):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg=COLORS["sidebar"])
        self.attributes("-alpha", 0.92)
        self._message_var = tk.StringVar(value=message)
        self._msg_index = 0

        w, h = 420, 120
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 2
        self.geometry("%dx%d+%d+%d" % (w, h, max(0, x), max(0, y)))

        box = tk.Frame(self, bg=COLORS["sidebar"], padx=24, pady=20)
        box.pack(fill=tk.BOTH, expand=True)
        tk.Label(box, text="🍷 Savory", font=FONTS["subtitle"], fg=COLORS["text_light"], bg=COLORS["sidebar"]).pack(anchor=tk.W)
        tk.Label(
            box,
            textvariable=self._message_var,
            font=FONTS["body"],
            fg=COLORS["accent_warm"],
            bg=COLORS["sidebar"],
        ).pack(anchor=tk.W, pady=(12, 0))
        self._progress = tk.Frame(box, bg=COLORS["accent2"], height=3)
        self._progress.pack(fill=tk.X, pady=(16, 0))
        self._animate_bar()
        self._rotate_messages()

    def _animate_bar(self, step=0):
        if not self.winfo_exists():
            return
        width = 0.15 + (step % 20) * 0.04
        self._progress.place(relx=0, rely=1.0, relwidth=min(1.0, width), anchor=tk.SW)
        self.after(80, lambda: self._animate_bar(step + 1))

    def _rotate_messages(self):
        if not self.winfo_exists():
            return
        self._msg_index = (self._msg_index + 1) % len(LOADING_MESSAGES)
        self._message_var.set(LOADING_MESSAGES[self._msg_index])
        self.after(1400, self._rotate_messages)

    def close(self):
        if self.winfo_exists():
            self.destroy()


def bind_hover_glow(widget: tk.Misc, normal_border: str, glow_border: str | None = None) -> None:
    """Microinteracción de glow en hover para frames con highlightthickness."""
    glow = glow_border or COLORS["accent2"]

    def on_enter(_e=None):
        try:
            widget.configure(highlightbackground=glow)
        except tk.TclError:
            pass

    def on_leave(_e=None):
        try:
            widget.configure(highlightbackground=normal_border)
        except tk.TclError:
            pass

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
