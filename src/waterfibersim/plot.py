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
    dnu = sig.nu_b_mhz[:, sel] - sig.baseline_mhz[sel]      # differenza dalla misura di base, metro per metro
    press = sig.pressure_bar[:, sel]
    h = sig.times_s / 3600
    z = f["z_m"].to_numpy()

    fig = plt.figure(figsize=(15, 20), dpi=100)
    gs = fig.add_gridspec(4, 1, height_ratios=[1, 1, 1.6, 1.1], hspace=0.6, top=0.94)
    consumi = "" if sig.demand_multiplier == 1 else f", consumi \u00d7{sig.demand_multiplier:g}"
    fig.suptitle(f"Segnale vero (senza rumore, temperatura costante), fibra {fid}{consumi}", fontsize=15,
                 fontweight="bold", x=0.02, ha="left")

    def bande(ax, testo=True):
        key = f["leg"] + "|" + f["pipe"].fillna("")
        for _, b in f.groupby(key.ne(key.shift()).cumsum()):
            z0, leg, pid = b["z_m"].iloc[0], b["leg"].iloc[0], b["pipe"].iloc[0]
            ax.axvline(z0, color="#495057", lw=0.6, alpha=0.6)
            if testo and isinstance(pid, str):
                ax.text((z0 + b["z_m"].iloc[-1]) / 2, 1.01, pid, transform=ax.get_xaxis_transform(), ha="center",
                        fontsize=8.5, color=LEG_COLORS[leg], fontweight="bold")

    sens = (f["leg"] == "sensing").to_numpy()
    ore = [(4, "#1f5fbf"), (8, "#c92a2a")]
    # rapporto MHz/bar della fibra a elica (lineare: Δν = k · p); vale solo sul tratto a elica
    mhz_per_bar = dnu[:, sens].mean() / np.nanmean(press[:, sens])
    k_txt = f"{mhz_per_bar:.1f}".replace(".", ",")

    def asse_bar(ax, offset_mhz=0.0, nome="pressione equivalente"):
        sec = ax.secondary_yaxis("right", functions=(lambda m: (m - offset_mhz) / mhz_per_bar,
                                                     lambda b: b * mhz_per_bar + offset_mhz))
        sec.set_ylabel(f"{nome} [bar]\n(sull'elica: 1 bar = {k_txt} MHz)", color="#2b8a3e", fontsize=9)
        sec.tick_params(colors="#2b8a3e")
        return sec

    # 1. frequenza assoluta lungo la fibra: a vuoto (misura di base) e con il carico in due orari
    ax = fig.add_subplot(gs[0])
    nu_vuoto = sig.baseline_mhz[sel]
    ax.plot(z, nu_vuoto, color="#495057", lw=2, ls="--", label="a vuoto, 0 bar (misura di base): ogni metro ha la sua")
    for hh, c in ore:
        i = int(np.argmin(abs(h - hh)))
        ax.plot(z, sig.nu_b_mhz[i, sel], color=c, lw=1.6, label=f"con l'acqua in pressione, ore {hh:02d}:00")
    bande(ax)
    ax.set_ylabel("\u03bd_B [MHz]")
    ax.axhline(sig.coef.nu_b0_mhz, color="#adb5bd", lw=0.8, ls=":")
    # in bar: per ogni tubo sull'elica, quanto la curva sta sopra la misura di base (non un asse: la base cambia per metro)
    pipes_s = f.loc[sens, "pipe"]
    for pid in pd.unique(pipes_s):
        m = np.flatnonzero(sens & (f["pipe"] == pid).to_numpy())
        righe = []
        for hh, c in ore:
            i = int(np.argmin(abs(h - hh)))
            dm = dnu[i, m].mean()
            righe.append((f"{hh:02d}:00  +{dm:.0f} MHz = {dm / mhz_per_bar:.2f} bar".replace(".", ","), c))
        ytop = sig.nu_b_mhz[:, sel][:, m].max()
        for r, (txt, c) in enumerate(righe):
            ax.text(z[m].mean(), ytop + 8 + 14 * (len(righe) - 1 - r), txt, ha="center", fontsize=8, color=c)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + 30)
    ax.set_xlabel("z = distanza lungo la fibra dalla porta A [m]")
    ax.legend(loc="center right", fontsize=9)
    ax.set_title("1. frequenza Brillouin lungo la fibra: a vuoto e con il carico (valori assoluti, come in Bertulessi "
                 "2023 Fig. 7a). La misura di base NON è piatta: la posa ha tirato la fibra", fontsize=11, loc="left",
                 pad=16)

    # 2. differenza rispetto alla misura di base
    ax = fig.add_subplot(gs[1])
    for hh, c in ore:
        i = int(np.argmin(abs(h - hh)))
        ax.plot(z, dnu[i], color=c, lw=1.5, label=f"ore {hh:02d}:00")
    bande(ax)
    ax.set_ylabel("\u0394\u03bd_B [MHz]")
    asse_bar(ax)
    ax.set_xlabel("z [m]")
    ax.legend(loc="center right")
    medio = f"circa +{dnu[:, sens].mean():.0f} MHz (circa {np.nanmean(press[:, sens]):.1f} bar)".replace(".", ",")
    ax.set_title(f"2. differenza rispetto alla misura di base: \u0394\u03bd_B = \u03bd_B \u2212 \u03bd_B a vuoto. "
                 f"Fibra a elica sui tubi in PE {medio} in media; riferimento e cavi 0", fontsize=11, loc="left", pad=16)

    # 3. variazione rispetto alla media del giorno
    ax = fig.add_subplot(gs[2])
    var = dnu - dnu.mean(axis=0)
    v = np.abs(var).max()
    im = ax.imshow(var, aspect="auto", origin="lower", cmap="RdBu_r", vmin=-v, vmax=v,
                   extent=[z[0], z[-1], h[0], h[-1] + (h[1] - h[0])])
    cb = fig.colorbar(im, ax=ax, label="\u0394\u03bd_B \u2212 media del giorno [MHz]", pad=0.25, location="bottom",
                      shrink=0.4, aspect=40)
    cbs = cb.ax.secondary_xaxis("top", functions=(lambda m: m / mhz_per_bar, lambda b: b * mhz_per_bar))
    cbs.set_xlabel(f"[bar] (sull'elica: 1 bar = {k_txt} MHz)", color="#2b8a3e", fontsize=9)
    cbs.tick_params(colors="#2b8a3e", labelsize=8)
    bande(ax)
    ax.set_ylabel("ora del giorno [h]")
    ax.set_xlabel("z = distanza lungo la fibra dalla porta A [m]")
    ax.set_title("3. tempo \u00d7 posizione: VARIAZIONE nella giornata (rosso = pressione più alta della media); "
                 "sigle arancioni = elica, blu = riferimento", fontsize=11, loc="left", pad=16)

    def punto(pid, leg):
        m = np.flatnonzero((f["pipe"] == pid).to_numpy() & (f["leg"] == leg).to_numpy())
        return m[int(np.argmin(abs(f["s_pipe_m"].to_numpy()[m] - sig_mid(f, pid))))] if len(m) else None

    # tubi coperti dall'elica, nell'ordine in cui li percorre la fibra; arancione via via più scuro
    tubi = list(pd.unique(f.loc[sens, "pipe"]))
    colori = plt.get_cmap("Oranges")(np.linspace(0.45, 0.95, len(tubi)))
    punti = {pid: punto(pid, "sensing") for pid in tubi}

    # 4. tutti i tubi nel tempo: Δν_B a metà di ciascun tubo (a destra la pressione in bar)
    ax = fig.add_subplot(gs[3])
    for pid, c in zip(tubi, colori):
        j = punti[pid]
        esc = f"{np.ptp(dnu[:, j]):.1f} MHz = {np.ptp(press[:, j]):.2f} bar".replace(".", ",")
        ax.step(h, dnu[:, j], where="post", color=c, lw=2,
                label=f"{pid}, a metà (z = {z[j]:.0f} m): {np.nanmean(press[:, j]):.2f} bar in media, "
                      f"escursione {esc}".replace(".", ",", 1))
    ax.set_ylabel("\u0394\u03bd_B [MHz]")
    asse_bar(ax, nome="pressione")
    ax.set_xlabel("ora del giorno [h]")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=9, ncol=2, frameon=False)
    ax.set_title("4. nel tempo, fibra a elica a metà di OGNI tubo: segue la pressione; più lontano dal serbatoio, "
                 "pressione più bassa e cali più forti", fontsize=11, loc="left")

    path = Path(path)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def sig_mid(f, pid):
    s = f.loc[f["pipe"] == pid, "s_pipe_m"]
    return (s.min() + s.max()) / 2
