"""Profilo a riposo: la frequenza Brillouin di ogni metro di fibra a tubo vuoto (0 bar), rispetto a nu_B0.

Non è piatto: la posa tira la fibra, e non in modo uniforme. Valori di riferimento da Bertulessi et al.,
Sensors 23, 6205 (2023), Fig. 7a (tubo PN16, fibra fissata all'esterno con nastro), letti a occhio:
  - tratto a elica: da circa +180 a circa +105 MHz rispetto ai cavi (pre-deformazione della posa);
  - tratto libero per la temperatura: circa +65 MHz (l'articolo non dice perché);
  - cavi: 0.
Ipotesi dichiarate (vedi docs/fonti.md): per ogni tubo, inizio e fine del tratto a elica estratti a caso
nell'intervallo [105, 180] MHz (pendenza in salita, in discesa o quasi piatta); piccole ondulazioni di circa 1 MHz.
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
        for pid in pd.unique(pipe[(fib == f) & (leg == "sensing")]):
            m = np.flatnonzero((fib == f) & (leg == "sensing") & (pipe == pid))
            a, b = rng.uniform(*HELIX_RANGE_MHZ, size=2)
            t = (z[m] - z[m].min()) / max(np.ptp(z[m]), 1e-9)
            off[m] = a + (b - a) * t
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
