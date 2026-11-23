"""Scenario di percorso: una o più fibre posate sulla rete (file in scenario_paths/).

Ogni fibra è un anello BOTDA: il tratto di misura (sensing leg) parte dalla porta A e segue `route`;
il tratto di riferimento (reference leg) ripercorre gli stessi tubi al contrario fino alla porta B.
Qui si legge e si valida il file; la geometria lungo z la costruisce fibermap.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import yaml

from .network import Network, load_network

_SCENARIO_KEYS = {"title", "description", "network", "pipes", "fibers"}
_FIBER_KEYS = {"id", "interrogator", "sampling_step_m", "sensing_leg", "reference_leg", "route", "junction_m"}
_INTERROGATOR_KEYS = {"node", "technique", "channel"}
_LEG_KEYS = {"layout", "angle_deg", "bonding"}
_LAYOUTS = {"helix", "straight"}
_BONDINGS = {"embedded", "bonded", "loose_tube"}
_TECHNIQUES = {"BOTDA"}           # per ora solo la BOTDA ad anello


@dataclass(frozen=True)
class Interrogator:
    node: str
    technique: str
    channel: int


@dataclass(frozen=True)
class Leg:
    layout: str                    # "helix" | "straight"
    bonding: str                   # "embedded" | "bonded" | "loose_tube"
    angle_deg: float | None = None  # solo per l'elica: angolo rispetto all'asse del tubo

    @property
    def fiber_per_pipe_m(self) -> float:
        """Metri di fibra per metro di tubo: 1/cos(α) sull'elica, 1 se dritta."""
        return 1.0 / math.cos(math.radians(self.angle_deg)) if self.layout == "helix" else 1.0


@dataclass(frozen=True)
class Segment:
    """Un passo del percorso: un tubo (percorso da `from_node` a `to_node`) o un cavo di collegamento."""

    kind: str                      # "pipe" | "lead"
    from_node: str | None
    to_node: str
    pipe: str | None = None
    lead_m: float | None = None    # lunghezza del cavo (solo per i lead)


@dataclass(frozen=True)
class Fiber:
    id: str
    interrogator: Interrogator
    sampling_step_m: float
    sensing_leg: Leg
    reference_leg: Leg
    route: tuple[Segment, ...]
    junction_m: float


@dataclass
class Scenario:
    path: Path
    title: str
    description: str
    network: Network
    fibers: tuple[Fiber, ...]


def _check(raw: dict, keys: set, where: str) -> None:
    if not isinstance(raw, dict):
        raise ValueError(f"{where}: expected a mapping, got {type(raw).__name__}")
    unknown = set(raw) - keys
    if unknown:
        raise ValueError(f"{where}: unknown keys {sorted(unknown)}; allowed {sorted(keys)}")


def _resolve(base: Path, p: str) -> Path:
    """Percorso relativo alla cartella dello scenario oppure alla cartella corrente."""
    for cand in (base / p, Path(p)):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"{p}: not found (relative to {base} or to the current directory)")


def _leg(raw: dict, where: str) -> Leg:
    _check(raw, _LEG_KEYS, where)
    leg = Leg(layout=raw["layout"], bonding=raw["bonding"], angle_deg=raw.get("angle_deg"))
    if leg.layout not in _LAYOUTS:
        raise ValueError(f"{where}.layout: {leg.layout!r} not in {sorted(_LAYOUTS)}")
    if leg.bonding not in _BONDINGS:
        raise ValueError(f"{where}.bonding: {leg.bonding!r} not in {sorted(_BONDINGS)}")
    if leg.layout == "helix" and not (leg.angle_deg and 0 < leg.angle_deg < 90):
        raise ValueError(f"{where}: a helix needs 0 < angle_deg < 90")
    return leg


def _route(raw: list, net: Network, where: str) -> tuple[Segment, ...]:
    segs, pos, used = [], None, set()
    for i, s in enumerate(raw):
        w = f"{where}[{i}]"
        if "lead" in s:
            _check(s, {"lead", "to", "from"}, w)
            if "to" not in s:
                raise ValueError(f"{w}: a lead needs 'to' (the node it reaches)")
            frm = s.get("from")
            if frm is not None and pos is not None and frm != pos:
                raise ValueError(f"{w}: lead starts at {frm} but the route is at {pos}")
            for n in (frm, s["to"]):
                if n is not None and n not in net.node_xy:
                    raise ValueError(f"{w}: node {n} not in the network")
            segs.append(Segment("lead", frm if frm is not None else pos, s["to"], lead_m=float(s["lead"])))
            pos = s["to"]
        else:
            _check(s, {"pipe", "from"}, w)
            pid, frm = s["pipe"], s["from"]
            if pid not in net.pipes:
                raise ValueError(f"{w}: pipe {pid} not in the network")
            p = net.pipes[pid]
            if frm not in (p.start_node, p.end_node):
                raise ValueError(f"{w}: {frm} is not an end of {pid} ({p.start_node}-{p.end_node})")
            if pos is not None and frm != pos:
                raise ValueError(f"{w}: {pid} starts at {frm} but the route is at {pos} (add a lead)")
            if pid in used:
                raise ValueError(f"{w}: {pid} already used: a fiber cannot pass twice on the same pipe")
            used.add(pid)
            to = p.end_node if frm == p.start_node else p.start_node
            segs.append(Segment("pipe", frm, to, pipe=pid))
            pos = to
    if not used:
        raise ValueError(f"{where}: the route covers no pipe")
    return tuple(segs)


def load_scenario(path: str | Path) -> Scenario:
    """Legge uno scenario di percorso e controlla che ogni fibra sia un percorso continuo sulla rete."""
    path = Path(path)
    raw = yaml.safe_load(path.read_text())
    _check(raw, _SCENARIO_KEYS, path.name)
    base = path.parent
    net = load_network(_resolve(base, raw["network"]), _resolve(base, raw["pipes"]))

    fibers, ids = [], set()
    for j, f in enumerate(raw["fibers"]):
        w = f"fibers[{j}]"
        _check(f, _FIBER_KEYS, w)
        if f["id"] in ids:
            raise ValueError(f"{w}: duplicate fiber id {f['id']}")
        ids.add(f["id"])
        _check(f["interrogator"], _INTERROGATOR_KEYS, f"{w}.interrogator")
        itg = Interrogator(**f["interrogator"])
        if itg.technique not in _TECHNIQUES:
            raise ValueError(f"{w}.interrogator.technique: {itg.technique!r} not supported yet")
        fibers.append(Fiber(
            id=f["id"],
            interrogator=itg,
            sampling_step_m=float(f["sampling_step_m"]),
            sensing_leg=_leg(f["sensing_leg"], f"{w}.sensing_leg"),
            reference_leg=_leg(f["reference_leg"], f"{w}.reference_leg"),
            route=_route(f["route"], net, f"{w}.route"),
            junction_m=float(f["junction_m"]),
        ))
    channels = [(f.interrogator.node, f.interrogator.channel) for f in fibers]
    if len(set(channels)) != len(channels):
        raise ValueError("two fibers on the same interrogator channel")
    return Scenario(path=path, title=raw.get("title", path.stem), description=raw.get("description", ""),
                    network=net, fibers=tuple(fibers))
