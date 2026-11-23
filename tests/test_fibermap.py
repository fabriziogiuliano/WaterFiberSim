"""Verifiche del passo 1 (README §1.5) sullo scenario A."""

import math
from pathlib import Path

import pytest

from waterfibersim.fiber import load_scenario
from waterfibersim.fibermap import build_fiber_map, fiber_length_m

ROOT = Path(__file__).resolve().parents[1]
K = 1 / math.cos(math.radians(70))


@pytest.fixture(scope="module")
def scen(monkeypatch_module=None):
    import os
    os.chdir(ROOT)                      # i percorsi nello scenario sono relativi alla radice del repo
    return load_scenario(ROOT / "scenario_paths" / "A_main_line.yaml")


def test_total_length(scen):
    f = scen.fibers[0]
    pipes_m = sum(scen.network.pipes[s.pipe].length_m for s in f.route if s.kind == "pipe")
    leads_m = sum(s.lead_m for s in f.route if s.kind == "lead")
    assert pipes_m == 600 and leads_m == 15
    assert fiber_length_m(f, scen) == pytest.approx(2 * leads_m + pipes_m * K + f.junction_m + pipes_m)


def test_each_pipe_twice_full_range(scen):
    m = build_fiber_map(scen.fibers[0], scen)
    for pid in ["P0", "P1", "P2", "P7", "P8"]:
        for leg in ["sensing", "reference"]:
            s = m[(m["pipe"] == pid) & (m.leg == leg)]["s_pipe_m"]
            L = scen.network.pipes[pid].length_m
            assert len(s) > 0, (pid, leg)
            assert s.min() >= -1e-9 and s.max() <= L + 1e-9
            assert s.min() < 1.0 and s.max() > L - 1.0, (pid, leg, s.min(), s.max())


def test_order_and_ends(scen):
    m = build_fiber_map(scen.fibers[0], scen)
    legs = m["leg"].tolist()
    assert legs[0] == "lead" and legs[-1] == "lead"
    first = m[m.leg == "sensing"].iloc[0]
    assert first["pipe"] == "P0" and first.s_pipe_m == pytest.approx(0.0)        # parte da R1, inizio di P0
    jn = m[m.leg == "junction"].iloc[0]
    assert (jn.x, jn.y) == scen.network.node_xy["J33"]                           # giunzione in fondo, su J33


def test_same_pipe_point_twice(scen):
    """Il punto a metà di P1 compare sia sull'elica sia sul riferimento, in posizioni z diverse."""
    m = build_fiber_map(scen.fibers[0], scen)
    p = m[(m["pipe"] == "P1") & ((m.s_pipe_m - 50).abs() < 0.5)]
    assert set(p.leg) == {"sensing", "reference"}
    assert p[p.leg == "sensing"].z_m.mean() < p[p.leg == "reference"].z_m.mean()


def test_bad_route_rejected(tmp_path, scen):
    bad = (ROOT / "scenario_paths" / "A_main_line.yaml").read_text().replace("{pipe: P2, from: J12}", "{pipe: P8, from: J23}")
    f = tmp_path / "bad.yaml"
    f.write_text(bad.replace("network/", str(ROOT / "network") + "/"))
    with pytest.raises(ValueError):
        load_scenario(f)
