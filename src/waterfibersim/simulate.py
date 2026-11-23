"""Passo 2: segnale "vero" (senza rumore e senza ottica) lungo la fibra nel tempo.

    EPANET -> pressione nei nodi -> pressione lungo il tubo (lineare tra i due nodi)
           -> deformazione della parete (Lamé) -> deformazione della fibra (elica; riferimento = 0)
           -> nu_B(z, t)

Semplificazioni di questo passo: temperatura costante (dT = 0), nessuna "nota a riposo" per metro, nessun rumore,
nessuno spettro (L0 arriva al passo 3), niente creep. Sono le etichette vere L1/L2 dei passi successivi.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .brillouin import BrillouinCoefficients, brillouin_shift_mhz
from .fiber import Scenario
from .fibermap import build_map
from .hydraulics import run_hydraulics
from .mechanics import helix_strain_ue, wall_strain_ue

MPA_TO_BAR = 10.0


@dataclass
class TrueSignal:
    fiber_map: pd.DataFrame        # (Z righe) una riga per campione lungo le fibre
    times_s: np.ndarray            # (T,)
    pressure_bar: np.ndarray       # (T, Z) pressione dell'acqua nel punto del tubo; NaN su cavi e giunzione
    strain_ue: np.ndarray          # (T, Z) deformazione della fibra
    nu_b_mhz: np.ndarray           # (T, Z) frequenza Brillouin vera
    coef: BrillouinCoefficients

    def save(self, out: str | Path) -> Path:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        self.fiber_map.to_csv(out / "fiber_map.csv", index=False, float_format="%.3f")
        np.savez_compressed(
            out / "signal_true.npz",
            times_s=self.times_s, z_m=self.fiber_map["z_m"].to_numpy(),
            fiber=self.fiber_map["fiber"].to_numpy(dtype=str), leg=self.fiber_map["leg"].to_numpy(dtype=str),
            pipe=self.fiber_map["pipe"].fillna("").to_numpy(dtype=str),
            pressure_bar=self.pressure_bar.astype(np.float32), strain_ue=self.strain_ue.astype(np.float32),
            nu_b_mhz=self.nu_b_mhz, nu_b0_mhz=self.coef.nu_b0_mhz)
        return out / "signal_true.npz"


def simulate_true(scenario: Scenario, duration_s: int = 86_400, step_s: int = 900,
                  coef: BrillouinCoefficients = BrillouinCoefficients()) -> TrueSignal:
    net = scenario.network
    fmap = build_map(scenario)
    hyd = run_hydraulics(net.inp_path, duration_s, step_s)
    col = {n: i for i, n in enumerate(hyd.nodes)}
    p_nodes = hyd.pressure_mpa()                                   # (T, N)
    T, Z = len(hyd.times_s), len(fmap)
    pressure = np.full((T, Z), np.nan)
    strain = np.zeros((T, Z))
    angle = {f.id: f.sensing_leg.angle_deg for f in scenario.fibers}

    for pid in fmap["pipe"].dropna().unique():
        p = net.pipes[pid]
        rows = np.flatnonzero(fmap["pipe"].to_numpy() == pid)
        frac = fmap["s_pipe_m"].to_numpy()[rows] / p.length_m
        pa, pb = p_nodes[:, col[p.start_node]], p_nodes[:, col[p.end_node]]
        p_mpa = pa[:, None] * (1 - frac) + pb[:, None] * frac   # pressione lineare lungo il tubo
        pressure[:, rows] = p_mpa * MPA_TO_BAR
        sens = fmap["leg"].to_numpy()[rows] == "sensing"
        if sens.any():
            eps_t, eps_z = wall_strain_ue(p, p_mpa[:, sens])
            fid = fmap["fiber"].to_numpy()[rows][sens]
            for f in np.unique(fid):
                m = fid == f
                strain[:, rows[sens][m]] = helix_strain_ue(eps_t[:, m], eps_z[:, m], angle[f])
        # tratto di riferimento: fibra libera nel tubetto, deformazione 0 (resta 0)

    return TrueSignal(fmap, hyd.times_s, pressure, strain, brillouin_shift_mhz(strain, 0.0, coef), coef)
