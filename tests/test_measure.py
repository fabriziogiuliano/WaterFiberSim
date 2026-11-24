"""Passo 3b: spettri grezzi e fit di esempio."""

import os
from pathlib import Path

import numpy as np
import pytest

from waterfibersim.fiber import load_scenario
from waterfibersim.measure import fit_peak_mhz, simulate_raw
from waterfibersim.simulate import simulate_true

ROOT = Path(__file__).resolve().parents[1]


def test_fit_close_to_soto():
    """Lorentziana 58 MHz, passo 1 MHz, SNR 16: errore del fit entro il 30 % della formula di [ST13] (Eq. 8)."""
    rng = np.random.default_rng(1)
    fr = np.arange(10_750.0, 11_301.0, 1.0)
    nu0 = 11_000.3
    y = 1 / (1 + ((fr - nu0) / 29) ** 2) + rng.normal(size=(5000, len(fr))) / 16
    err = fit_peak_mhz(y, fr, 58) - nu0
    expected = np.sqrt(0.75 * 1 * 58) / 16
    assert abs(np.nanmean(err)) < 0.05
    assert expected <= np.nanstd(err) < 1.3 * expected


def test_raw_shapes_and_no_noise_fit():
    os.chdir(ROOT)
    sc = load_scenario(ROOT / "scenario_paths" / "S0a_single_pipe_flat.yaml")
    f = sc.fibers[0]
    sig = simulate_true(sc, duration_s=3600, step_s=3600)
    raw = simulate_raw(sig, f, every_min=60)
    T, Z, F = raw.spectra.shape
    assert T == 2 and Z == len(raw.z_m) and F == len(raw.freq_mhz)
    assert np.allclose(np.diff(raw.z_m), f.sampling_interval_m)
    leg = raw.points["leg"].to_numpy()
    nu = fit_peak_mhz(raw.spectra, raw.freq_mhz, f.interrogator.linewidth_mhz)
    uni = (np.abs(raw.nu_true_mean - raw.nu_true_center) < 0.05) & (leg == "sensing")[None, :]
    assert np.nanstd((nu - raw.nu_true_mean)[uni]) < 1.5 * raw.sigma_expected_mhz.max()
