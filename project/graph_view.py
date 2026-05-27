"""Panel de visualizacion del grafo con matplotlib y networkx."""

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

BG = COLORS["surface"]
TEXT = COLORS["text"]
MAX_RESTAURANTS = 40


class GraphPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg=BG, **kwargs)
        self._highlight_ids: set[str] = set()
        self._focus_user_id: str | None = None
        self._graph_data = {"nodes": [], "edges": []}

        self.figure = plt.Figure(figsize=(4.4, 5.8), dpi=96, facecolor=BG)
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
                    fontsize=10,
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
                color=TEXT,
                fontsize=11,
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
            g.add_edge(
                src,
                tgt,
                rel=e.get("rel", ""),
                score=e.get("score"),
                weight=e.get("weight"),
            )

        if not g.nodes:
            self.canvas.draw_idle()
            return

        pos = nx.spring_layout(g, seed=42, k=1.4, iterations=60)

        labels = {nid: (g.nodes[nid].get("name") or nid)[:12] for nid in g.nodes}
        colors = []
        sizes = []
        for nid in g.nodes:
            label = g.nodes[nid].get("label", "")
            base = NODE_COLORS.get(label, "#a6adc8")
            if nid in self._highlight_ids:
                colors.append(COLORS["warning"])
                sizes.append(620)
            else:
                colors.append(base)
                if label == "Preference":
                    sizes.append(260)
                elif label in ("User", "Restaurant"):
                    sizes.append(460)
                else:
                    sizes.append(360)

        nx.draw_networkx_nodes(g, pos, ax=self.ax, node_color=colors, node_size=sizes, alpha=0.95)
        nx.draw_networkx_labels(g, pos, labels=labels, font_size=8, font_color=TEXT, ax=self.ax)

        edge_labels = {}
        for u, v in list(g.edges):
            rel = g.edges[u, v].get("rel", "")
            extra = ""
            sc = g.edges[u, v].get("score")
            wt = g.edges[u, v].get("weight")
            if rel == "HAS_PREFERENCE" and sc is not None:
                extra = " %.0f" % sc
            elif rel == "MATCHES_PREFERENCE" and wt is not None:
                extra = " %.1f" % wt
            edge_labels[(u, v)] = (rel[:10] + extra)[:14]

        try:
            nx.draw_networkx_edges(
                g,
                pos,
                ax=self.ax,
                edge_color="#6c7086",
                arrows=True,
                arrowsize=9,
                width=0.9,
                alpha=0.75,
                connectionstyle="arc3,rad=0.15",
            )
            nx.draw_networkx_edge_labels(
                g,
                pos,
                edge_labels=edge_labels,
                font_size=6,
                font_color="#bac2de",
                ax=self.ax,
            )
        except Exception:
            nx.draw_networkx_edges(
                g,
                pos,
                ax=self.ax,
                edge_color="#6c7086",
                arrows=False,
                width=0.9,
                alpha=0.75,
                connectionstyle="arc3,rad=0.15",
            )

        legend_items = [
            Patch(facecolor=NODE_COLORS["User"], label="Usuario"),
            Patch(facecolor=NODE_COLORS["Restaurant"], label="Restaurante"),
            Patch(facecolor=NODE_COLORS["Cuisine"], label="Cocina"),
            Patch(facecolor=NODE_COLORS["Zone"], label="Zona"),
            Patch(facecolor=NODE_COLORS["Preference"], label="Preferencia"),
        ]
        self.ax.legend(
            handles=legend_items,
            loc="lower left",
            fontsize=7,
            facecolor=COLORS["surface2"],
            edgecolor=COLORS["surface3"],
            labelcolor=TEXT,
        )

        self.figure.tight_layout(pad=0.2)
        self.canvas.draw_idle()