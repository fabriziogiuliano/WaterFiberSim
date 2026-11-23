"""Disegni di verifica."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .fiber import Scenario

LEG_COLORS = {"lead": "#adb5bd", "sensing": "#ff6a00", "junction": "#343a40", "reference": "#1f5fbf"}


def plot_map(scenario: Scenario, fmap: pd.DataFrame, path: str | Path) -> Path:
    """Rete con la fibra colorata secondo z (tratto di misura) + la fibra "srotolata" per tratti."""
    net = scenario.network
    fibers = list(fmap["fiber"].unique())
    fig = plt.figure(figsize=(15, 4.2 + 1.6 * len(fibers)), dpi=100)
    gs = fig.add_gridspec(len(fibers), 2, width_ratios=[1, 2.2], wspace=0.15, hspace=0.9)
    fig.suptitle(f"Mappa fibra → tubo: {scenario.title}", fontsize=15, fontweight="bold", x=0.02, ha="left")

    ax = fig.add_subplot(gs[:, 0])
    for pid, p in net.pipes.items():
        (xa, ya), (xb, yb) = net.node_xy[p.start_node], net.node_xy[p.end_node]
        ax.plot([xa, xb], [ya, yb], color="#dee2e6", lw=6, solid_capstyle="round", zorder=1)
        ax.text((xa + xb) / 2 + 6, (ya + yb) / 2 + 6, pid, fontsize=8, color="#868e96")
    for n, (x, y) in net.node_xy.items():
        ax.plot(x, y, "o", ms=5, color="#495057", zorder=3)
        ax.text(x - 6, y + 6, n, fontsize=8, ha="right")
    sens = fmap[fmap["leg"] == "sensing"]
    sc = ax.scatter(sens["x"], sens["y"], c=sens["z_m"], cmap="viridis", s=8, zorder=2)
    fig.colorbar(sc, ax=ax, shrink=0.7, label="z sul tratto di misura [m]")
    ax.set_aspect("equal")
    ax.set_title("rete: posizione dei campioni dell'elica", fontsize=11)
    ax.axis("off")

    for i, fid in enumerate(fibers):
        ax = fig.add_subplot(gs[i, 1])
        f = fmap[fmap["fiber"] == fid]
        step = f["z_m"].diff().median()
        blocks = (f["leg"] + "|" + f["pipe"].fillna("")).ne((f["leg"] + "|" + f["pipe"].fillna("")).shift()).cumsum()
        for _, b in f.groupby(blocks):
            z0, z1 = b["z_m"].iloc[0], b["z_m"].iloc[-1] + step
            leg, pid = b["leg"].iloc[0], b["pipe"].iloc[0]
            ax.barh(0, z1 - z0, left=z0, height=0.8, color=LEG_COLORS[leg], edgecolor="white", lw=0.8)
            if pid and z1 - z0 > 40:
                ax.text((z0 + z1) / 2, 0, pid, ha="center", va="center", fontsize=8.5, color="white", fontweight="bold")
        ax.set_yticks([])
        ax.set_xlim(0, f["z_m"].max() + step)
        ax.set_xlabel("z = distanza lungo la fibra dalla porta A [m]")
        ax.set_title(f"fibra {fid}: arancione = elica (misura), blu = dritto (riferimento), grigio = cavi, "
                     f"nero = giunzione", fontsize=10, loc="left")
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
    path = Path(path)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path
