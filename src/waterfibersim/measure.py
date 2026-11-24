"""Passo 3b: il dato grezzo L0, cioè gli spettri Brillouin rumorosi che darebbe lo strumento, più un fit di esempio.

Dal segnale vero (calcolato fine, ogni calc_step_m) allo spettro di ogni punto dello strumento:
  1. punti dello strumento ogni sampling_interval_m = c / (2 n f_ADC) lungo la fibra                 (passo 3a)
  2. ogni punto è una media sulla risoluzione spatial_resolution_m = c tau / (2 n):
         lo spettro misurato è la MEDIA degli spettri locali dentro la finestra (finestra centrata, 🧮)
     [B23] §2.1: "strain and temperature variations are integrated on a spatial interval of 2 m"
  3. spettro locale: lorentziana con FWHM = linewidth_mhz, picco normalizzato a 1, centrata su nu_B locale
     [ST13] Fig. 5: "The distribution maps a resonant Lorentzian profile"; normalizzazione 0 lontano, 1 al picco
  4. frequenze: dalla finestra di scansione, a passi di freq_step_mhz
  5. rumore: gaussiano, indipendente per ogni frequenza, sigma = 1 / SNR(z)          [ST13] §3 e Appendice:
     "additive Gaussian uncorrelated noise"; "the noise amplitude σ … directly representing the inverse of the
     local SNR". SNR(z) da instrument.snr_linear (medie, risoluzione, attenuazione).
Misura di base: stessi passi con il segnale a 0 bar e alla temperatura della misura di base, rumore indipendente;
se si mediano `baseline_repeats` misure di base, il loro rumore cala come 1/sqrt(n) (🧮). ATTENZIONE: il rumore della
misura di base è lo stesso in tutte le misure successive: non si riduce mediando nel tempo.

Fit di esempio ([ST13] §3): stima grezza del picco (massimo dello spettro lisciato su 5 punti), poi parabola ai
minimi quadrati sui punti entro ±FWHM/2 dalla stima (equivale a eta = 0,5), nu = -b / (2a); la finestra si
ricentra sul picco stimato e si ripete (fino a 3 passate: [ST13] Appendice, fit "iterative multi-pass").

Semplificazioni dichiarate: ampiezza del guadagno normalizzata (l'attenuazione entra solo nell'SNR); niente
polarizzazione, niente svuotamento della pompa, niente tempi morti; la misura di un istante è istantanea.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .fiber import Fiber
from .instrument import snr_linear

CHUNK = 400            # punti dello strumento elaborati insieme (memoria)


@dataclass
class RawMeasurement:
    fiber_id: str
    freq_mhz: np.ndarray            # (F,) frequenze della scansione
    z_m: np.ndarray                 # (Zi,) punti dello strumento lungo la fibra
    times_s: np.ndarray             # (Ti,) istanti delle misure
    spectra: np.ndarray             # (Ti, Zi, F) L0: guadagno Brillouin normalizzato, rumoroso
    baseline_spectra: np.ndarray    # (Zi, F) L0 della misura di base
    points: pd.DataFrame            # (Zi righe) leg, pipe, s_pipe_m nel centro di ogni punto
    nu_true_center: np.ndarray      # (Ti, Zi) etichetta: nu_B vera nel centro del punto
    nu_true_mean: np.ndarray        # (Ti, Zi) etichetta: media di nu_B vera nella finestra
    baseline_true_mean: np.ndarray  # (Zi,)
    pressure_bar: np.ndarray        # (Ti, Zi) etichetta nel centro
    delta_t_c: np.ndarray           # (Ti, Zi) etichetta nel centro
    sigma_expected_mhz: np.ndarray  # (Zi,) incertezza attesa di un fit ([ST13] Eq. 7, eta = 0,5)

    def save(self, out: str | Path) -> Path:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"raw_L0_{self.fiber_id}.npz"
        np.savez_compressed(
            path, freq_mhz=self.freq_mhz, z_m=self.z_m, times_s=self.times_s,
            spectra=self.spectra.astype(np.float16), baseline_spectra=self.baseline_spectra.astype(np.float16),
            leg=self.points["leg"].to_numpy(dtype=str), pipe=self.points["pipe"].fillna("").to_numpy(dtype=str),
            s_pipe_m=self.points["s_pipe_m"].to_numpy(),
            nu_true_center=self.nu_true_center, nu_true_mean=self.nu_true_mean,
            baseline_true_mean=self.baseline_true_mean, pressure_bar=self.pressure_bar.astype(np.float32),
            delta_t_c=self.delta_t_c.astype(np.float32), sigma_expected_mhz=self.sigma_expected_mhz)
        return path


def _spectra(nu_local: np.ndarray, freq: np.ndarray, fwhm: float) -> np.ndarray:
    """Media di lorentziane: nu_local (P, n) -> spettri (P, F)."""
    x = (freq[None, None, :] - nu_local[:, :, None]) / (fwhm / 2)
    return (1.0 / (1.0 + x * x)).mean(axis=1)


def _window_spectra(nu_calc: np.ndarray, idx: np.ndarray, half: int, freq: np.ndarray, fwhm: float) -> np.ndarray:
    """Spettri dei punti dello strumento (indici idx sulla griglia di calcolo), media su ±half punti di calcolo."""
    n = len(nu_calc)
    offs = np.arange(-half, half + 1)
    out = np.empty((len(idx), len(freq)))
    for a in range(0, len(idx), CHUNK):
        j = np.clip(idx[a:a + CHUNK, None] + offs[None, :], 0, n - 1)
        out[a:a + CHUNK] = _spectra(nu_calc[j], freq, fwhm)
    return out


def simulate_raw(sig, fiber: Fiber, every_min: float = 60.0, seed: int = 0, baseline_repeats: int = 1) -> RawMeasurement:
    """baseline_repeats: quante misure di base si mediano (il loro rumore cala come 1/sqrt(n))."""
    i = fiber.interrogator
    f = sig.fiber_map
    calc = np.flatnonzero(f["fiber"].to_numpy() == fiber.id)
    calc = calc[np.argsort(f["z_m"].to_numpy()[calc])]
    z_calc = f["z_m"].to_numpy()[calc]
    z_inst = np.arange(0.0, z_calc[-1] + 1e-9, fiber.sampling_interval_m)
    idx = np.clip(np.searchsorted(z_calc, z_inst), 0, len(z_calc) - 1)        # centro di ogni punto
    half = int(round(fiber.spatial_resolution_m / 2 / fiber.calc_step_m))
    lo, hi = i.scan_window_ghz
    freq = np.arange(lo * 1000, hi * 1000 + 1e-6, i.freq_step_mhz)
    step = max(1, int(round(every_min * 60 / np.median(np.diff(sig.times_s)))))
    t_sel = np.arange(0, len(sig.times_s), step)
    rng = np.random.default_rng(seed)
    sigma_noise = 1.0 / snr_linear(fiber, z_inst)                                  # (Zi,)

    def window_mean(v):
        offs = np.arange(-half, half + 1)
        j = np.clip(idx[:, None] + offs[None, :], 0, len(calc) - 1)
        return v[j].mean(axis=1)

    spectra = np.empty((len(t_sel), len(z_inst), len(freq)), dtype=np.float32)
    nu_c = np.empty((len(t_sel), len(z_inst)))
    nu_m = np.empty((len(t_sel), len(z_inst)))
    for k, t in enumerate(t_sel):
        nu = sig.nu_b_mhz[t, calc]
        spectra[k] = _window_spectra(nu, idx, half, freq, i.linewidth_mhz) \
            + rng.normal(size=(len(z_inst), len(freq))) * sigma_noise[:, None]
        nu_c[k] = nu[idx]
        nu_m[k] = window_mean(nu)
    base = sig.baseline_mhz[calc]
    base_spectra = _window_spectra(base, idx, half, freq, i.linewidth_mhz) \
        + rng.normal(size=(len(z_inst), len(freq))) * sigma_noise[:, None] / np.sqrt(baseline_repeats)

    k_fit = 3 * i.freq_step_mhz * i.linewidth_mhz / (8 * np.sqrt(2) * 0.5 ** 1.5)
    points = f.iloc[calc[idx]][["leg", "pipe", "s_pipe_m"]].reset_index(drop=True)
    return RawMeasurement(fiber.id, freq, z_inst, sig.times_s[t_sel], spectra, base_spectra.astype(np.float32),
                          points, nu_c, nu_m, window_mean(base), sig.pressure_bar[np.ix_(t_sel, calc[idx])],
                          sig.delta_t_c[np.ix_(t_sel, calc[idx])], np.sqrt(k_fit) * sigma_noise)


def fit_peak_mhz(spectra: np.ndarray, freq: np.ndarray, fwhm: float, passes: int = 3) -> np.ndarray:
    """Fit di esempio ([ST13]): parabola sui punti entro ±FWHM/2 dalla stima grezza del picco. (..., F) -> (...)."""
    y = np.asarray(spectra, dtype=np.float64)
    shape = y.shape[:-1]
    y = y.reshape(-1, y.shape[-1])
    step = freq[1] - freq[0]
    h = max(1, int(round(fwhm / 2 / step)))
    smooth = pd.DataFrame(y.T).rolling(5, center=True, min_periods=1).mean().to_numpy().T
    i0 = np.clip(np.argmax(smooth, axis=1), h, len(freq) - 1 - h)
    x = np.arange(-h, h + 1) * step                                   # stesse ascisse per tutti: matrice unica
    A = np.vstack([x ** 2, x, np.ones_like(x)]).T
    P = np.linalg.pinv(A)                                             # (3, 2h+1)
    rows = np.arange(len(y))[:, None]
    for _ in range(passes):          # più passate: la finestra si ricentra sul picco stimato ([ST13] Appendice)
        win = y[rows, i0[:, None] + np.arange(-h, h + 1)[None, :]]
        a, b, _ = (win @ P.T).T
        with np.errstate(divide="ignore", invalid="ignore"):
            nu = freq[i0] - b / (2 * a)
        ok = (a < 0) & np.isfinite(nu)
        i_new = np.clip(np.round((np.where(ok, nu, freq[i0]) - freq[0]) / step).astype(int), h, len(freq) - 1 - h)
        if np.array_equal(i_new, i0):
            break
        i0 = i_new
    nu = np.where(ok, nu, np.nan)                                     # parabola rivolta in basso: picco valido
    return nu.reshape(shape)
