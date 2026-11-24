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
from .plot import plot_compensation, plot_compensation_measured, plot_map, plot_raw, plot_true_signal, plot_uncertainty
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
    c = sub.add_parser("compensate", help="temperature compensation with the reference leg and remaining errors (T3)")
    c.add_argument("scenario")
    c.add_argument("--out", default="out")
    c.add_argument("--hour", type=int, default=8)
    c.add_argument("--measured", action="store_true", help="on the noisy measured data (spectra + fit, step 3b)")
    c.add_argument("--hours", type=float, default=24)
    c.add_argument("--every-min", type=float, default=60)
    c.add_argument("--baseline-repeats", type=int, default=1, help="baseline measurements averaged")
    c.add_argument("--seed", type=int, default=0)
    ms = sub.add_parser("measure", help="raw data L0: noisy Brillouin spectra of the instrument + example fit (3b)")
    ms.add_argument("scenario")
    ms.add_argument("--out", default="out")
    ms.add_argument("--hours", type=float, default=24)
    ms.add_argument("--every-min", type=float, default=60, help="one instrument measurement every N minutes")
    ms.add_argument("--seed", type=int, default=0)
    va = sub.add_parser("validate", help="validation campaign: every hypothesis against an independent reference")
    va.add_argument("--out", default="docs/10-validazione.md")
    va.add_argument("--quick", action="store_true", help="skip the slow check on noisy data")
    kn = sub.add_parser("knobs", help="sensitivity study of the simulator knobs (figures for chapter 9)")
    kn.add_argument("--out", default="docs/img")
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

    if a.cmd == "knobs":
        from .knobs import run as run_knobs
        for k_, v_ in run_knobs(Path.cwd(), Path(a.out)).items():
            print(f"  {k_:16s} {v_:.4g}")

    if a.cmd == "validate":
        from .validation import run_all, write_report
        checks, liner = run_all(Path.cwd(), with_noise=not a.quick)
        for c in checks:
            print(f"  [{c.esito:4s}] {c.area:13s} {c.cosa}: {c.nostro} vs {c.riferimento}")
        for r in liner:
            print(f"  {r['mhz_per_bar']:7.2f} MHz/bar  {r['caso']}")
        print(f"written {write_report(checks, liner, Path(a.out))}")

    if a.cmd == "instrument":
        report_instrument(load_scenario(a.scenario), Path(a.out))

    if a.cmd == "compensate" and a.measured:
        report_compensation_measured(load_scenario(a.scenario), Path(a.out), a.hours, a.every_min,
                                     a.baseline_repeats, a.seed)
    elif a.cmd == "compensate":
        report_compensation(load_scenario(a.scenario), Path(a.out), a.hour)

    if a.cmd == "measure":
        report_measure(load_scenario(a.scenario), Path(a.out), a.hours, a.every_min, a.seed)

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


def report_compensation(sc, out: Path, hour: int) -> None:
    import numpy as np

    from .compensation import apparent_pressure_bar, compensated_pressure_bar, random_error_bar

    if sc.temperature is None:
        raise SystemExit("this scenario has no `temperature` section: nothing to compensate")
    out.mkdir(parents=True, exist_ok=True)
    sig = simulate_true(sc)
    t = int(np.argmin(abs(sig.times_s / 3600 - hour)))
    K = sc.temperature.helix_mhz_per_c
    for f in sc.fibers:
        h = np.flatnonzero((sig.fiber_map["fiber"].to_numpy() == f.id) & (sig.fiber_map["leg"].to_numpy() == "sensing"))
        true = sig.pressure_bar[t, h]

        def err(est):
            e = est[h] - true
            return f"mean {np.nanmean(e):+.3f}, max |{np.nanmax(abs(e)):.3f}| bar"

        def comp(k, L=0.0, mode="moving"):
            return compensated_pressure_bar(sig, sc, f, k, L, mode, t_idx=t)[0]

        L_eq = (K / sig.coef.c_t_mhz_per_c) ** 2 * f.spatial_resolution_m
        print(f"fiber {f.id}, {hour:02d}:00, dT from the baseline {sig.delta_t_c[t, h].min():+.1f} to "
              f"{sig.delta_t_c[t, h].max():+.1f} degC, helix K = {K:g} MHz/degC (true)")
        print(f"  not compensated:                        {err(apparent_pressure_bar(sig, sc, f)[t])}")
        print(f"  true K, point by point (interpolated):  {err(comp(K))}")
        for k_ass in (3.5, 8.0):
            print(f"  K = {k_ass:g} (systematic):                  {err(comp(k_ass))}")
        for L, mode in ((20.0, "moving"), (L_eq, "moving"), (L_eq, "adaptive"), (200.0, "adaptive")):
            print(f"  true K, reference {mode:8s} average over {L:3.0f} m: {err(comp(K, L, mode))}")
        for L in (0.0, 20.0, L_eq, 200.0):
            tot, hel, th = random_error_bar(sc, f, K, L)
            print(f"  random error, one measurement, reference averaged over {L:5.0f} m: {float(tot):.3f} bar "
                  f"(helix {hel:.3f}, temperature {float(th):.3f})")
        png = plot_compensation(sc, sig, f, out / f"compensation_{f.id}.png", hour)
        print(f"  written {png}")


def report_measure(sc, out: Path, hours: float, every_min: float, seed: int) -> None:
    import numpy as np

    from .instrument import helix_mhz_per_bar
    from .measure import fit_peak_mhz, simulate_raw

    sig = simulate_true(sc, duration_s=int(hours * 3600), seed=seed)
    for f in sc.fibers:
        print(describe_instrument(f))
        raw = simulate_raw(sig, f, every_min, seed)
        path = raw.save(out)
        fw = f.interrogator.linewidth_mhz
        nu = fit_peak_mhz(raw.spectra, raw.freq_mhz, fw)
        nu_b = fit_peak_mhz(raw.baseline_spectra, raw.freq_mhz, fw)
        np.savez_compressed(out / f"fit_L1_{f.id}.npz", z_m=raw.z_m, times_s=raw.times_s, nu_fit_mhz=nu,
                            baseline_fit_mhz=nu_b)
        leg = raw.points["leg"].to_numpy()
        uni = np.abs(raw.nu_true_mean - raw.nu_true_center) < 0.05      # punti lontani dai cambi di tratto
        err = nu - raw.nu_true_mean
        T, Z, F = raw.spectra.shape
        print(f"  L0: {T} measurements x {Z} points x {F} frequencies -> {path} ({path.stat().st_size / 1e6:.0f} MB)")
        for L in ("sensing", "reference", "lead"):
            m = (leg == L)[None, :] & uni
            if m.any():
                print(f"  fit error on {L:9s} (uniform stretches): std {np.nanstd(err[m]):.3f} MHz, "
                      f"mean {np.nanmean(err[m]):+.3f}; expected [ST13] {raw.sigma_expected_mhz[leg == L].mean():.3f} MHz")
        print(f"  largest errors where the 2 m window mixes different stretches: max |{np.nanmax(abs(err)):.1f}| MHz; "
              f"failed fits: {int(np.isnan(nu).sum())}")
        k = float(np.nanmean(list(helix_mhz_per_bar(sc, f, sig.coef).values())))
        png = plot_raw(raw, nu, nu_b, fw, out / f"raw_{f.id}.png", k)
        print(f"  written {png}")


def report_compensation_measured(sc, out: Path, hours: float, every_min: float, repeats: int, seed: int) -> None:
    import warnings

    import numpy as np

    from .compensation import compensate_measured, mixed_window_mask
    from .measure import fit_peak_mhz, simulate_raw

    if sc.temperature is None:
        raise SystemExit("this scenario has no `temperature` section: nothing to compensate")
    out.mkdir(parents=True, exist_ok=True)
    sig = simulate_true(sc, duration_s=int(hours * 3600), seed=seed)
    K = sc.temperature.helix_mhz_per_c
    for f in sc.fibers:
        fw = f.interrogator.linewidth_mhz
        L_eq = (K / sig.coef.c_t_mhz_per_c) ** 2 * f.spatial_resolution_m
        runs = {}
        for rep in sorted({repeats, 10}):
            raw = simulate_raw(sig, f, every_min, seed, baseline_repeats=rep)
            runs[rep] = (raw, fit_peak_mhz(raw.spectra, raw.freq_mhz, fw), fit_peak_mhz(raw.baseline_spectra, raw.freq_mhz, fw))
        raw = runs[repeats][0]
        P = raw.points
        bad = mixed_window_mask(raw, f)
        H = np.flatnonzero((P["leg"].to_numpy() == "sensing") & ~bad)
        hot = np.zeros(len(raw.z_m), bool)
        for hs in sc.temperature.hotspots:
            hot |= (P["pipe"].to_numpy() == hs.pipe) & (P["s_pipe_m"].between(hs.from_m - 15, hs.to_m + 15)).to_numpy()
        far, near = H[~hot[H]], H[hot[H]]
        strategies = [("point by point", 0.0, "moving"), ("moving 20 m", 20.0, "moving"),
                      (f"moving {L_eq:.0f} m", L_eq, "moving"), (f"adaptive {L_eq:.0f} m", L_eq, "adaptive")]
        print(f"fiber {f.id}: {len(raw.times_s)} measurements, helix points used {len(H)} "
              f"(excluded {int(bad.sum())} points whose 2 m window mixes stretches), K = {K:g} MHz/degC")
        print(f"  {'strategy':22s} {'baseline':>8s}  {'random (1 sigma)':>16s}  {'frozen (baseline)':>17s}  {'hotspot bias':>12s}")
        results = {}
        for rep, (rw, nu, nb) in runs.items():
            for name, L, mode in strategies:
                est = compensate_measured(rw, nu, nb, sc, f, K, L, mode)
                e = est - rw.pressure_bar
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)       # colonne fuori dall'elica: tutte NaN
                    e_t = np.nanmean(e, axis=0)
                rand = np.nanstd(e[:, far] - e_t[far])
                froz = np.nanstd(e_t[far])
                hb = np.nanmax(abs(e_t[near])) if len(near) else float("nan")
                print(f"  {name:22s} {'x' + str(rep):>8s}  {rand:13.3f} bar  {froz:14.3f} bar  {hb:9.3f} bar")
                results[(name, rep)] = (est, e_t)
        zoom = None
        if len(near):
            zoom = (raw.z_m[near].min() - 100, raw.z_m[near].max() + 100)
        colors = ["#ced4da", "#69db7c", "#2b8a3e", "#1971c2"]
        it = {"point by point": "punto per punto", "moving": "media mobile", "adaptive": "media adattiva"}

        def ital(n):
            for a_, b_ in it.items():
                n = n.replace(a_, b_)
            return n

        curves = {f"{ital(n)} (misura di base ×{repeats})": (results[(n, repeats)][0], c)
                  for (n, _, _), c in zip(strategies, colors)}
        ad = strategies[-1][0]
        frozen = {f"punto per punto, misura di base ×{repeats}": (results[(strategies[0][0], repeats)][1], "#adb5bd"),
                  f"{ital(ad)}, misura di base ×{repeats}": (results[(ad, repeats)][1], "#1971c2"),
                  f"{ital(ad)}, misura di base ×10 (media di 10)": (results[(ad, 10)][1], "#c92a2a")}
        png = plot_compensation_measured(raw, curves, out / f"compensation_measured_{f.id}.png", zoom, frozen)
        print(f"  written {png}")


def describe_instrument(f) -> str:
    """Le manopole dello strumento (tempi) e i metri che ne derivano."""
    i = f.interrogator
    return (f"  instrument {f.id}: pulse {i.pulse_width_ns:g} ns -> spatial resolution {f.spatial_resolution_m:.2f} m; "
            f"ADC {i.adc_sample_rate_msps:g} MS/s (one sample every {1e3 / i.adc_sample_rate_msps:.1f} ns) -> "
            f"sampling interval {f.sampling_interval_m:.3f} m  [dz = c t / (2 n), n = {f.group_index}]")


if __name__ == "__main__":
    main()
