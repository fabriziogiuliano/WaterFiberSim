"""Numeri di riferimento della meccanica (docs/A-fonti.md)."""

import math

import numpy as np
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
    assert float(eps_t) == pytest.approx(309, abs=1)    # A-fonti.md: ~309 µε
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


def test_multilayer_one_layer_equals_lame():
    """Un solo strato: il modello a strati coincide con la formula chiusa sulla superficie esterna."""
    from waterfibersim.mechanics import multilayer_strain_ue, pipe_layers

    p = pipe()
    layers, r = pipe_layers(p)
    et, ez = multilayer_strain_ue(layers, 0.1, r)
    et0, ez0 = wall_strain_ue(p, 0.1)
    assert float(et) == pytest.approx(float(et0), rel=1e-9)
    assert float(ez) == pytest.approx(float(ez0), rel=1e-9)


def test_multilayer_split_layer_is_neutral():
    """Lo stesso materiale spezzato in due strati incollati dà lo stesso risultato."""
    from waterfibersim.mechanics import Layer, multilayer_strain_ue

    one = [Layer(0.045, 0.055, 1.0, 0.4)]
    two = [Layer(0.045, 0.050, 1.0, 0.4), Layer(0.050, 0.055, 1.0, 0.4)]
    for r in (0.045, 0.05, 0.055):
        assert np.allclose(multilayer_strain_ue(one, 0.1, r), multilayer_strain_ue(two, 0.1, r))


def test_liner_in_rigid_host_feels_little():
    """Guaina (8 GPa) dentro ghisa (170 GPa): la fibra nella guaina sente molto meno che su un tubo in PE."""
    rigid = pipe(outer_diameter_mm=222, wall_thickness_mm=6.3, E_GPa=170, nu=0.26, liner=Liner(6, 8))
    et, _ = wall_strain_ue(rigid, 0.1)
    pe, _ = wall_strain_ue(pipe(), 0.1)
    assert float(et) < 0.05 * float(pe)


def test_demand_multiplier_increases_daily_variation():
    import os
    from pathlib import Path

    import numpy as np

    from waterfibersim.hydraulics import run_hydraulics
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    r1 = run_hydraulics("network/grid_3x3.inp", 86_400, 3600, 1.0)
    r3 = run_hydraulics("network/grid_3x3.inp", 86_400, 3600, 3.0)
    j = r1.nodes.index("J33")
    assert np.ptp(r3.pressure_m[:, j]) > 5 * np.ptp(r1.pressure_m[:, j])   # perdite di carico ~ Q^1,852
