"""Temperatura del terreno lungo le fibre (passo T2): solo il terreno, l'acqua arriverà dopo.

Fonti (docs/fonti.md, sezione "Temperatura"):
  - il tratto libero sente solo la temperatura: C_T = 1 MHz/°C                                   [B23] Eq. 1
  - l'elica la sente anche attraverso la dilatazione del tubo: sensibilità complessiva
    `helix_mhz_per_c`, forbice circa 3,5 ([B23] con K_T = 4) - 8 MHz/°C ([SB20], tubo trattenuto) ⚠️
  - variazione stagionale alla profondità delle condotte: circa 11-15 °C in 90 giorni           [SB20]
  - da un punto all'altro della città il terreno a 1 m può differire fino a circa 10 °C          [AV17]

Modello (ipotesi dichiarate):
  - la misura di base è fatta con il terreno a `baseline_c`; conta solo la variazione da allora:
        dT(z, t) = soil_c - baseline_c + drift_c_per_day * t + punti caldi(z)
  - i punti caldi sono variazioni LOCALI in più dalla misura di base (per esempio sotto il sole d'estate),
    con rampe di `HOTSPOT_RAMP_M` metri ai bordi (il terreno non ha salti di temperatura);
  - elica e riferimento sullo stesso tubo, nello stesso punto, hanno la stessa temperatura;
  - cavi e giunzione sono nello stesso terreno (stesso dT di fondo, senza punti caldi).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

HOTSPOT_RAMP_M = 5.0          # ipotesi: transizione di qualche metro ai bordi di un punto caldo

_KEYS = {"baseline_c", "soil_c", "drift_c_per_day", "helix_mhz_per_c", "hotspots"}
_HOTSPOT_KEYS = {"pipe", "from_m", "to_m", "delta_c"}


@dataclass(frozen=True)
class Hotspot:
    pipe: str
    from_m: float            # lungo il tubo, dal nodo di inizio dell'.inp
    to_m: float
    delta_c: float           # variazione in più dalla misura di base


@dataclass(frozen=True)
class SoilTemperature:
    baseline_c: float        # terreno quando è stata fatta la misura di base (0 bar)
    soil_c: float            # terreno all'inizio della simulazione
    drift_c_per_day: float   # deriva stagionale
    helix_mhz_per_c: float   # sensibilità dell'elica alla temperatura (fibra + dilatazione del tubo)
    hotspots: tuple[Hotspot, ...] = ()


def parse_temperature(raw: dict | None, pipes: set[str]) -> SoilTemperature | None:
    if raw is None:
        return None
    unknown = set(raw) - _KEYS
    if unknown:
        raise ValueError(f"temperature: unknown keys {sorted(unknown)}; allowed {sorted(_KEYS)}")
    missing = _KEYS - {"hotspots"} - set(raw)
    if missing:
        raise ValueError(f"temperature: missing {sorted(missing)}")
    hs = []
    for i, h in enumerate(raw.get("hotspots") or []):
        unknown = set(h) - _HOTSPOT_KEYS
        if unknown or set(h) != _HOTSPOT_KEYS:
            raise ValueError(f"temperature.hotspots[{i}]: keys must be {sorted(_HOTSPOT_KEYS)}")
        if h["pipe"] not in pipes:
            raise ValueError(f"temperature.hotspots[{i}]: pipe {h['pipe']} not in the network")
        if not h["from_m"] < h["to_m"]:
            raise ValueError(f"temperature.hotspots[{i}]: from_m must be below to_m")
        hs.append(Hotspot(h["pipe"], float(h["from_m"]), float(h["to_m"]), float(h["delta_c"])))
    t = SoilTemperature(float(raw["baseline_c"]), float(raw["soil_c"]), float(raw["drift_c_per_day"]),
                        float(raw["helix_mhz_per_c"]), tuple(hs))
    if t.helix_mhz_per_c <= 0:
        raise ValueError("temperature.helix_mhz_per_c must be positive")
    return t


def _hotspot_profile(s: np.ndarray, h: Hotspot) -> np.ndarray:
    """0 fuori, delta_c dentro, rampe lineari di HOTSPOT_RAMP_M ai bordi."""
    up = np.clip((s - (h.from_m - HOTSPOT_RAMP_M)) / HOTSPOT_RAMP_M, 0, 1)
    down = np.clip(((h.to_m + HOTSPOT_RAMP_M) - s) / HOTSPOT_RAMP_M, 0, 1)
    return h.delta_c * np.minimum(up, down)


def delta_t_c(temp: SoilTemperature | None, fmap: pd.DataFrame, times_s: np.ndarray) -> np.ndarray:
    """Variazione di temperatura dalla misura di base, (T, Z)."""
    T, Z = len(times_s), len(fmap)
    if temp is None:
        return np.zeros((T, Z))
    local = np.zeros(Z)
    pipe = fmap["pipe"].to_numpy()
    s = fmap["s_pipe_m"].to_numpy()
    for h in temp.hotspots:
        m = pipe == h.pipe
        local[m] += _hotspot_profile(s[m], h)
    base = temp.soil_c - temp.baseline_c + temp.drift_c_per_day * np.asarray(times_s, dtype=float) / 86_400
    return base[:, None] + local[None, :]
