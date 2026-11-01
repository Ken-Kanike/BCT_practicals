#!/usr/bin/env python3
"""Draw the Merkle tree that was actually built for Experiment 1."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "experiments" / "01-truffle-merkle" / "output" / "merkle-tree.json"
OUT = BASE / "experiments" / "01-truffle-merkle" / "output" / "05_merkle_tree.png"


def short(value: str, n: int = 10) -> str:
    return f"{value[:n]}...{value[-6:]}"


data = json.loads(DATA.read_text())
layers = data["layers"]
transactions = data["transactions"]

fig, ax = plt.subplots(figsize=(16, 9), facecolor="#0b1020")
ax.set_facecolor("#0b1020")
ax.axis("off")

positions = []
for level, layer in enumerate(layers):
    y = level * 2.0
    width = 2 ** (len(layers) - 1)
    row = []
    for i, node in enumerate(layer):
        x = (i + 0.5) * (width / len(layer)) * 2.0
        row.append((x, y, node))
    positions.append(row)

for level in range(len(positions) - 1):
    for i, (x, y, _) in enumerate(positions[level]):
        parent = positions[level + 1][i // 2]
        ax.plot([x, parent[0]], [y + 0.35, parent[1] - 0.35], color="#3b4a7a", lw=1.2, zorder=1)

for level, row in enumerate(positions):
    for i, (x, y, node) in enumerate(row):
        if level == 0:
            label = f"L{i}\n{short(node)}"
            color = "#1f6feb"
        elif level == len(positions) - 1:
            label = f"ROOT\n{short(node, 14)}"
            color = "#238636"
        else:
            label = short(node)
            color = "#6e40c9"
        box = FancyBboxPatch(
            (x - 1.25, y - 0.42),
            2.5,
            0.84,
            boxstyle="round,pad=0.04,rounding_size=0.12",
            linewidth=1.2,
            edgecolor="#8b949e",
            facecolor=color,
            zorder=2,
        )
        ax.add_patch(box)
        ax.text(x, y, label, ha="center", va="center", color="white", fontsize=8, family="monospace", zorder=3)

for i, tx in enumerate(transactions):
    x = positions[0][i][0]
    ax.text(x, -1.0, tx, ha="center", va="top", color="#c9d1d9", fontsize=9, family="monospace", rotation=12)

ax.set_xlim(-1, max(p[0] for p in positions[0]) + 1)
ax.set_ylim(-1.8, len(layers) * 2.0)
ax.set_title(
    "Experiment 1 - Merkle tree built from 5 transactions (keccak256, sorted pairs)",
    color="#e6edf3",
    fontsize=16,
    pad=18,
)
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=160, facecolor=fig.get_facecolor())
print(f"wrote {OUT}")
