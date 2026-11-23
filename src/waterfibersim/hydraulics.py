"""Idraulica nel tempo con owa-epanet (stessa libreria e versione di edge-slm-emulator)."""

from __future__ import annotations

import os
import tempfile
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from epanet import toolkit as en

warnings.filterwarnings("ignore", module="epanet")

M_WATER_TO_MPA = 9.80665e-3       # 1 m di colonna d'acqua = rho * g * 1 m = 9806,65 Pa


@dataclass
class HydraulicResult:
    times_s: np.ndarray            # (T,) istanti di misura
    nodes: list[str]
    pressure_m: np.ndarray         # (T, N) pressione nei nodi [m di colonna d'acqua]

    def pressure_mpa(self) -> np.ndarray:
        return self.pressure_m * M_WATER_TO_MPA


def run_hydraulics(inp_path: str | Path, duration_s: int, step_s: int) -> HydraulicResult:
    """Simulazione in regime (periodo esteso) e pressione nei nodi ogni `step_s` secondi.

    EPANET risolve le pressioni a ogni passo idraulico; qui il passo è `step_s`. Con gli andamenti di
    domanda orari della rete di prova la pressione cambia a scalini di un'ora.
    """
    rpt = os.path.join(tempfile.gettempdir(), f"waterfibersim-{os.getpid()}.rpt")
    ph = en.createproject()
    try:
        en.open(ph, str(inp_path), rpt, "")
        en.settimeparam(ph, en.DURATION, int(duration_s))
        en.settimeparam(ph, en.HYDSTEP, int(step_s))
        en.settimeparam(ph, en.REPORTSTEP, int(step_s))
        n = en.getcount(ph, en.NODECOUNT)
        nodes = [en.getnodeid(ph, i) for i in range(1, n + 1)]
        times, press = [], []
        en.openH(ph)
        en.initH(ph, 0)
        while True:
            t = en.runH(ph)
            if t % step_s == 0 and (not times or t != times[-1]):
                times.append(t)
                press.append([en.getnodevalue(ph, i, en.PRESSURE) for i in range(1, n + 1)])
            if en.nextH(ph) <= 0:
                break
        en.closeH(ph)
        en.close(ph)
    finally:
        en.deleteproject(ph)
    return HydraulicResult(np.array(times), nodes, np.array(press))
