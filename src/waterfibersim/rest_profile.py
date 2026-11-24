"""Profilo a riposo: la frequenza Brillouin di ogni metro di fibra a tubo vuoto (0 bar), rispetto a nu_B0.

Non è piatto: la posa tira la fibra, e non in modo uniforme. Valori di riferimento da Bertulessi et al.,
Sensors 23, 6205 (2023), Fig. 7a (tubo PN16, fibra fissata all'esterno con nastro), letti a occhio:
  - tratto a elica: da circa +180 a circa +105 MHz rispetto ai cavi (pre-deformazione della posa);
  - tratto libero per la temperatura: circa +65 MHz (l'articolo non dice perché);
  - cavi: 0.
Ipotesi dichiarate (vedi docs/A-fonti.md), nessun dato su tubi lunghi:
  - lungo un'elica avvolta senza interruzioni il profilo cambia in modo CONTINUO: valori estratti a caso in
    [105, 180] MHz in punti di controllo ogni REST_KNOT_M metri di fibra, uniti da segmenti;
    i nodi EPANET (rubinetti) non interrompono la posa, quindi non creano salti;
  - SALTO solo dove la posa riparte da capo: dopo un cavo (per esempio in un pozzetto) o dove cambia il tubo
    (diametro esterno, materiale, guaina);
  - piccole ondulazioni di circa 1 MHz.
Per la fibra annegata nella guaina (MATRIS, `embedded`) gli stessi numeri sono solo un segnaposto: lì la nota a
riposo nasce soprattutto dalla polimerizzazione, e forma e valori sono da verificare.
Il profilo non cambia nel tempo: si cancella sottraendo la misura di base.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .fiber import Scenario

HELIX_RANGE_MHZ = (105.0, 180.0)     # [B23] Fig. 7a, tratto a elica (letto a occhio)
LOOSE_TUBE_MHZ = 65.0                # [B23] Fig. 7a, tratto libero (letto a occhio)
RIPPLE_MHZ = 1.0                     # ipotesi
RIPPLE_LENGTH_M = 8.0                # ipotesi: ondulazioni lente, su qualche metro
REST_KNOT_M = 300.0                  # ipotesi: punti di controllo ogni ~300 m di fibra (~100 m di tubo a 70°)


def rest_offset_mhz(fmap: pd.DataFrame, scenario: Scenario, seed: int = 0) -> np.ndarray:
    """Scostamento a riposo (MHz) di ogni campione della mappa rispetto alla fibra non tirata."""
    rng = np.random.default_rng(seed)
    off = np.zeros(len(fmap))
    leg = fmap["leg"].to_numpy()
    pipe = fmap["pipe"].to_numpy()
    fib = fmap["fiber"].to_numpy()
    z = fmap["z_m"].to_numpy()
    bonding = {f.id: (f.sensing_leg.bonding, f.reference_leg.bonding) for f in scenario.fibers}

    for f in np.unique(fib):
        sens_bond, ref_bond = bonding[f]
        for run in _sensing_runs(np.flatnonzero((fib == f) & (leg == "sensing")), z, pipe, scenario):
            zr = z[run]
            n_knots = max(2, int(np.ceil(np.ptp(zr) / REST_KNOT_M)) + 1)
            knots_z = np.linspace(zr.min(), zr.max(), n_knots)
            off[run] = np.interp(zr, knots_z, rng.uniform(*HELIX_RANGE_MHZ, size=n_knots))
        m = (fib == f) & (leg == "reference")
        if ref_bond == "loose_tube":
            off[m] = LOOSE_TUBE_MHZ

        # piccole ondulazioni lente lungo tutta la fibra (non sui cavi)
        sel = np.flatnonzero((fib == f) & (leg != "lead"))
        if len(sel) > 1:
            step = np.median(np.diff(z[sel]))
            n = max(1, int(RIPPLE_LENGTH_M / step))
            noise = np.convolve(rng.normal(0, 1, len(sel) + n), np.ones(n) / n, mode="same")[:len(sel)]
            off[sel] += RIPPLE_MHZ * noise / (noise.std() + 1e-12)
    return off


def _sensing_runs(idx: np.ndarray, z: np.ndarray, pipe: np.ndarray, scenario: Scenario) -> list[np.ndarray]:
    """Divide i campioni dell'elica (ordinati lungo z) in tratti di posa continua.

    Un tratto finisce dove la fibra lascia il tubo (buco in z: un cavo in mezzo) o dove cambia il tubo
    (diametro esterno, materiale, guaina): lì la fibra va riavvolta da capo.
    """
    if len(idx) == 0:
        return []
    idx = idx[np.argsort(z[idx])]
    step = np.median(np.diff(z[idx])) if len(idx) > 1 else 1.0
    pipes = scenario.network.pipes

    def kind(pid):
        p = pipes[pid]
        return (p.material, p.outer_diameter_mm, p.liner)

    cut = [0]
    for i in range(1, len(idx)):
        a, b = idx[i - 1], idx[i]
        if z[b] - z[a] > 1.5 * step or kind(pipe[a]) != kind(pipe[b]):
            cut.append(i)
    cut.append(len(idx))
    return [idx[c0:c1] for c0, c1 in zip(cut[:-1], cut[1:])]
