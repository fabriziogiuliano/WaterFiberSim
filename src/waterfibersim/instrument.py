"""Incertezza attesa dello strumento e tempo di misura, dalle manopole dello scenario.

Modello di Soto & Thévenaz, Opt. Express 21, 31347 (2013) [ST13] (vedi docs/A-fonti.md):
  - incertezza sul picco con fit parabolico dei punti sopra eta * picco, Eq. 7:
        sigma_nu = (1 / SNR) * sqrt(3 * delta * dnu_B / (8 * sqrt(2) * (1 - eta)^(3/2)))
    (eta = 0,5 -> Eq. 8: sigma_nu = (1 / SNR) * sqrt(3/4 * delta * dnu_B));
  - SNR lungo la fibra, Eq. 9 riscritta:
        SNR(z) = SNR0 * (dz / dz0) * sqrt(N_AV) * exp(-alpha * z)
    con SNR0 dato a risoluzione dz0 e UNA traccia, alpha attenuazione di andata (in neper/m).

Semplificazioni dichiarate (🧮): SNR lineare = 10^(dB/10) (come nella validazione di [ST13]); z contato dalla
porta A da cui parte l'impulso; il termine exp(-alpha L) della sonda è costante lungo la fibra e si considera già
dentro SNR0; nessuna amplificazione, nessuno svuotamento della pompa.

Tempo minimo di misura (🧮, tempo di volo): una traccia dura l'andata e ritorno sull'intero anello, 2 L n / c,
quindi T_min = (numero di passi di frequenza) * N_AV * 2 L n / c. Lo strumento vero ha anche tempi morti
(cambio di frequenza, elaborazione: [ST13] §3), non modellati: il tempo vero è più lungo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .brillouin import BrillouinCoefficients
from .fiber import C_M_PER_S, Fiber, Scenario
from .mechanics import helix_strain_ue, wall_strain_ue

ETA_DEFAULT = 0.5      # soglia del fit: punti sopra metà picco [ST13] Eq. 8


def db_to_linear(db: float) -> float:
    return 10.0 ** (db / 10.0)


def alpha_np_per_m(att_db_per_km: float) -> float:
    """Attenuazione da dB/km a neper/m: P(z) = P0 exp(-alpha z)."""
    return att_db_per_km * math.log(10) / 10 / 1000


def snr_linear(fiber: Fiber, z_m) -> np.ndarray:
    """SNR della traccia al picco lungo la fibra [ST13] Eq. 9."""
    i = fiber.interrogator
    snr0 = db_to_linear(i.snr0_db)
    return (snr0 * fiber.spatial_resolution_m / i.snr0_resolution_m * math.sqrt(i.n_averages)
            * np.exp(-alpha_np_per_m(fiber.attenuation_db_per_km) * np.asarray(z_m, dtype=float)))


def sigma_nu_mhz(fiber: Fiber, z_m, eta: float = ETA_DEFAULT) -> np.ndarray:
    """Deviazione standard della frequenza Brillouin stimata, per UNA misura [ST13] Eq. 7."""
    i = fiber.interrogator
    k = 3 * i.freq_step_mhz * i.linewidth_mhz / (8 * math.sqrt(2) * (1 - eta) ** 1.5)
    return np.sqrt(k) / snr_linear(fiber, z_m)


def n_freq_steps(fiber: Fiber) -> int:
    lo, hi = fiber.interrogator.scan_window_ghz
    return int(round((hi - lo) * 1000 / fiber.interrogator.freq_step_mhz)) + 1


def min_measurement_time_s(fiber: Fiber, loop_length_m: float) -> float:
    """Limite inferiore del tempo di una misura completa (tutte le frequenze, tutte le medie)."""
    trace_s = 2 * loop_length_m * fiber.group_index / C_M_PER_S
    return n_freq_steps(fiber) * fiber.interrogator.n_averages * trace_s


def helix_mhz_per_bar(scenario: Scenario, fiber: Fiber, coef: BrillouinCoefficients) -> dict[str, float]:
    """Sensibilità dell'elica (MHz per bar) per ogni tubo; NaN dove il modello non c'è (tubo risanato)."""
    out = {}
    for seg in fiber.route:
        if seg.kind != "pipe":
            continue
        p = scenario.network.pipes[seg.pipe]
        try:
            et, ez = wall_strain_ue(p, 0.1)       # 1 bar = 0,1 MPa
            out[seg.pipe] = float(helix_strain_ue(et, ez, fiber.sensing_leg.angle_deg)) * coef.c_eps_mhz_per_ue
        except NotImplementedError:
            out[seg.pipe] = float("nan")
    return out


@dataclass
class WindowCheck:
    nu_min_mhz: float
    nu_max_mhz: float
    usable_lo_mhz: float      # il picco deve stare almeno mezza larghezza dentro la finestra (fit sopra metà picco)
    usable_hi_mhz: float

    @property
    def ok(self) -> bool:
        return self.usable_lo_mhz <= self.nu_min_mhz and self.nu_max_mhz <= self.usable_hi_mhz


def check_scan_window(fiber: Fiber, nu_b_mhz: np.ndarray) -> WindowCheck:
    """Tutti i picchi (in ogni punto e in ogni istante) devono cadere nella finestra di scansione."""
    lo, hi = fiber.interrogator.scan_window_ghz
    half = fiber.interrogator.linewidth_mhz / 2
    return WindowCheck(float(np.nanmin(nu_b_mhz)), float(np.nanmax(nu_b_mhz)), lo * 1000 + half, hi * 1000 - half)


def uncertainty_table(scenario: Scenario, fiber: Fiber, fmap: pd.DataFrame,
                      coef: BrillouinCoefficients = BrillouinCoefficients()) -> pd.DataFrame:
    """Incertezza a inizio, metà e fine del tratto a elica di ogni tubo, e sul riferimento."""
    f = fmap[fmap["fiber"] == fiber.id]
    k = helix_mhz_per_bar(scenario, fiber, coef)
    rows = []
    for (leg, pid), b in f[f["leg"].isin(["sensing", "reference"])].groupby(["leg", "pipe"], sort=False):
        z = b["z_m"].to_numpy()
        for where, zz in (("start", z.min()), ("end", z.max())):
            s = float(sigma_nu_mhz(fiber, zz))
            rows.append({"leg": leg, "pipe": pid, "where": where, "z_m": zz,
                         "snr_db": 10 * math.log10(float(snr_linear(fiber, zz))), "sigma_mhz": s,
                         "sigma_bar": s / k[pid] if leg == "sensing" else float("nan"),
                         "sigma_c": s / coef.c_t_mhz_per_c if leg == "reference" else float("nan")})
    return pd.DataFrame(rows)
