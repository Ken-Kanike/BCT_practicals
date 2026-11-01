#!/usr/bin/env python3
"""Draw the block-chain and Merkle-tree structure for Experiment 8."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def rounded(ax, x, y, w, h, edge, fill, lw=1.8):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            linewidth=lw,
            edgecolor=edge,
            facecolor=fill,
        )
    )


def arrow(ax, start, end, color="#2c5f8a", style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=14,
            linewidth=1.6,
            color=color,
        )
    )


def block(ax, x, y, title, rows, edge, fill):
    w, h = 3.75, 2.35
    rounded(ax, x, y, w, h, edge, fill)
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=edge)
    for index, (label, value) in enumerate(rows):
        ax.text(x + 0.22, y + h - 0.72 - index * 0.30, f"{label:7s} {value}",
                ha="left", va="center", fontsize=7.9, color="#243b53",
                family="monospace")


def main() -> None:
    fig, ax = plt.subplots(figsize=(14, 8.2))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    ax.set_facecolor("#fbfdff")

    ax.text(7.0, 7.85, "Blockchain Structure: Hash-Linked Blocks and Merkle Root",
            ha="center", va="center", fontsize=17, fontweight="bold", color="#17324a")

    block(
        ax, 0.35, 4.85, "Block 0  (Genesis)",
        [
            ("index", "0"),
            ("prev", "000...000"),
            ("merkle", "e3f8838b..."),
            ("nonce", "92677"),
            ("hash", "00007926..."),
            ("txs", "3 coinbase"),
        ],
        "#b7791f", "#fff6e8",
    )
    block(
        ax, 5.1, 4.85, "Block 1",
        [
            ("index", "1"),
            ("prev", "00007926..."),
            ("merkle", "3e5192cc..."),
            ("nonce", "367974"),
            ("hash", "00003868..."),
            ("txs", "coinbase + 3"),
        ],
        "#2c5f8a", "#e8f1fb",
    )
    block(
        ax, 9.85, 4.85, "Block 2",
        [
            ("index", "2"),
            ("prev", "00003868..."),
            ("merkle", "d85afd8d..."),
            ("nonce", "18965"),
            ("hash", "0000c2ec..."),
            ("txs", "coinbase + 1"),
        ],
        "#2f855a", "#e9f7ef",
    )

    arrow(ax, (4.15, 6.0), (5.05, 6.0), color="#b7791f")
    arrow(ax, (8.9, 6.0), (9.8, 6.0), color="#2c5f8a")
    ax.text(4.6, 6.22, "prev_hash", ha="center", va="center", fontsize=8, color="#4a5568")
    ax.text(9.35, 6.22, "prev_hash", ha="center", va="center", fontsize=8, color="#4a5568")

    # Merkle tree panel
    panel_x, panel_y, panel_w, panel_h = 0.35, 0.35, 13.3, 4.05
    rounded(ax, panel_x, panel_y, panel_w, panel_h, "#6b8fb3", "#f3f8fd", lw=1.5)
    ax.text(panel_x + panel_w / 2, panel_y + panel_h - 0.28,
            "Merkle tree for Block 1", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#1f4f78")

    leaves = [
        (1.35, "cb (54.00)"),
        (4.15, "tx1 9e20..."),
        (6.95, "tx2 6046..."),
        (9.75, "tx3 be9a..."),
    ]
    for x, label in leaves:
        rounded(ax, x, 0.85, 2.2, 0.55, "#2c5f8a", "#ffffff", lw=1.2)
        ax.text(x + 1.1, 1.12, label, ha="center", va="center",
                fontsize=8.5, family="monospace", color="#243b53")

    rounded(ax, 2.75, 1.95, 2.2, 0.55, "#2c5f8a", "#e8f1fb", lw=1.2)
    ax.text(3.85, 2.22, "H(cb|tx1)", ha="center", va="center",
            fontsize=8.5, family="monospace", color="#243b53")
    rounded(ax, 8.35, 1.95, 2.2, 0.55, "#2c5f8a", "#e8f1fb", lw=1.2)
    ax.text(9.45, 2.22, "H(tx2|tx3)", ha="center", va="center",
            fontsize=8.5, family="monospace", color="#243b53")
    rounded(ax, 5.55, 3.0, 2.9, 0.6, "#b7791f", "#fff6e8", lw=1.5)
    ax.text(7.0, 3.3, "Merkle root  3e5192cc...", ha="center", va="center",
            fontsize=9.0, family="monospace", color="#7b341e")

    for x in (2.45, 5.25):
        arrow(ax, (x, 1.4), (3.85, 1.95), color="#6b8fb3")
    for x in (8.05, 10.85):
        arrow(ax, (x, 1.4), (9.45, 1.95), color="#6b8fb3")
    arrow(ax, (4.95, 2.5), (6.4, 3.0), color="#b7791f")
    arrow(ax, (8.95, 2.5), (7.6, 3.0), color="#b7791f")

    ax.text(7.0, 0.5,
            "Changing any transaction changes its hash -> the Merkle root -> the block hash -> every later block.",
            ha="center", va="center", fontsize=9.5, color="#4a5568")

    ax.text(7.0, 4.5,
            "Proof of Work: SHA-256(block header) must start with 0000 (difficulty = 4).",
            ha="center", va="center", fontsize=9.5, style="italic", color="#2c5f8a")

    out = Path(__file__).resolve().parent.parent / "experiments/08-blockchain-mining/output/01_blockchain_structure.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
