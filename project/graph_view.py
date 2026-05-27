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


class GraphPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg=BG, **kwargs)
        self._highlight_ids: set[str] = set()
        self._graph_data = {"nodes": [], "edges": []}

        self.figure = plt.Figure(figsize=(4.4, 5.8), dpi=96, facecolor=BG)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(BG)
        self.ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().configure(bg=BG)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def render(self, graph_data, highlight_nodes=None):
        self._graph_data = graph_data or {"nodes": [], "edges": []}
        self._highlight_ids = set(highlight_nodes or [])
        self._draw()

    def highlight_nodes(self, node_ids=None):
        self._highlight_ids = set(node_ids or [])
        self._draw()

    def _draw(self):
        self.ax.clear()
        self.ax.set_facecolor(BG)
        self.ax.axis("off")

        nodes = self._graph_data.get("nodes") or []
        edges = self._graph_data.get("edges") or []
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
            g.add_edge(
                e["source"],
                e["target"],
                rel=e.get("rel", ""),
                score=e.get("score"),
                weight=e.get("weight"),
            )

        pos = nx.spring_layout(g, seed=42, k=1.1, iterations=50)

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
                    sizes.append(340)
                elif label in ("User", "Restaurant"):
                    sizes.append(460)
                else:
                    sizes.append(360)

        nx.draw_networkx_nodes(g, pos, ax=self.ax, node_color=colors, node_size=sizes, alpha=0.95)
        nx.draw_networkx_labels(g, pos, labels=labels, font_size=8, font_color=TEXT, ax=self.ax)
        nx.draw_networkx_edges(
            g,
            pos,
            ax=self.ax,
            edge_color="#6c7086",
            arrows=True,
            arrowsize=9,
            width=0.9,
            alpha=0.75,
        )

        edge_labels = {}
        for u, v in g.edges:
            rel = g.edges[u, v].get("rel", "")
            extra = ""
            if rel == "HAS_PREFERENCE" and g.edges[u, v].get("score") is not None:
                extra = f" {g.edges[u, v]['score']:.0f}"
            elif rel == "MATCHES_PREFERENCE" and g.edges[u, v].get("weight") is not None:
                extra = f" {g.edges[u, v]['weight']:.1f}"
            edge_labels[(u, v)] = (rel[:10] + extra)[:14]

        nx.draw_networkx_edge_labels(
            g,
            pos,
            edge_labels=edge_labels,
            font_size=6,
            font_color="#bac2de",
            ax=self.ax,
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