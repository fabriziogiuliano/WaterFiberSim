"""
Scenari di percorso della fibra (scenario_paths) sulla rete di prova (network/grid_3x3.inp).

Per ogni proposta: tubi coperti in ordine dalla porta A, cavi di collegamento (lead), lunghezza di fibra.
Il tratto di riferimento (dritto, libero) ripercorre sempre gli stessi tubi al contrario: non è disegnato a parte.
Uso:  python docs/img/scenario_paths.py  ->  docs/img/scenario_paths.png + docs/img/scenario_paths.drawio.svg
I percorsi si leggono dai file scenario_paths/*.yaml: per cambiarli, modificare i YAML e rigenerare.
"""
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

XY = {"R1": (0, 400), "J11": (0, 200), "J12": (100, 200), "J13": (200, 200), "J21": (0, 100), "J22": (100, 100),
      "J23": (200, 100), "J31": (0, 0), "J32": (100, 0), "J33": (200, 0)}
PIPES = {"P0": ("R1", "J11", 200), "P1": ("J11", "J12", 100), "P2": ("J12", "J13", 100), "P3": ("J21", "J22", 100),
         "P4": ("J22", "J23", 100), "P5": ("J31", "J32", 100), "P6": ("J32", "J33", 100), "P7": ("J13", "J23", 100),
         "P8": ("J23", "J33", 100), "P9": ("J12", "J22", 100), "P10": ("J22", "J32", 100), "P11": ("J11", "J21", 100),
         "P12": ("J21", "J31", 100)}
DEMAND = {"J13", "J31", "J33"}
K = 1 / math.cos(math.radians(70))      # m di fibra per m di tubo sull'elica
LEAD_IN, JUNCTION = 15, 2
ARANCIO, VIOLA, GRIGIO, TESTO = "#ff6a00", "#7048e8", "#adb5bd", "#1b1f24"

# i percorsi si leggono dai file scenario_paths/*.yaml (unica fonte: figura e scenari non possono divergere)
import yaml  # noqa: E402

RADICE = Path(__file__).resolve().parents[2]


def _route(r):
    out = []
    for s in r:
        if "lead" in s:
            out.append(("lead", s["lead"], s.get("from"), s["to"]))
        else:
            out.append(("pipe", s["pipe"], s["from"]))
    return out


OPZIONI = []
for f in sorted((RADICE / "scenario_paths").glob("*.yaml")):
    sc = yaml.safe_load(f.read_text())
    fibre = [_route(fb["route"]) for fb in sc["fibers"]]
    coperti = {s[1] for r in fibre for s in r if s[0] == "pipe"}
    nf = len(fibre)
    sotto = (f"{nf} fibra" if nf == 1 else f"{nf} fibre ({nf} canali)") + f" · {len(coperti)} tubi su {len(PIPES)}"
    OPZIONI.append((sc["title"], sotto, fibre, sc["description"]))

def lunghezze(route):
    tubi = sum(PIPES[s[1]][2] for s in route if s[0] == "pipe")
    lead = sum(s[1] for s in route if s[0] == "lead")
    return tubi, lead, 2 * lead + tubi * K + JUNCTION + tubi   # andata (lead + elica) + giunzione + ritorno


fig, axs = plt.subplots(1, 3, figsize=(21, 10.5), dpi=100, gridspec_kw=dict(wspace=0.12, left=0.03, right=0.97,
                                                                              top=0.76, bottom=0.27))
fig.suptitle("Scenari di percorso della fibra (scenario_paths)", fontsize=21, fontweight="bold", color=TESTO,
             x=0.03, ha="left", y=0.97)
fig.text(0.03, 0.905, "Arancione/viola: tubi coperti, numerati nell'ordine in cui li percorre il tratto a elica partendo "
         "dalla porta A (freccia = verso).  Tratteggio: cavi di collegamento (lead), non su un tubo.\n"
         "Il tratto di riferimento (dritto, libero, solo temperatura) ripercorre gli stessi tubi al contrario fino alla "
         "porta B: non è disegnato a parte.", fontsize=12.5, color="#495057", va="top", linespacing=1.4)

for ax, (titolo, sotto, fibre, nota) in zip(axs, OPZIONI):
    ax.set_aspect("equal")
    ax.set_xlim(-120, 300)
    ax.set_ylim(-45, 470)
    ax.axis("off")
    ax.set_title(f"{titolo}\n", fontsize=17, fontweight="bold", color=TESTO, loc="left")
    ax.text(0.0, 1.0, sotto, transform=ax.transAxes, fontsize=13.5, color="#495057", va="bottom")
    for pid, (a, b, _) in PIPES.items():           # rete di base
        (x0, y0), (x1, y1) = XY[a], XY[b]
        ax.plot([x0, x1], [y0, y1], color=GRIGIO, lw=5, solid_capstyle="round", zorder=1)
        ax.text((x0 + x1) / 2 + (7 if x0 == x1 else 0), (y0 + y1) / 2 + (0 if x0 == x1 else -14), pid, fontsize=10,
                color="#868e96", ha="left" if x0 == x1 else "center", va="center", zorder=2)
    for n, (x, y) in XY.items():
        r = n == "R1"
        ax.plot(x, y, "s" if r else "o", ms=13 if r else 9, color="#1971c2" if r else ("#2b8a3e" if n in DEMAND else "#495057"),
                zorder=5)
        ax.text(x - 9, y + 9, n, fontsize=11, ha="right", va="bottom", color=TESTO, zorder=6)
    ax.add_patch(FancyBboxPatch((-88, 385), 62, 30, boxstyle="round,pad=2", fc="#1b1f24", ec="none", zorder=4))
    ax.text(-57, 400, "interr.", color="white", fontsize=10.5, ha="center", va="center", zorder=6)
    ax.plot([-26, 0], [400, 400], color="#1b1f24", lw=2, zorder=3)

    righe = []
    for f, route in enumerate(fibre):
        col = ARANCIO if f == 0 else VIOLA
        off = 0 if len(fibre) == 1 else (-4 if f == 0 else 4)
        k = 0
        for s in route:
            if s[0] == "lead":
                if s[2] is None and s[3] != "R1":      # cavo dall'interrogatore a un nodo lontano
                    (x1, y1) = XY[s[3]]
                    xl = -45 - 22 * f
                    ax.plot([-26, xl, xl, x1], [395 - 8 * f, 395 - 8 * f, y1, y1], color=col, lw=2, ls="--", zorder=3)
                    ax.text(xl - 4, (395 + y1) / 2, f"lead {s[1]} m", color=col, fontsize=10, rotation=90, ha="right",
                            va="center")
                elif s[2] is not None:
                    (x0, y0), (x1, y1) = XY[s[2]], XY[s[3]]
                    ax.plot([x0, x1], [y0, y1], color=col, lw=2, ls="--", zorder=3)
                    ax.text((x0 + x1) / 2 + 8, (y0 + y1) / 2 + 8, f"lead {s[1]} m", color=col, fontsize=10)
                continue
            k += 1
            pid, frm = s[1], s[2]
            a, b, _ = PIPES[pid]
            to = b if frm == a else a
            (x0, y0), (x1, y1) = XY[frm], XY[to]
            dx, dy = (off, 0) if x0 == x1 else (0, off)
            ax.plot([x0 + dx, x1 + dx], [y0 + dy, y1 + dy], color=col, lw=6, solid_capstyle="round", zorder=3)
            mx, my = (x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy
            ax.annotate("", xy=(mx + (x1 - x0) * 0.12, my + (y1 - y0) * 0.12), xytext=(mx - (x1 - x0) * 0.12, my - (y1 - y0) * 0.12),
                        arrowprops=dict(arrowstyle="-|>", color="white", lw=2, mutation_scale=16), zorder=4)
            ax.text(x0 + (x1 - x0) * 0.25 + dx, y0 + (y1 - y0) * 0.25 + dy, str(k), fontsize=9.5, color="white",
                    fontweight="bold", ha="center", va="center", zorder=6,
                    bbox=dict(boxstyle="circle,pad=0.2", fc=col, ec="white", lw=1.2))
        tubi, lead, fibra = lunghezze(route)
        n_fibra = f"{fibra:,.0f}".replace(",", ".")
        righe.append((col, f"fibra {f + 1}: {tubi:.0f} m di tubo, {lead:.0f} m di cavo  →  ~{n_fibra} m di fibra"))
    y = -0.04
    for col, r in righe:
        ax.text(0.0, y, r, transform=ax.transAxes, fontsize=11.5, color=col, fontweight="bold", va="top")
        y -= 0.05
    ax.text(0.0, y - 0.01, nota, transform=ax.transAxes, fontsize=12.5, color=TESTO, va="top", linespacing=1.4)

fig.text(0.03, 0.035, "Lunghezza di fibra = 2 × cavi + tubi × 2,92 (elica a 70°) + giunzione 2 m + tubi × 1 (riferimento).  "
         "Nodi: quadrato blu = serbatoio R1 con l'interrogatore; verde = utenze (J13, J31, J33).\n"
         "Gli interrogatori BOTDA commerciali leggono fibre da decine di km (Prysmian DITEST: 80 km per canale, 4 canali "
         "ad anello): qui la lunghezza non è un vincolo.", fontsize=12, color="#495057", linespacing=1.45)
out = Path(__file__).with_name("scenario_paths.png")
fig.savefig(out, dpi=100, facecolor="white")
print("scritto", out)
for titolo, _, fibre, _ in OPZIONI:
    print(titolo, [tuple(round(v) for v in lunghezze(r)) for r in fibre])


# ---------------------------------------------------------------- versione modificabile in draw.io
import sys  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from drawio_svg import Drawing  # noqa: E402

d = Drawing(1420, 830, nome="scenario_paths")
d.label(40, 40, "Scenari di percorso della fibra (scenario_paths)", size=22, weight="bold", w=900)
d.label(40, 68, ["Arancione/viola: tubi coperti, numerati nell'ordine in cui li percorre il tratto a elica partendo "
                 "dalla porta A (triangolo = verso). Tratteggio: cavi di collegamento (lead), non su un tubo.",
                 "Il tratto di riferimento (dritto, libero, solo temperatura) ripercorre gli stessi tubi al contrario "
                 "fino alla porta B: non è disegnato a parte."], size=12.5, color="#495057", w=1340)
Y0 = 215


def P2(ox, nodo):
    x, y = XY[nodo]
    return ox + x, Y0 + (400 - y)


for i, (titolo, sotto, fibre, nota) in enumerate(OPZIONI):
    ox = 120 + i * 460
    d.label(ox - 80, 150, titolo, size=17, weight="bold", w=380)
    d.label(ox - 80, 172, sotto, size=13, color="#495057", w=380)
    for pid, (a, b, _) in PIPES.items():
        (x0, y0), (x1, y1) = P2(ox, a), P2(ox, b)
        d.line([(x0, y0), (x1, y1)], color=GRIGIO, sw=6)
        if x0 == x1:
            d.label(x0 + 8, (y0 + y1) / 2 + 4, pid, size=10, color="#868e96", w=40)
        else:
            d.label((x0 + x1) / 2, y0 + 17, pid, size=10, color="#868e96", anchor="middle", w=40)
    d.box(ox - 88, Y0 - 14, 60, 28, ["interr."], fill="#1b1f24", stroke="#1b1f24", color="#ffffff", size=11,
          bold_first=False)
    d.line([(ox - 28, Y0), (ox, Y0)], color="#1b1f24", sw=2)
    righe = []
    for f, route in enumerate(fibre):
        col = ARANCIO if f == 0 else VIOLA
        off = 0 if len(fibre) == 1 else (-4 if f == 0 else 4)
        k = 0
        for s in route:
            if s[0] == "lead":
                if s[2] is None and s[3] != "R1":
                    x1, y1 = P2(ox, s[3])
                    xl = ox - 58 - 24 * f
                    d.line([(xl, Y0 + 14), (xl, y1), (x1, y1)], color=col, sw=2, dashed=True)
                    d.label(xl - 6, (Y0 + y1) / 2 + 40, f"lead {s[1]} m", size=10, color=col, rotation=-90, w=90)
                elif s[2] is not None:
                    (x0, y0), (x1, y1) = P2(ox, s[2]), P2(ox, s[3])
                    d.line([(x0, y0), (x1, y1)], color=col, sw=2, dashed=True)
                    d.label((x0 + x1) / 2 + 8, (y0 + y1) / 2 - 4, f"lead {s[1]} m", size=10, color=col, w=80)
                continue
            k += 1
            pid, frm = s[1], s[2]
            a, b, _ = PIPES[pid]
            to = b if frm == a else a
            (x0, y0), (x1, y1) = P2(ox, frm), P2(ox, to)
            dx, dy = (off, 0) if x0 == x1 else (0, off)
            d.line([(x0 + dx, y0 + dy), (x1 + dx, y1 + dy)], color=col, sw=7)
            verso = ("e" if x1 > x0 else "w") if y0 == y1 else ("s" if y1 > y0 else "n")
            d.triangle(x0 + (x1 - x0) * 0.62 + dx, y0 + (y1 - y0) * 0.62 + dy, verso, "#ffffff", s=5)
            d.circle(x0 + (x1 - x0) * 0.28 + dx, y0 + (y1 - y0) * 0.28 + dy, 9, col, stroke="#ffffff", text=str(k),
                     size=10)
        tubi, lead, fibra = lunghezze(route)
        n_fibra = f"{fibra:,.0f}".replace(",", ".")
        righe.append((col, f"fibra {f + 1}: {tubi:.0f} m di tubo, {lead:.0f} m di cavo → ~{n_fibra} m di fibra"))
    for n, (x, y) in XY.items():
        px, py = P2(ox, n)
        if n == "R1":
            d.square(px, py, 14, "#1971c2")
        else:
            d.circle(px, py, 6, "#2b8a3e" if n in DEMAND else "#495057")
        d.label(px - 9, py - 9, n, size=11, anchor="end", w=40)
    y = 665
    for col, r in righe:
        d.label(ox - 80, y, r, size=11.5, color=col, weight="bold", w=420)
        y += 20
    d.label(ox - 80, y + 6, nota.split("\n"), size=12, w=400)

d.label(40, 790, ["Lunghezza di fibra = 2 × cavi + tubi × 2,92 (elica a 70°) + giunzione 2 m + tubi × 1 (riferimento). "
                  "Nodi: quadrato blu = serbatoio R1 con l'interrogatore; verde = utenze (J13, J31, J33).",
                  "Gli interrogatori BOTDA commerciali leggono fibre da decine di km (Prysmian DITEST: 80 km per canale, "
                  "4 canali ad anello): qui la lunghezza non è un vincolo."], size=11.5, color="#495057", w=1340)
print("scritto", d.save(Path(__file__).with_name("scenario_paths.drawio.svg")))
