"""Panel de visualizacion del grafo con matplotlib y networkx."""

from __future__ import annotations

import tkinter as tk

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

NODE_COLORS = {
    "User": "#4a9eff",
    "Restaurant": "#4ade80",
    "Cuisine": "#fb923c",
    "Zone": "#f87171",
}

BG = "#1e1e2e"
TEXT = "#cdd6f4"


class GraphPanel(tk.Frame):
    """Grafo embebido en Tkinter."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg=BG, **kwargs)
        self._highlight_ids: set[str] = set()
        self._graph_data = {"nodes": [], "edges": []}

        self.figure = plt.Figure(figsize=(4.2, 5.5), dpi=96, facecolor=BG)
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
                fontsize=10,
                transform=self.ax.transAxes,
            )
            self.canvas.draw_idle()
            return

        g = nx.DiGraph()
        for n in nodes:
            g.add_node(n["id"], label=n.get("label", ""), name=n.get("name", n["id"]))
        for e in edges:
            g.add_edge(e["source"], e["target"], rel=e.get("rel", ""))

        pos = nx.spring_layout(g, seed=42, k=0.85, iterations=40)

        labels = {nid: (g.nodes[nid].get("name") or nid)[:10] for nid in g.nodes}
        colors = []
        sizes = []
        edge_colors = []
        for nid in g.nodes:
            label = g.nodes[nid].get("label", "")
            base = NODE_COLORS.get(label, "#a6adc8")
            if nid in self._highlight_ids:
                colors.append("#f9e2af")
                sizes.append(520)
            else:
                colors.append(base)
                sizes.append(380 if label in ("User", "Restaurant") else 300)

        nx.draw_networkx_nodes(
            g,
            pos,
            ax=self.ax,
            node_color=colors,
            node_size=sizes,
            alpha=0.95,
        )
        nx.draw_networkx_labels(
            g,
            pos,
            labels=labels,
            font_size=6,
            font_color=TEXT,
            ax=self.ax,
        )
        nx.draw_networkx_edges(
            g,
            pos,
            ax=self.ax,
            edge_color="#6c7086",
            arrows=True,
            arrowsize=8,
            width=0.8,
            alpha=0.7,
        )
        edge_labels = {
            (u, v): g.edges[u, v].get("rel", "")[:12]
            for u, v in g.edges
        }
        nx.draw_networkx_edge_labels(
            g,
            pos,
            edge_labels=edge_labels,
            font_size=5,
            font_color="#bac2de",
            ax=self.ax,
        )

        self.figure.tight_layout(pad=0.2)
        self.canvas.draw_idle()