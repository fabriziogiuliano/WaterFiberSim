"""Riga di comando:
    python -m waterfibersim map scenario_paths/A_main_line.yaml --out out/A
    python -m waterfibersim run scenario_paths/A_main_line.yaml --out out/A --hours 24 --step-min 15
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
            print(f"fiber {f.id}: {fiber_length_m(f, sc):.1f} m, {int((fmap['fiber'] == f.id).sum())} samples")
        print(f"written {csv} and {png}")

    if a.cmd == "run":
        sc = load_scenario(a.scenario)
        sig = simulate_true(sc, duration_s=int(a.hours * 3600), step_s=int(a.step_min * 60))
        npz = sig.save(a.out)
        for f in sc.fibers:
            plot_true_signal(sig, Path(a.out) / f"signal_true_{f.id}.png", f.id)
        T, Z = sig.nu_b_mhz.shape
        print(f"{T} measurements x {Z} positions; written {npz} and figures in {a.out}")


if __name__ == "__main__":
    main()
