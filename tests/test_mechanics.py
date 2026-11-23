"""Numeri di riferimento della meccanica (docs/fonti.md)."""

import math

import pytest

from waterfibersim.brillouin import brillouin_shift_mhz
from waterfibersim.mechanics import helix_strain_ue, wall_strain_ue
from waterfibersim.network import Liner, PipeSpec


def pipe(**kw):
    base = dict(id="X", start_node="a", end_node="b", length_m=100, inner_diameter_mm=90, material="PE100",
                outer_diameter_mm=110, wall_thickness_mm=10, E_GPa=1.05, nu=0.4, depth_m=1)
    base.update(kw)
    return PipeSpec(**base)


def test_pe_dn110_one_bar():
    eps_t, eps_z = wall_strain_ue(pipe(), 0.1)          # 1 bar = 0,1 MPa
    assert float(eps_t) == pytest.approx(309, abs=1)    # fonti.md: ~309 µε
    assert float(eps_z) == pytest.approx(39, abs=1)
    eps_f = helix_strain_ue(eps_t, eps_z, 70)
    assert float(eps_f) == pytest.approx(277, abs=1)    # ~277 µε
    assert float(brillouin_shift_mhz(eps_f)) - 10880 == pytest.approx(13.8, abs=0.1)   # ~14 MHz/bar


def test_cast_iron_is_much_stiffer():
    pe, _ = wall_strain_ue(pipe(), 0.1)
    ci, _ = wall_strain_ue(pipe(outer_diameter_mm=160, wall_thickness_mm=8, E_GPa=170, nu=0.26), 0.1)
    assert float(ci) < float(pe) / 50


def test_helix_limits():
    assert float(helix_strain_ue(100, 10, 90 - 1e-9)) == pytest.approx(100)
    assert float(helix_strain_ue(100, 10, 1e-9)) == pytest.approx(10)
    assert float(helix_strain_ue(100, 10, 45)) == pytest.approx(55)


def test_liner_not_silently_ignored():
    with pytest.raises(NotImplementedError):
        wall_strain_ue(pipe(liner=Liner(6, 8)), 0.1)
