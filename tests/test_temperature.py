"""Temperatura del terreno (passo T2): riferimento a C_T, elica a helix_mhz_per_c, punti caldi locali."""

import os
from pathlib import Path

import numpy as np
import pytest

from waterfibersim.fiber import load_scenario
from waterfibersim.simulate import simulate_true

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def pair():
    os.chdir(ROOT)
    kw = dict(duration_s=6 * 3600, step_s=3600, seed=5)
    cold = simulate_true(load_scenario(ROOT / "scenario_paths" / "S1t_street_flat_soil.yaml"), **kw)
    flat = simulate_true(load_scenario(ROOT / "scenario_paths" / "S1_street_flat.yaml"), **kw)
    return cold, flat


def test_uniform_scenario_has_no_hotspot(pair):
    cold, _ = pair
    assert np.ptp(cold.delta_t_c[0]) == pytest.approx(0)              # S1t: stesso dT ovunque


def test_temperature_adds_on_top_of_pressure(pair):
    cold, flat = pair
    sc = load_scenario(ROOT / "scenario_paths" / "S1t_street_flat_soil.yaml")
    leg = cold.fiber_map["leg"].to_numpy()
    extra = cold.nu_b_mhz - flat.nu_b_mhz                              # stessa pressione, stesso profilo a riposo
    dT = cold.delta_t_c
    assert np.allclose(extra[:, leg == "reference"], dT[:, leg == "reference"] * cold.coef.c_t_mhz_per_c)
    assert np.allclose(extra[:, leg == "sensing"], dT[:, leg == "sensing"] * sc.temperature.helix_mhz_per_c)
    assert np.allclose(cold.strain_ue, flat.strain_ue)                  # la pressione non cambia


def test_drift_and_hotspot():
    os.chdir(ROOT)
    cold = simulate_true(load_scenario(ROOT / "scenario_paths" / "S1th_street_flat_soil_hotspot.yaml"),
                         duration_s=6 * 3600, step_s=3600, seed=5)
    f = cold.fiber_map
    dT = cold.delta_t_c
    out = ((f["pipe"] == "P2") & (f["leg"] == "sensing")).to_numpy()
    assert dT[0, out] == pytest.approx(-8.0)                            # 10 - 18 °C
    assert dT[-1, out][0] == pytest.approx(-8.0 - 0.15 * 6 / 24)        # deriva di 6 ore
    hot = ((f["pipe"] == "P6") & (f["s_pipe_m"].between(30, 50))).to_numpy()
    assert np.allclose(dT[0, hot], -5.0)                                # punto caldo: +3 °C in più


def test_compensation(pair):
    """K giusto: torna la pressione vera; K sbagliato: errore sistematico (K_vero - K) * dT / k_bar."""
    from waterfibersim.compensation import compensated_pressure_bar
    from waterfibersim.instrument import helix_mhz_per_bar

    cold, _ = pair
    sc = load_scenario(ROOT / "scenario_paths" / "S1t_street_flat_soil.yaml")
    f = sc.fibers[0]
    h = (cold.fiber_map["leg"] == "sensing").to_numpy()
    good = compensated_pressure_bar(cold, sc, f, sc.temperature.helix_mhz_per_c)
    assert np.allclose(good[:, h], cold.pressure_bar[:, h], atol=1e-6)
    k = helix_mhz_per_bar(sc, f, cold.coef)["P1"]
    wrong = compensated_pressure_bar(cold, sc, f, 3.5)
    expected = (sc.temperature.helix_mhz_per_c - 3.5) * cold.delta_t_c[:, h] / k
    assert np.allclose(wrong[:, h] - cold.pressure_bar[:, h], expected, atol=1e-6)


def test_adaptive_average_keeps_hotspot_and_interpolation_has_no_steps():
    """S1th: punto per punto (interpolato) senza scalini; media adattiva molto meglio della mobile sul punto caldo."""
    from waterfibersim.compensation import compensated_pressure_bar

    os.chdir(ROOT)
    sc = load_scenario(ROOT / "scenario_paths" / "S1th_street_flat_soil_hotspot.yaml")
    sig = simulate_true(sc, duration_s=3600, step_s=3600, seed=5)
    f, K = sc.fibers[0], sc.temperature.helix_mhz_per_c
    h = (sig.fiber_map["leg"] == "sensing").to_numpy()

    def max_err(**kw):
        return np.nanmax(abs(compensated_pressure_bar(sig, sc, f, K, t_idx=0, **kw)[0, h] - sig.pressure_bar[0, h]))

    assert max_err() < 0.005
    assert max_err(ref_avg_m=74, mode="adaptive") < 0.5 * max_err(ref_avg_m=74, mode="moving")
