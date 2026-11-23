"""Riga di comando:  python -m waterfibersim map scenario_paths/A_main_line.yaml --out out/A"""

import argparse
from pathlib import Path

from .fiber import load_scenario
from .fibermap import build_map, fiber_length_m
from .plot import plot_map


def main(argv=None):
    ap = argparse.ArgumentParser(prog="waterfibersim")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("map", help="fiber -> pipe map of a path scenario (CSV + figure)")
    m.add_argument("scenario")
    m.add_argument("--out", default="out")
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


if __name__ == "__main__":
    main()
