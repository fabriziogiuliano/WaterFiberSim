"""Incertezza dello strumento: il modello riproduce i numeri di Soto & Thévenaz 2013 [ST13]."""

import math
import os
from dataclasses import replace
from pathlib import Path

import pytest

from waterfibersim.fiber import load_scenario
from waterfibersim.instrument import min_measurement_time_s, sigma_nu_mhz, snr_linear

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def fiber():
    os.chdir(ROOT)
    return load_scenario(ROOT / "scenario_paths" / "S1_street_flat.yaml").fibers[0]


def test_soto_validation_point(fiber):
    """[ST13] §3: SNR 9,4 dB, delta 1 MHz, FWHM 58 MHz -> circa 0,75 MHz misurati (Eq. 8: 0,76)."""
    snr = 10 ** (9.4 / 10)
    i = fiber.interrogator
    assert math.sqrt(0.75 * i.freq_step_mhz * i.linewidth_mhz) / snr == pytest.approx(0.76, abs=0.02)


def test_b23_settings_give_about_0_4_mhz(fiber):
    """Impostazioni di [B23] (256 medie, 1 MHz) con SNR0 = 0 dB a 2 m: circa 0,41 MHz all'ingresso."""
    assert float(sigma_nu_mhz(fiber, 0.0)) == pytest.approx(0.41, abs=0.02)


def test_scaling_laws(fiber):
    """sigma ~ 1/sqrt(N_AV), ~ sqrt(delta); SNR cala con la distanza."""
    s0 = float(sigma_nu_mhz(fiber, 0.0))
    more = replace(fiber, interrogator=replace(fiber.interrogator, n_averages=fiber.interrogator.n_averages * 4))
    coarse = replace(fiber, interrogator=replace(fiber.interrogator, freq_step_mhz=fiber.interrogator.freq_step_mhz * 4))
    assert float(sigma_nu_mhz(more, 0.0)) == pytest.approx(s0 / 2)
    assert float(sigma_nu_mhz(coarse, 0.0)) == pytest.approx(s0 * 2)
    assert float(snr_linear(fiber, 4000)) < float(snr_linear(fiber, 0))


def test_min_time(fiber):
    """551 passi x 256 medie x andata e ritorno su 4 km: qualche secondo."""
    assert 4 < min_measurement_time_s(fiber, 3946) < 7
