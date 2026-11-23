"""Mappa "metro di fibra -> tubo": per ogni campione lungo la fibra, dove si trova sulla rete.

z si conta dalla porta A (dove lo strumento legge). Lungo l'anello si incontrano, in ordine:
  cavi e tubi del percorso, tratto di misura (elica)  ->  giunzione  ->
  gli stessi tubi e cavi al contrario, tratto di riferimento (dritto)  ->  porta B.
Ogni punto di un tubo compare quindi due volte: una sul tratto di misura, una su quello di riferimento.

s_pipe_m è la distanza dal nodo iniziale del tubo nell'.inp (start_node), uguale per i due tratti:
così le due righe dello stesso punto del tubo hanno lo stesso (pipe, s_pipe_m).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .fiber import Fiber, Scenario

COLUMNS = ["fiber", "z_m", "leg", "pipe", "s_pipe_m", "x", "y"]


def _pieces(fiber: Fiber, net):
    """Tratti consecutivi lungo z: (leg, pipe, lunghezza di fibra, s all'inizio, s alla fine, nodo per i punti fissi)."""
    out = []
    for seg in fiber.route:                                     # andata: tratto di misura
        out.append(_piece(seg, fiber.sensing_leg, net, forward=True))
    out.append(("junction", None, fiber.junction_m, None, None, fiber.route[-1].to_node))
    for seg in reversed(fiber.route):                           # ritorno: tratto di riferimento
        out.append(_piece(seg, fiber.reference_leg, net, forward=False))
    return out


def _piece(seg, leg, net, forward):
    if seg.kind == "lead":
        return ("lead", None, seg.lead_m, None, None, None)
    p = net.pipes[seg.pipe]
    frm, to = (seg.from_node, seg.to_node) if forward else (seg.to_node, seg.from_node)
    s0 = 0.0 if frm == p.start_node else p.length_m              # s misurato da start_node
    s1 = p.length_m - s0
    name = "sensing" if forward else "reference"
    return (name, seg.pipe, p.length_m * leg.fiber_per_pipe_m, s0, s1, None)


def build_fiber_map(fiber: Fiber, scenario: Scenario) -> pd.DataFrame:
    """Mappa di una fibra, un campione ogni `sampling_step_m` da z = 0 (porta A) alla porta B."""
    net = scenario.network
    pieces = _pieces(fiber, net)
    total = sum(pc[2] for pc in pieces)
    z = np.arange(0.0, total + 1e-9, fiber.sampling_step_m)
    starts = np.cumsum([0.0] + [pc[2] for pc in pieces[:-1]])
    idx = np.searchsorted(starts, z, side="right") - 1

    leg, pipe = np.empty(z.size, dtype=object), np.empty(z.size, dtype=object)
    s, x, y = (np.full(z.size, np.nan) for _ in range(3))
    for k, (name, pid, length, s0, s1, node) in enumerate(pieces):
        m = idx == k
        leg[m], pipe[m] = name, pid
        if pid is not None:
            frac = (z[m] - starts[k]) / length
            s[m] = s0 + (s1 - s0) * frac
            p = net.pipes[pid]
            (xa, ya), (xb, yb) = net.node_xy[p.start_node], net.node_xy[p.end_node]
            x[m] = xa + (xb - xa) * s[m] / p.length_m           # tubi dritti tra i due nodi (nessun vertice)
            y[m] = ya + (yb - ya) * s[m] / p.length_m
        elif node is not None:
            x[m], y[m] = net.node_xy[node]
    return pd.DataFrame({"fiber": fiber.id, "z_m": z, "leg": leg, "pipe": pipe, "s_pipe_m": s, "x": x, "y": y},
                        columns=COLUMNS)


def build_map(scenario: Scenario) -> pd.DataFrame:
    """Mappa di tutte le fibre dello scenario, una sotto l'altra (colonna `fiber`)."""
    return pd.concat([build_fiber_map(f, scenario) for f in scenario.fibers], ignore_index=True)


def fiber_length_m(fiber: Fiber, scenario: Scenario) -> float:
    """Lunghezza totale dell'anello, dalla porta A alla porta B."""
    return float(sum(pc[2] for pc in _pieces(fiber, scenario.network)))
