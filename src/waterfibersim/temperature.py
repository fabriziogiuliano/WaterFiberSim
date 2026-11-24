"""Temperatura del terreno lungo le fibre (passo T2): solo il terreno, l'acqua arriverà dopo.

Fonti (docs/A-fonti.md, sezione "Temperatura"):
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

Acqua (sezione facoltativa `water`, [BL24] Blokker et al., Water 16, 2796, 2024, Eq. 1-3):
  - l'acqua esce dal serbatoio a `source_c` e lungo il tubo tende alla temperatura del terreno:
        T(s) = T_terreno + (T_ingresso - T_terreno) * exp(-k * s / v)     (s dal nodo a monte, v velocità)
        k = 4 a_w / (D1^2 [1/Nu + l_w ln(D2/D1) / (2 l_tubo) + l_w ln(D3/D2) / (2 l_terreno)]),  D3 = D2 + 2 TSoI D1
        Nu = 0,027 Re^0,8 Pr^0,33 (Re > 2300, ⚠️ [BL24] la dà per Re > 10000), Nu = 3,66 (laminare)
  - nei nodi le acque in arrivo si mescolano pesate con la portata;
  - quasi stazionario: in ogni istante si usano le portate di quell'istante (⚠️ semplificazione);
  - acqua ferma: temperatura del terreno;
  - elica e ritorno (libero nel tubetto, nella stessa guaina) vedono la temperatura dell'acqua nello stesso istante
    (decisione di posa MATRIS, dump §13.4n); cavi e giunzione vedono il terreno.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

HOTSPOT_RAMP_M = 5.0          # ipotesi: transizione di qualche metro ai bordi di un punto caldo

_KEYS = {"baseline_c", "soil_c", "drift_c_per_day", "helix_mhz_per_c", "hotspots", "water"}
_WATER_KEYS = {"source_c", "soil_k_w_mk", "pipe_k_w_mk", "tsoi"}

# proprietà dell'acqua a 20 °C, [BL24] §2.1
ALPHA_WATER = 0.14e-6         # diffusività termica [m²/s]
LAMBDA_WATER = 0.57           # conducibilità termica [W/(m·K)]
NU_WATER = 1.0e-6             # viscosità cinematica [m²/s] ⚠️ valore di manuale, non da [BL24]
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
    water: "WaterTemperature | None" = None


@dataclass(frozen=True)
class WaterTemperature:
    source_c: float           # acqua in uscita dai serbatoi
    soil_k_w_mk: float        # conducibilità del terreno                    [BL24]: sabbia asciutta 1,6
    pipe_k_w_mk: float        # conducibilità del tubo                       PE100: 0,38 (scheda)
    tsoi: float               # sfera di influenza termica (D3 = D2 + 2 TSoI D1)   [BL24]: 1-2 raggi

def parse_temperature(raw: dict | None, pipes: set[str]) -> SoilTemperature | None:
    if raw is None:
        return None
    unknown = set(raw) - _KEYS
    if unknown:
        raise ValueError(f"temperature: unknown keys {sorted(unknown)}; allowed {sorted(_KEYS)}")
    missing = _KEYS - {"hotspots", "water"} - set(raw)
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
    water = None
    if raw.get("water") is not None:
        w = raw["water"]
        if set(w) != _WATER_KEYS:
            raise ValueError(f"temperature.water: keys must be {sorted(_WATER_KEYS)}")
        if hs:
            raise ValueError("temperature: hotspots together with water are not supported yet")
        water = WaterTemperature(float(w["source_c"]), float(w["soil_k_w_mk"]), float(w["pipe_k_w_mk"]),
                                 float(w["tsoi"]))
    t = SoilTemperature(float(raw["baseline_c"]), float(raw["soil_c"]), float(raw["drift_c_per_day"]),
                        float(raw["helix_mhz_per_c"]), tuple(hs), water)
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


def heat_rate_per_s(pipe, velocity_m_s: float, w: WaterTemperature) -> float:
    """k di [BL24] Eq. 2 per un tubo e una velocità."""
    import math
    D1 = pipe.inner_diameter_mm / 1000
    D2 = pipe.outer_diameter_mm / 1000
    D3 = D2 + 2 * w.tsoi * D1
    re = velocity_m_s * D1 / NU_WATER
    nu = 3.66 if re < 2300 else 0.027 * re ** 0.8 * (NU_WATER / ALPHA_WATER) ** 0.33
    r = 1 / nu + LAMBDA_WATER * math.log(D2 / D1) / (2 * w.pipe_k_w_mk) + LAMBDA_WATER * math.log(D3 / D2) / (2 * w.soil_k_w_mk)
    return 4 * ALPHA_WATER / (D1 ** 2 * r)


def water_delta_t_c(temp: SoilTemperature, network, hyd, fmap: pd.DataFrame) -> np.ndarray:
    """dT dalla misura di base, (T, Z), con la temperatura dell'acqua nei tubi e del terreno su cavi e giunzione."""
    w = temp.water
    times = hyd.times_s
    soil = temp.soil_c + temp.drift_c_per_day * times / 86_400                  # (T,)
    T, Z = len(times), len(fmap)
    out = np.repeat((soil - temp.baseline_c)[:, None], Z, axis=1)             # cavi e giunzione: terreno
    node_idx = {n: i for i, n in enumerate(hyd.nodes)}
    link_idx = {l: i for i, l in enumerate(hyd.links)}
    pipes = network.pipes
    reservoirs = {n for n, k in network.node_kind.items() if k in ("reservoir", "tank")}
    fpipe = fmap["pipe"].to_numpy()
    fs = fmap["s_pipe_m"].to_numpy()
    rows = {pid: np.flatnonzero(fpipe == pid) for pid in pd.unique(fpipe[pd.notna(fpipe)])}
    eps = 1e-6
    for t in range(T):
        tb = soil[t]
        head = hyd.head_m[t]
        t_node: dict[str, float] = {}
        inflow: dict[str, list[tuple[float, float]]] = {}
        for n in sorted(hyd.nodes, key=lambda n: -head[node_idx[n]]):          # da monte a valle
            if n in reservoirs:
                t_node[n] = w.source_c
            else:
                ins = inflow.get(n, [])
                q = sum(qq for qq, _ in ins)
                t_node[n] = sum(qq * tt for qq, tt in ins) / q if q > eps else tb
            for pid, p in pipes.items():                                       # tubi che escono da n
                qf = hyd.flow_lps[t, link_idx[pid]]
                up, down = (p.start_node, p.end_node) if qf >= 0 else (p.end_node, p.start_node)
                if up != n:
                    continue
                v = hyd.velocity_m_s[t, link_idx[pid]]
                k = heat_rate_per_s(p, v, w)
                t_in = t_node[n]
                if pid in rows:
                    r = rows[pid]
                    dist = fs[r] if qf >= 0 else p.length_m - fs[r]
                    tw = tb + (t_in - tb) * np.exp(-k * dist / v) if v > 1e-4 else np.full(len(r), tb)
                    out[t, r] = tw - temp.baseline_c
                t_out = tb + (t_in - tb) * np.exp(-k * p.length_m / v) if v > 1e-4 else tb
                inflow.setdefault(down, []).append((abs(qf), t_out))
    return out
