"""Interfaz grafica del sistema de recomendacion de restaurantes."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

import database
from graph_view import GraphPanel
from recommendation import (
    actualizar_usuario,
    crear_usuario,
    obtener_cocinas,
    obtener_datos_grafo,
    obtener_historial_usuario,
    obtener_usuario_detalle,
    obtener_usuarios,
    obtener_zonas,
    recomendar_restaurantes,
)

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
ENTRY_BG = "#313244"
BORDER = "#45475a"


class RestaurantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Recomendacion de Restaurantes")
        self.minsize(1280, 720)
        self.geometry("1280x720")
        self.configure(bg=BG)

        self._zonas: list[str] = []
        self._cocinas: list[str] = []
        self._usuarios: list[dict] = []
        self._cuisine_vars: dict[str, tk.BooleanVar] = {}
        self._edit_cuisine_vars: dict[str, tk.BooleanVar] = {}

        self._apply_theme()
        self._build_layout()
        self._set_status("Iniciando...")

        self.after(100, self._startup)

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=FG, fieldbackground=ENTRY_BG, bordercolor=BORDER)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TButton", background=ENTRY_BG, foreground=FG, padding=6)
        style.map("TButton", background=[("active", BORDER)])
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=FG)
        style.configure("TCombobox", fieldbackground=ENTRY_BG, foreground=FG, background=ENTRY_BG)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=ENTRY_BG, foreground=FG, padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", BORDER)])
        style.configure("Treeview", background=ENTRY_BG, foreground=FG, fieldbackground=ENTRY_BG, rowheight=24)
        style.configure("Treeview.Heading", background=BORDER, foreground=FG)
        style.configure("Horizontal.TPanedwindow", background=BG)
        style.configure("Vertical.TScrollbar", background=ENTRY_BG)

    def _build_layout(self):
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(paned)
        right = ttk.Frame(paned, width=360)
        paned.add(left, weight=7)
        paned.add(right, weight=3)

        self.notebook = ttk.Notebook(left)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._tab_add = ttk.Frame(self.notebook)
        self._tab_edit = ttk.Frame(self.notebook)
        self._tab_rec = ttk.Frame(self.notebook)
        self._tab_hist = ttk.Frame(self.notebook)
        self.notebook.add(self._tab_add, text="Agregar Usuario")
        self.notebook.add(self._tab_edit, text="Editar Usuario")
        self.notebook.add(self._tab_rec, text="Recomendador")
        self.notebook.add(self._tab_hist, text="Historial")

        self._build_tab_add()
        self._build_tab_edit()
        self._build_tab_rec()
        self._build_tab_hist()

        graph_title = ttk.Label(right, text="Grafo Neo4j", font=("Segoe UI", 11, "bold"))
        graph_title.pack(anchor=tk.W, pady=(0, 4))
        self.graph_panel = GraphPanel(right)
        self.graph_panel.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Listo")
        status = ttk.Label(self, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN)
        status.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=(0, 6))

    def _build_tab_add(self):
        f = self._tab_add
        self.add_id = tk.StringVar()
        self.add_nombre = tk.StringVar()
        self.add_presupuesto = tk.StringVar()
        self.add_zona = tk.StringVar()

        self._form_row(f, 0, "ID", ttk.Entry(f, textvariable=self.add_id, width=28))
        self._form_row(f, 1, "Nombre", ttk.Entry(f, textvariable=self.add_nombre, width=28))
        self._form_row(f, 2, "Presupuesto", ttk.Entry(f, textvariable=self.add_presupuesto, width=28))
        self.add_zona_cb = ttk.Combobox(f, textvariable=self.add_zona, state="readonly", width=26)
        self._form_row(f, 3, "Zona", self.add_zona_cb)

        ttk.Label(f, text="Cocinas preferidas").grid(row=4, column=0, sticky=tk.NW, padx=12, pady=8)
        self.add_cuisine_frame = ttk.Frame(f)
        self.add_cuisine_frame.grid(row=4, column=1, sticky=tk.W, pady=8)

        ttk.Button(f, text="Guardar", command=self._on_guardar_usuario).grid(
            row=5, column=1, sticky=tk.W, pady=16
        )

    def _build_tab_edit(self):
        f = self._tab_edit
        self.edit_user_cb = ttk.Combobox(f, state="readonly", width=28)
        self.edit_user_cb.bind("<<ComboboxSelected>>", lambda _e: self._load_edit_user())
        self._form_row(f, 0, "Usuario", self.edit_user_cb)

        self.edit_id = tk.StringVar()
        self.edit_nombre = tk.StringVar()
        self.edit_presupuesto = tk.StringVar()
        self.edit_zona = tk.StringVar()

        self._form_row(f, 1, "ID", ttk.Entry(f, textvariable=self.edit_id, state="readonly", width=28))
        self._form_row(f, 2, "Nombre", ttk.Entry(f, textvariable=self.edit_nombre, width=28))
        self._form_row(f, 3, "Presupuesto", ttk.Entry(f, textvariable=self.edit_presupuesto, width=28))
        self.edit_zona_cb = ttk.Combobox(f, textvariable=self.edit_zona, state="readonly", width=26)
        self._form_row(f, 4, "Zona", self.edit_zona_cb)

        ttk.Label(f, text="Cocinas preferidas").grid(row=5, column=0, sticky=tk.NW, padx=12, pady=8)
        self.edit_cuisine_frame = ttk.Frame(f)
        self.edit_cuisine_frame.grid(row=5, column=1, sticky=tk.W, pady=8)

        ttk.Button(f, text="Actualizar", command=self._on_actualizar_usuario).grid(
            row=6, column=1, sticky=tk.W, pady=16
        )

    def _build_tab_rec(self):
        f = self._tab_rec
        self.rec_user_cb = ttk.Combobox(f, state="readonly", width=30)
        self._form_row(f, 0, "Usuario", self.rec_user_cb)
        ttk.Button(f, text="Obtener recomendaciones", command=self._on_recomendar).grid(
            row=1, column=1, sticky=tk.W, pady=12
        )
        cols = ("nombre", "rating", "precio", "zona", "cocinas", "similares", "misma_zona")
        self.rec_tree = ttk.Treeview(f, columns=cols, show="headings", height=14)
        headings = {
            "nombre": "Restaurante",
            "rating": "Rating",
            "precio": "Precio",
            "zona": "Zona",
            "cocinas": "Cocinas",
            "similares": "Similares",
            "misma_zona": "Misma zona",
        }
        for c in cols:
            self.rec_tree.heading(c, text=headings[c])
            self.rec_tree.column(c, width=120 if c != "nombre" else 160)
        self.rec_tree.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=12, pady=8)
        f.rowconfigure(2, weight=1)
        f.columnconfigure(1, weight=1)

    def _build_tab_hist(self):
        f = self._tab_hist
        self.hist_user_cb = ttk.Combobox(f, state="readonly", width=30)
        self._form_row(f, 0, "Usuario", self.hist_user_cb)
        ttk.Button(f, text="Cargar historial", command=self._on_historial).grid(
            row=1, column=1, sticky=tk.W, pady=12
        )
        cols = ("restaurante", "fecha", "nota", "rating", "precio", "zona", "cocinas")
        self.hist_tree = ttk.Treeview(f, columns=cols, show="headings", height=14)
        for c, t in zip(
            cols,
            ("Restaurante", "Fecha", "Nota pers.", "Rating", "Precio", "Zona", "Cocinas"),
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
            zonas = obtener_zonas()
            cocinas = obtener_cocinas()
            usuarios = obtener_usuarios()
            grafo = obtener_datos_grafo()
            return zonas, cocinas, usuarios, grafo

        def ok(data):
            zonas, cocinas, usuarios, grafo = data
            self._zonas = zonas
            self._cocinas = cocinas
            self._usuarios = usuarios
            self._refresh_reference_data()
            self.graph_panel.render(grafo)
            messagebox.showinfo("Conexion", "Conexion con Neo4j verificada correctamente.")

        def err(exc):
            messagebox.showerror("Conexion", f"No se pudo conectar a Neo4j:\n{exc}")
            self.destroy()

        self._run_async(work, on_ok=ok, on_err=err, busy_msg="Verificando conexion Neo4j...")

    def _refresh_reference_data(self):
        self.add_zona_cb["values"] = self._zonas
        self.edit_zona_cb["values"] = self._zonas
        ids = [u["id"] for u in self._usuarios]
        labels = [f"{u['id']} - {u['nombre']}" for u in self._usuarios]
        self.edit_user_cb["values"] = labels
        self.rec_user_cb["values"] = labels
        self.hist_user_cb["values"] = labels
        self._rebuild_cuisine_checks(self.add_cuisine_frame, self._cuisine_vars)
        self._rebuild_cuisine_checks(self.edit_cuisine_frame, self._edit_cuisine_vars)

    def _rebuild_cuisine_checks(self, parent, var_map: dict):
        for w in parent.winfo_children():
            w.destroy()
        var_map.clear()
        for i, cocina in enumerate(self._cocinas):
            var = tk.BooleanVar(value=False)
            var_map[cocina] = var
            ttk.Checkbutton(parent, text=cocina, variable=var).grid(row=i // 2, column=i % 2, sticky=tk.W, padx=4)

    def _selected_cocinas(self, var_map: dict) -> list[str]:
        return [name for name, var in var_map.items() if var.get()]

    def _parse_presupuesto(self, value: str) -> int:
        try:
            p = int(str(value).strip())
            if p < 0:
                raise ValueError
            return p
        except ValueError as exc:
            raise ValueError("Presupuesto debe ser un entero positivo.") from exc

    def _refresh_graph(self):
        def work():
            return obtener_datos_grafo()

        def ok(grafo):
            highlight = []
            uid = self.edit_id.get().strip()
            if uid:
                highlight.append(f"User:{uid}")
            self.graph_panel.render(grafo, highlight_nodes=highlight or None)

        self._run_async(work, on_ok=ok, busy_msg="Actualizando grafo...")

    def _reload_users(self, select_id=None):
        def work():
            return obtener_usuarios()

        def ok(usuarios):
            self._usuarios = usuarios
            self._refresh_reference_data()
            if select_id:
                for i, u in enumerate(self._usuarios):
                    if u["id"] == select_id:
                        self.edit_user_cb.current(i)
                        self._load_edit_user()
                        break
            self._refresh_graph()

        self._run_async(work, on_ok=ok, busy_msg="Recargando usuarios...")

    def _on_guardar_usuario(self):
        uid = self.add_id.get().strip()
        nombre = self.add_nombre.get().strip()
        zona = self.add_zona.get().strip()
        cocinas = self._selected_cocinas(self._cuisine_vars)
        if not uid or not nombre or not zona:
            messagebox.showwarning("Validacion", "Complete ID, nombre y zona.")
            return
        try:
            presupuesto = self._parse_presupuesto(self.add_presupuesto.get())
        except ValueError as exc:
            messagebox.showwarning("Validacion", str(exc))
            return

        def work():
            crear_usuario(uid, nombre, presupuesto, zona, cocinas)
            return uid

        def ok(new_id):
            messagebox.showinfo("Exito", f"Usuario {new_id} creado.")
            self.add_id.set("")
            self.add_nombre.set("")
            self.add_presupuesto.set("")
            self._reload_users(select_id=new_id)

        self._run_async(work, on_ok=ok, busy_msg="Guardando usuario...")

    def _load_edit_user(self):
        idx = self.edit_user_cb.current()
        if idx < 0 or idx >= len(self._usuarios):
            return
        uid = self._usuarios[idx]["id"]

        def work():
            return obtener_usuario_detalle(uid)

        def ok(detalle):
            if not detalle:
                messagebox.showwarning("Usuario", "No se encontro el usuario.")
                return
            self.edit_id.set(detalle["id"])
            self.edit_nombre.set(detalle.get("nombre") or "")
            self.edit_presupuesto.set(str(detalle.get("presupuesto") or ""))
            self.edit_zona.set(detalle.get("zona") or "")
            liked = set(detalle.get("cocinas") or [])
            for name, var in self._edit_cuisine_vars.items():
                var.set(name in liked)
            self.graph_panel.highlight_nodes([f"User:{detalle['id']}"])

        self._run_async(work, on_ok=ok, busy_msg="Cargando usuario...")

    def _on_actualizar_usuario(self):
        uid = self.edit_id.get().strip()
        nombre = self.edit_nombre.get().strip()
        zona = self.edit_zona.get().strip()
        cocinas = self._selected_cocinas(self._edit_cuisine_vars)
        if not uid or not nombre or not zona:
            messagebox.showwarning("Validacion", "Seleccione usuario y complete nombre y zona.")
            return
        try:
            presupuesto = self._parse_presupuesto(self.edit_presupuesto.get())
        except ValueError as exc:
            messagebox.showwarning("Validacion", str(exc))
            return

        def work():
            actualizar_usuario(uid, nombre, presupuesto, zona, cocinas)
            return uid

        def ok(updated_id):
            messagebox.showinfo("Exito", f"Usuario {updated_id} actualizado.")
            self._reload_users(select_id=updated_id)

        self._run_async(work, on_ok=ok, busy_msg="Actualizando usuario...")

    def _current_user_id(self, combobox: ttk.Combobox) -> str | None:
        idx = combobox.current()
        if idx < 0 or idx >= len(self._usuarios):
            return None
        return self._usuarios[idx]["id"]

    def _on_recomendar(self):
        uid = self._current_user_id(self.rec_user_cb)
        if not uid:
            messagebox.showwarning("Recomendador", "Seleccione un usuario.")
            return

        def work():
            return recomendar_restaurantes(uid)

        def ok(rows):
            for item in self.rec_tree.get_children():
                self.rec_tree.delete(item)
            for r in rows:
                cocinas = ", ".join(r.get("cocinas") or [])
                self.rec_tree.insert(
                    "",
                    tk.END,
                    values=(
                        r.get("nombre"),
                        r.get("rating"),
                        r.get("precio"),
                        r.get("zona") or "",
                        cocinas,
                        r.get("usuarios_similares"),
                        "Si" if r.get("misma_zona") else "No",
                    ),
                )
            self.graph_panel.highlight_nodes([f"User:{uid}"])
            if not rows:
                messagebox.showinfo("Recomendador", "Sin recomendaciones para este usuario.")

        self._run_async(work, on_ok=ok, busy_msg="Calculando recomendaciones...")

    def _on_historial(self):
        uid = self._current_user_id(self.hist_user_cb)
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
            self.graph_panel.highlight_nodes([f"User:{uid}"])

        self._run_async(work, on_ok=ok, busy_msg="Cargando historial...")


def main():
    app = RestaurantApp()
    app.mainloop()
    database.close()


if __name__ == "__main__":
    main()