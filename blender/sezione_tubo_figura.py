"""Didascalie sullo spaccato 3D del tubo (blender/sezione_tubo_3d.png + .json) -> docs/img/sezione_tubo.png.

    python blender/sezione_tubo_figura.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import textwrap

from matplotlib.patches import Circle, Ellipse

QUI = Path(__file__).resolve().parent
RENDER, INFO = QUI / "sezione_tubo_3d.png", QUI / "sezione_tubo_3d.json"
USCITA = QUI.parent / "docs" / "img" / "sezione_tubo.png"
TESTO, GRIGIO = "#1b1f24", "#5c636a"

VOCI = [
    ("ospite", (-120, 150), "Tubo ospite", "Il tubo esistente da risanare (per esempio in ghisa)."),
    ("guaina", (60, 170), "Guaina di risanamento", "Polimerizzata in opera dentro il tubo ospite; contiene la fibra."),
    ("elica", (-150, 150), "Fibra a elica (andata)", "Annegata nella guaina: si allunga quando la pressione dilata il tubo. "
                                                    "Sente pressione e temperatura."),
    ("tubicino", (-60, -170), "Tubicino con la fibra di riferimento (ritorno)",
     "Annegato nella guaina; la fibra dentro è libera e non viene tirata. Sente solo la temperatura."),
    ("acqua", (170, 120), "Acqua in pressione", "Spinge sulle pareti e dilata il tubo."),
]


def numero(ax, x, y, n, r=22):
    ax.add_patch(Circle((x, y), r, fc=TESTO, ec="white", lw=2.5, zorder=5))
    ax.text(x, y, str(n), color="white", ha="center", va="center", fontsize=15, fontweight="bold", zorder=6)


def main():
    img = plt.imread(RENDER)
    px = json.loads(INFO.read_text())["pixel"]
    fig = plt.figure(figsize=(20, 9), dpi=100, facecolor="white")
    ax = fig.add_axes([0.0, 0.04, 0.62, 0.86])
    ax.imshow(img)
    ax.set_axis_off()
    for n, (k, (dx, dy), _, _) in enumerate(VOCI, start=1):
        u, v = px[k]
        ax.plot([u, u + dx], [v, v + dy], color=TESTO, lw=1.6, zorder=4)
        ax.plot(u, v, "o", ms=6, color=TESTO, zorder=4)
        numero(ax, u + dx, v + dy, n)
    fig.text(0.02, 0.95, "Sezione del tubo risanato con il sensore in fibra ottica", fontsize=22, fontweight="bold",
             color=TESTO, va="top")
    y = 0.80
    W, H = fig.get_size_inches() * fig.dpi
    r = 17
    for n, (_, _, titolo, testo) in enumerate(VOCI, start=1):
        fig.patches.append(Ellipse((0.648, y - 0.013), 2 * r / W, 2 * r / H, transform=fig.transFigure, fc=TESTO,
                                   ec="none", figure=fig))
        fig.text(0.648, y - 0.013, str(n), ha="center", va="center", color="white", fontsize=13, fontweight="bold")
        fig.text(0.668, y, titolo, fontsize=15, fontweight="bold", color=TESTO, va="top")
        fig.text(0.668, y - 0.042, "\n".join(textwrap.wrap(testo, 58)), fontsize=12.5, color=TESTO, va="top",
                 linespacing=1.35)
        y -= 0.145
    fig.text(0.02, 0.03, "Spessori non in scala; gli strati sono accorciati e un quarto è tolto per mostrare l'interno.",
             fontsize=12, style="italic", color=GRIGIO)
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(USCITA, facecolor="white")
    print(f"scritto {USCITA}")


if __name__ == "__main__":
    main()
