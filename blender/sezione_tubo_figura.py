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
    # ritaglio sul tubo (sfondo trasparente) più il margine per i numeri delle didascalie
    import numpy as np
    ys, xs = np.nonzero(img[:, :, 3] > 0.02)
    pts = [(u + dx, v + dy) for k, (dx, dy), _, _ in VOCI for u, v in [px[k]]]
    m = 40
    x0 = int(max(0, min(xs.min(), min(p[0] for p in pts)) - m))
    x1 = int(min(img.shape[1], max(xs.max(), max(p[0] for p in pts)) + m))
    y0 = int(max(0, min(ys.min(), min(p[1] for p in pts)) - m))
    y1 = int(min(img.shape[0], max(ys.max(), max(p[1] for p in pts)) + m))
    crop = img[y0:y1, x0:x1]
    h_in = 6.0
    w_img = h_in * crop.shape[1] / crop.shape[0]
    w_leg = 6.2
    fig = plt.figure(figsize=(w_img + w_leg, h_in), dpi=110, facecolor="white")
    ax = fig.add_axes([0.0, 0.0, w_img / (w_img + w_leg), 1.0])
    ax.imshow(crop)
    ax.set_axis_off()
    for n, (k, (dx, dy), _, _) in enumerate(VOCI, start=1):
        u, v = px[k][0] - x0, px[k][1] - y0
        ax.plot([u, u + dx], [v, v + dy], color=TESTO, lw=1.6, zorder=4)
        ax.plot(u, v, "o", ms=6, color=TESTO, zorder=4)
        numero(ax, u + dx, v + dy, n)
    W, H = fig.get_size_inches() * fig.dpi
    xl = w_img / (w_img + w_leg) + 0.015
    r = 15
    y = 0.93
    for n, (_, _, titolo, testo) in enumerate(VOCI, start=1):
        fig.patches.append(Ellipse((xl + r / W, y - 0.02), 2 * r / W, 2 * r / H, transform=fig.transFigure, fc=TESTO,
                                   ec="none", figure=fig))
        fig.text(xl + r / W, y - 0.02, str(n), ha="center", va="center", color="white", fontsize=12, fontweight="bold")
        fig.text(xl + 3 * r / W, y, titolo, fontsize=13, fontweight="bold", color=TESTO, va="top")
        righe = textwrap.wrap(testo, 52)
        fig.text(xl + 3 * r / W, y - 0.055, "\n".join(righe), fontsize=11, color=TESTO, va="top", linespacing=1.3)
        y -= 0.075 + 0.05 * len(righe) + 0.04
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(USCITA, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    print(f"scritto {USCITA}")


if __name__ == "__main__":
    main()
