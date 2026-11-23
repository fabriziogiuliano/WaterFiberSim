"""Rete idrica: EPANET .inp (idraulica, letto con owa-epanet) + tubi.yaml (meccanica).

L'.inp non si modifica; i parametri meccanici di ogni tubo sono
`default` del YAML, sovrascritti dalle voci in `tubi`.
"""

from __future__ import annotations

import os
import tempfile
import warnings
from dataclasses import dataclass
from pathlib import Path

import yaml
from epanet import toolkit as en

# gli avvisi di EPANET arrivano come warning Python: non devono fermare il caricamento
warnings.filterwarnings("ignore", module="epanet")

# unità di portata SI: con queste EPANET dà lunghezze in m e diametri in mm
_SI_FLOW_UNITS = {en.LPS, en.LPM, en.MLD, en.CMH, en.CMD, en.CMS}

# chiavi YAML (italiano) -> attributi Python (inglese)
_PIPE_KEYS = {
    "materiale": "material",
    "diametro_esterno_mm": "outer_diameter_mm",
    "spessore_mm": "wall_thickness_mm",
    "E_GPa": "E_GPa",
    "nu": "nu",
    "profondita_m": "depth_m",
    "guaina": "liner",
}
_LINER_KEYS = {"spessore_mm": "thickness_mm", "E_GPa": "E_GPa"}

# tolleranza sul confronto tra diametro interno dal YAML e diametro dell'.inp
_DIAMETER_TOL_MM = 0.5


@dataclass(frozen=True)
class Liner:
    """Guaina di relining, all'interno del tubo ospite."""

    thickness_mm: float
    E_GPa: float


@dataclass(frozen=True)
class PipeSpec:
    """Un tubo: geometria dall'.inp, meccanica da tubi.yaml."""

    id: str
    start_node: str
    end_node: str
    length_m: float
    inner_diameter_mm: float  # dall'.inp (diametro idraulico)
    material: str
    outer_diameter_mm: float
    wall_thickness_mm: float
    E_GPa: float
    nu: float
    depth_m: float
    liner: Liner | None = None


@dataclass
class Network:
    """Rete caricata: percorso dell'.inp, tubi con i parametri risolti, coordinate dei nodi."""

    inp_path: Path
    pipes: dict[str, PipeSpec]
    node_xy: dict[str, tuple[float, float]]


def _translate(raw: dict, keys: dict, where: str) -> dict:
    unknown = set(raw) - set(keys)
    if unknown:
        raise ValueError(f"{where}: chiavi sconosciute {sorted(unknown)}; ammesse {sorted(keys)}")
    return {keys[k]: v for k, v in raw.items()}


def _read_inp(inp_path: Path) -> tuple[dict[str, dict], dict[str, tuple[float, float]]]:
    """Tubi (nodi, lunghezza, diametro) e coordinate dei nodi dall'.inp."""
    rpt = os.path.join(tempfile.gettempdir(), f"waterfibersim-{os.getpid()}.rpt")
    ph = en.createproject()
    try:
        en.open(ph, str(inp_path), rpt, "")
        if en.getflowunits(ph) not in _SI_FLOW_UNITS:
            raise ValueError(f"{inp_path}: servono unità SI (LPS, CMH, ...), non unità US")
        node_xy = {
            en.getnodeid(ph, i): tuple(en.getcoord(ph, i))
            for i in range(1, en.getcount(ph, en.NODECOUNT) + 1)
        }
        pipes = {}
        for i in range(1, en.getcount(ph, en.LINKCOUNT) + 1):
            if en.getlinktype(ph, i) not in (en.PIPE, en.CVPIPE):
                continue  # pompe e valvole non portano fibra
            a, b = en.getlinknodes(ph, i)
            pipes[en.getlinkid(ph, i)] = {
                "start_node": en.getnodeid(ph, a),
                "end_node": en.getnodeid(ph, b),
                "length_m": en.getlinkvalue(ph, i, en.LENGTH),
                "inner_diameter_mm": en.getlinkvalue(ph, i, en.DIAMETER),
            }
        en.close(ph)
    finally:
        en.deleteproject(ph)
    return pipes, node_xy


def load_network(inp_path: str | Path, pipes_yaml: str | Path) -> Network:
    """Legge l'.inp con owa-epanet e associa a ogni tubo i parametri di tubi.yaml.

    Errore se il YAML nomina tubi inesistenti, usa chiavi sconosciute o se il
    diametro interno ricavato dal YAML non coincide con quello dell'.inp.
    """
    inp_path = Path(inp_path)
    inp_pipes, node_xy = _read_inp(inp_path)
    cfg = yaml.safe_load(Path(pipes_yaml).read_text())

    default = _translate(cfg.get("default", {}), _PIPE_KEYS, "default")
    overrides = cfg.get("tubi", {}) or {}

    missing = set(overrides) - set(inp_pipes)
    if missing:
        raise ValueError(f"tubi.yaml: tubi non presenti nell'.inp: {sorted(missing)}")

    pipes: dict[str, PipeSpec] = {}
    for name, geom in inp_pipes.items():
        params = {**default, **_translate(overrides.get(name, {}), _PIPE_KEYS, f"tubi.{name}")}
        if params.get("liner") is not None:
            params["liner"] = Liner(**_translate(params["liner"], _LINER_KEYS, f"tubi.{name}.guaina"))

        spec = PipeSpec(id=name, **geom, **params)

        liner_t = spec.liner.thickness_mm if spec.liner else 0.0
        expected = spec.outer_diameter_mm - 2 * spec.wall_thickness_mm - 2 * liner_t
        if abs(expected - spec.inner_diameter_mm) > _DIAMETER_TOL_MM:
            raise ValueError(
                f"{name}: diametro interno dal YAML {expected:.1f} mm "
                f"≠ diametro nell'.inp {spec.inner_diameter_mm:.1f} mm"
            )
        pipes[name] = spec

    return Network(inp_path=inp_path, pipes=pipes, node_xy=node_xy)
