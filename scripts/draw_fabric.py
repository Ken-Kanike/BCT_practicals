#!/usr/bin/env python3
"""Draw the Hyperledger Fabric test-network topology used in Experiment 5."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = (
    Path(__file__).resolve().parent.parent
    / "experiments"
    / "05-hyperledger-chaincode"
    / "output"
    / "01_fabric_topology.png"
)

fig, ax = plt.subplots(figsize=(15, 8.5), facecolor="#0b1020")
ax.set_facecolor("#0b1020")
ax.axis("off")
ax.set_xlim(0, 15)
ax.set_ylim(0, 8.5)


def box(x, y, w, h, title, subtitle, color, edge="#8b949e"):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.05,rounding_size=0.18",
        linewidth=1.3,
        edgecolor=edge,
        facecolor=color,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center", color="white", fontsize=12, fontweight="bold", zorder=3)
    ax.text(x + w / 2, y + h * 0.28, subtitle, ha="center", va="center", color="#dbe4ff", fontsize=9.5, family="monospace", zorder=3)


def arrow(x1, y1, x2, y2, label=""):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=1.4,
            color="#6ea8ff",
            connectionstyle="arc3,rad=0.08",
            zorder=1,
        )
    )
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, label, ha="center", va="bottom", color="#9fb3d9", fontsize=8.5)


box(5.6, 7.0, 3.8, 1.1, "Orderer (Raft)", "orderer.example.com:7050", "#8b5cf6")
box(5.4, 5.2, 4.2, 0.95, "Channel: mychannel", "Fabric v2.4.9 · channel ID mychannel", "#1f6feb")

box(1.4, 2.8, 4.0, 1.45, "Org1 MSP", "peer0.org1.example.com:7051", "#0f766e")
box(9.6, 2.8, 4.0, 1.45, "Org2 MSP", "peer0.org2.example.com:9051", "#0f766e")

box(1.4, 0.8, 4.0, 1.15, "Chaincode: asset-transfer", "Go · v1.0 · sequence 1", "#b45309")
box(9.6, 0.8, 4.0, 1.15, "Chaincode: asset-transfer", "Go · v1.0 · sequence 1", "#b45309")

arrow(7.5, 6.95, 7.5, 6.2, "broadcast / deliver")
arrow(5.4, 5.45, 3.4, 4.3, "join + endorse")
arrow(9.6, 5.45, 11.6, 4.3, "join + endorse")
arrow(3.4, 2.75, 3.4, 2.0, "install + approve")
arrow(11.6, 2.75, 11.6, 2.0, "install + approve")

ax.text(7.5, 3.55, "Endorsement policy\nOrg1MSP AND Org2MSP", ha="center", va="center", color="#c9d1d9", fontsize=10)
ax.text(
    7.5,
    8.35,
    "Experiment 5 — Hyperledger Fabric test network and chaincode lifecycle",
    ha="center",
    va="center",
    color="#e6edf3",
    fontsize=15,
    fontweight="bold",
)

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=160, facecolor=fig.get_facecolor())
print(f"wrote {OUT}")
