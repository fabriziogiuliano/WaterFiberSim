"""Profilo a riposo: forma da Bertulessi 2023 Fig. 7a e cancellazione con la misura di base."""

import os
from pathlib import Path

import numpy as np
import pytest

from waterfibersim.fiber import load_scenario
from waterfibersim.simulate import simulate_true

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def sig():
    os.chdir(ROOT)
    sc = load_scenario(ROOT / "scenario_paths" / "A_main_line.yaml")
    return simulate_true(sc, duration_s=6 * 3600, step_s=3600, seed=1)


def test_rest_values(sig):
    leg = sig.fiber_map["leg"].to_numpy()
    assert np.all(np.abs(sig.rest_mhz[leg == "lead"]) < 1e-9)                       # cavi: 0
    assert 100 < sig.rest_mhz[leg == "sensing"].mean() < 185                          # elica: +105...+180
    assert sig.rest_mhz[leg == "reference"].mean() == pytest.approx(65, abs=2)        # tratto libero: +65


def test_rest_cancels_with_baseline(sig):
    leg = sig.fiber_map["leg"].to_numpy()
    diff = sig.nu_b_mhz - sig.baseline_mhz
    assert np.allclose(diff[:, leg == "reference"], 0)                                # riferimento: solo temperatura
    assert np.allclose(diff, sig.strain_ue * sig.coef.c_eps_mhz_per_ue)               # resta solo la pressione


def test_seed_reproducible():
    os.chdir(ROOT)
    sc = load_scenario(ROOT / "scenario_paths" / "A_main_line.yaml")
    a = simulate_true(sc, duration_s=3600, step_s=3600, seed=3).rest_mhz
    b = simulate_true(sc, duration_s=3600, step_s=3600, seed=3).rest_mhz
    c = simulate_true(sc, duration_s=3600, step_s=3600, seed=4).rest_mhz
    assert np.array_equal(a, b) and not np.array_equal(a, c)


def _jumps(sig, pid_a, pid_b):
    """Salto del profilo a riposo tra l'ultimo campione dell'elica su pid_a e il primo su pid_b."""
    f = sig.fiber_map
    sens = (f["leg"] == "sensing").to_numpy()
    a = np.flatnonzero(sens & (f["pipe"] == pid_a).to_numpy()).max()
    b = np.flatnonzero(sens & (f["pipe"] == pid_b).to_numpy()).min()
    return abs(sig.rest_mhz[b] - sig.rest_mhz[a])


def test_rest_continuous_on_same_pipe_type():
    """Strada S1: un solo tubo continuo spezzato dai rubinetti: nessun salto ai nodi (solo ondulazioni ~1 MHz)."""
    os.chdir(ROOT)
    sig = simulate_true(load_scenario(ROOT / "scenario_paths" / "S1_street_flat.yaml"),
                        duration_s=3600, step_s=3600, seed=2)
    assert max(_jumps(sig, f"P{i}", f"P{i + 1}") for i in range(1, 10)) < 3


def test_rest_jumps_where_pipe_changes(sig):
    """Griglia A: P1 (DN160) -> P2 (DN125) cambia tubo: lì la posa riparte e il valore è estratto di nuovo."""
    from waterfibersim.rest_profile import _sensing_runs
    f = sig.fiber_map
    idx = np.flatnonzero((f["leg"] == "sensing").to_numpy())
    sc = load_scenario(ROOT / "scenario_paths" / "A_main_line.yaml")
    runs = _sensing_runs(idx, f["z_m"].to_numpy(), f["pipe"].to_numpy(), sc)
    first_pipe = [f["pipe"].iloc[r[0]] for r in runs]
    assert first_pipe == ["P1", "P2", "P7"]          # P1 | P2 (DN125) | P7+P8 (DN110, posa continua)
