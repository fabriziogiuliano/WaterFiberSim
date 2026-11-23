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


def plot_true_signal(sig, path: str | Path, fiber_id: str | None = None) -> Path:
    """Segnale vero di una fibra: variazione nel giorno (tempo x posizione), profili, serie nel tempo."""
    import numpy as np

    fm = sig.fiber_map
    fid = fiber_id or fm["fiber"].iloc[0]
    sel = np.flatnonzero(fm["fiber"].to_numpy() == fid)
    f = fm.iloc[sel].reset_index(drop=True)
    dnu = sig.nu_b_mhz[:, sel] - sig.coef.nu_b0_mhz
    press = sig.pressure_bar[:, sel]
    h = sig.times_s / 3600
    z = f["z_m"].to_numpy()

    fig = plt.figure(figsize=(15, 17), dpi=100)
    gs = fig.add_gridspec(4, 1, height_ratios=[1.5, 1, 1, 1.1], hspace=0.5)
    fig.suptitle(f"Segnale vero (senza rumore, temperatura costante), fibra {fid}", fontsize=15, fontweight="bold",
                 x=0.02, ha="left")

    def bande(ax, testo=True):
        key = f["leg"] + "|" + f["pipe"].fillna("")
        for _, b in f.groupby(key.ne(key.shift()).cumsum()):
            z0, leg, pid = b["z_m"].iloc[0], b["leg"].iloc[0], b["pipe"].iloc[0]
            ax.axvline(z0, color="#495057", lw=0.6, alpha=0.6)
            if testo and isinstance(pid, str):
                ax.text((z0 + b["z_m"].iloc[-1]) / 2, 1.01, pid, transform=ax.get_xaxis_transform(), ha="center",
                        fontsize=8.5, color=LEG_COLORS[leg], fontweight="bold")

    # 1. variazione rispetto alla media del giorno
    ax = fig.add_subplot(gs[0])
    var = dnu - dnu.mean(axis=0)
    v = np.abs(var).max()
    im = ax.imshow(var, aspect="auto", origin="lower", cmap="RdBu_r", vmin=-v, vmax=v,
                   extent=[z[0], z[-1], h[0], h[-1] + (h[1] - h[0])])
    fig.colorbar(im, ax=ax, label="\u0394\u03bd_B \u2212 media del giorno [MHz]", pad=0.01)
    bande(ax)
    ax.set_ylabel("ora del giorno [h]")
    ax.set_xlabel("z = distanza lungo la fibra dalla porta A [m]")
    ax.set_title("1. tempo \u00d7 posizione: VARIAZIONE nella giornata (rosso = pressione più alta della media); "
                 "sigle arancioni = elica, blu = riferimento", fontsize=11, loc="left", pad=16)

    # 2. profilo assoluto
    ax = fig.add_subplot(gs[1])
    for hh, c in ((4, "#1f5fbf"), (8, "#c92a2a")):
        i = int(np.argmin(abs(h - hh)))
        ax.plot(z, dnu[i], color=c, lw=1.5, label=f"ore {hh:02d}:00")
    bande(ax)
    ax.set_ylabel("\u0394\u03bd_B = \u03bd_B \u2212 \u03bd_B0 [MHz]")
    ax.set_xlabel("z [m]")
    ax.legend(loc="upper right")
    ax.set_title("2. profilo lungo la fibra rispetto al tubo vuoto: fibra a elica sui tubi in PE circa +70 MHz "
                 "(circa 4,8 bar); riferimento e cavi 0", fontsize=11, loc="left", pad=16)

    def punto(pid, leg):
        m = np.flatnonzero((f["pipe"] == pid).to_numpy() & (f["leg"] == leg).to_numpy())
        return m[int(np.argmin(abs(f["s_pipe_m"].to_numpy()[m] - sig_mid(f, pid))))] if len(m) else None

    # 3. fibra a elica sul tubo in PE nel tempo + pressione
    ax = fig.add_subplot(gs[2])
    j = punto("P1", "sensing")
    ax.step(h, dnu[:, j], where="post", color="#ff6a00", lw=2, label=f"\u0394\u03bd_B, elica a metà di P1 (z = {z[j]:.0f} m)")
    ax.set_ylabel("\u0394\u03bd_B [MHz]", color="#ff6a00")
    ax2 = ax.twinx()
    ax2.step(h, press[:, j], where="post", color="#2b8a3e", lw=1.2, ls="--", label="pressione dell'acqua in quel punto")
    ax2.set_ylabel("pressione [bar]", color="#2b8a3e")
    ax.legend(loc="lower left", fontsize=9)
    ax2.legend(loc="lower right", fontsize=9)
    ax.set_xlabel("ora del giorno [h]")
    escursione = f"{np.ptp(dnu[:, j]):.1f} MHz = {np.ptp(press[:, j]):.2f} bar".replace(".", ",")
    ax.set_title(f"3. nel tempo, fibra a elica sul tubo in PE (plastica), a metà di P1: segue la pressione (escursione {escursione})", fontsize=11, loc="left")

    # 4. si vede o no? variazione nella giornata in tre punti contro l'errore tipico dello strumento
    ax = fig.add_subplot(gs[3])
    ERRORE_MHZ = 0.5          # indicativo: Bertulessi 2023 §2.1, "better than ... 10 µε" (limite superiore,
                              # statistica non dichiarata). Al passo 3 diventa un parametro (Soto & Thévenaz 2013).
    ax.axhspan(-ERRORE_MHZ, ERRORE_MHZ, color="#adb5bd", alpha=0.35, lw=0,
               label="errore indicativo dello strumento, ±0,5 MHz (Bertulessi 2023: limite superiore, statistica non dichiarata)")
    for pid, leg, c, lab in (("P1", "sensing", "#ff6a00", "fibra a elica sul tubo in PE (P1)"),
                             ("P1", "reference", "#1f5fbf", "fibra di riferimento, libera (P1)")):
        jj = punto(pid, leg)
        if jj is not None:
            serie = dnu[:, jj] - dnu[:, jj].mean()
            ax.step(h, serie, where="post", color=c, lw=2.2 if leg == "sensing" and pid == "P1" else 1.8,
                    label=f"{lab}: escursione {np.ptp(serie):.2f} MHz".replace(".", ","))
    ax.set_ylim(-2, 2)
    ax.set_ylabel("variazione rispetto\nalla media del giorno [MHz]")
    ax.set_xlabel("ora del giorno [h]")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), fontsize=9, ncol=1, frameon=False)
    ax.set_title("4. SI VEDE O NO? Variazione nella giornata a metà di P1, fibra a elica e fibra di riferimento, "
                 "confrontata con un errore indicativo dello strumento", fontsize=11, loc="left")

    path = Path(path)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def sig_mid(f, pid):
    s = f.loc[f["pipe"] == pid, "s_pipe_m"]
    return (s.min() + s.max()) / 2
