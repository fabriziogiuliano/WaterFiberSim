"""Campagna di validazione: ogni ipotesi del simulatore confrontata con un dato indipendente (articolo, scheda,
formula ufficiale). Più gli esperimenti sulla guaina (modello a strati). Genera docs/10-validazione.md.

Esito: OK = entro la tolleranza dichiarata; DIFF = differenza spiegata (scritta nella nota); KO = da indagare.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .brillouin import BrillouinCoefficients
from .fiber import C_M_PER_S, load_scenario
from .mechanics import Layer, helix_strain_ue, multilayer_strain_ue

COEF = BrillouinCoefficients()
FT, CFS = 0.3048, 0.028316846592          # piede [m], piede cubo al secondo [m³/s]


@dataclass
class Check:
    area: str
    cosa: str
    nostro: str
    riferimento: str
    fonte: str
    esito: str
    nota: str = ""


def _lame_outer(beta: float, nu: float, E_mpa: float, p_mpa: float) -> tuple[float, float]:
    k = beta ** 2 / (1 - beta ** 2) * p_mpa / E_mpa
    return (2 - nu) * k * 1e6, (1 - 2 * nu) * k * 1e6


def check_hydraulics(root: Path) -> Check:
    """S0a: perdita di carico nel tubo da 1 km calcolata da EPANET contro la formula di Hazen-Williams del manuale."""
    from .hydraulics import run_hydraulics
    sc = load_scenario(root / "scenario_paths" / "S0a_single_pipe_flat.yaml")
    h = run_hydraulics(sc.network.inp_path, 86_400, 3600)
    t = 8
    il = h.links.index("P1")
    q_m3s = abs(h.flow_lps[t, il]) / 1000
    p = sc.network.pipes["P1"]
    dh_epanet = h.head_m[t, h.nodes.index("N0")] - h.head_m[t, h.nodes.index("N1")]
    C = 140.0
    A = 4.727 * C ** -1.852 * (p.inner_diameter_mm / 1000 / FT) ** -4.871 * (p.length_m / FT)
    dh_formula = A * (q_m3s / CFS) ** 1.852 * FT
    err = abs(dh_epanet - dh_formula) / dh_formula
    return Check("idraulica", "perdita di carico, tubo PE DN110 da 1 km alle 08:00 (S0a)",
                 f"{dh_epanet:.3f} m", f"{dh_formula:.3f} m", "EPANET 2.2, Tab. 3.1 (h = A q^1,852, A = 4,727 C^-1,852 d^-4,871 L)",
                 "OK" if err < 0.01 else "KO", f"differenza {err * 100:.2f} %")


def checks_mechanics() -> list[Check]:
    """[B23]: tubo PN16 OD 63 mm, elica con spira Lc = 0,198 m e passo S = 0,05 m (Tab. 1, fase I)."""
    beta, nu, E1, E2 = 0.78, 0.4, 1050.0, 4470.0              # [B23] Tab. 2, PN16
    alpha = math.degrees(math.acos(0.05 / 0.198))             # [B23] Eq. 3: Lc = sqrt(S^2 + Ce^2)
    out = []
    for p_bar, meas in ((5, 73), (10, 200)):
        et, ez = _lame_outer(beta, nu, E1, p_bar / 10)
        f_el = float(helix_strain_ue(et, ez, alpha)) * COEF.c_eps_mhz_per_ue
        e_c = 1 / (1 / E1 + 1 / E2)                           # Burgers senza il termine che cresce col tempo
        et2, ez2 = _lame_outer(beta, nu, e_c, p_bar / 10)
        f_vi = float(helix_strain_ue(et2, ez2, alpha)) * COEF.c_eps_mhz_per_ue
        ratio = meas / f_vi
        out.append(Check("meccanica", f"spostamento Brillouin sull'elica, PN16 OD 63, {p_bar} bar (α = {alpha:.1f}°)",
                         f"{f_el:.0f} MHz elastico; {f_vi:.0f} MHz con E2 (Burgers)", f"{meas} MHz misurati",
                         "[B23] §3.1 e Tab. 2",
                         "OK" if abs(ratio - 1) < 0.15 else "DIFF",
                         ("con il rilassamento viscoelastico (E2) il modello torna entro il 15 %; il solo elastico "
                          "sottostima" if abs(ratio - 1) < 0.15 else
                          f"misurato {ratio:.1f} volte il modello: a 10 bar il PE esce dal comportamento lineare "
                          "(creep, termine η3 di Burgers, non modellato); il simulatore è elastico")))
    # minimo misurabile [B23] §4: PN10 OD 63, accuratezza 10 µε -> 0,016 bar
    et, _ = _lame_outer(0.86, 0.4, 1050.0, 0.1)
    pmin = 10 / et
    out.append(Check("meccanica", "minima variazione di pressione misurabile, PN10 OD 63, accuratezza 10 µε",
                     f"{pmin:.3f} bar (Lamé, superficie esterna)", "0,016 bar", "[B23] §4",
                     "OK" if abs(pmin - 0.016) / 0.016 < 0.5 else "DIFF",
                     "stesso ordine di grandezza; [B23] non dice con quale formula lo ricava"))
    return out


def checks_instrument(root: Path) -> list[Check]:
    from .instrument import sigma_nu_mhz
    f = load_scenario(root / "scenario_paths" / "S1_street_flat.yaml").fibers[0]
    out = []
    snr = 10 ** (9.4 / 10)
    s = math.sqrt(0.75 * 1 * 58) / snr
    out.append(Check("strumento", "incertezza sul picco, SNR 9,4 dB, δ 1 MHz, Δν_B 58 MHz, 200 medie",
                     f"{s:.2f} MHz", "0,75 MHz misurati", "[ST13] §3, Fig. 6–9", "OK" if abs(s - 0.75) < 0.1 else "KO"))
    s0 = float(sigma_nu_mhz(f, 0.0))
    out.append(Check("strumento", "incertezza con le impostazioni di [B23] (20 ns, 1 MHz, 256 medie), SNR0 = 0 dB",
                     f"{s0:.2f} MHz", "migliore di 0,5 MHz (10 µε)", "[B23] §2.1; [ST13] Eq. 8–9",
                     "OK" if s0 <= 0.5 else "KO", "il valore dichiarato è un limite superiore"))
    out.append(Check("strumento", "passo di campionamento da 125 MS/s; risoluzione da 20 ns",
                     f"{f.sampling_interval_m:.2f} m; {f.spatial_resolution_m:.2f} m", "0,8 m; 2 m",
                     "[B23] §2.1", "OK" if abs(f.sampling_interval_m - 0.8) < 0.05 else "KO",
                     f"con n = {f.group_index} (⚠️ da scheda della fibra); con n = 1,5 i valori coincidono"))
    return out


def check_fit() -> Check:
    from .measure import fit_peak_mhz
    rng = np.random.default_rng(1)
    fr = np.arange(10_750.0, 11_301.0, 1.0)
    y = 1 / (1 + ((fr - 11_000.3) / 29) ** 2) + rng.normal(size=(4000, len(fr))) / 16
    sd = float(np.nanstd(fit_peak_mhz(y, fr, 58) - 11_000.3))
    formula = math.sqrt(0.75 * 58) / 16
    return Check("dato grezzo", "fit parabolico su spettri lorentziani sintetici (SNR 16, δ 1 MHz, 58 MHz)",
                 f"{sd:.3f} MHz", f"{formula:.3f} MHz (Eq. 8)", "[ST13] Eq. 8 e Appendice",
                 "DIFF", f"+{(sd / formula - 1) * 100:.0f} %: la formula assume una parabola; [ST13]: il fattore √(3/4) "
                         "dipende dalla funzione fittata")


def check_water() -> Check:
    from .temperature import WaterTemperature, heat_rate_per_s
    from .network import PipeSpec
    pe = PipeSpec("x", "a", "b", 100, 90, "PE100", 110, 10, 1.0, 0.4, 1)
    w = WaterTemperature(14, 1.6, 0.38, 1)
    tau = [1 / heat_rate_per_s(pe, v, w) / 3600 for v in (0.0, 0.2, 0.8)]
    return Check("temperatura", "costante di tempo acqua–terreno, PE DN110 in sabbia, acqua ferma / 0,2 / 0,8 m/s",
                 " / ".join(f"{x:.1f} h" for x in tau), "\"minutes to hours\"", "[BL24] §1, Eq. 2",
                 "OK" if all(0.1 < x < 10 for x in tau) else "KO")


def check_compensation(root: Path) -> Check:
    from .compensation import compensate_measured, random_error_bar
    from .measure import fit_peak_mhz, simulate_raw
    from .simulate import simulate_true
    sc = load_scenario(root / "scenario_paths" / "S1t_street_flat_soil.yaml")
    f = sc.fibers[0]
    K = sc.temperature.helix_mhz_per_c
    sig = simulate_true(sc, duration_s=6 * 3600)
    raw = simulate_raw(sig, f, 60, seed=3)
    fw = f.interrogator.linewidth_mhz
    est = compensate_measured(raw, fit_peak_mhz(raw.spectra, raw.freq_mhz, fw),
                              fit_peak_mhz(raw.baseline_spectra, raw.freq_mhz, fw), sc, f, K, 74, "moving")
    sim = float(np.nanstd(est - raw.pressure_bar))
    model = float(random_error_bar(sc, f, K, 74)[0])
    return Check("compensazione", "errore di una misura compensata, riferimento mediato su 74 m (S1t)",
                 f"{sim:.3f} bar (spettri rumorosi + fit)", f"{model:.3f} bar (formula di propagazione)",
                 "coerenza interna: [ST13] + propagazione degli errori", "OK" if abs(sim / model - 1) < 0.35 else "KO",
                 "il fit fa circa il 17 % peggio della formula di [ST13]: atteso un valore un po' più alto")


# --- esperimenti sulla guaina -------------------------------------------------------------------------------------

def liner_experiments() -> list[dict]:
    """MHz per bar sull'elica (70°) per combinazioni tubo ospite / guaina / strato comprimibile.

    Valori dei materiali (vedi docs/A-fonti.md): PE100 E 1,1 GPa (scheda), ν 0,4 ([B23]); ghisa E 170 GPa, ν 0,26 (⚠️);
    guaina CIPP in feltro E 1,724 GPa (minimo ASTM F1216), in vetro UV E 10,3 GPa (scheda Vortex, fogna);
    ν della guaina 0,35 e spessore 6 mm ⚠️; strato comprimibile ipotetico.
    """
    def run(name, layers, r_fiber, note=""):
        et, ez = multilayer_strain_ue(layers, 0.1, r_fiber)
        mhz = float(helix_strain_ue(et, ez, 70)) * COEF.c_eps_mhz_per_ue
        return {"caso": name, "mhz_per_bar": mhz, "nota": note}

    rows = []
    # riferimento: tubo PE DN110 SDR11 senza guaina, fibra fuori
    rows.append(run("PE DN110 SDR11, fibra sulla superficie esterna (rete di prova, [B23])",
                    [Layer(0.045, 0.055, 1.1, 0.4)], 0.055, "riferimento"))
    hosts = {"ghisa DN200 integra (E 170 GPa)": (0.1047, 0.111, 170.0, 0.26),
             "ghisa DN200 degradata (E ridotto a 1/10)": (0.1047, 0.111, 17.0, 0.26),
             "PE DN160 SDR11 (E 1,1 GPa)": (0.0654, 0.080, 1.1, 0.4)}
    liners = {"CIPP feltro 6 mm (E 1,7 GPa)": (0.006, 1.724), "CIPP vetro UV 6 mm (E 10,3 GPa)": (0.006, 10.3)}
    for hn, (ri, ro, E, nu) in hosts.items():
        for ln, (t, El) in liners.items():
            layers = [Layer(ri - t, ri, El, 0.35), Layer(ri, ro, E, nu)]
            rows.append(run(f"{ln} in {hn}", layers, ri - t / 2))
    # idea dell'utente: strato comprimibile tra guaina e ospite rigido; fibra nella pelle interna
    ri, ro = 0.1047, 0.111
    for skin_t, skin_E, skin in ((0.003, 1.724, "pelle in feltro 3 mm"), (0.006, 10.3, "pelle in vetro 6 mm")):
        for soft_t, soft_E in ((0.010, 0.05), (0.010, 0.5)):
            a = ri - soft_t
            layers = [Layer(a - skin_t, a, skin_E, 0.35), Layer(a, ri, soft_E, 0.3), Layer(ri, ro, 170.0, 0.26)]
            M = soft_E * 1e3 * 0.7 / (1.3 * 0.4)
            rows.append(run(f"ghisa integra + strato comprimibile {soft_t * 1000:.0f} mm (E {soft_E * 1000:.0f} MPa, "
                            f"confinato circa {M:.0f} MPa) + {skin}", layers, a - skin_t / 2, "ipotesi (idea dell'utente)"))
    return rows


def run_all(root: Path, with_noise: bool = True) -> tuple[list[Check], list[dict]]:
    checks = [check_hydraulics(root), *checks_mechanics(), *checks_instrument(root), check_fit(), check_water()]
    if with_noise:
        checks.append(check_compensation(root))
    return checks, liner_experiments()


def write_report(checks: list[Check], liner: list[dict], path: Path) -> Path:
    L = ["# 10. Validazione del simulatore", "",
         "*Pagina generata da `python -m waterfibersim validate` (poi `python docs/navigazione.py` per la navigazione).*", "",
         "Ogni riga confronta un risultato del simulatore con un dato indipendente. Esiti: **OK** entro la tolleranza; "
         "**DIFF** differenza capita e spiegata nella nota; **KO** da indagare. Commento e conclusioni nel [capitolo 8](08-logica-del-simulatore.md) e nel [capitolo 11](11-risultati-e-questioni-aperte.md).",
         "## 10.1 Confronto con riferimenti indipendenti", "", "| area | cosa | simulatore | riferimento | fonte | esito | nota |", "|---|---|---|---|---|---|---|"]
    for c in checks:
        L.append(f"| {c.area} | {c.cosa} | {c.nostro} | {c.riferimento} | {c.fonte} | **{c.esito}** | {c.nota} |")
    L += ["", "## 10.2 Sensibilità della fibra nella guaina (modello multistrato)", "",
          "Spostamento Brillouin sull'elica a 70° per 1 bar; fibra a metà guaina (o della pelle). Rumore di una misura "
          "con le impostazioni di [B23]: circa 0,4–0,5 MHz, quindi per vedere 0,1 bar servono almeno circa 4–5 MHz/bar.", "",
          "| caso | MHz per bar | 0,1 bar visibile in una misura? | nota |", "|---|---|---|---|"]
    for r in liner:
        vis = "sì" if r["mhz_per_bar"] * 0.1 > 0.45 else "no"
        L.append(f"| {r['caso']} | {r['mhz_per_bar']:.2f} | {vis} | {r['nota']} |")
    path.write_text("\n".join(L) + "\n")
    return path
