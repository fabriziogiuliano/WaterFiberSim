"""Passo T3: compensazione della temperatura con il tratto di riferimento, e quanto errore resta.

Catena (per ogni punto dell'elica, sul segnale vero senza rumore):
  1. dnu_elica = nu - misura di base                          (pressione + temperatura)
  2. sul riferimento, stesso tubo:  dT = dnu_rif / C_T, INTERPOLATA nel punto del tubo dell'elica
     (facoltativo: media del riferimento su `ref_avg_m` metri per ridurre il rumore:
      "moving"   = media mobile semplice: sfuma le variazioni locali;
      "adaptive" = media solo dei vicini con temperatura entro `tol_c` da quella del punto (filtro sigma):
                   non attraversa i bordi delle variazioni locali)
  3. dnu_pressione = dnu_elica - K_assunto * dT_stimata      (K = sensibilità dell'elica alla temperatura)
  4. pressione = dnu_pressione / (MHz per bar dell'elica)

Errori che restano (🧮, propagazione degli errori; incertezze sigma da instrument.py, [ST13]):
  - sistematico: (K_vero - K_assunto) * dT / k_bar  -> non cala con le medie, va calibrato;
                 la media mobile del riferimento sfuma le variazioni locali (punti caldi) -> errore ai bordi;
  - casuale, per una misura, differenza dalla misura di base (x sqrt 2) su elica e riferimento:
        sigma_p = sqrt(2) * sqrt(sigma_elica^2 + (K / C_T)^2 * sigma_rif^2 / N_rif) / k_bar
    con N_rif = punti indipendenti del riferimento nella media = max(1, ref_avg_m / risoluzione).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .brillouin import BrillouinCoefficients
from .fiber import Fiber, Scenario
from .instrument import helix_mhz_per_bar, sigma_nu_mhz


ADAPTIVE_TOL_C = 0.5     # ipotesi: soglia del filtro adattivo (dell'ordine del rumore del riferimento, circa 0,5 °C)


def reference_delta_t(sig, fiber: Fiber, ref_avg_m: float = 0.0, mode: str = "moving",
                      tol_c: float = ADAPTIVE_TOL_C, t_idx=None) -> tuple[np.ndarray, np.ndarray]:
    """dT stimata dal riferimento: (righe del riferimento ordinate per z, dT (T', R)), eventualmente mediata.

    t_idx: istanti da calcolare (tutti se None): il filtro adattivo è pesante.
    """
    f = sig.fiber_map
    rows = np.flatnonzero((f["fiber"].to_numpy() == fiber.id) & (f["leg"].to_numpy() == "reference"))
    rows = rows[np.argsort(f["z_m"].to_numpy()[rows])]
    times = np.arange(len(sig.times_s)) if t_idx is None else np.atleast_1d(t_idx)
    dT = (sig.nu_b_mhz[np.ix_(times, rows)] - sig.baseline_mhz[rows]) / sig.coef.c_t_mhz_per_c
    n = max(1, int(round(ref_avg_m / fiber.calc_step_m))) if ref_avg_m > 0 else 1
    if n == 1:
        return rows, dT
    if mode == "moving":
        return rows, pd.DataFrame(dT.T).rolling(n, center=True, min_periods=1).mean().to_numpy().T
    if mode != "adaptive":
        raise ValueError(f"unknown averaging mode {mode!r}")
    half = n // 2
    out = np.empty_like(dT)
    for k in range(dT.shape[0]):
        x = np.pad(dT[k], half, constant_values=np.nan)
        win = np.lib.stride_tricks.sliding_window_view(x, 2 * half + 1)     # (R, finestra)
        ok = np.abs(win - dT[k][:, None]) <= tol_c
        out[k] = np.nansum(np.where(ok, win, 0.0), axis=1) / np.maximum(ok.sum(axis=1), 1)
    return rows, out


def compensated_pressure_bar(sig, scenario: Scenario, fiber: Fiber, helix_mhz_per_c_assumed: float,
                             ref_avg_m: float = 0.0, mode: str = "moving", tol_c: float = ADAPTIVE_TOL_C,
                             t_idx=None) -> np.ndarray:
    """Pressione stimata sull'elica dopo la compensazione (NaN fuori dall'elica), (T', Z).

    La temperatura del riferimento viene INTERPOLATA, tubo per tubo, nel punto del tubo di ogni campione dell'elica
    (niente "punto più vicino": evita gli scalini dovuti alla griglia di calcolo).
    """
    f = sig.fiber_map
    rows, dT_ref = reference_delta_t(sig, fiber, ref_avg_m, mode, tol_c, t_idx)
    times = np.arange(len(sig.times_s)) if t_idx is None else np.atleast_1d(t_idx)
    k = helix_mhz_per_bar(scenario, fiber, sig.coef)
    pipe = f["pipe"].to_numpy()
    s = f["s_pipe_m"].to_numpy()
    fib = f["fiber"].to_numpy() == fiber.id
    leg = f["leg"].to_numpy()
    out = np.full((len(times), len(f)), np.nan)
    for pid in pd.unique(pipe[fib & (leg == "sensing")]):
        h = np.flatnonzero(fib & (leg == "sensing") & (pipe == pid))
        r_sel = pipe[rows] == pid
        if not r_sel.any():
            continue
        rs = s[rows][r_sel]
        order = np.argsort(rs)
        dT_h = np.array([np.interp(s[h], rs[order], dT_ref[i, r_sel][order]) for i in range(len(times))])
        dnu_h = sig.nu_b_mhz[np.ix_(times, h)] - sig.baseline_mhz[h]
        out[:, h] = (dnu_h - helix_mhz_per_c_assumed * dT_h) / k[pid]
    return out


def apparent_pressure_bar(sig, scenario: Scenario, fiber: Fiber) -> np.ndarray:
    """Pressione letta SENZA compensare: tutta la differenza dalla misura di base presa per pressione."""
    f = sig.fiber_map
    h = np.flatnonzero((f["fiber"].to_numpy() == fiber.id) & (f["leg"].to_numpy() == "sensing"))
    k = helix_mhz_per_bar(scenario, fiber, sig.coef)
    out = np.full(sig.nu_b_mhz.shape, np.nan)
    kb = np.array([k[p] for p in f["pipe"].to_numpy()[h]])
    out[:, h] = (sig.nu_b_mhz[:, h] - sig.baseline_mhz[h]) / kb
    return out


def random_error_bar(scenario: Scenario, fiber: Fiber, helix_mhz_per_c: float, ref_avg_m,
                     z_m: float = 0.0, coef: BrillouinCoefficients = BrillouinCoefficients()):
    """Errore casuale (1 sigma) sulla pressione compensata, per una misura, in funzione della media del riferimento.

    Restituisce (totale, solo elica, solo temperatura) in bar.
    """
    s = float(sigma_nu_mhz(fiber, z_m))                       # stesso ordine su elica e riferimento (pochi km)
    k = float(np.nanmean(list(helix_mhz_per_bar(scenario, fiber, coef).values())))
    n_ref = np.maximum(1.0, np.asarray(ref_avg_m, dtype=float) / fiber.spatial_resolution_m)
    helix = math.sqrt(2) * s / k
    thermal = math.sqrt(2) * (helix_mhz_per_c / coef.c_t_mhz_per_c) * s / np.sqrt(n_ref) / k
    return np.sqrt(helix ** 2 + thermal ** 2), helix, thermal
