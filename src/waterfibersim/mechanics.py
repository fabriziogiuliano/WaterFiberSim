"""Dalla pressione interna alla deformazione della parete e della fibra.

Fonti (vedi docs/A-fonti.md):
- deformazione circonferenziale sulla superficie esterna, tubo a parete spessa (Lamé):
      eps_theta = (2 - nu) * beta^2 / (1 - beta^2) * p / E,    beta = r_interno / r_esterno
  Bertulessi et al., Sensors 23, 6205 (2023), Eq. 4-6;
- deformazione assiale sulla superficie esterna, tubo a fondi chiusi:
      eps_z = (1 - 2 nu) * beta^2 / (1 - beta^2) * p / E          (Lamé, scienza delle costruzioni)
- fibra a elica con angolo alpha rispetto all'asse:
      eps_fibra = eps_theta * sin^2(alpha) + eps_z * cos^2(alpha)  (trasformazione della deformazione)

Tubi con più strati (tubo ospite + guaina, ed eventuali strati in più): Lamé a N strati, strati incollati
(spostamento radiale e pressione continui alle interfacce), deformazione assiale uguale in tutti gli strati e fondi chiusi
(la forza assiale bilancia p · pi · r_interno^2). Soluzione in ogni strato u = A r + B / r (scienza delle costruzioni).
Con un solo strato coincide con le formule sopra (verificato nei test).

Ipotesi dichiarate: comportamento elastico (niente creep del PE: modello di Burgers in [B23], più avanti);
trasferimento della deformazione alla fibra al 100 %; la fibra di riferimento libera nel tubetto non si deforma.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .network import PipeSpec


LINER_NU_DEFAULT = 0.35      # ⚠️ coefficiente di Poisson della guaina se non dato: valore da sostituire con il laminato MATRIS


@dataclass(frozen=True)
class Layer:
    """Uno strato del tubo: raggi interno ed esterno [m], modulo [GPa], Poisson."""

    r_in_m: float
    r_out_m: float
    E_GPa: float
    nu: float


def multilayer_strain_ue(layers: list[Layer], p_mpa, r_fiber_m: float) -> tuple[np.ndarray, np.ndarray]:
    """(eps_theta, eps_z) in microstrain al raggio r_fiber_m, per una pressione interna p [MPa].

    Strati dall'interno all'esterno, incollati; esterno libero; deformazione piana generalizzata a fondi chiusi.
    """
    n = len(layers)
    for a, b in zip(layers[:-1], layers[1:]):
        if abs(a.r_out_m - b.r_in_m) > 1e-9:
            raise ValueError("layers must be contiguous")
    lam = [L.E_GPa * 1e3 * L.nu / ((1 + L.nu) * (1 - 2 * L.nu)) for L in layers]       # MPa
    mu = [L.E_GPa * 1e3 / (2 * (1 + L.nu)) for L in layers]
    # incognite: A_1, B_1, ..., A_n, B_n, eps_z  (soluzione per p = 1 MPa, poi lineare)
    M = np.zeros((2 * n + 1, 2 * n + 1))
    rhs = np.zeros(2 * n + 1)
    iz = 2 * n

    def sigma_r_row(i, r):
        row = np.zeros(2 * n + 1)
        row[2 * i] = 2 * (lam[i] + mu[i])
        row[2 * i + 1] = -2 * mu[i] / r ** 2
        row[iz] = lam[i]
        return row

    k = 0
    M[k] = sigma_r_row(0, layers[0].r_in_m); rhs[k] = -1.0; k += 1                  # sigma_r = -p dentro
    M[k] = sigma_r_row(n - 1, layers[-1].r_out_m); rhs[k] = 0.0; k += 1             # esterno libero
    for i in range(n - 1):
        r = layers[i].r_out_m
        M[k, 2 * i], M[k, 2 * i + 1] = r, 1 / r                                     # u continuo
        M[k, 2 * i + 2], M[k, 2 * i + 3] = -r, -1 / r
        k += 1
        M[k] = sigma_r_row(i, r) - sigma_r_row(i + 1, r); k += 1                    # sigma_r continuo
    for i, L in enumerate(layers):                                                  # fondi chiusi
        area = math.pi * (L.r_out_m ** 2 - L.r_in_m ** 2)
        M[k, 2 * i] += 2 * lam[i] * area
        M[k, iz] += (lam[i] + 2 * mu[i]) * area
    rhs[k] = math.pi * layers[0].r_in_m ** 2
    sol = np.linalg.solve(M, rhs)
    i = next((j for j, L in enumerate(layers) if L.r_in_m - 1e-12 <= r_fiber_m <= L.r_out_m + 1e-12), None)
    if i is None:
        raise ValueError("fiber radius outside the pipe wall")
    eps_t = sol[2 * i] + sol[2 * i + 1] / r_fiber_m ** 2
    p = np.asarray(p_mpa, dtype=float)
    return eps_t * p * 1e6, sol[iz] * p * 1e6


def pipe_layers(pipe: PipeSpec) -> tuple[list[Layer], float]:
    """Strati di un tubo e raggio della fibra: senza guaina, superficie esterna; con guaina, metà della guaina."""
    r_e = pipe.outer_diameter_mm / 2000
    r_h = r_e - pipe.wall_thickness_mm / 1000
    host = Layer(r_h, r_e, pipe.E_GPa, pipe.nu)
    if pipe.liner is None:
        return [host], r_e
    t = pipe.liner.thickness_mm / 1000
    nu = pipe.liner.nu if getattr(pipe.liner, "nu", None) is not None else LINER_NU_DEFAULT
    liner = Layer(r_h - t, r_h, pipe.liner.E_GPa, nu)
    return [liner, host], r_h - t / 2          # fibra annegata a metà guaina (⚠️ posizione da confermare)


def _lame_factor(pipe: PipeSpec) -> float:
    """beta^2 / (1 - beta^2) / E  [1/MPa]."""
    r_e = pipe.outer_diameter_mm / 2
    r_i = r_e - pipe.wall_thickness_mm
    beta2 = (r_i / r_e) ** 2
    return beta2 / (1 - beta2) / (pipe.E_GPa * 1000.0)


def wall_strain_ue(pipe: PipeSpec, p_mpa) -> tuple[np.ndarray, np.ndarray]:
    """(eps_theta, eps_z) nel punto della fibra, in microstrain, per una pressione interna p [MPa].

    Senza guaina: superficie esterna (formula chiusa). Con guaina: modello a strati, fibra a metà guaina.
    """
    if pipe.liner is not None:
        layers, r_f = pipe_layers(pipe)
        return multilayer_strain_ue(layers, p_mpa, r_f)
    k = _lame_factor(pipe) * np.asarray(p_mpa, dtype=float) * 1e6
    return (2 - pipe.nu) * k, (1 - 2 * pipe.nu) * k


def helix_strain_ue(eps_theta, eps_z, angle_deg: float) -> np.ndarray:
    """Deformazione lungo una fibra a elica con angolo `angle_deg` rispetto all'asse del tubo."""
    s2 = math.sin(math.radians(angle_deg)) ** 2
    return np.asarray(eps_theta) * s2 + np.asarray(eps_z) * (1 - s2)
