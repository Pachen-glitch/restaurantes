"""Interfaz grafica premium del sistema de recomendacion gastronomica."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

import database
import styles
from analytics_view import AnalyticsPanel
from graph_view import GraphPanel
from hero_banner import HeroBanner
from mood_selector import MoodSelector
from onboarding import ONBOARDING_STEPS, OnboardingWizard
from profile_visualizer import ProfileVisualizer
from recommendation import (
    PREF_LABELS_ES,
    obtener_usuario_detalle,
    obtener_datos_grafo,
    obtener_historial_usuario,
    obtener_usuarios,
    obtener_zonas,
    recomendar_restaurantes_inteligente,
    usuario_existe,
)
from ui_animations import LOADING_MESSAGES, LoadingOverlay, fade_in, warm_flash
from ui_widgets import HomeCard, RestaurantCard, ScrollableFrame, ShadowCard, Sidebar
from user_manager import (
    actualizar_usuario,
    crear_usuario_base,
    ensure_preference_catalog,
    generar_siguiente_user_id,
    guardar_perfil_gastronomico,
    obtener_perfil_gastronomico,
)
from restaurant_importer import import_guatemala_restaurants


class RestaurantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Savory — Guatemala City")
        self.minsize(1280, 760)
        self.geometry("1360x820")

        styles.apply_theme(self)

        self._zonas: list[str] = []
        self._usuarios: list[dict] = []
        self._current_user_id: str | None = None
        self._catalog_imported = False
        self._rec_rows: list[dict] = []
        self._pages: dict[str, ttk.Frame] = {}
        self._loading_overlay: LoadingOverlay | None = None

        self._build_layout()
        self._set_status("Iniciando...")
        self.after(100, self._startup)

    def _build_layout(self):
        self._active_user_var = tk.StringVar(value="")
        self._header_tagline_var = tk.StringVar(value="Buen apetito 🍷")

        header = tk.Frame(self, bg=styles.COLORS["header"], height=styles.SPACING["header_height"])
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Frame(header, bg=styles.COLORS["header_border"], height=1).pack(side=tk.BOTTOM, fill=tk.X)

        left_h = tk.Frame(header, bg=styles.COLORS["header"])
        left_h.pack(side=tk.LEFT, padx=styles.SPACING["page_x"], pady=18)
        tk.Label(
            left_h,
            text="Savory",
            font=styles.FONTS["brand"],
            fg=styles.COLORS["accent"],
            bg=styles.COLORS["header"],
        ).pack(anchor=tk.W)

        right_h = tk.Frame(header, bg=styles.COLORS["header"])
        right_h.pack(side=tk.RIGHT, padx=styles.SPACING["page_x"], pady=18)
        self._user_chip = tk.Label(
            right_h,
            textvariable=self._active_user_var,
            font=styles.FONTS["badge"],
            fg=styles.COLORS["text_light"],
            bg=styles.COLORS["accent2"],
            padx=12,
            pady=5,
        )
        tk.Label(
            right_h,
            text="👤",
            font=("Segoe UI", 18),
            bg=styles.COLORS["surface3"],
            fg=styles.COLORS["text"],
            padx=8,
            pady=4,
        ).pack(side=tk.RIGHT)
        tk.Label(
            right_h,
            textvariable=self._header_tagline_var,
            font=styles.FONTS["header_tag"],
            fg=styles.COLORS["muted"],
            bg=styles.COLORS["header"],
        ).pack(side=tk.RIGHT, padx=(0, 14))

        body = tk.Frame(self, bg=styles.COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True)

        self.sidebar = Sidebar(body, on_navigate=self._show_page)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.main = ttk.Frame(body, style="Content.TFrame", padding=styles.SPACING["page_pad"])
        self.main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_page_home()
        self._build_page_onboarding()
        self._build_page_profile()
        self._build_page_rec()
        self._build_page_insights()
        self._build_page_graph()
        self._build_page_settings()

        self.status_var = tk.StringVar(value="Listo")
        status = tk.Frame(self, bg=styles.COLORS["surface3"], height=28)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(
            status,
            textvariable=self.status_var,
            anchor=tk.W,
            font=styles.FONTS["small"],
            fg=styles.COLORS["muted"],
            bg=styles.COLORS["surface3"],
            padx=16,
        ).pack(fill=tk.X)

        self._show_page("home")

    def _page(self, key: str) -> ttk.Frame:
        frame = ttk.Frame(self.main, style="Content.TFrame")
        self._pages[key] = frame
        return frame

    def _show_page(self, key: str):
        if hasattr(self, "main"):
            warm_flash(self.main)
        for k, frame in self._pages.items():
            frame.pack_forget()
        page = self._pages.get(key)
        if page:
            page.pack(fill=tk.BOTH, expand=True)
            fade_in(page)
        if key == "graph":
            self._refresh_graph(self._current_user_id)
        if key == "insights" and hasattr(self, "analytics_panel"):
            if self._current_user_id:
                for i, u in enumerate(self._usuarios):
                    if u["id"] == self._current_user_id:
                        self.analytics_panel.user_cb.current(i)
                        break
            self.analytics_panel.refresh()

    def _section_title(self, parent, title: str, subtitle: str = ""):
        box = ttk.Frame(parent, style="Content.TFrame")
        box.pack(fill=tk.X, pady=(0, styles.SPACING["section_gap"]))
        ttk.Label(box, text=title, style="Hero.TLabel").pack(anchor=tk.W)
        if subtitle:
            ttk.Label(box, text=subtitle, style="Muted.TLabel").pack(anchor=tk.W, pady=(6, 0))
        return box

    def _build_page_home(self):
        f = self._page("home")
        HeroBanner(
            f,
            on_create_profile=self._start_create_profile,
            on_explore=lambda: self._nav("rec"),
        ).pack(fill=tk.X, pady=(0, 24))

        cards = ttk.Frame(f, style="Content.TFrame")
        cards.pack(fill=tk.BOTH, expand=True)
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)
        cards.columnconfigure(2, weight=1)

        for col, (icon, title, desc, action, handler) in enumerate(
            (
                ("✨", "Crear perfil", "Cuéntanos qué te gusta y descubre lugares para ti.", "Comenzar", "create"),
                ("🍽️", "Recomendaciones", "Lugares pensados para tu estilo.", "Explorar", "rec"),
                ("🧬", "Tu estilo", "Conoce tu perfil gastronómico.", "Ver perfil", "profile"),
            )
        ):
            cmd = self._start_create_profile if handler == "create" else (lambda p=handler: self._nav(p))
            card = HomeCard(cards, icon, title, desc, action, command=cmd)
            card.grid(row=0, column=col, sticky=tk.NSEW, padx=(0 if col == 0 else 10, 10 if col < 2 else 0))

    def _build_page_onboarding(self):
        f = self._page("onboarding")
        self._section_title(
            f,
            "Crear perfil gastronómico",
            "Cuéntanos qué te gusta — descubre lugares que encajen contigo.",
        )

        form_card = ShadowCard(f, padx=24, pady=18)
        form_card.pack(fill=tk.X, pady=(0, 16))
        form_inner = form_card.content()

        self.onb_id = tk.StringVar()
        self.onb_nombre = tk.StringVar()
        self.onb_presupuesto = tk.StringVar()
        self.onb_zona = tk.StringVar()

        grid = ttk.Frame(form_inner, style="Card.TFrame")
        grid.pack(fill=tk.X)
        fields = [
            ("ID (auto)", None, self.onb_id, True),
            ("Tu nombre", ttk.Entry, self.onb_nombre, False),
            ("Presupuesto (Q)", ttk.Entry, self.onb_presupuesto, False),
            ("Zona", None, self.onb_zona, False),
        ]
        for i, (label, widget_cls, var, is_label) in enumerate(fields):
            ttk.Label(grid, text=label, style="Card.TLabel").grid(row=i, column=0, sticky=tk.W, padx=4, pady=8)
            if is_label:
                ttk.Label(grid, textvariable=var, style="Step.TLabel").grid(row=i, column=1, sticky=tk.W, pady=8)
            elif widget_cls is ttk.Entry:
                widget_cls(grid, textvariable=var, width=32).grid(row=i, column=1, sticky=tk.W, pady=8)
            else:
                self.onb_zona_cb = ttk.Combobox(grid, textvariable=var, state="readonly", width=30)
                self.onb_zona_cb.grid(row=i, column=1, sticky=tk.W, pady=8)

        wizard_wrap = tk.Frame(f, bg=styles.COLORS["bg"])
        wizard_wrap.pack(fill=tk.BOTH, expand=True, pady=8)
        self.wizard = OnboardingWizard(
            wizard_wrap,
            on_step_change=self._on_wizard_step,
            on_complete=self._on_wizard_complete,
        )
        self.wizard.pack(fill=tk.BOTH, expand=True)
        self._on_wizard_step()

        actions = ttk.Frame(f, style="Content.TFrame")
        actions.pack(fill=tk.X, pady=8)
        self.btn_import_gt = ttk.Button(
            actions,
            text="Importar catálogo real (220)",
            style="Secondary.TButton",
            command=self._on_import_guatemala,
        )
        self.btn_import_gt.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            actions,
            text="Crear perfil",
            style="Accent.TButton",
            command=lambda: self._on_save_onboarding(auto_navigate=True),
        ).pack(side=tk.LEFT)

    def _build_page_profile(self):
        f = self._page("profile")
        self.profile_visualizer = ProfileVisualizer(f)
        self.profile_visualizer.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        top = ttk.Frame(f, style="Content.TFrame")
        top.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(top, text="Usuario", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.perfil_user_cb = ttk.Combobox(top, state="readonly", width=36)
        self.perfil_user_cb.pack(side=tk.LEFT)
        self.perfil_user_cb.bind("<<ComboboxSelected>>", lambda _e: self._load_perfil_user())
        ttk.Button(top, text="Repetir onboarding", style="Secondary.TButton", command=lambda: self._nav("onboarding")).pack(side=tk.LEFT, padx=12)

        body = ttk.Frame(f, style="Content.TFrame")
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        pref_card = tk.Frame(
            body,
            bg=styles.COLORS["surface2"],
            highlightbackground=styles.COLORS["card_border"],
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        pref_card.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 8))
        tk.Label(pref_card, text="Preferencias activas", font=styles.FONTS["subtitle"], bg=styles.COLORS["surface2"], fg=styles.COLORS["text"]).pack(
            anchor=tk.W, pady=(0, 8)
        )
        cols = ("preferencia", "score")
        self.perfil_tree = ttk.Treeview(pref_card, columns=cols, show="headings", height=14)
        self.perfil_tree.heading("preferencia", text="Preferencia")
        self.perfil_tree.heading("score", text="Intensidad")
        self.perfil_tree.column("preferencia", width=200)
        self.perfil_tree.column("score", width=80)
        self.perfil_tree.pack(fill=tk.BOTH, expand=True)

        edit_card = tk.Frame(
            body,
            bg=styles.COLORS["surface2"],
            highlightbackground=styles.COLORS["card_border"],
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        edit_card.grid(row=0, column=1, sticky=tk.NSEW, padx=(8, 0))
        tk.Label(edit_card, text="Datos básicos", font=styles.FONTS["subtitle"], bg=styles.COLORS["surface2"], fg=styles.COLORS["text"]).pack(
            anchor=tk.W, pady=(0, 12)
        )
        self.edit_nombre = tk.StringVar()
        self.edit_presupuesto = tk.StringVar()
        self.edit_zona = tk.StringVar()
        for label, var in (("Nombre", self.edit_nombre), ("Presupuesto", self.edit_presupuesto)):
            row = tk.Frame(edit_card, bg=styles.COLORS["surface2"])
            row.pack(fill=tk.X, pady=6)
            tk.Label(row, text=label, font=styles.FONTS["body"], bg=styles.COLORS["surface2"], width=12, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=var, width=28).pack(side=tk.LEFT)
        row = tk.Frame(edit_card, bg=styles.COLORS["surface2"])
        row.pack(fill=tk.X, pady=6)
        tk.Label(row, text="Zona", font=styles.FONTS["body"], bg=styles.COLORS["surface2"], width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.edit_zona_cb = ttk.Combobox(row, textvariable=self.edit_zona, state="readonly", width=26)
        self.edit_zona_cb.pack(side=tk.LEFT)
        ttk.Button(edit_card, text="Actualizar", style="Accent.TButton", command=self._on_update_basic).pack(anchor=tk.W, pady=(16, 0))

    def _build_page_rec(self):
        f = self._page("rec")
        self._section_title(f, "Recomendaciones", "Pensadas para tu estilo y mood del día.")

        self.mood_selector = MoodSelector(f)
        self.mood_selector.pack(fill=tk.X, pady=(0, 12))

        toolbar = ttk.Frame(f, style="Content.TFrame")
        toolbar.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(toolbar, text="Usuario", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.rec_user_cb = ttk.Combobox(toolbar, state="readonly", width=34)
        self.rec_user_cb.pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Recomendar", style="Accent.TButton", command=self._on_recomendar).pack(
            side=tk.LEFT, padx=16
        )

        self.rec_scroll = ScrollableFrame(f)
        self.rec_scroll.pack(fill=tk.BOTH, expand=True)
        self.rec_empty = tk.Label(
            self.rec_scroll.inner,
            text="Selecciona un usuario y pulsa «Recomendar»\npara descubrir lugares que encajan contigo.",
            font=styles.FONTS["body"],
            fg=styles.COLORS["muted"],
            bg=styles.COLORS["bg"],
            justify=tk.CENTER,
        )
        self.rec_empty.pack(pady=80)

    def _build_page_insights(self):
        f = self._page("insights")
        self.analytics_panel = AnalyticsPanel(f)
        self.analytics_panel.pack(fill=tk.BOTH, expand=True)

    def _build_page_graph(self):
        f = self._page("graph")
        self._section_title(f, "Mapa de afinidades", "Conexiones entre tus gustos y los lugares.")
        graph_card = tk.Frame(
            f,
            bg=styles.COLORS["graph_bg"],
            highlightbackground=styles.COLORS["card_border"],
            highlightthickness=1,
        )
        graph_card.pack(fill=tk.BOTH, expand=True)
        self.graph_panel = GraphPanel(graph_card)
        self.graph_panel.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _build_page_settings(self):
        f = self._page("settings")
        self._section_title(f, "Ajustes", "Catálogo, historial y preferencias.")

        sett = tk.Frame(
            f,
            bg=styles.COLORS["surface2"],
            highlightbackground=styles.COLORS["card_border"],
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        sett.pack(fill=tk.X, pady=(0, 16))
        tk.Label(sett, text="Catálogo de restaurantes", font=styles.FONTS["subtitle"], bg=styles.COLORS["surface2"]).pack(anchor=tk.W)
        tk.Label(
            sett,
            text="Importa más de 210 restaurantes reales de Ciudad de Guatemala (MERGE, no borra datos).",
            font=styles.FONTS["small"],
            fg=styles.COLORS["muted"],
            bg=styles.COLORS["surface2"],
            wraplength=600,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(6, 12))
        ttk.Button(sett, text="Importar catálogo", style="Accent.TButton", command=self._on_import_guatemala).pack(anchor=tk.W)

        hist_box = ttk.Frame(f, style="Content.TFrame")
        hist_box.pack(fill=tk.BOTH, expand=True)
        row = ttk.Frame(hist_box, style="Content.TFrame")
        row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row, text="Historial de visitas", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.hist_user_cb = ttk.Combobox(row, state="readonly", width=34)
        self.hist_user_cb.pack(side=tk.LEFT)
        ttk.Button(row, text="Cargar", style="Secondary.TButton", command=self._on_historial).pack(side=tk.LEFT, padx=12)

        cols = ("restaurante", "fecha", "nota", "rating", "precio", "zona", "cocinas")
        self.hist_tree = ttk.Treeview(hist_box, columns=cols, show="headings", height=12)
        for c, t in zip(cols, ("Restaurante", "Fecha", "Nota", "Rating", "Precio", "Zona", "Cocinas")):
            self.hist_tree.heading(c, text=t)
            self.hist_tree.column(c, width=110)
        self.hist_tree.pack(fill=tk.BOTH, expand=True)

    def _nav(self, page: str):
        self.sidebar.set_active(page)

    def _update_header_user(self):
        uid = self._current_user_id
        if not uid:
            self._active_user_var.set("")
            self._user_chip.pack_forget()
            self._header_tagline_var.set("Buen apetito 🍷")
            return
        name = uid
        for u in self._usuarios:
            if u["id"] == uid:
                name = u.get("nombre") or uid
                break
        first = name.split()[0] if name else uid
        self._header_tagline_var.set("Buen apetito 🍷")
        self._active_user_var.set(first)
        self._user_chip.pack(side=tk.RIGHT, padx=(0, 10))

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _run_async(self, work, on_ok=None, on_err=None, busy_msg=None):
        msg = busy_msg or LOADING_MESSAGES[0]
        self._set_status(msg)
        try:
            if self._loading_overlay and self._loading_overlay.winfo_exists():
                self._loading_overlay.close()
            self._loading_overlay = LoadingOverlay(self, message=msg)
        except tk.TclError:
            self._loading_overlay = None

        def runner():
            try:
                result = work()
                self.after(0, lambda: self._async_done(result, None, on_ok, on_err))
            except Exception as exc:
                self.after(0, lambda: self._async_done(None, exc, on_ok, on_err))

        threading.Thread(target=runner, daemon=True).start()

    def _async_done(self, result, error, on_ok, on_err):
        if self._loading_overlay and self._loading_overlay.winfo_exists():
            self._loading_overlay.close()
            self._loading_overlay = None
        if error:
            self._set_status("Error")
            if on_err:
                on_err(error)
            else:
                messagebox.showerror("Error", str(error))
            return
        self._set_status("Listo")
        if on_ok:
            on_ok(result)

    def _startup(self):
        def work():
            database.get_connection().verify_connection()
            ensure_preference_catalog()
            zonas = obtener_zonas()
            usuarios = obtener_usuarios()
            grafo = obtener_datos_grafo()
            return zonas, usuarios, grafo

        def ok(data):
            zonas, usuarios, grafo = data
            self._assign_next_user_id()
            self._zonas = zonas
            self._usuarios = usuarios
            self._refresh_reference_data()
            self.graph_panel.render(grafo)

        def err(exc):
            messagebox.showerror("Conexión", "No se pudo conectar a Neo4j:\n%s" % exc)
            self.destroy()

        self._run_async(work, on_ok=ok, on_err=err, busy_msg="Conectando con Neo4j...")

    def _refresh_reference_data(self):
        self.onb_zona_cb["values"] = self._zonas
        self.edit_zona_cb["values"] = self._zonas
        labels = ["%s — %s" % (u["id"], u["nombre"]) for u in self._usuarios]
        ids = [u["id"] for u in self._usuarios]
        for cb in (self.perfil_user_cb, self.rec_user_cb, self.hist_user_cb):
            cb["values"] = labels
        if hasattr(self, "analytics_panel"):
            self.analytics_panel.set_users(labels, ids)

    def _parse_presupuesto(self, value: str) -> int:
        try:
            p = int(str(value).strip())
            if p < 0:
                raise ValueError
            return p
        except ValueError as exc:
            raise ValueError("Presupuesto debe ser un entero positivo.") from exc

    def _refresh_graph(self, highlight_user: str | None = None):
        uid = highlight_user or self._current_user_id

        def work():
            return obtener_datos_grafo(focus_user_id=uid)

        def ok(grafo):
            highlight = ["User:%s" % uid] if uid else None
            self.graph_panel.render(grafo, highlight_nodes=highlight, focus_user_id=uid)

        self._run_async(work, on_ok=ok, busy_msg="Actualizando grafo...")

    def _reload_users(self, select_id: str | None = None, on_complete=None):
        def work():
            return obtener_usuarios()

        def ok(usuarios):
            self._usuarios = usuarios
            self._refresh_reference_data()
            if select_id:
                for i, u in enumerate(self._usuarios):
                    if u["id"] == select_id:
                        for cb in (self.perfil_user_cb, self.rec_user_cb, self.hist_user_cb):
                            cb.current(i)
                        break
            self._current_user_id = select_id
            self._update_header_user()
            self._refresh_graph(select_id)
            if on_complete:
                on_complete()

        self._run_async(work, on_ok=ok, busy_msg="Recargando usuarios...")

    def _start_create_profile(self):
        self.sidebar.set_active("onboarding")
        self._reset_onboarding_form()
        self._assign_next_user_id()

    def _reset_onboarding_form(self):
        self.onb_nombre.set("")
        self.onb_presupuesto.set("")
        self.onb_zona.set("")
        if hasattr(self, "onb_zona_cb") and self._zonas:
            self.onb_zona_cb["values"] = self._zonas
        wizard = getattr(self, "wizard", None)
        if wizard is not None:
            wizard.reset()
        self._on_wizard_step()

    def _on_wizard_step(self):
        wizard = getattr(self, "wizard", None)
        if wizard is None:
            return
        self.onb_presupuesto.set(str(wizard.get_presupuesto_sugerido()))

    def _on_wizard_complete(self):
        self.onb_presupuesto.set(str(self.wizard.get_presupuesto_sugerido()))
        self._on_save_onboarding(auto_navigate=True)

    def _assign_next_user_id(self):
        def work():
            return generar_siguiente_user_id()

        def ok(uid):
            self.onb_id.set(uid)

        self._run_async(work, on_ok=ok, busy_msg="Generando ID...")

    def _on_import_guatemala(self):
        if self._catalog_imported:
            messagebox.showinfo("Catálogo", "El catálogo ya fue importado en esta sesión.")
            return

        def work():
            result = import_guatemala_restaurants()
            ensure_preference_catalog()
            return result

        def ok(result):
            self._catalog_imported = True
            if hasattr(self, "btn_import_gt"):
                self.btn_import_gt.state(["disabled"])
            imported = result.get("imported", 0) if isinstance(result, dict) else int(result or 0)
            removed = 0
            if isinstance(result, dict):
                removed = int(result.get("legacy_removed", 0) or 0) + int(result.get("stale_removed", 0) or 0)
            messagebox.showinfo(
                "Catálogo",
                "Importados %d restaurantes reales.\nEliminados %d registros antiguos sin visitas."
                % (imported, removed),
            )
            self._zonas = obtener_zonas()
            self._refresh_reference_data()
            self._refresh_graph(self._current_user_id)

        self._run_async(work, on_ok=ok, busy_msg="Importando catálogo...")

    def _render_rec_cards(self, rows: list[dict]):
        self.rec_scroll.clear()
        if not rows:
            lbl = tk.Label(
                self.rec_scroll.inner,
                text="Sin recomendaciones para este usuario.\nPrueba completar el onboarding o ampliar presupuesto.",
                font=styles.FONTS["body"],
                fg=styles.COLORS["muted"],
                bg=styles.COLORS["bg"],
                justify=tk.CENTER,
            )
            lbl.pack(pady=80)
            return
        for r in rows:
            card = RestaurantCard(self.rec_scroll.inner, r, pref_labels=PREF_LABELS_ES)
            card.pack(fill=tk.X, pady=8, padx=4)

    def _on_save_onboarding(self, auto_navigate: bool = False):
        uid = self.onb_id.get().strip() or generar_siguiente_user_id()
        nombre = self.onb_nombre.get().strip()
        zona = self.onb_zona.get().strip()
        if not uid or not nombre or not zona:
            messagebox.showwarning("Validación", "Completa nombre y zona.")
            return
        if any(s is None for s in self.wizard._selections):
            messagebox.showwarning(
                "Perfil",
                "Completa los %d pasos del cuestionario." % len(ONBOARDING_STEPS),
            )
            return
        try:
            presupuesto = self._parse_presupuesto(self.onb_presupuesto.get())
        except ValueError as exc:
            messagebox.showwarning("Validación", str(exc))
            return
        profile = self.wizard.get_final_profile()

        def work():
            if not usuario_existe(uid):
                crear_usuario_base(uid, nombre, presupuesto, zona)
            guardar_perfil_gastronomico(uid, profile)
            return uid

        def ok(new_id):
            self._current_user_id = new_id
            self._update_header_user()

            def after_reload():
                if auto_navigate:
                    self.sidebar.set_active("rec")
                    self._nav("rec")
                    self._on_recomendar()
                else:
                    messagebox.showinfo("¡Listo!", "Perfil guardado para %s." % new_id)

            self._reload_users(select_id=new_id, on_complete=after_reload)

        self._run_async(work, on_ok=ok, busy_msg="Guardando tu perfil…")

    def _current_user_id_from_cb(self, combobox: ttk.Combobox) -> str | None:
        idx = combobox.current()
        if idx < 0 or idx >= len(self._usuarios):
            return None
        return self._usuarios[idx]["id"]

    def _load_perfil_user(self):
        uid = self._current_user_id_from_cb(self.perfil_user_cb)
        if not uid:
            return
        self._current_user_id = uid
        self._update_header_user()

        def work():
            detalle = obtener_usuario_detalle(uid)
            perfil = obtener_perfil_gastronomico(uid)
            return detalle, perfil

        def ok(data):
            detalle, perfil = data
            if not detalle:
                messagebox.showwarning("Usuario", "Usuario no encontrado.")
                return
            self.edit_nombre.set(detalle.get("nombre") or "")
            self.edit_presupuesto.set(str(detalle.get("presupuesto") or ""))
            self.edit_zona.set(detalle.get("zona") or "")
            for item in self.perfil_tree.get_children():
                self.perfil_tree.delete(item)
            for pref, score in sorted(perfil.items(), key=lambda x: -x[1]):
                self.perfil_tree.insert("", tk.END, values=(pref, round(score, 1)))
            self.onb_id.set(detalle["id"])
            self.onb_nombre.set(detalle.get("nombre") or "")
            self.onb_presupuesto.set(str(detalle.get("presupuesto") or ""))
            self.onb_zona.set(detalle.get("zona") or "")
            self.wizard.load_profile(perfil)
            self.profile_visualizer.render(perfil)
            self.graph_panel.highlight_nodes(["User:%s" % uid])

        self._run_async(work, on_ok=ok, busy_msg="Cargando perfil...")

    def _on_update_basic(self):
        uid = self._current_user_id_from_cb(self.perfil_user_cb)
        if not uid:
            messagebox.showwarning("Perfil", "Selecciona un usuario.")
            return
        nombre = self.edit_nombre.get().strip()
        zona = self.edit_zona.get().strip()
        if not nombre or not zona:
            messagebox.showwarning("Validación", "Nombre y zona son obligatorios.")
            return
        try:
            presupuesto = self._parse_presupuesto(self.edit_presupuesto.get())
        except ValueError as exc:
            messagebox.showwarning("Validación", str(exc))
            return

        def work():
            det = obtener_usuario_detalle(uid)
            cocinas = (det or {}).get("cocinas") or []
            actualizar_usuario(uid, nombre, presupuesto, zona, cocinas)
            profile = self.wizard.get_final_profile()
            if profile:
                guardar_perfil_gastronomico(uid, profile)
            return uid

        def ok(updated_id):
            messagebox.showinfo("Actualizado", "Datos guardados correctamente.")
            self._reload_users(select_id=updated_id)

        self._run_async(work, on_ok=ok, busy_msg="Actualizando...")

    def _on_recomendar(self):
        uid = self._current_user_id_from_cb(self.rec_user_cb)
        if not uid:
            messagebox.showwarning("Recomendador", "Selecciona un usuario.")
            return
        self._current_user_id = uid
        self._update_header_user()

        def work():
            mood = self.mood_selector.selected_mood if hasattr(self, "mood_selector") else None
            return recomendar_restaurantes_inteligente(uid, mood=mood)

        def ok(rows):
            self._rec_rows = rows or []
            self._render_rec_cards(self._rec_rows)
            self._refresh_graph(uid)
            warm_flash(self.rec_scroll)

        self._run_async(work, on_ok=ok, busy_msg="Buscando lugares para ti…")

    def _on_historial(self):
        uid = self._current_user_id_from_cb(self.hist_user_cb)
        if not uid:
            messagebox.showwarning("Historial", "Selecciona un usuario.")
            return
        self._current_user_id = uid
        self._update_header_user()

        def work():
            return obtener_historial_usuario(uid)

        def ok(rows):
            for item in self.hist_tree.get_children():
                self.hist_tree.delete(item)
            for v in rows:
                cocinas = ", ".join(v.get("cocinas") or [])
                self.hist_tree.insert(
                    "",
                    tk.END,
                    values=(
                        v.get("nombre"),
                        v.get("fecha"),
                        v.get("calificacion_personal"),
                        v.get("rating"),
                        v.get("precio"),
                        v.get("zona") or "",
                        cocinas,
                    ),
                )
            self._refresh_graph(uid)

        self._run_async(work, on_ok=ok, busy_msg="Cargando historial...")


def main():
    app = RestaurantApp()
    app.mainloop()
    database.close()


if __name__ == "__main__":
    main()
