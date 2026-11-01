#!/usr/bin/env python3
"""Draw the permissioned-network architecture used in the Experiment 6 case study."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def box(ax, x, y, w, h, title, body="", color="#e8f1fb", edge="#2c5f8a", dashed=False):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=1.6,
        edgecolor=edge,
        facecolor=color,
        linestyle="--" if dashed else "-",
    )
    ax.add_patch(patch)
    if body:
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color="#17324a")
        ax.text(x + w / 2, y + h * 0.30, body, ha="center", va="center",
                fontsize=8.6, color="#24455f")
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color="#17324a")


def arrow(ax, start, end, color="#2c5f8a", style="-|>", dashed=False, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=14,
            linewidth=1.5,
            color=color,
            linestyle="--" if dashed else "-",
            connectionstyle=f"arc3,rad={rad}",
        )
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(14, 8.2))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    ax.set_facecolor("#fbfdff")

    # Channel boundary
    channel = FancyBboxPatch(
        (1.75, 0.55),
        10.6,
        6.9,
        boxstyle="round,pad=0.05,rounding_size=0.15",
        linewidth=2.0,
        edgecolor="#6b8fb3",
        facecolor="#f3f8fd",
        linestyle="--",
    )
    ax.add_patch(channel)
    ax.text(7.05, 7.18, "mychannel  (Org1 + Org2)", ha="center", va="center",
            fontsize=13, fontweight="bold", color="#1f4f78")

    # Orderer and peers
    box(ax, 5.35, 5.55, 3.3, 1.05, "Orderer", "Raft ordering service", "#fff4e0", "#b7791f")
    box(ax, 2.35, 3.25, 3.15, 1.25, "peer0.org1", "endorser + committer", "#e8f1fb", "#2c5f8a")
    box(ax, 8.6, 3.25, 3.15, 1.25, "peer0.org2", "endorser + committer", "#e8f1fb", "#2c5f8a")

    # Clients
    box(ax, 0.15, 3.35, 1.35, 1.05, "Alice", "Org1 producer", "#e9f7ef", "#2f855a")
    box(ax, 12.5, 3.35, 1.35, 1.05, "Bob", "Org2 retailer", "#e9f7ef", "#2f855a")

    # Private collection and public ledger
    box(ax, 2.05, 1.0, 3.75, 1.1, "Private collection",
        "assetPrivateDetails\nallowed orgs: Org1 only", "#fdeef4", "#b83280")
    box(ax, 6.65, 1.0, 4.85, 1.1, "Public world state",
        "id, owner, value, status, private hash", "#eef7ee", "#2f855a")

    # Org3 outsider
    box(ax, 0.15, 5.9, 1.5, 1.0, "Org3", "Mallory", "#fde8e8", "#c53030", dashed=True)
    arrow(ax, (1.65, 6.35), (2.35, 6.15), color="#c53030", dashed=True)
    ax.text(2.0, 6.5, "X", ha="center", va="center", fontsize=18,
            fontweight="bold", color="#c53030")

    # Arrows
    arrow(ax, (1.5, 3.85), (2.35, 3.85))
    arrow(ax, (12.5, 3.85), (11.75, 3.85))
    arrow(ax, (4.2, 4.45), (5.7, 5.55), rad=-0.12)
    arrow(ax, (9.85, 4.45), (8.3, 5.55), rad=0.12)
    arrow(ax, (5.7, 5.55), (4.2, 4.45), rad=0.12, color="#b7791f", dashed=True)
    arrow(ax, (8.3, 5.55), (9.85, 4.45), rad=-0.12, color="#b7791f", dashed=True)
    arrow(ax, (3.3, 3.25), (3.3, 2.1), color="#b83280", dashed=True)
    arrow(ax, (5.2, 3.25), (7.4, 2.1), color="#2f855a")
    arrow(ax, (9.8, 3.25), (9.1, 2.1), color="#2f855a")

    ax.text(1.85, 4.0, "proposal", fontsize=8, color="#2c5f8a")
    ax.text(11.95, 4.0, "proposal", fontsize=8, color="#2c5f8a")
    ax.text(4.55, 4.95, "endorse", fontsize=8, color="#2c5f8a", rotation=30)
    ax.text(9.45, 4.95, "endorse", fontsize=8, color="#2c5f8a", rotation=-30)
    ax.text(5.55, 5.25, "block", fontsize=8, color="#b7791f", rotation=-30)
    ax.text(8.45, 5.25, "block", fontsize=8, color="#b7791f", rotation=30)
    ax.text(5.55, 2.65, "commit", fontsize=8, color="#2f855a")
    ax.text(9.55, 2.65, "commit", fontsize=8, color="#2f855a")
    ax.text(3.45, 2.55, "private\ndissemination", fontsize=8, color="#b83280", ha="center")

    ax.text(7.05, 0.18, "Endorsement policy: Org1 AND Org2   |   "
            "Private data: Org1 only   |   Public state: all channel members",
            ha="center", va="center", fontsize=9, color="#4a5568")

    out = Path(__file__).resolve().parent.parent / "experiments/06-hyperledger-case-study/output/01_architecture.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
