"""Riga di comando:
    python -m waterfibersim map scenario_paths/A_main_line.yaml --out out/A
    python -m waterfibersim run scenario_paths/A_main_line.yaml --out out/A --hours 24 --step-min 15
    python -m waterfibersim run scenario_paths/A_main_line.yaml --out out/A_x3 --demand-multiplier 3
    python -m waterfibersim instrument scenario_paths/S1_street_flat.yaml --out out/S1
"""

import argparse
from pathlib import Path

from .fiber import load_scenario
from .fibermap import build_map, fiber_length_m
from .plot import plot_map, plot_true_signal, plot_uncertainty
from .simulate import simulate_true


def main(argv=None):
    ap = argparse.ArgumentParser(prog="waterfibersim")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("map", help="fiber -> pipe map of a path scenario (CSV + figure)")
    m.add_argument("scenario")
    m.add_argument("--out", default="out")
    r = sub.add_parser("run", help="true signal along the fibers over time (step 2: no noise, no optics)")
    r.add_argument("scenario")
    r.add_argument("--out", default="out")
    r.add_argument("--hours", type=float, default=24)
    r.add_argument("--step-min", type=float, default=15)
    r.add_argument("--demand-multiplier", type=float, default=1.0, help="multiply all demands (EPANET Demand Multiplier)")
    r.add_argument("--seed", type=int, default=0, help="seed of the random rest profile")
    r.add_argument("--no-rest-profile", action="store_true", help="flat rest profile (all metres at nu_B0)")
    u = sub.add_parser("instrument", help="expected instrument uncertainty and measurement time (Soto & Thevenaz 2013)")
    u.add_argument("scenario")
    u.add_argument("--out", default="out")
    a = ap.parse_args(argv)

    if a.cmd == "map":
        sc = load_scenario(a.scenario)
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        fmap = build_map(sc)
        csv = out / "fiber_map.csv"
        fmap.to_csv(csv, index=False, float_format="%.3f")
        png = plot_map(sc, fmap, out / "fiber_map.png")
        for f in sc.fibers:
            print(f"fiber {f.id}: {fiber_length_m(f, sc):.1f} m, {int((fmap['fiber'] == f.id).sum())} calculation points "
                  f"(every {f.calc_step_m} m)")
            print(describe_instrument(f))
        print(f"written {csv} and {png}")

    if a.cmd == "instrument":
        report_instrument(load_scenario(a.scenario), Path(a.out))

    if a.cmd == "run":
        sc = load_scenario(a.scenario)
        sig = simulate_true(sc, duration_s=int(a.hours * 3600), step_s=int(a.step_min * 60),
                            demand_multiplier=a.demand_multiplier, seed=a.seed, rest_profile=not a.no_rest_profile)
        npz = sig.save(a.out)
        for f in sc.fibers:
            plot_true_signal(sig, Path(a.out) / f"signal_true_{f.id}.png", f.id)
        T, Z = sig.nu_b_mhz.shape
        for f in sc.fibers:
            print(describe_instrument(f))
        print(f"{T} hydraulic times x {Z} calculation points (true signal, no instrument yet); "
              f"written {npz} and figures in {a.out}")


def report_instrument(sc, out: Path) -> None:
    import math

    from .instrument import (check_scan_window, helix_mhz_per_bar, min_measurement_time_s, n_freq_steps,
                             uncertainty_table)
    from .brillouin import BrillouinCoefficients

    out.mkdir(parents=True, exist_ok=True)
    fmap = build_map(sc)
    sig = simulate_true(sc)
    coef = BrillouinCoefficients()
    for f in sc.fibers:
        i = f.interrogator
        L = fiber_length_m(f, sc)
        print(describe_instrument(f))
        tab = uncertainty_table(sc, f, fmap, coef)
        sens, ref = tab[tab["leg"] == "sensing"], tab[tab["leg"] == "reference"]
        k = helix_mhz_per_bar(sc, f, coef)
        print(f"  helix sensitivity: " + ", ".join(f"{p} {v:.1f}" for p, v in k.items()) + " MHz/bar")
        print(f"  ONE measurement, helix: SNR {sens['snr_db'].max():.1f} -> {sens['snr_db'].min():.1f} dB, "
              f"sigma_nu {sens['sigma_mhz'].min():.3f} -> {sens['sigma_mhz'].max():.3f} MHz "
              f"= {sens['sigma_bar'].min():.4f} -> {sens['sigma_bar'].max():.4f} bar")
        print(f"  ONE measurement, reference: sigma_nu {ref['sigma_mhz'].min():.3f} -> {ref['sigma_mhz'].max():.3f} MHz "
              f"= {ref['sigma_c'].min():.3f} -> {ref['sigma_c'].max():.3f} degC")
        print(f"  difference from the baseline (two noisy measurements, x sqrt 2): helix up to "
              f"{sens['sigma_mhz'].max() * math.sqrt(2):.3f} MHz = {sens['sigma_bar'].max() * math.sqrt(2):.4f} bar")
        t = min_measurement_time_s(f, L)
        print(f"  scan: {n_freq_steps(f)} frequency steps x {i.n_averages} averages, loop {L:.0f} m -> "
              f"minimum measurement time {t:.1f} s (dead times of the instrument not included)")
        cols = (sig.fiber_map["fiber"] == f.id).to_numpy()
        w = check_scan_window(f, sig.nu_b_mhz[:, cols])
        print(f"  scan window {i.scan_window_ghz[0]}-{i.scan_window_ghz[1]} GHz, peaks usable in "
              f"{w.usable_lo_mhz:.0f}-{w.usable_hi_mhz:.0f} MHz; true peaks {w.nu_min_mhz:.0f}-{w.nu_max_mhz:.0f} MHz: "
              f"{'OK' if w.ok else 'OUT OF WINDOW'}")
        png = plot_uncertainty(sc, fmap, f, out / f"uncertainty_{f.id}.png")
        print(f"  written {png}")


def describe_instrument(f) -> str:
    """Le manopole dello strumento (tempi) e i metri che ne derivano."""
    i = f.interrogator
    return (f"  instrument {f.id}: pulse {i.pulse_width_ns:g} ns -> spatial resolution {f.spatial_resolution_m:.2f} m; "
            f"ADC {i.adc_sample_rate_msps:g} MS/s (one sample every {1e3 / i.adc_sample_rate_msps:.1f} ns) -> "
            f"sampling interval {f.sampling_interval_m:.3f} m  [dz = c t / (2 n), n = {f.group_index}]")


if __name__ == "__main__":
    main()
