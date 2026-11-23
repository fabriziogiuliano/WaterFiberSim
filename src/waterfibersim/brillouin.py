"""Dalla deformazione e dalla temperatura della fibra alla frequenza Brillouin.

    nu_B = nu_B0 + C_eps * eps + C_T * dT

Coefficienti standard di Bertulessi et al., Sensors 23, 6205 (2023), Eq. 1: C_T = 1 MHz/°C, C_eps = 0,05 MHz/µε,
con l'avvertenza che dipendono dal cavo e dall'incollaggio. nu_B0 = 10 880 MHz è il valore a riposo della
fibra non tirata in [B23] Fig. 7a, letto a occhio: è solo un riferimento.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BrillouinCoefficients:
    nu_b0_mhz: float = 10_880.0
    c_eps_mhz_per_ue: float = 0.05
    c_t_mhz_per_c: float = 1.0


def brillouin_shift_mhz(strain_ue, delta_t_c=0.0, coef: BrillouinCoefficients = BrillouinCoefficients()) -> np.ndarray:
    """nu_B [MHz] per una deformazione [µε] e una variazione di temperatura [°C]."""
    return coef.nu_b0_mhz + coef.c_eps_mhz_per_ue * np.asarray(strain_ue) + coef.c_t_mhz_per_c * np.asarray(delta_t_c)
