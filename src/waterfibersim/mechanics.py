"""Dalla pressione interna alla deformazione della parete e della fibra.

Fonti (vedi docs/fonti.md):
- deformazione circonferenziale sulla superficie esterna, tubo a parete spessa (Lamé):
      eps_theta = (2 - nu) * beta^2 / (1 - beta^2) * p / E,    beta = r_interno / r_esterno
  Bertulessi et al., Sensors 23, 6205 (2023), Eq. 4-6;
- deformazione assiale sulla superficie esterna, tubo a fondi chiusi:
      eps_z = (1 - 2 nu) * beta^2 / (1 - beta^2) * p / E          (Lamé, scienza delle costruzioni)
- fibra a elica con angolo alpha rispetto all'asse:
      eps_fibra = eps_theta * sin^2(alpha) + eps_z * cos^2(alpha)  (trasformazione della deformazione)

Ipotesi dichiarate: comportamento elastico (niente creep del PE: modello di Burgers in [B23], più avanti);
trasferimento della deformazione alla fibra al 100 %; la fibra di riferimento libera nel tubetto non si deforma.
"""

from __future__ import annotations

import math

import numpy as np

from .network import PipeSpec


def _lame_factor(pipe: PipeSpec) -> float:
    """beta^2 / (1 - beta^2) / E  [1/MPa]."""
    if pipe.liner is not None:
        raise NotImplementedError(f"{pipe.id}: relined pipe (host + liner) needs a multilayer model, not yet implemented")
    r_e = pipe.outer_diameter_mm / 2
    r_i = r_e - pipe.wall_thickness_mm
    beta2 = (r_i / r_e) ** 2
    return beta2 / (1 - beta2) / (pipe.E_GPa * 1000.0)


def wall_strain_ue(pipe: PipeSpec, p_mpa) -> tuple[np.ndarray, np.ndarray]:
    """(eps_theta, eps_z) sulla superficie esterna, in microstrain, per una pressione interna p [MPa]."""
    k = _lame_factor(pipe) * np.asarray(p_mpa, dtype=float) * 1e6
    return (2 - pipe.nu) * k, (1 - 2 * pipe.nu) * k


def helix_strain_ue(eps_theta, eps_z, angle_deg: float) -> np.ndarray:
    """Deformazione lungo una fibra a elica con angolo `angle_deg` rispetto all'asse del tubo."""
    s2 = math.sin(math.radians(angle_deg)) ** 2
    return np.asarray(eps_theta) * s2 + np.asarray(eps_z) * (1 - s2)
