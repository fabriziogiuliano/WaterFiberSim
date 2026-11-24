"""Passo T3: compensazione della temperatura con il tratto di riferimento, e quanto errore resta.

Catena (per ogni punto dell'elica, sul segnale vero senza rumore):
  1. dnu_elica = nu - misura di base                          (pressione + temperatura)
  2. sul riferimento, stesso tubo, stesso punto del tubo:  dT_stimata = dnu_rif / C_T
     (facoltativo: media mobile del riferimento su `ref_avg_m` metri, per ridurre il rumore)
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


def pair_reference(fmap: pd.DataFrame, fiber_id: str) -> np.ndarray:
    """Per ogni riga della mappa: indice della riga del riferimento sullo stesso tubo nel punto più vicino (-1 se no)."""
    out = np.full(len(fmap), -1)
    fib = fmap["fiber"].to_numpy() == fiber_id
    leg = fmap["leg"].to_numpy()
    pipe = fmap["pipe"].to_numpy()
    s = fmap["s_pipe_m"].to_numpy()
    for pid in pd.unique(pipe[fib & (leg == "sensing")]):
        h = np.flatnonzero(fib & (leg == "sensing") & (pipe == pid))
        r = np.flatnonzero(fib & (leg == "reference") & (pipe == pid))
        if len(r) == 0:
            continue
        order = np.argsort(s[r])
        rs = s[r][order]
        j = np.clip(np.searchsorted(rs, s[h]), 1, len(rs) - 1)
        nearer = np.where(np.abs(rs[j - 1] - s[h]) <= np.abs(rs[j] - s[h]), j - 1, j)
        out[h] = r[order][nearer]
    return out


def reference_delta_t(sig, fiber: Fiber, ref_avg_m: float = 0.0) -> np.ndarray:
    """dT stimata dal riferimento, (T, Z): valore solo sulle righe del riferimento, mediato su ref_avg_m metri."""
    f = sig.fiber_map
    rows = np.flatnonzero((f["fiber"].to_numpy() == fiber.id) & (f["leg"].to_numpy() == "reference"))
    rows = rows[np.argsort(f["z_m"].to_numpy()[rows])]
    dnu = sig.nu_b_mhz[:, rows] - sig.baseline_mhz[rows]
    dT = dnu / sig.coef.c_t_mhz_per_c
    if ref_avg_m > 0:
        n = max(1, int(round(ref_avg_m / fiber.calc_step_m)))
        dT = pd.DataFrame(dT.T).rolling(n, center=True, min_periods=1).mean().to_numpy().T
    out = np.full(sig.nu_b_mhz.shape, np.nan)
    out[:, rows] = dT
    return out


def compensated_pressure_bar(sig, scenario: Scenario, fiber: Fiber, helix_mhz_per_c_assumed: float,
                             ref_avg_m: float = 0.0) -> np.ndarray:
    """Pressione stimata sull'elica dopo la compensazione (NaN fuori dall'elica), (T, Z)."""
    f = sig.fiber_map
    pair = pair_reference(f, fiber.id)
    dT_ref = reference_delta_t(sig, fiber, ref_avg_m)
    k = helix_mhz_per_bar(scenario, fiber, sig.coef)
    out = np.full(sig.nu_b_mhz.shape, np.nan)
    h = np.flatnonzero(pair >= 0)
    dnu_h = sig.nu_b_mhz[:, h] - sig.baseline_mhz[h]
    dnu_p = dnu_h - helix_mhz_per_c_assumed * dT_ref[:, pair[h]]
    kb = np.array([k[p] for p in f["pipe"].to_numpy()[h]])
    out[:, h] = dnu_p / kb
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
