"""Panel de visualizacion del grafo — estilo gastronomico premium."""

from __future__ import annotations

import tkinter as tk

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch

from styles import COLORS

NODE_COLORS = {
    "User": COLORS["user"],
    "Restaurant": COLORS["restaurant"],
    "Cuisine": COLORS["cuisine"],
    "Zone": COLORS["zone"],
    "Preference": COLORS["preference"],
}

BG = COLORS["graph_bg"]
TEXT = COLORS["text_light"]
EDGE_COLOR = COLORS["graph_edge"]
MAX_RESTAURANTS = 55


class GraphPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg=BG, **kwargs)
        self._highlight_ids: set[str] = set()
        self._focus_user_id: str | None = None
        self._graph_data = {"nodes": [], "edges": []}

        self.figure = plt.Figure(figsize=(6.5, 5.5), dpi=100, facecolor=BG)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(BG)
        self.ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().configure(bg=BG)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def render(self, graph_data, highlight_nodes=None, focus_user_id=None):
        self._graph_data = graph_data or {"nodes": [], "edges": []}
        self._highlight_ids = set(highlight_nodes or [])
        self._focus_user_id = focus_user_id
        self._draw()

    def highlight_nodes(self, node_ids=None):
        self._highlight_ids = set(node_ids or [])
        self._draw()

    def _subsample(self, nodes: list, edges: list) -> tuple[list, list]:
        by_id = {n["id"]: n for n in nodes}
        restaurant_ids = [n["id"] for n in nodes if n.get("label") == "Restaurant"]
        if len(restaurant_ids) <= MAX_RESTAURANTS:
            filtered = [e for e in edges if e.get("source") != e.get("target")]
            return nodes, filtered

        focus = self._focus_user_id
        user_nid = "User:" + focus if focus else None
        priority: set[str] = set()
        if user_nid and user_nid in by_id:
            for e in edges:
                if e.get("source") == user_nid or e.get("target") == user_nid:
                    other = e["target"] if e.get("source") == user_nid else e["source"]
                    if by_id.get(other, {}).get("label") == "Restaurant":
                        priority.add(other)
        for hid in self._highlight_ids:
            if by_id.get(hid, {}).get("label") == "Restaurant":
                priority.add(hid)

        keep_rest = list(priority)
        remaining = [rid for rid in restaurant_ids if rid not in priority]
        slots = max(0, MAX_RESTAURANTS - len(keep_rest))
        step = max(1, len(remaining) // max(1, slots)) if remaining and slots else 1
        for i in range(0, len(remaining), step):
            if len(keep_rest) >= MAX_RESTAURANTS:
                break
            keep_rest.append(remaining[i])

        keep_nodes = {nid for nid, n in by_id.items() if n.get("label") != "Restaurant"}
        keep_nodes.update(keep_rest)
        if user_nid:
            keep_nodes.add(user_nid)

        new_nodes = [n for n in nodes if n["id"] in keep_nodes]
        new_edges = [
            e
            for e in edges
            if e.get("source") in keep_nodes
            and e.get("target") in keep_nodes
            and e.get("source") != e.get("target")
        ]
        return new_nodes, new_edges

    def _draw(self):
        try:
            self._draw_inner()
        except Exception:
            try:
                self.ax.clear()
                self.ax.set_facecolor(BG)
                self.ax.axis("off")
                self.ax.text(
                    0.5,
                    0.5,
                    "No se pudo dibujar el grafo",
                    ha="center",
                    va="center",
                    color=TEXT,
                    fontsize=11,
                    transform=self.ax.transAxes,
                )
                self.canvas.draw_idle()
            except Exception:
                pass

    def _draw_inner(self):
        self.ax.clear()
        self.ax.set_facecolor(BG)
        self.ax.axis("off")

        nodes = list(self._graph_data.get("nodes") or [])
        edges = list(self._graph_data.get("edges") or [])
        nodes, edges = self._subsample(nodes, edges)

        if not nodes:
            self.ax.text(
                0.5,
                0.5,
                "Sin datos de grafo",
                ha="center",
                va="center",
                color=COLORS["muted"],
                fontsize=12,
                transform=self.ax.transAxes,
            )
            self.canvas.draw_idle()
            return

        g = nx.DiGraph()
        for n in nodes:
            g.add_node(n["id"], label=n.get("label", ""), name=n.get("name", n["id"]))
        for e in edges:
            src, tgt = e.get("source"), e.get("target")
            if not src or not tgt or src == tgt:
                continue
            g.add_edge(src, tgt, rel=e.get("rel", ""), weight=e.get("weight"))

        if not g.nodes:
            self.canvas.draw_idle()
            return

        pref_nodes = [n for n in g.nodes if g.nodes[n].get("label") == "Preference"]
        other_nodes = [n for n in g.nodes if g.nodes[n].get("label") != "Preference"]
        pos = {}
        if other_nodes:
            sub = g.subgraph(other_nodes)
            pos.update(nx.spring_layout(sub, seed=42, k=2.0, iterations=100))
        if pref_nodes and other_nodes:
            import math

            cx = sum(pos[n][0] for n in other_nodes) / len(other_nodes)
            cy = sum(pos[n][1] for n in other_nodes) / len(other_nodes)
            radius = 1.85
            for i, nid in enumerate(pref_nodes):
                angle = 2 * math.pi * i / max(1, len(pref_nodes))
                pos[nid] = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        elif pref_nodes:
            pos.update(nx.circular_layout(g))

        labels = {nid: (g.nodes[nid].get("name") or nid)[:14] for nid in g.nodes}
        colors = []
        sizes = []
        for nid in g.nodes:
            label = g.nodes[nid].get("label", "")
            base = NODE_COLORS.get(label, COLORS["muted"])
            if nid in self._highlight_ids:
                colors.append(COLORS["accent2"])
                sizes.append(680)
            else:
                colors.append(base)
                if label == "Preference":
                    sizes.append(260)
                elif label in ("User", "Restaurant"):
                    sizes.append(560)
                else:
                    sizes.append(420)

        nx.draw_networkx_nodes(
            g,
            pos,
            ax=self.ax,
            node_color=colors,
            node_size=sizes,
            alpha=0.88,
            edgecolors=COLORS["glow"],
            linewidths=1.2,
        )
        nx.draw_networkx_labels(
            g,
            pos,
            labels=labels,
            font_size=8,
            font_color=TEXT,
            font_family="sans-serif",
            ax=self.ax,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "#2C1810", "edgecolor": "none", "alpha": 0.65},
        )

        match_edges = [(u, v) for u, v, d in g.edges(data=True) if d.get("rel") == "MATCHES_PREFERENCE"]
        other_edges = [(u, v) for u, v, d in g.edges(data=True) if d.get("rel") != "MATCHES_PREFERENCE"]

        if other_edges:
            try:
                nx.draw_networkx_edges(
                    g,
                    pos,
                    edgelist=other_edges,
                    ax=self.ax,
                    edge_color=EDGE_COLOR,
                    arrows=True,
                    arrowsize=8,
                    width=0.8,
                    alpha=0.35,
                    connectionstyle="arc3,rad=0.12",
                    min_source_margin=12,
                    min_target_margin=12,
                )
            except Exception:
                nx.draw_networkx_edges(
                    g,
                    pos,
                    edgelist=other_edges,
                    ax=self.ax,
                    edge_color=EDGE_COLOR,
                    arrows=False,
                    width=0.8,
                    alpha=0.35,
                )

        if match_edges:
            # Muchas aristas MATCHES_PREFERENCE: sin flechas ni connectionstyle (mas rapido y sin warnings).
            nx.draw_networkx_edges(
                g,
                pos,
                edgelist=match_edges,
                ax=self.ax,
                edge_color=COLORS["accent2"],
                arrows=False,
                width=0.9,
                alpha=0.45,
            )

        self.ax.set_title("Mapa de afinidades culinarias", color=TEXT, fontsize=11, pad=12, alpha=0.9)
        legend_items = [
            Patch(facecolor=NODE_COLORS["User"], label="Usuario", edgecolor="none"),
            Patch(facecolor=NODE_COLORS["Restaurant"], label="Restaurante", edgecolor="none"),
            Patch(facecolor=NODE_COLORS["Cuisine"], label="Cocina", edgecolor="none"),
            Patch(facecolor=NODE_COLORS["Zone"], label="Zona", edgecolor="none"),
            Patch(facecolor=NODE_COLORS["Preference"], label="Preferencia", edgecolor="none"),
        ]
        self.ax.legend(
            handles=legend_items,
            loc="upper right",
            fontsize=8,
            framealpha=0.9,
            facecolor="#2C1810",
            edgecolor=COLORS["graph_edge"],
            labelcolor=TEXT,
        )

        self.figure.tight_layout(pad=0.4)
        self.canvas.draw_idle()
