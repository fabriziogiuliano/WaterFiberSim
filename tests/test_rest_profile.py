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
