"""Riga di comando:
    python -m waterfibersim map scenario_paths/A_main_line.yaml --out out/A
    python -m waterfibersim run scenario_paths/A_main_line.yaml --out out/A --hours 24 --step-min 15
    python -m waterfibersim run scenario_paths/A_main_line.yaml --out out/A_x3 --demand-multiplier 3
"""

import argparse
from pathlib import Path

from .fiber import load_scenario
from .fibermap import build_map, fiber_length_m
from .plot import plot_map, plot_true_signal
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


def describe_instrument(f) -> str:
    """Le manopole dello strumento (tempi) e i metri che ne derivano."""
    i = f.interrogator
    return (f"  instrument {f.id}: pulse {i.pulse_width_ns:g} ns -> spatial resolution {f.spatial_resolution_m:.2f} m; "
            f"ADC {i.adc_sample_rate_msps:g} MS/s (one sample every {1e3 / i.adc_sample_rate_msps:.1f} ns) -> "
            f"sampling interval {f.sampling_interval_m:.3f} m  [dz = c t / (2 n), n = {f.group_index}]")


if __name__ == "__main__":
    main()
