#!/usr/bin/env python3
"""Draw the three-platform comparison used in Experiment 7."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

PLATFORMS = [
    (
        "Bitcoin",
        "#f7931a",
        "#fff6e8",
        [
            "Public / permissionless",
            "Proof of Work (mining)",
            "UTXO transaction model",
            "21 million BTC supply",
            "ECDSA signatures",
            "Probabilistic finality",
            "Use: payments, store of value",
        ],
    ),
    (
        "Corda (R3)",
        "#c8102e",
        "#fdecef",
        [
            "Permissioned consortium",
            "Transaction-level consensus",
            "State objects + contracts",
            "Notary prevents double-spend",
            "Only parties see the data",
            "Java / Kotlin contracts",
            "Use: finance, insurance, trade",
        ],
    ),
    (
        "Polkadot",
        "#e6007a",
        "#fdeaf4",
        [
            "Relay chain + parachains",
            "Nominated Proof of Stake",
            "Shared security for parachains",
            "XCM cross-chain messages",
            "Forkless runtime upgrades",
            "Bridges to external chains",
            "Use: interoperability, DeFi",
        ],
    ),
]


def main() -> None:
    fig, ax = plt.subplots(figsize=(15, 7.4))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 7.4)
    ax.axis("off")
    ax.set_facecolor("#fbfdff")

    ax.text(7.5, 6.95, "Three Blockchain Platforms", ha="center", va="center",
            fontsize=20, fontweight="bold", color="#17324a")
    ax.text(7.5, 6.55, "Experiment 7 - Bitcoin, Corda and Polkadot case study",
            ha="center", va="center", fontsize=11, color="#4a5568")

    for index, (name, edge, fill, points) in enumerate(PLATFORMS):
        x = 0.5 + index * 4.85
        y = 1.05
        w, h = 4.45, 5.0
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.04,rounding_size=0.12",
                linewidth=2.2,
                edgecolor=edge,
                facecolor=fill,
            )
        )
        ax.text(x + w / 2, y + h - 0.45, name, ha="center", va="center",
                fontsize=15, fontweight="bold", color=edge)
        for row, point in enumerate(points):
            ax.text(x + 0.35, y + h - 1.15 - row * 0.52, f"\u2022  {point}",
                    ha="left", va="center", fontsize=10.4, color="#243b53")

    ax.text(7.5, 0.45,
            "Public trust vs. consortium privacy vs. cross-chain interoperability",
            ha="center", va="center", fontsize=10.5, style="italic", color="#4a5568")

    out = Path(__file__).resolve().parent.parent / "experiments/07-bitcoin-corda-polkadot/output/01_platform_comparison.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
