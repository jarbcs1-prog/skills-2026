from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

GRAPHML_NS = "http://graphml.graphdrawing.org/xmlns"


class InsightGraph:
    def __init__(self, notes: list[dict[str, Any]], insights: list[dict[str, Any]]):
        self.nodes = [note["path"] for note in notes]
        node_set = set(self.nodes)
        self._edges: set[tuple[str, str]] = set()
        for insight in insights:
            sources = [source for source in insight.get("sources", []) if source in node_set]
            if len(sources) == 2:
                a, b = sorted(sources)
                self._edges.add((a, b))

    def edges(self) -> list[tuple[str, str]]:
        return sorted(self._edges)

    def communities(self) -> dict[int, list[str]]:
        parent = {node: node for node in self.nodes}

        def find(node: str) -> str:
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        def union(a: str, b: str) -> None:
            root_a = find(a)
            root_b = find(b)
            if root_a != root_b:
                parent[root_b] = root_a

        for a, b in self.edges():
            if a in parent and b in parent:
                union(a, b)

        groups: dict[str, list[str]] = {}
        for node in sorted(self.nodes):
            root = find(node)
            groups.setdefault(root, []).append(node)
        return {index: members for index, members in enumerate(sorted(groups.values(), key=lambda m: m[0]))}

    def export_graphml(self, path: Path) -> None:
        ET.register_namespace("", GRAPHML_NS)
        root = ET.Element(f"{{{GRAPHML_NS}}}graphml")
        key = ET.SubElement(root, f"{{{GRAPHML_NS}}}key")
        key.set("id", "communities")
        key.set("for", "graph")
        key.set("attr.name", "communities")
        key.set("attr.type", "string")
        graph = ET.SubElement(root, f"{{{GRAPHML_NS}}}graph")
        graph.set("edgedefault", "undirected")
        data = ET.SubElement(graph, f"{{{GRAPHML_NS}}}data")
        data.set("key", "communities")
        data.text = "; ".join(",".join(members) for members in self.communities().values())
        for node in self.nodes:
            node_el = ET.SubElement(graph, f"{{{GRAPHML_NS}}}node")
            node_el.set("id", node)
        for a, b in self.edges():
            edge_el = ET.SubElement(graph, f"{{{GRAPHML_NS}}}edge")
            edge_el.set("source", a)
            edge_el.set("target", b)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)
