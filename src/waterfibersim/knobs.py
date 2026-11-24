"""Studio delle manopole (variabili) del simulatore: per ognuna, cosa succede se la si gira.

Usa le stesse funzioni del simulatore (instrument, mechanics, compensation, temperature), su una fibra e un tubo di
riferimento (scenario S1: PE100 DN110 SDR11, interrogatore con le impostazioni di [B23]). Scrive le figure del
capitolo 9 in docs/img/manopole_*.png e restituisce i numeri citati nel testo.

    python -m waterfibersim knobs
"""

from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .brillouin import BrillouinCoefficients
from .fiber import C_M_PER_S, load_scenario
from .instrument import sigma_nu_mhz
from .mechanics import Layer, helix_strain_ue, multilayer_strain_ue
from .network import PipeSpec

COEF = BrillouinCoefficients()
VERDE = "#2b8a3e"


def _pe(E=1.0, sdr=11.0, od=110.0, nu=0.4) -> PipeSpec:
    t = od / sdr
    return PipeSpec("x", "a", "b", 100, od - 2 * t, "PE100", od, t, E, nu, 1)


def _mhz_per_bar_pe(E=1.0, sdr=11.0, angle=70.0, nu=0.4) -> float:
    p = _pe(E, sdr, nu=nu)
    r_e = p.outer_diameter_mm / 2000
    et, ez = multilayer_strain_ue([Layer(r_e - p.wall_thickness_mm / 1000, r_e, E, nu)], 0.1, r_e)
    return float(helix_strain_ue(et, ez, angle)) * COEF.c_eps_mhz_per_ue


def _bar_axis(ax, k, label="pressione equivalente [bar]"):
    sec = ax.secondary_yaxis("right", functions=(lambda m: m / k, lambda b: b * k))
    sec.set_ylabel(f"{label}\n(elica su PE: 1 bar = {k:.1f} MHz)".replace(".", ","), color=VERDE, fontsize=9)
    sec.tick_params(colors=VERDE)


def _save(fig, path):
    fig.savefig(path, bbox_inches="tight", facecolor="white", dpi=100)
    plt.close(fig)


def instrument_figure(root: Path, out: Path) -> dict:
    f0 = load_scenario(root / "scenario_paths" / "S1_street_flat.yaml").fibers[0]
    k = _mhz_per_bar_pe()
    i0 = f0.interrogator
    nums = {}

    def fib(**kw):
        return replace(f0, interrogator=replace(i0, **kw))

    fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=100)
    fig.suptitle("Manopole dello strumento: incertezza di UNA misura e tempo di misura (Soto & Thévenaz 2013)",
                 fontsize=14, fontweight="bold", x=0.02, ha="left")
    ax = axs[0, 0]
    nav = np.logspace(0, np.log10(65000), 200)
    for d in (1, 2, 5):
        ax.plot(nav, [float(sigma_nu_mhz(fib(n_averages=int(n), freq_step_mhz=d), 0)) for n in nav], label=f"passo δ = {d} MHz")
    ax.axvline(256, color="#868e96", ls=":")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("medie per passo di frequenza N_AV"); ax.set_ylabel("σ_ν [MHz]")
    ax.set_title("Grafico 1 — medie e passo di frequenza (impulso 20 ns, inizio fibra)", loc="left", fontsize=11)
    ax.legend(); _bar_axis(ax, k)
    nums["sigma_256_1"] = float(sigma_nu_mhz(f0, 0))
    nums["sigma_4096_1"] = float(sigma_nu_mhz(fib(n_averages=4096), 0))
    nums["sigma_256_5"] = float(sigma_nu_mhz(fib(freq_step_mhz=5), 0))

    ax = axs[0, 1]
    tau = np.linspace(5, 100, 200)
    sig = [float(sigma_nu_mhz(fib(pulse_width_ns=t), 0)) for t in tau]
    ax.plot(tau, sig, color="#c92a2a")
    ax.axvline(20, color="#868e96", ls=":")
    ax.set_xlabel("durata dell'impulso τ [ns]  (risoluzione = c·τ/(2n): 10 ns ≈ 1 m)"); ax.set_ylabel("σ_ν [MHz]")
    ax.set_title("Grafico 2 — durata dell'impulso: più corto = più risoluzione, più rumore", loc="left", fontsize=11)
    _bar_axis(ax, k)
    nums["sigma_10ns"] = float(sigma_nu_mhz(fib(pulse_width_ns=10), 0))
    nums["sigma_50ns"] = float(sigma_nu_mhz(fib(pulse_width_ns=50), 0))

    ax = axs[1, 0]
    z = np.linspace(0, 50_000, 300)
    for n in (256, 4096):
        ax.plot(z / 1000, sigma_nu_mhz(fib(n_averages=n), z), label=f"N_AV = {n}")
    ax.axvspan(0, 4, color="#d3f9d8", alpha=0.6, label="le nostre fibre (≤ 4 km)")
    ax.set_yscale("log"); ax.set_xlabel("distanza lungo la fibra [km] (attenuazione 0,2 dB/km)")
    ax.set_ylabel("σ_ν [MHz]"); ax.legend()
    ax.set_title("Grafico 3 — distanza: conta solo oltre qualche decina di km", loc="left", fontsize=11)
    _bar_axis(ax, k)
    nums["sigma_4km"] = float(sigma_nu_mhz(f0, 4000))
    nums["sigma_50km"] = float(sigma_nu_mhz(f0, 50_000))

    ax = axs[1, 1]
    for L, win in ((2000, 0.55), (4000, 0.55), (4000, 1.0)):
        steps = win * 1000 / 1 + 1
        t = steps * nav * 2 * L * f0.group_index / C_M_PER_S
        ax.plot(nav, t, label=f"anello {L / 1000:.0f} km, finestra {win:g} GHz, δ 1 MHz".replace(".", ","))
    ax.axhline(900, color="#868e96", ls="--"); ax.text(1.5, 1000, "passo idraulico (15 min)", fontsize=9, color="#495057")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.legend(fontsize=9)
    ax.set_xlabel("medie per passo N_AV"); ax.set_ylabel("tempo minimo di una misura [s]")
    ax.set_title("Grafico 4 — tempo di misura (senza i tempi morti dello strumento)", loc="left", fontsize=11)
    nums["t_256_4km"] = 551 * 256 * 2 * 4000 * f0.group_index / C_M_PER_S
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    _save(fig, out / "manopole_strumento.png")
    return nums


def mechanics_figure(out: Path) -> dict:
    nums = {}
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=100)
    fig.suptitle("Manopole meccaniche: quanti MHz per bar sente la fibra a elica", fontsize=14, fontweight="bold",
                 x=0.02, ha="left")
    ax = axs[0, 0]
    a = np.linspace(0, 89, 200)
    ax.plot(a, [_mhz_per_bar_pe(angle=x) for x in a], color="#ff6a00")
    ax.axvline(70, color="#868e96", ls=":")
    ax2 = ax.twinx()
    ax2.plot(a, 1 / np.cos(np.radians(a)), color="#1f5fbf", ls="--")
    ax2.set_ylim(0, 6); ax2.set_ylabel("metri di fibra per metro di tubo (blu)", color="#1f5fbf")
    ax.set_xlabel("angolo dell'elica rispetto all'asse α [°]"); ax.set_ylabel("MHz per bar (arancione)")
    ax.set_title("Grafico 1 — angolo dell'elica (PE100 DN110 SDR11)", loc="left", fontsize=11)
    for x in (0, 45, 70, 80):
        nums[f"angle_{x}"] = _mhz_per_bar_pe(angle=x)

    ax = axs[0, 1]
    sdr = np.linspace(7.4, 26, 200)
    ax.plot(sdr, [_mhz_per_bar_pe(sdr=s) for s in sdr], color="#ff6a00")
    for s, lab in ((11, "SDR11 (PN16)"), (17, "SDR17 (PN10)")):
        ax.plot(s, _mhz_per_bar_pe(sdr=s), "o", color="#212529"); ax.annotate(lab, (s, _mhz_per_bar_pe(sdr=s)),
                                                                              (s + 0.5, _mhz_per_bar_pe(sdr=s) - 2))
        nums[f"sdr_{s}"] = _mhz_per_bar_pe(sdr=s)
    ax.set_xlabel("SDR = diametro esterno / spessore"); ax.set_ylabel("MHz per bar")
    ax.set_title("Grafico 2 — spessore del tubo (a parità di SDR il diametro non conta)", loc="left", fontsize=11)

    ax = axs[1, 0]
    E = np.linspace(0.6, 1.6, 200)
    ax.plot(E, [_mhz_per_bar_pe(E=e) for e in E], color="#ff6a00", label="ν = 0,40")
    ax.plot(E, [_mhz_per_bar_pe(E=e, nu=0.45) for e in E], color="#ff6a00", ls="--", label="ν = 0,45")
    ax.axvspan(1.0, 1.1, color="#d3f9d8", alpha=0.7, label="E del PE100 da fonti (1,0–1,1 GPa)")
    ax.set_xlabel("modulo elastico del PE E [GPa]"); ax.set_ylabel("MHz per bar"); ax.legend()
    ax.set_title("Grafico 3 — rigidezza del PE (il creep la abbassa nel tempo)", loc="left", fontsize=11)
    nums["E_1.0"], nums["E_1.1"] = _mhz_per_bar_pe(E=1.0), _mhz_per_bar_pe(E=1.1)

    ax = axs[1, 1]
    El = np.logspace(np.log10(0.3), np.log10(15), 200)
    hosts = {"ghisa DN200 integra (170 GPa)": (0.1047, 0.111, 170.0, 0.26),
             "ghisa DN200 degradata (17 GPa)": (0.1047, 0.111, 17.0, 0.26),
             "PE DN160 SDR11 (1,1 GPa)": (0.0654, 0.080, 1.1, 0.4)}
    for name, (ri, ro, Eh, nuh) in hosts.items():
        vals = []
        for e in El:
            et, ez = multilayer_strain_ue([Layer(ri - 0.006, ri, e, 0.35), Layer(ri, ro, Eh, nuh)], 0.1, ri - 0.003)
            vals.append(float(helix_strain_ue(et, ez, 70)) * COEF.c_eps_mhz_per_ue)
        ax.plot(El, vals, label=name)
    ax.axhline(4.5, color="#c92a2a", ls="--"); ax.text(0.32, 5, "sotto: 0,1 bar non si vede in una misura", color="#c92a2a",
                                                       fontsize=9)
    ax.axvspan(1.7, 10.3, color="#e9ecef", alpha=0.7, label="guaine CIPP (feltro – vetro)")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.legend(fontsize=9)
    ax.set_xlabel("modulo della guaina [GPa] (spessore 6 mm, fibra a metà)"); ax.set_ylabel("MHz per bar")
    ax.set_title("Grafico 4 — guaina dentro il tubo ospite (modello a strati)", loc="left", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    _save(fig, out / "manopole_meccanica.png")
    return nums


def temperature_figure(root: Path, out: Path) -> dict:
    from .compensation import random_error_bar
    from .temperature import WaterTemperature, heat_rate_per_s
    sc = load_scenario(root / "scenario_paths" / "S1t_street_flat_soil.yaml")
    f = sc.fibers[0]
    k = _mhz_per_bar_pe()
    nums = {}
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=100)
    fig.suptitle("Manopole della temperatura e della compensazione", fontsize=14, fontweight="bold", x=0.02, ha="left")
    ax = axs[0, 0]
    K = np.linspace(3.5, 8, 50)
    ax.plot(K, K / k, color="#c92a2a")
    ax.set_xlabel("sensibilità dell'elica alla temperatura K [MHz/°C]"); ax.set_ylabel("bar apparenti per 1 °C")
    ax.set_title("Grafico 1 — quanto pesa 1 °C non compensato", loc="left", fontsize=11)
    nums["bar_per_c_min"], nums["bar_per_c_max"] = 3.5 / k, 8 / k

    ax = axs[0, 1]
    dT = np.linspace(0, 15, 100)
    for dK in (0.5, 1.0, 2.5):
        ax.plot(dT, dK * dT / k, label=f"errore su K = {dK:g} MHz/°C".replace(".", ","))
    ax.axvspan(11, 15, color="#ffe3e3", alpha=0.6, label="escursione stagionale [SB20]")
    ax.set_xlabel("ΔT dalla misura di base [°C]"); ax.set_ylabel("errore sistematico [bar]"); ax.legend(fontsize=9)
    ax.set_title("Grafico 2 — errore se K è sbagliato (non cala con le medie)", loc="left", fontsize=11)
    nums["sys_1K_10C"] = 1.0 * 10 / k

    ax = axs[1, 0]
    L = np.linspace(0, 300, 300)
    for Kv in (3.5, 6, 8):
        ax.plot(L, random_error_bar(sc, f, Kv, L)[0], label=f"K = {Kv:g} MHz/°C".replace(".", ","))
    ax.set_xlabel("lunghezza della media del riferimento [m]"); ax.set_ylabel("errore casuale di una misura [bar]")
    ax.legend(); ax.set_title("Grafico 3 — media del riferimento (compensazione)", loc="left", fontsize=11)
    for Kv in (3.5, 6, 8):
        nums[f"rand_K{Kv}_0"] = float(random_error_bar(sc, f, Kv, 0)[0])
        nums[f"rand_K{Kv}_74"] = float(random_error_bar(sc, f, Kv, 74)[0])

    ax = axs[1, 1]
    v = np.linspace(0.01, 1.5, 200)
    pe = _pe()
    for ts in (0, 1, 2):
        w = WaterTemperature(14, 1.6, 0.38, ts)
        tau = np.array([1 / heat_rate_per_s(pe, x, w) / 3600 for x in v])
        ax.plot(v, np.exp(-(1000 / v) / (tau * 3600)), label=f"sfera di influenza {ts}")
    ax.set_xlabel("velocità dell'acqua [m/s]"); ax.set_ylabel("quota della differenza serbatoio–terreno\nche arriva dopo 1 km")
    ax.legend(); ax.set_title("Grafico 4 — temperatura dell'acqua dopo 1 km di tubo PE DN110 [BL24]", loc="left", fontsize=11)
    w = WaterTemperature(14, 1.6, 0.38, 1)
    nums["water_frac_0.8"] = math.exp(-(1000 / 0.8) * heat_rate_per_s(pe, 0.8, w))
    nums["water_frac_0.1"] = math.exp(-(1000 / 0.1) * heat_rate_per_s(pe, 0.1, w))
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    _save(fig, out / "manopole_temperatura.png")
    return nums


def hydraulics_figure(out: Path) -> dict:
    """Strada di 1 km, 10 tratti, un rubinetto ogni 100 m: escursione giornaliera in fondo (Hazen-Williams, [EPA])."""
    def drop_bar(q_tap, d_m, mult, C=140.0):
        h = 0.0
        for kk in range(10, 0, -1):                       # tratto i porta i rubinetti a valle
            q = kk * q_tap * mult / 1000 + (q_tap * mult / 1000 if kk == 10 else 0)
            h += 10.67 * 100 * q ** 1.852 / (C ** 1.852 * d_m ** 4.87)
        return h * 0.0980665
    nums = {}
    fig, axs = plt.subplots(1, 2, figsize=(15, 5), dpi=100)
    fig.suptitle("Manopole idrauliche: quanto cambia la pressione nella giornata (strada di 1 km, Hazen-Williams)",
                 fontsize=14, fontweight="bold", x=0.02, ha="left")
    q = np.linspace(0.05, 0.6, 100)
    for d, lab in ((0.0736, "DN90 SDR11"), (0.090, "DN110 SDR11"), (0.1022, "DN125 SDR11")):
        exc = [drop_bar(x, d, 1.6) - drop_bar(x, d, 0.35) for x in q]
        axs[0].plot(q, exc, label=lab)
        vel = [11 * x * 1.6 / 1000 / (math.pi * d * d / 4) for x in q]
        axs[1].plot(q, vel, label=lab)
    axs[0].axvline(0.3, color="#868e96", ls=":")
    axs[0].set_xlabel("prelievo medio per rubinetto [L/s] (11 rubinetti)"); axs[0].set_ylabel("escursione in fondo alla strada [bar]")
    axs[0].set_title("Grafico 1 — il segnale da misurare: picco (×1,6) contro notte (×0,35)", loc="left", fontsize=11)
    axs[0].legend()
    axs[1].axhspan(0.5, 1.5, color="#d3f9d8", alpha=0.6, label="velocità di progetto (manuali)")
    axs[1].set_xlabel("prelievo medio per rubinetto [L/s]"); axs[1].set_ylabel("velocità al picco all'inizio [m/s]")
    axs[1].set_title("Grafico 2 — criterio di progetto: velocità al picco", loc="left", fontsize=11); axs[1].legend()
    nums["exc_0.3_110"] = drop_bar(0.3, 0.090, 1.6) - drop_bar(0.3, 0.090, 0.35)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    _save(fig, out / "manopole_idraulica.png")
    return nums


def run(root: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    nums = {}
    nums.update(instrument_figure(root, out))
    nums.update(mechanics_figure(out))
    nums.update(temperature_figure(root, out))
    nums.update(hydraulics_figure(out))
    return nums
