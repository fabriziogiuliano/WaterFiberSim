"""Disegni di verifica."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .fiber import Scenario

LEG_COLORS = {"lead": "#adb5bd", "sensing": "#ff6a00", "junction": "#343a40", "reference": "#1f5fbf"}


M_WATER_TO_BAR = 0.0980665   # 1 m di colonna d'acqua in bar


def plot_map(scenario: Scenario, fmap: pd.DataFrame, path: str | Path) -> Path:
    """Rete con la fibra colorata secondo z (tratto di misura) + la fibra "srotolata" per tratti.

    Rete tutta su una riga (una strada): al posto della pianta, il profilo della strada (quote, serbatoio,
    rubinetti, interrogatore).
    """
    net = scenario.network
    if len({y for _, y in net.node_xy.values()}) == 1:
        return _plot_map_line(scenario, fmap, path)
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
        _fiber_bar(fig.add_subplot(gs[i, 1]), fmap[fmap["fiber"] == fid], fid, height=0.8)
    return _save(fig, path)


def _plot_map_line(scenario: Scenario, fmap: pd.DataFrame, path: str | Path) -> Path:
    """Strada: grafico 1 = profilo (quote, pelo dell'acqua, rubinetti, interrogatore); poi la fibra srotolata."""
    net = scenario.network
    fibers = list(fmap["fiber"].unique())
    fig = plt.figure(figsize=(15, 4.6 + 1.5 * len(fibers)), dpi=100)
    gs = fig.add_gridspec(1 + len(fibers), 1, height_ratios=[3.2] + [1.0] * len(fibers), hspace=0.75)
    fig.suptitle(f"Mappa fibra → tubo: {scenario.title}", fontsize=15, fontweight="bold", x=0.02, ha="left")

    ax = fig.add_subplot(gs[0])
    jn = sorted((n for n, k in net.node_kind.items() if k == "junction"), key=lambda n: net.node_xy[n][0])
    xs = [net.node_xy[n][0] for n in jn]
    el = [net.node_elev_m[n] for n in jn]
    span = max(xs) - min(xs)
    ax.fill_between(xs, el, min(el) - 8, color="#e9dcc9", zorder=0)                  # terreno
    ax.plot(xs, el, color="#1f5fbf", lw=4, solid_capstyle="round", zorder=2, label="tubo con la fibra a elica")
    for pid, p in net.pipes.items():
        if net.node_kind[p.start_node] == "junction" and net.node_kind[p.end_node] == "junction":
            xm = (net.node_xy[p.start_node][0] + net.node_xy[p.end_node][0]) / 2
            ym = (net.node_elev_m[p.start_node] + net.node_elev_m[p.end_node]) / 2
            ax.text(xm, ym - 1.2, pid, ha="center", va="top", fontsize=8.5, color="#1f5fbf", fontweight="bold")
    taps = [n for n in jn if net.base_demand_lps.get(n, 0) > 0]
    for n in jn:
        x, e = net.node_xy[n][0], net.node_elev_m[n]
        ax.plot(x, e, "o", ms=5, color="#212529", zorder=3)
        ax.text(x, e + 1.0, n, ha="center", va="bottom", fontsize=8)
    for n in taps:
        x, e = net.node_xy[n][0], net.node_elev_m[n]
        ax.annotate("", (x, e - 4.5), (x, e - 0.6), arrowprops=dict(arrowstyle="-|>", color="#2b8a3e", lw=1.4))
    if taps:
        q = net.base_demand_lps[taps[0]]
        ax.plot([], [], color="#2b8a3e", marker="v", ls="", label=f"rubinetto (prelievo di base {q:g} L/s,\nvaria nel giorno)".replace(".", ","))

    for r in (n for n, k in net.node_kind.items() if k == "reservoir"):
        head = net.node_elev_m[r]
        # il serbatoio è collegato al nodo più vicino della strada
        xr = net.node_xy[r][0]
        near = min(jn, key=lambda n: abs(net.node_xy[n][0] - xr))
        xn, en_ = net.node_xy[near][0], net.node_elev_m[near]
        side = -1 if xr <= xn else 1
        w = 0.05 * span
        x0 = xn + side * 0.03 * span
        x1 = x0 + side * w
        ax.fill_between(sorted([x0, x1]), en_, head, color="#a5d8ff", zorder=1)
        ax.plot(sorted([x0, x1]), [head, head], color="#1971c2", lw=2)
        ax.text((x0 + x1) / 2, head + 1.0, f"serbatoio {r}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.plot([min(xs) - 0.1 * span, max(xs) + 0.1 * span], [head, head], color="#1971c2", ls="--", lw=1,
                label=f"pelo dell'acqua del serbatoio ({head:g} m)")
        for n in (jn[0], jn[-1]):
            x, e = net.node_xy[n][0], net.node_elev_m[n]
            ax.annotate("", (x, e + 3.2), (x, head), arrowprops=dict(arrowstyle="<->", color="#868e96", lw=1))
            ax.text(x + 0.01 * span * (1 if n == jn[0] else -1), (e + head) / 2,
                    f"{head - e:g} m\n≈ {(head - e) * M_WATER_TO_BAR:.1f} bar".replace(".", ","),
                    ha="left" if n == jn[0] else "right", va="center", fontsize=8.5, color="#495057")

    for f in scenario.fibers:
        n = f.interrogator.node
        x, e = net.node_xy[n][0], net.node_elev_m[n]
        ax.plot(x, e + 6.5, "s", ms=11, color="#7048e8", zorder=4)
        ax.text(x - 0.012 * span, e + 6.5, f"interrogatore {f.id}", ha="right", va="center", fontsize=8.5, color="#7048e8")
    ax.plot([], [], "s", color="#7048e8", ls="", label="interrogatore (porte A e B\ndell'anello di fibra)")

    heads = [net.node_elev_m[r] for r, k in net.node_kind.items() if k == "reservoir"] or [max(el)]
    ax.set_ylim(min(el) - 8, max(heads) + 12)
    ax.set_xlim(min(xs) - 0.12 * span, max(xs) + 0.12 * span)
    ax.set_xlabel("distanza lungo la strada [m]")
    ax.set_ylabel("quota [m]")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8.5, frameon=False)
    ax.set_title("Grafico 1 — profilo della strada: pressione statica (nessun prelievo) = dislivello tra il pelo "
                 "dell'acqua e il tubo, circa 0,1 bar per metro", fontsize=11, loc="left")

    for i, fid in enumerate(fibers):
        _fiber_bar(fig.add_subplot(gs[1 + i]), fmap[fmap["fiber"] == fid], fid, height=0.6,
                   title_prefix=f"Grafico {2 + i} — ")
    return _save(fig, path)


def _fiber_bar(ax, f: pd.DataFrame, fid: str, height: float, title_prefix: str = "") -> None:
    """La fibra srotolata lungo z, a blocchi colorati per tratto; i tratti corti (cavi, giunzione) con un'etichetta."""
    step = f["z_m"].diff().median()
    key = f["leg"] + "|" + f["pipe"].fillna("")
    zmax = f["z_m"].max() + step
    nomi = {"lead": "cavo", "junction": "giunzione"}
    for _, b in f.groupby(key.ne(key.shift()).cumsum()):
        z0, z1 = b["z_m"].iloc[0], b["z_m"].iloc[-1] + step
        leg, pid = b["leg"].iloc[0], b["pipe"].iloc[0]
        ax.barh(0, z1 - z0, left=z0, height=height, color=LEG_COLORS[leg], edgecolor="white", lw=0.8)
        if pid and z1 - z0 > 0.025 * zmax:
            ax.text((z0 + z1) / 2, 0, pid, ha="center", va="center", fontsize=8.5, color="white", fontweight="bold")
        elif leg in nomi and z1 - z0 < 0.03 * zmax:
            ax.annotate(f"{nomi[leg]} {z1 - z0:.0f} m", ((z0 + z1) / 2, height / 2), ((z0 + z1) / 2, height / 2 + 0.45),
                        ha="center", fontsize=8, color="#495057", arrowprops=dict(arrowstyle="-", color="#868e96"))
    ax.set_yticks([])
    ax.set_ylim(-0.6, 1.2)
    ax.set_xlim(0, zmax)
    ax.set_xlabel("z = distanza lungo la fibra dalla porta A [m]")
    ax.set_title(f"{title_prefix}fibra {fid} srotolata: arancione = elica (misura, andata), "
                 f"blu = dritto (riferimento, ritorno), grigio = cavi, nero = giunzione", fontsize=10, loc="left")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)


def _save(fig, path: str | Path) -> Path:
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
    temp_txt = ("con la temperatura del terreno, NON compensata" if np.any(sig.delta_t_c != 0)
                else "temperatura costante")
    fig.suptitle(f"Segnale vero (senza rumore, {temp_txt}), fibra {fid}{consumi}", fontsize=15,
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
    # dalla sola pressione: la temperatura, se c'è, non deve entrare nel rapporto
    dnu_p = sig.strain_ue[:, sel] * sig.coef.c_eps_mhz_per_ue
    mhz_per_bar = dnu_p[:, sens].mean() / np.nanmean(press[:, sens])
    con_temp = bool(np.any(sig.delta_t_c != 0))
    k_txt = f"{mhz_per_bar:.1f}".replace(".", ",")

    def asse_bar(ax, offset_mhz=0.0, nome="pressione equivalente"):
        if con_temp:
            nome = "pressione APPARENTE"
        sec = ax.secondary_yaxis("right", functions=(lambda m: (m - offset_mhz) / mhz_per_bar,
                                                     lambda b: b * mhz_per_bar + offset_mhz))
        sec.set_ylabel(f"{nome} [bar]\n(sull'elica: 1 bar = {k_txt} MHz)", color="#2b8a3e", fontsize=9)
        sec.tick_params(colors="#2b8a3e")
        return sec

    # grafico 1: frequenza assoluta lungo la fibra: a vuoto (misura di base) e con il carico in due orari
    ax = fig.add_subplot(gs[0])
    nu_vuoto = sig.baseline_mhz[sel]
    ax.plot(z, nu_vuoto, color="#495057", lw=2, ls="--", label="A vuoto (0 bar)")
    for hh, c in ore:
        i = int(np.argmin(abs(h - hh)))
        ax.plot(z, sig.nu_b_mhz[i, sel], color=c, lw=1.6, label=f"con l'acqua in pressione, ore {hh:02d}:00")
    bande(ax)
    ax.set_ylabel("\u03bd_B [MHz]")
    ax.axhline(sig.coef.nu_b0_mhz, color="#adb5bd", lw=0.8, ls=":")
    # in bar: per ogni tubo sull'elica, quanto la curva sta sopra la misura di base (non un asse: la base cambia per metro)
    pipes_s = f.loc[sens, "pipe"]
    tubi1 = list(pd.unique(pipes_s))
    sfalsa = len(tubi1) > 5                 # tanti tubi: etichette su due livelli alternati per non sovrapporle
    for k, pid in enumerate(tubi1):
        m = np.flatnonzero(sens & (f["pipe"] == pid).to_numpy())
        righe = []
        for hh, c in ore:
            i = int(np.argmin(abs(h - hh)))
            dm = dnu[i, m].mean()
            righe.append((f"{hh:02d}:00  +{dm:.0f} MHz = {dm / mhz_per_bar:.2f} bar".replace(".", ","), c))
        if sfalsa:   # tanti tubi: solo i bar, a quota comune, su due livelli alternati
            righe = [(t.split("= ")[1], c) for t, c in righe]
            ytop = sig.nu_b_mhz[:, sel][:, sens[sel]].max() + (34 if k % 2 else 0)
        else:
            ytop = sig.nu_b_mhz[:, sel][:, m].max()
        for r, (txt, c) in enumerate(righe):
            ax.text(z[m].mean(), ytop + 8 + 14 * (len(righe) - 1 - r), txt, ha="center", fontsize=8, color=c)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + (75 if sfalsa else 30))
    if sfalsa or con_temp:
        nota = "sopra ogni tubo: pressione media sull'elica alle due ore"
        if con_temp:
            nota += " — APPARENTE: Δν/(MHz per bar), con dentro la temperatura non compensata"
        ax.text(0.005, 0.98, nota, transform=ax.transAxes, fontsize=8, va="top", color="#495057")
    ax.set_xlabel("z = distanza lungo la fibra dalla porta A [m]")
    ax.legend(loc="center right", fontsize=9)
    ax.set_title("Grafico 1 \u2014 frequenza Brillouin lungo la fibra: a vuoto e con il carico (valori assoluti, come in Bertulessi "
                 "2023 Fig. 7a). La misura di base NON è piatta: la posa ha tirato la fibra", fontsize=11, loc="left",
                 pad=16)

    # grafico 2: differenza rispetto alla misura di base
    ax = fig.add_subplot(gs[1])
    for hh, c in ore:
        i = int(np.argmin(abs(h - hh)))
        ax.plot(z, dnu[i], color=c, lw=1.5, label=f"ore {hh:02d}:00")
        if con_temp:
            ax.plot(z, dnu_p[i], color=c, lw=1, ls=":", label=f"ore {hh:02d}:00, solo pressione (senza temperatura)")
    bande(ax)
    ax.set_ylabel("\u0394\u03bd_B [MHz]")
    asse_bar(ax)
    ax.set_xlabel("z [m]")
    ax.legend(loc="center right")
    if con_temp:
        medio = (f"circa +{dnu[:, sens].mean():.0f} MHz (sembrerebbero {dnu[:, sens].mean() / mhz_per_bar:.1f} bar; "
                 f"la pressione vera è circa {np.nanmean(press[:, sens]):.1f} bar: il resto è temperatura)").replace(".", ",")
    else:
        medio = f"circa +{dnu[:, sens].mean():.0f} MHz (circa {np.nanmean(press[:, sens]):.1f} bar)".replace(".", ",")
    ax.set_title(f"Grafico 2 \u2014 differenza rispetto alla misura di base: \u0394\u03bd_B = \u03bd_B \u2212 \u03bd_B a vuoto. "
                 f"\nFibra a elica sui tubi in PE {medio} in media; riferimento e cavi " + ("solo temperatura" if con_temp else "0"), fontsize=11, loc="left", pad=16)

    # grafico 3: variazione rispetto alla media del giorno
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
    ax.set_title("Grafico 3 \u2014 tempo \u00d7 posizione: VARIAZIONE nella giornata (rosso = pressione più alta della media); "
                 "sigle arancioni = elica, blu = riferimento", fontsize=11, loc="left", pad=16)

    def punto(pid, leg):
        m = np.flatnonzero((f["pipe"] == pid).to_numpy() & (f["leg"] == leg).to_numpy())
        return m[int(np.argmin(abs(f["s_pipe_m"].to_numpy()[m] - sig_mid(f, pid))))] if len(m) else None

    # tubi coperti dall'elica, nell'ordine in cui li percorre la fibra; arancione via via più scuro
    tubi = list(pd.unique(f.loc[sens, "pipe"]))
    colori = plt.get_cmap("Oranges")(np.linspace(0.45, 0.95, len(tubi)))
    punti = {pid: punto(pid, "sensing") for pid in tubi}

    # grafico 4: tutti i tubi nel tempo: Δν_B a metà di ciascun tubo (a destra la pressione in bar)
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
    if len(tubi) > 1:
        t4 = ("Grafico 4 \u2014 nel tempo, fibra a elica a metà di OGNI tubo: segue la pressione; i cali più forti "
              "sono nei tubi più lontani dal serbatoio (si somma la perdita di carico dei tubi a monte)")
    else:
        t4 = "Grafico 4 \u2014 nel tempo, fibra a elica a metà del tubo: segue la pressione (cala quando si preleva)"
    ax.set_title(t4, fontsize=11, loc="left")

    path = Path(path)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def sig_mid(f, pid):
    s = f.loc[f["pipe"] == pid, "s_pipe_m"]
    return (s.min() + s.max()) / 2


def plot_uncertainty(scenario: Scenario, fmap: pd.DataFrame, fiber, path: str | Path) -> Path:
    """Incertezza attesa di UNA misura lungo la fibra ([ST13]), in MHz; a destra in bar sull'elica."""
    import numpy as np

    from .brillouin import BrillouinCoefficients
    from .instrument import helix_mhz_per_bar, sigma_nu_mhz, snr_linear

    f = fmap[fmap["fiber"] == fiber.id]
    z = f["z_m"].to_numpy()
    sig = sigma_nu_mhz(fiber, z)
    k = np.nanmean(list(helix_mhz_per_bar(scenario, fiber, BrillouinCoefficients()).values()))
    i = fiber.interrogator

    fig, ax = plt.subplots(figsize=(15, 4.6), dpi=100)
    for leg in ("lead", "sensing", "junction", "reference"):
        m = (f["leg"] == leg).to_numpy()
        ax.scatter(z[m], sig[m], s=1, color=LEG_COLORS[leg],
                   label={"lead": "cavi", "sensing": "elica (misura)", "junction": "giunzione",
                          "reference": "dritto (riferimento)"}[leg])
    ax.plot(z, sig * np.sqrt(2), color="#495057", ls="--", lw=1,
            label="differenza dalla misura di base (×√2: due misure rumorose)")
    ax.set_ylim(0, sig.max() * np.sqrt(2) * 1.25)
    ax.set_xlabel("z = distanza lungo la fibra dalla porta A [m]")
    ax.set_ylabel("incertezza σ_ν di una misura [MHz]")
    sec = ax.secondary_yaxis("right", functions=(lambda m: m / k, lambda b: b * k))
    sec.set_ylabel(f"[bar] sull'elica\n(1 bar = {k:.1f} MHz)".replace(".", ","), color="#2b8a3e", fontsize=9)
    sec.tick_params(colors="#2b8a3e")
    ax.legend(loc="lower left", fontsize=8.5, markerscale=6)
    snr0 = 10 * np.log10(snr_linear(fiber, 0.0))
    txt = (f"impulso {i.pulse_width_ns:g} ns (risoluzione {fiber.spatial_resolution_m:.2f} m), "
           f"passo {i.freq_step_mhz:g} MHz, {i.n_averages} medie, campana {i.linewidth_mhz:g} MHz, "
           f"SNR all'ingresso {snr0:.1f} dB con le medie (SNR₀ {i.snr0_db:g} dB a {i.snr0_resolution_m:g} m, 1 traccia), attenuazione {fiber.attenuation_db_per_km:g} dB/km").replace(".", ",")
    ax.set_title(f"Incertezza attesa dello strumento, fibra {fiber.id} (Soto & Thévenaz 2013, Eq. 7 e 9)\n{txt}",
                 fontsize=11, loc="left")
    return _save(fig, path)


def plot_compensation(scenario: Scenario, sig, fiber, path: str | Path, hour: int = 8,
                      k_range=(3.5, 8.0), ref_avg_m: float | None = None) -> Path:
    """Grafico 1: pressione lungo l'elica (vera, apparente, compensata). Grafico 2: errore casuale vs media del riferimento."""
    import numpy as np

    from .compensation import apparent_pressure_bar, compensated_pressure_bar, random_error_bar

    K = scenario.temperature.helix_mhz_per_c
    f = sig.fiber_map
    h = np.flatnonzero((f["fiber"].to_numpy() == fiber.id) & (f["leg"].to_numpy() == "sensing"))
    z = f["z_m"].to_numpy()[h]
    t = int(np.argmin(abs(sig.times_s / 3600 - hour)))
    L_eq = (K / sig.coef.c_t_mhz_per_c) ** 2 * fiber.spatial_resolution_m
    if ref_avg_m is None:
        ref_avg_m = L_eq

    fig = plt.figure(figsize=(15, 10), dpi=100)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.3, 1], hspace=0.45)
    fig.suptitle(f"Compensazione della temperatura con il riferimento, fibra {fiber.id} (passo T3)", fontsize=15,
                 fontweight="bold", x=0.02, ha="left")

    ax = fig.add_subplot(gs[0])
    ax.plot(z, sig.pressure_bar[t, h], color="#212529", lw=3, label="pressione vera (EPANET)")
    ax.plot(z, apparent_pressure_bar(sig, scenario, fiber)[t, h], color="#adb5bd", lw=1.5,
            label="letta SENZA compensare")
    for k_ass, c in ((k_range[0], "#f08c00"), (k_range[1], "#7048e8")):
        ax.plot(z, compensated_pressure_bar(sig, scenario, fiber, k_ass)[t, h], color=c, lw=1.2, ls="--",
                label=f"compensata con K = {k_ass:g} MHz/°C (vero {K:g}): errore SISTEMATICO".replace(".", ","))
    ax.plot(z, compensated_pressure_bar(sig, scenario, fiber, K, ref_avg_m)[t, h], color="#2b8a3e", lw=1.5,
            label=f"compensata con K giusto e riferimento mediato su {ref_avg_m:.0f} m (sfuma le variazioni locali)")
    ax.plot(z, compensated_pressure_bar(sig, scenario, fiber, K)[t, h], color="#c92a2a", lw=1, ls=":",
            label="compensata con K giusto, punto per punto (senza rumore: coincide con la vera)")
    ax.set_xlabel("z = distanza lungo la fibra dalla porta A [m] (solo il tratto a elica)")
    ax.set_ylabel("pressione [bar]")
    ax.legend(loc="lower left", fontsize=8.5)
    ax.set_title(f"Grafico 1 — pressione lungo l'elica alle {hour:02d}:00, senza rumore: cosa fa la compensazione e cosa "
                 f"sbaglia se K (sensibilità dell'elica alla temperatura) non è quello vero", fontsize=11, loc="left")

    ax = fig.add_subplot(gs[1])
    L = np.linspace(0, max(4 * L_eq, 50), 400)
    tot, hel, th = random_error_bar(scenario, fiber, K, L)
    ax.plot(L, tot * np.ones_like(L), color="#212529", lw=2.5, label="totale")
    ax.plot(L, hel * np.ones_like(L), color="#ff6a00", lw=1.5, ls="--", label="dall'elica (rumore dello strumento)")
    ax.plot(L, th, color="#1f5fbf", lw=1.5, ls="--", label=f"dal riferimento × K/C_T = {K:g} (temperatura)".replace(".", ","))
    ax.axvline(L_eq, color="#868e96", lw=1, ls=":")
    ax.text(L_eq, ax.get_ylim()[1] * 0.92, f"  {L_eq:.0f} m: i due contributi si eguagliano", fontsize=9, color="#495057")
    ax.set_xlabel("lunghezza su cui si media il riferimento [m]")
    ax.set_ylabel("errore casuale (1σ) [bar]")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("Grafico 2 — errore casuale di UNA misura compensata (differenza dalla misura di base), "
                 "in funzione della media del riferimento ([ST13] + propagazione degli errori)", fontsize=11, loc="left")
    return _save(fig, path)
