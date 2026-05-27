"""Interfaz grafica del sistema de recomendacion de restaurantes."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

import database
import styles
from graph_view import GraphPanel
from onboarding import OnboardingWizard
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
        self.title("Restaurantes IA - Guatemala City")
        self.minsize(1280, 720)
        self.geometry("1320x760")

        styles.apply_theme(self)

        self._zonas: list[str] = []
        self._usuarios: list[dict] = []
        self._current_user_id: str | None = None
        self._catalog_imported = False
        self._rec_rows: list[dict] = []

        self._build_layout()
        self._set_status("Iniciando...")
        self.after(100, self._startup)

    def _build_layout(self):
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)
        ttk.Label(header, text="Restaurantes IA", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Perfil gastronomico, catalogo Guatemala (210+) y grafo Neo4j",
            style="Muted.TLabel",
        ).pack(anchor=tk.W, pady=(2, 0))

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        left = ttk.Frame(paned)
        right = ttk.Frame(paned, width=380)
        paned.add(left, weight=7)
        paned.add(right, weight=3)

        self.notebook = ttk.Notebook(left)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._tab_onb = ttk.Frame(self.notebook)
        self._tab_perfil = ttk.Frame(self.notebook)
        self._tab_rec = ttk.Frame(self.notebook)
        self._tab_hist = ttk.Frame(self.notebook)
        self.notebook.add(self._tab_onb, text="Onboarding")
        self.notebook.add(self._tab_perfil, text="Perfil & Editar")
        self.notebook.add(self._tab_rec, text="Recomendador IA")
        self.notebook.add(self._tab_hist, text="Historial")

        self._build_tab_onboarding()
        self._build_tab_perfil()
        self._build_tab_rec()
        self._build_tab_hist()

        ttk.Label(right, text="Grafo Neo4j", style="Subtitle.TLabel").pack(anchor=tk.W, padx=4, pady=(0, 4))
        self.graph_panel = GraphPanel(right)
        self.graph_panel.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(self, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN).pack(
            fill=tk.X, side=tk.BOTTOM, padx=8, pady=(0, 6)
        )

    def _build_tab_onboarding(self):
        f = self._tab_onb
        self.onb_id = tk.StringVar()
        self.onb_nombre = tk.StringVar()
        self.onb_presupuesto = tk.StringVar()
        self.onb_zona = tk.StringVar()

        form = ttk.Frame(f, padding=12)
        form.pack(fill=tk.X)
        ttk.Label(form, textvariable=self.onb_id, style="Subtitle.TLabel").grid(row=0, column=1, sticky=tk.W, pady=6); ttk.Label(form, text="ID usuario (auto)").grid(row=0, column=0, sticky=tk.W, padx=12, pady=6)
        self._form_row(form, 1, "Nombre", ttk.Entry(form, textvariable=self.onb_nombre, width=30))
        self._form_row(form, 2, "Presupuesto (Q)", ttk.Entry(form, textvariable=self.onb_presupuesto, width=30))
        self.onb_zona_cb = ttk.Combobox(form, textvariable=self.onb_zona, state="readonly", width=28)
        self._form_row(form, 3, "Zona", self.onb_zona_cb)

        self.wizard = OnboardingWizard(f, on_step_change=self._on_wizard_step, on_complete=self._on_wizard_complete, padding=12)
        self.wizard.pack(fill=tk.BOTH, expand=True)

        actions = ttk.Frame(f, padding=12)
        actions.pack(fill=tk.X)
        self.btn_import_gt = ttk.Button(
            actions,
            text="Importar catalogo Guatemala (210+)",
            command=self._on_import_guatemala,
        )
        self.btn_import_gt.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(actions, text="Guardar perfil y usuario", style="Accent.TButton", command=self._on_save_onboarding).pack(
            side=tk.LEFT
        )

    def _build_tab_perfil(self):
        f = self._tab_perfil
        self.perfil_user_cb = ttk.Combobox(f, state="readonly", width=32)
        self.perfil_user_cb.bind("<<ComboboxSelected>>", lambda _e: self._load_perfil_user())
        self._form_row(f, 0, "Usuario", self.perfil_user_cb)

        ttk.Button(f, text="Repetir onboarding", command=lambda: self.notebook.select(self._tab_onb)).grid(
            row=1, column=1, sticky=tk.W, pady=8
        )

        cols = ("preferencia", "score")
        self.perfil_tree = ttk.Treeview(f, columns=cols, show="headings", height=16)
        self.perfil_tree.heading("preferencia", text="Preferencia")
        self.perfil_tree.heading("score", text="Score")
        self.perfil_tree.column("preferencia", width=220)
        self.perfil_tree.column("score", width=80)
        self.perfil_tree.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=12, pady=8)
        f.rowconfigure(2, weight=1)
        f.columnconfigure(1, weight=1)

        self.edit_nombre = tk.StringVar()
        self.edit_presupuesto = tk.StringVar()
        self.edit_zona = tk.StringVar()
        self._form_row(f, 3, "Nombre", ttk.Entry(f, textvariable=self.edit_nombre, width=30))
        self.edit_zona_cb = ttk.Combobox(f, textvariable=self.edit_zona, state="readonly", width=28)
        self._form_row(f, 4, "Zona", self.edit_zona_cb)
        self._form_row(f, 5, "Presupuesto", ttk.Entry(f, textvariable=self.edit_presupuesto, width=30))
        ttk.Button(f, text="Actualizar datos basicos", command=self._on_update_basic).grid(
            row=6, column=1, sticky=tk.W, pady=12
        )

    def _build_tab_rec(self):
        f = self._tab_rec
        self.rec_user_cb = ttk.Combobox(f, state="readonly", width=32)
        self._form_row(f, 0, "Usuario", self.rec_user_cb)
        ttk.Button(f, text="Recomendar con IA", style="Accent.TButton", command=self._on_recomendar).grid(
            row=1, column=1, sticky=tk.W, pady=10
        )
        cols = ("nombre", "score_total", "compatibilidad_pct", "similares", "rating", "precio", "zona")
        self.rec_tree = ttk.Treeview(f, columns=cols, show="headings", height=10)
        headings = {
            "nombre": "Restaurante",
            "score_total": "Score IA",
            "compatibilidad_pct": "Compat %",
            "similares": "Similares",
            "rating": "Rating",
            "precio": "Precio",
            "zona": "Zona",
        }
        for c in cols:
            self.rec_tree.heading(c, text=headings[c])
            w = 150 if c == "nombre" else 95
            self.rec_tree.column(c, width=w)
        self.rec_tree.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=12, pady=(8, 4))
        self.rec_tree.bind("<<TreeviewSelect>>", self._on_rec_select)
        self.rec_explain = tk.Text(f, height=8, wrap=tk.WORD, bg=styles.COLORS["surface2"], fg=styles.COLORS["text"])
        self.rec_explain.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, padx=12, pady=(0, 8))
        f.rowconfigure(2, weight=2)
        f.rowconfigure(3, weight=1)
        f.columnconfigure(1, weight=1)

    def _build_tab_hist(self):
        f = self._tab_hist
        self.hist_user_cb = ttk.Combobox(f, state="readonly", width=32)
        self._form_row(f, 0, "Usuario", self.hist_user_cb)
        ttk.Button(f, text="Cargar historial", command=self._on_historial).grid(row=1, column=1, sticky=tk.W, pady=10)
        cols = ("restaurante", "fecha", "nota", "rating", "precio", "zona", "cocinas")
        self.hist_tree = ttk.Treeview(f, columns=cols, show="headings", height=14)
        for c, t in zip(
            cols,
            ("Restaurante", "Fecha", "Nota", "Rating", "Precio", "Zona", "Cocinas"),
        ):
            self.hist_tree.heading(c, text=t)
            self.hist_tree.column(c, width=110)
        self.hist_tree.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=12, pady=8)
        f.rowconfigure(2, weight=1)
        f.columnconfigure(1, weight=1)

    def _form_row(self, parent, row, label, widget):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=12, pady=6)
        widget.grid(row=row, column=1, sticky=tk.W, pady=6)

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _run_async(self, work, on_ok=None, on_err=None, busy_msg="Procesando..."):
        self._set_status(busy_msg)

        def runner():
            try:
                result = work()
                self.after(0, lambda: self._async_done(result, None, on_ok, on_err))
            except Exception as exc:
                self.after(0, lambda: self._async_done(None, exc, on_ok, on_err))

        threading.Thread(target=runner, daemon=True).start()

    def _async_done(self, result, error, on_ok, on_err):
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
            messagebox.showerror("Conexion", f"No se pudo conectar a Neo4j:\n{exc}")
            self.destroy()

        self._run_async(work, on_ok=ok, on_err=err, busy_msg="Conectando Neo4j y catalogo...")

    def _refresh_reference_data(self):
        self.onb_zona_cb["values"] = self._zonas
        self.edit_zona_cb["values"] = self._zonas
        labels = [f"{u['id']} - {u['nombre']}" for u in self._usuarios]
        for cb in (self.perfil_user_cb, self.rec_user_cb, self.hist_user_cb):
            cb["values"] = labels

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
            highlight = [f"User:{uid}"] if uid else None
            self.graph_panel.render(grafo, highlight_nodes=highlight, focus_user_id=uid)

        self._run_async(work, on_ok=ok, busy_msg="Actualizando grafo...")

    def _reload_users(self, select_id: str | None = None):
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
            self._refresh_graph(select_id)

        self._run_async(work, on_ok=ok, busy_msg="Recargando usuarios...")

    def _on_wizard_step(self):
        self.onb_presupuesto.set(str(self.wizard.get_presupuesto_sugerido()))

    def _on_wizard_complete(self):
        self.onb_presupuesto.set(str(self.wizard.get_presupuesto_sugerido()))
        if messagebox.askyesno("Onboarding", "Perfil listo. Desea guardar el usuario ahora?"):
            self._on_save_onboarding()

    def _assign_next_user_id(self):
        def work():
            return generar_siguiente_user_id()

        def ok(uid):
            self.onb_id.set(uid)

        self._run_async(work, on_ok=ok, busy_msg="Generando ID de usuario...")

    def _on_import_guatemala(self):
        if self._catalog_imported:
            messagebox.showinfo("Importacion", "El catalogo Guatemala ya fue importado en esta sesion.")
            return

        def work():
            count = import_guatemala_restaurants()
            ensure_preference_catalog()
            return count

        def ok(count):
            self._catalog_imported = True
            self.btn_import_gt.state(["disabled"])
            messagebox.showinfo("Importacion", "Importados %d restaurantes (MERGE)." % count)
            self._zonas = obtener_zonas()
            self._refresh_reference_data()
            self._refresh_graph(self._current_user_id)

        self._run_async(work, on_ok=ok, busy_msg="Importando catalogo Guatemala...")

    def _on_rec_select(self, _event=None):
        sel = self.rec_tree.selection()
        if not sel:
            return
        idx = self.rec_tree.index(sel[0])
        if idx < 0 or idx >= len(self._rec_rows):
            return
        row = self._rec_rows[idx]
        lines = row.get("explicacion") or []
        coincidencias = row.get("coincidencias") or []
        if lines:
            text = lines[0] + "\n"
            text += "\n".join("- " + line for line in lines[1:])
        else:
            text = ""
        if coincidencias:
            labels = [PREF_LABELS_ES.get(p, p.replace("_", " ")) for p in coincidencias[:6]]
            text += "\n\nPreferencias coincidentes: " + ", ".join(labels)
        self.rec_explain.delete("1.0", tk.END)
        self.rec_explain.insert(tk.END, text or "Sin explicacion disponible.")

    def _on_save_onboarding(self):
        uid = self.onb_id.get().strip() or generar_siguiente_user_id()
        nombre = self.onb_nombre.get().strip()
        zona = self.onb_zona.get().strip()
        if not uid or not nombre or not zona:
            messagebox.showwarning("Validacion", "Complete ID, nombre y zona.")
            return
        if any(s is None for s in self.wizard._selections):
            messagebox.showwarning("Onboarding", "Complete los 7 pasos del cuestionario.")
            return
        try:
            presupuesto = self._parse_presupuesto(self.onb_presupuesto.get())
        except ValueError as exc:
            messagebox.showwarning("Validacion", str(exc))
            return
        profile = self.wizard.get_final_profile()

        def work():
            if not usuario_existe(uid):
                crear_usuario_base(uid, nombre, presupuesto, zona)
            guardar_perfil_gastronomico(uid, profile)
            return uid

        def ok(new_id):
            self._current_user_id = new_id
            messagebox.showinfo("Exito", f"Perfil gastronomico guardado para {new_id}.")
            self._reload_users(select_id=new_id)

        self._run_async(work, on_ok=ok, busy_msg="Guardando usuario y perfil...")

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

        def work():
            from recommendation import obtener_usuario_detalle

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
            self.graph_panel.highlight_nodes([f"User:{uid}"])

        self._run_async(work, on_ok=ok, busy_msg="Cargando perfil...")

    def _on_update_basic(self):
        uid = self._current_user_id_from_cb(self.perfil_user_cb)
        if not uid:
            messagebox.showwarning("Perfil", "Seleccione un usuario.")
            return
        nombre = self.edit_nombre.get().strip()
        zona = self.edit_zona.get().strip()
        if not nombre or not zona:
            messagebox.showwarning("Validacion", "Nombre y zona son obligatorios.")
            return
        try:
            presupuesto = self._parse_presupuesto(self.edit_presupuesto.get())
        except ValueError as exc:
            messagebox.showwarning("Validacion", str(exc))
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
            messagebox.showinfo("Exito", "Datos actualizados.")
            self._reload_users(select_id=updated_id)

        self._run_async(work, on_ok=ok, busy_msg="Actualizando usuario...")

    def _on_recomendar(self):
        uid = self._current_user_id_from_cb(self.rec_user_cb)
        if not uid:
            messagebox.showwarning("Recomendador", "Seleccione un usuario.")
            return
        self._current_user_id = uid

        def work():
            return recomendar_restaurantes_inteligente(uid)

        def ok(rows):
            self._rec_rows = rows or []
            for item in self.rec_tree.get_children():
                self.rec_tree.delete(item)
            for r in rows:
                self.rec_tree.insert(
                    "",
                    tk.END,
                    values=(
                        r.get("nombre"),
                        r.get("score_total"),
                        r.get("compatibilidad_pct", r.get("match_pref")),
                        r.get("similares", r.get("usuarios_similares")),
                        r.get("rating"),
                        r.get("precio"),
                        r.get("zona") or "",
                    ),
                )
            self.rec_explain.delete("1.0", tk.END)
            children = self.rec_tree.get_children()
            if children:
                self.rec_tree.selection_set(children[0])
                self.rec_tree.focus(children[0])
                self._on_rec_select()
            if not rows:
                messagebox.showinfo("Recomendador", "Sin recomendaciones para este usuario.")

        self._run_async(work, on_ok=ok, busy_msg="Calculando recomendaciones IA...")

    def _on_historial(self):
        uid = self._current_user_id_from_cb(self.hist_user_cb)
        if not uid:
            messagebox.showwarning("Historial", "Seleccione un usuario.")
            return

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