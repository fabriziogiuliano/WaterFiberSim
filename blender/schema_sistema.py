"""
WaterFiberSim - figura sintetica del sistema per il README (docs/img/sistema.png).

Versione ridotta di blender/tubo_fibra.png (che resta nel cap. 3): lo spaccato 3D con poche didascalie brevi e
la fibra "srotolata" con la relazione che separa pressione e temperatura. Numeri come in schema_sensore.py
(tubo PE DN110, elica a 70°; fonti in docs/A-fonti.md).

    python blender/schema_sistema.py
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
from schema_sensore import C_EPS, EPS_1BAR, INFO, RENDER  # noqa: E402

USCITA = QUI.parent / "docs" / "img" / "sistema.png"
TESTO, GRIGIO, ARANCIO, CHIARO, ROSSO = "#1b1f24", "#6b6f76", "#ff6a00", "#ffb37a", "#d40000"

VOCI = [  # chiave nel .json, spostamento del numero (pixel), titolo, testo
    ("interrogatore", (-10, -150), "Interrogatore BOTDA", "manda la luce nella fibra e legge la risposta"),
    ("cavo", (120, 130), "Cavi di collegamento", "nel terreno: sentono la temperatura del terreno"),
    ("elica", (-130, -160), "Fibra a elica nella guaina", "si allunga con il tubo: pressione + temperatura"),
    ("riferimento", (150, 190), "Fibra di ritorno nel tubicino", "libera, non viene tirata: solo temperatura"),
    ("giunzione", (-20, -130), "Giunzione", "andata e ritorno sono la stessa fibra"),
    ("acqua", (-150, 160), "Acqua in pressione", "dilata il tubo"),
]


def numero(ax, x, y, n, r=24):
    ax.add_patch(Circle((x, y), r, fc=TESTO, ec="white", lw=3, zorder=5))
    ax.text(x, y, str(n), color="white", ha="center", va="center", fontsize=17, fontweight="bold", zorder=6)


def main():
    img = plt.imread(RENDER)
    px = json.loads(INFO.read_text())["pixel"]
    x0, x1, y0, y1 = 90, 1720, 200, 800
    img = img[y0:y1, x0:x1]
    fig = plt.figure(figsize=(12, 11.2), dpi=110, facecolor="white")

    # --- spaccato con i numeri
    ax = fig.add_axes([0.0, 0.53, 1.0, 0.47])
    ax.imshow(img)
    ax.set_axis_off()
    for n, (k, (dx, dy), _, _) in enumerate(VOCI, 1):
        u, v = px[k][0] - x0, px[k][1] - y0
        ax.plot([u, u + dx], [v, v + dy], color=TESTO, lw=2, zorder=4)
        ax.plot(u, v, "o", ms=7, color=TESTO, zorder=4)
        numero(ax, u + dx, v + dy, n)

    # --- legenda su due colonne
    for n, (_, _, titolo, testo) in enumerate(VOCI, 1):
        col, rig = (n - 1) % 2, (n - 1) // 2
        x, y = 0.04 + col * 0.49, 0.515 - rig * 0.062
        fig.patches.append(Circle((x + 0.012, y - 0.011), 0.0125, transform=fig.transFigure, fc=TESTO, ec="none",
                                  figure=fig))
        fig.text(x + 0.012, y - 0.011, str(n), ha="center", va="center", color="white", fontsize=13,
                 fontweight="bold")
        fig.text(x + 0.035, y, titolo, fontsize=15, fontweight="bold", color=TESTO, va="top")
        fig.text(x + 0.035, y - 0.026, testo, fontsize=13.5, color=TESTO, va="top")

    # --- fibra srotolata
    fig.text(0.04, 0.31, "La fibra srotolata: ogni punto del tubo compare due volte nei dati", fontsize=16,
             fontweight="bold", color=TESTO, va="top")
    ax = fig.add_axes([0.04, 0.12, 0.92, 0.17])
    ax.set_xlim(0, 100)
    ax.set_ylim(-1.6, 2.2)
    ax.set_axis_off()
    tratti = [(0, 8, "#c4c8cf", "cavo", "terreno"), (8, 56, ARANCIO, "elica", "pressione + temperatura"),
              (56, 57, "#444", "", ""), (57, 92, CHIARO, "ritorno", "solo temperatura"),
              (92, 100, "#c4c8cf", "cavo", "terreno")]
    for a, b, c, nome, nota in tratti:
        ax.add_patch(Rectangle((a, 0), b - a, 0.8, fc=c, ec="white", lw=2))
        if nome:
            ax.text((a + b) / 2, 0.4, nome, ha="center", va="center", fontsize=14, fontweight="bold",
                    color="white" if c == ARANCIO else TESTO)
            ax.text((a + b) / 2, -0.15, nota, ha="center", va="top", fontsize=13, color=TESTO)
    ax.text(0, 1.0, "porta A", fontsize=13, fontweight="bold", va="bottom")
    ax.text(100, 1.0, "porta B", fontsize=13, fontweight="bold", va="bottom", ha="right")
    z1, z2 = 8 + 48 * 0.4, 57 + 35 * 0.6            # stesso punto del tubo (al 40 %) sull'elica e sul ritorno
    for z, lab in ((z1, "$z_1$"), (z2, "$z_2$")):
        ax.add_patch(FancyArrowPatch((z, 1.9), (z, 0.85), arrowstyle="-|>", mutation_scale=20, lw=2.2, color=ROSSO))
        ax.text(z + 1, 1.45, lab, color=ROSSO, fontsize=16, va="center")
    ax.annotate("", xy=(100, -1.2), xytext=(0, -1.2), arrowprops=dict(arrowstyle="->", lw=1.8, color=TESTO))
    ax.text(50, -1.3, "distanza lungo la fibra dalla porta A", ha="center", va="top", fontsize=13, color=GRIGIO)

    # --- relazione che separa pressione e temperatura
    fig.text(0.04, 0.095, r"ritorno ($z_2$):   $\Delta\nu_B = C_T\,\Delta T$   $\rightarrow$   $\Delta T$",
             fontsize=15, color=TESTO, va="top")
    fig.text(0.04, 0.055, r"elica ($z_1$):   $\Delta\nu_B = C_\varepsilon\,\varepsilon + K\,\Delta T$   "
             r"$\rightarrow$   $\varepsilon$   $\rightarrow$   pressione", fontsize=15, color=TESTO, va="top")
    c_eps = f"{C_EPS:.2f}".replace(".", "{,}")
    fig.text(0.04, 0.018, rf"$C_T \approx 1$ MHz/°C,  $C_\varepsilon \approx {c_eps}$ MHz/µε,  "
             r"$K \approx 3{,}5$–$8$ MHz/°C (da calibrare);  "
             rf"PE DN110, elica a 70°: 1 bar $\approx$ {EPS_1BAR * C_EPS:.0f} MHz", fontsize=12.5, color=GRIGIO,
             va="top")
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(USCITA, facecolor="white")
    print(f"scritto {USCITA}")


if __name__ == "__main__":
    main()
