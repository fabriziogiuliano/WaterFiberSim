"""
WaterFiberSim - figura esplicativa del sensore (blender/tubo_fibra.png).

Prende lo spaccato 3D renderizzato da tubo_fibra.py (tubo_fibra_3d.png + .json con le
posizioni dei punti notevoli) e aggiunge:
  1. didascalie numerate sullo spaccato;
  2. il fenomeno fisico (effetto Brillouin) spiegato senza prerequisiti;
  3. la fibra "srotolata": cosa riceve chi elabora i dati e come si separano
     temperatura e allungamento (e quindi pressione).

Uso (serve solo matplotlib, non Blender):
  python blender/schema_sensore.py
I numeri sono indicativi (tubo PE DN110, elica a 70°): servono a dare gli ordini di grandezza.
"""
import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle

QUI = Path(__file__).parent
RENDER, INFO, USCITA = QUI / "tubo_fibra_3d.png", QUI / "tubo_fibra_3d.json", QUI / "tubo_fibra.png"

ARANCIO, ROSSO, GRIGIO, BLU = "#ff6a00", "#d40000", "#6b6f76", "#1f5fbf"
TESTO = "#1b1f24"

# ---- numeri dell'esempio (indicativi) ----------------------------------------
ALFA = 70
K = 1 / np.cos(np.radians(ALFA))          # m di fibra per m di tubo (2,92)
L_TUBO, CAVO = 100.0, 15.0                # tubo da 100 m, cavi di collegamento da 15 m
GIUNTO = 2.0
Z_ELICA0 = CAVO
Z_ELICA1 = Z_ELICA0 + L_TUBO * K
Z_RIT0 = Z_ELICA1 + GIUNTO
Z_RIT1 = Z_RIT0 + L_TUBO
Z_FINE = Z_RIT1 + CAVO
X_P = 40.0                                # punto del tubo dell'esempio
Z1 = Z_ELICA0 + X_P * K                   # lo stesso punto sull'elica...
Z2 = Z_RIT0 + (L_TUBO - X_P)              # ...e sul ritorno (percorso al contrario)
# Fonti: vedi docs/A-fonti.md. Coefficienti e parametri del PE da Bertulessi et al., Sensors 23, 6205 (2023).
C_EPS, C_T = 0.05, 1.0                    # MHz/µε, MHz/°C (fibra standard; Bertulessi 2023, Eq. 1)
E_PE, NU_PE = 1050.0, 0.4                 # MPa, - (Bertulessi 2023, Tab. 2)
DE_MM, SP_MM = 110.0, 10.0                # tubo dell'esempio: PE DN110, spessore 10 mm
BETA = (DE_MM / 2 - SP_MM) / (DE_MM / 2)  # raggio interno / esterno
P_1BAR = 0.1                              # MPa
# deformazioni sulla superficie esterna, tubo a fondi chiusi (Lamé; Bertulessi 2023, Eq. 4-6 per ε_θ)
EPS_THETA = (2 - NU_PE) * BETA**2 / (1 - BETA**2) * P_1BAR / E_PE * 1e6     # µε
EPS_Z = (1 - 2 * NU_PE) * BETA**2 / (1 - BETA**2) * P_1BAR / E_PE * 1e6     # µε
S2 = np.sin(np.radians(ALFA)) ** 2
EPS_1BAR = EPS_THETA * S2 + EPS_Z * (1 - S2)  # µε sentiti dall'elica per 1 bar
K_T_ELICA = 6.0                           # MHz/°C sull'elica: forbice 3,5-8 dalle fonti, DA CALIBRARE (docs/A-fonti.md)


def box(ax, x, y, w, h, colore="#f4f6f9", bordo="#c9ced6"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.012",
                                transform=ax.transAxes, fc=colore, ec=bordo, lw=1.2, zorder=0))


ALTEZZA_IN = 25                              # altezza della figura in pollici


def riga(fs):
    """Altezza di una riga di testo (font `fs` pt) in coordinate di figura."""
    return fs * 1.45 / 72 / ALTEZZA_IN


def paragrafo(fig, x, y, n, titolo, testo, larghezza, colore_n=TESTO, fs=13.5, stacco=0.9):
    """Numero tondo + titolo in grassetto + testo a capo dopo `larghezza` caratteri. Ritorna la y successiva."""
    # cerchio disegnato come forma (raggio fisso in pixel), numero centrato: stessa misura per 1 o 2 cifre
    r_px = 17
    W, H = fig.get_size_inches() * fig.dpi
    w, h = 2 * r_px / W, 2 * r_px / H
    cx, cy = x + w / 2, y - h / 2 + 0.002
    fig.patches.append(Ellipse((cx, cy), w, h, transform=fig.transFigure, fc=colore_n, ec="none", figure=fig))
    fig.text(cx, cy, str(n), fontsize=14 if n < 10 else 12, fontweight="bold", color="white", ha="center",
             va="center")
    fig.text(x + 0.03, y, titolo, fontsize=fs + 2, fontweight="bold", va="top", color=TESTO)
    y -= riga(fs + 2) * 1.15
    righe = []
    for blocco in testo.split("\n"):
        righe += textwrap.wrap(blocco, larghezza) or [""]
    fig.text(x + 0.03, y, "\n".join(righe), fontsize=fs, va="top", color=TESTO, linespacing=1.35)
    return y - riga(fs) * 0.95 * len(righe) - riga(fs) * stacco


def numero(ax, x, y, n, r=17, colore=TESTO):
    ax.add_patch(Circle((x, y), r, fc=colore, ec="white", lw=2.5, zorder=5))
    ax.text(x, y, str(n), color="white", ha="center", va="center", fontsize=15 if n < 10 else 11.5,
            fontweight="bold", zorder=6)


def main():
    info = json.loads(INFO.read_text())
    img = plt.imread(RENDER)
    x0, x1, y0, y1 = 90, 1720, 250, 760           # ritaglio dello spaccato (pixel)
    img = img[y0:y1, x0:x1]
    px = {k: (u - x0, v - y0) for k, (u, v) in info["pixel"].items()}

    fig = plt.figure(figsize=(24, ALTEZZA_IN), dpi=100, facecolor="white")
    fig.text(0.5, 0.985, "Il sensore in fibra ottica sul tubo: UNA sola fibra che va e torna allo stesso strumento",
             ha="center", va="top", fontsize=27, fontweight="bold", color=TESTO)
    fig.text(0.5, 0.966, "misura distribuita di tipo BOTDA (Brillouin)  ·  spessori e fibra esagerati per vederli",
             ha="center", va="top", fontsize=17, color=GRIGIO)

    # ================= 1. spaccato con didascalie =================================
    ax = fig.add_axes([0.01, 0.635, 0.60, 0.32])
    ax.imshow(img)
    ax.set_axis_off()
    # posizione del numero (spostata dal punto, per non coprire il disegno) -> punto indicato
    etichette = [
        (1, "interrogatore", (-10, -150)),
        (2, "porta_A", (70, -120)),
        (3, "porta_B", (90, 75)),
        (4, "elica", (-130, -160)),
        (5, "riferimento", (150, 190)),
        (6, "giunzione", (-20, -130)),
        (7, "acqua", (-150, 160)),
        (8, "guaina", (10, -190)),
        (9, "ospite", (120, -140)),
        (10, "cavo", (120, 130)),
    ]
    for n, k, (dx, dy) in etichette:
        (u, v) = px[k]
        ax.plot([u, u + dx], [v, v + dy], color=TESTO, lw=1.6, zorder=4)
        ax.plot(u, v, "o", ms=6, color=TESTO, zorder=4)
        numero(ax, u + dx, v + dy, n)

    # legenda numerata
    voci = [
        (1, "Interrogatore (BOTDA)", "Lo strumento di misura. Contiene sia i TRASMETTITORI (laser) sia il "
                                     "RICEVITORE. I DUE capi della fibra arrivano qui: la fibra è un anello."),
        (2, "Porta A  =  inizio della fibra (z = 0)  →  QUI SI LEGGE",
         "ESCONO gli impulsi di interrogazione (\"pompa\": 20 ns, forti). RIENTRA la luce di lettura, dopo aver "
         "fatto tutto l'anello: lo strumento la manda al ricevitore."),
        (3, "Porta B  =  fine della fibra",
         "ESCE la luce di lettura (\"sonda\"): un tono ottico continuo e debole, che percorre l'anello al contrario "
         "fino ad A. Gli impulsi che arrivano in B non si leggono."),
        (4, "Tratto a ELICA, annegato nella guaina", "Gira intorno al tubo (70° rispetto all'asse). La guaina "
                                                   "polimerizza in opera e ancora la fibra: quando la pressione "
                                                   "dilata il tubo, la fibra viene tirata.\n"
                                                    "Sente: PRESSIONE + TEMPERATURA."),
        (5, "Tratto DRITTO, libero in un tubicino", "Il tubicino è annegato nella guaina, ma la fibra dentro scorre libera, come un filo in una "
                                                 "cannuccia: il tubo si dilata ma lei non viene tirata.\nSente: SOLO TEMPERATURA."),
        (6, "Giunzione", "Qui il tratto a elica e il tratto dritto sono saldati: è la STESSA fibra che torna "
                         "indietro."),
        (7, "Acqua in pressione", "Spinge sulle pareti (frecce rosse) e le dilata pochissimo: in PE circa "
                                  f"{EPS_THETA / 1e4:.2f}\u00a0% per bar (DN110).".replace(".", ",", 1)),
        (8, "Guaina in composito (relining)", "Lo strato che contiene la fibra."),
        (9, "Tubo ospite", "Il tubo esistente, tagliato per vedere dentro."),
        (10, "Cavi di collegamento", "La stessa fibra, protetta in un cavo, dall'interrogatore all'inizio del tubo e "
                                     "ritorno (nello scenario: `lead`). Sta nel terreno, non sul tubo: sente solo la "
                                     "temperatura del terreno."),
    ]
    y = 0.955
    for n, titolo, testo in voci:
        y = paragrafo(fig, 0.625, y, n, titolo, testo, 84, fs=11.5, stacco=0.3)
    fig.text(0.03, 0.672, "Frecce arancioni sulla fibra: verso in cui cresce la distanza z, contata dalla porta A, dove "
             "si legge.\nGli impulsi viaggiano in questo verso, la luce di lettura nel verso opposto.   "
             "La fibra è di un solo colore perché è UNA sola.",
             fontsize=13, style="italic", va="top", color=GRIGIO, linespacing=1.35)

    # ================= 2. il fenomeno fisico ======================================
    fig.text(0.02, 0.617, "Il fenomeno fisico: la fibra \"suona\" come una corda di chitarra (effetto Brillouin)",
             fontsize=22, fontweight="bold", color=TESTO, va="top")
    passi = [
        ("Nel vetro ci sono onde sonore.",
         "Il vetro della fibra vibra continuamente con onde sonore minuscole, che hanno una \"nota\" propria: "
         "circa 10,8 GHz (miliardi di vibrazioni al secondo)."),
        ("La luce torna indietro con la frequenza spostata di quella nota.",
         "La luce laser che incontra queste onde viene in piccola parte rimandata indietro, con la frequenza "
         "spostata esattamente della nota. Lo spostamento si chiama frequenza Brillouin, ν_B."),
        ("La nota cambia con allungamento e temperatura.",
         "Come una corda di chitarra: se la tiri, la nota sale; anche il calore la cambia.\n"
         "Δν_B  =  0,05 MHz × (allungamento in µε)  +  1 MHz × (ΔT in °C)        "
         "[1 µε = 1 micrometro di allungamento per metro]"),
        ("La BOTDA \"ascolta\" la nota in ogni punto.",
         "Gli impulsi di interrogazione (pompa, dalla porta A) e la luce di lettura continua (sonda, dalla porta B) "
         "si incrociano in ogni punto della fibra. Dove la differenza tra le loro frequenze (Δν) è uguale "
         "alla nota del punto, l'impulso cede energia alla luce di lettura: alla porta A arriva un gradino di luce "
         "in più. Lo strumento ripete la misura con tanti Δν (per esempio da 10,75 a 10,95 GHz) e, per "
         "ogni punto, guarda quanto è alto il gradino: ottiene la curva qui a destra."),
        ("Il punto lo dice il tempo.",
         "La luce nella fibra fa circa 1 m ogni 5 ns: dal ritardo tra la partenza dell'impulso e l'arrivo del "
         "gradino alla porta A, lo strumento sa in quale metro di fibra è nato (10 ns = 1 m, perché la luce fa "
         "andata e ritorno). Così ogni metro di fibra è un sensore."),
    ]
    y = 0.598
    for i, (titolo, testo) in enumerate(passi, 1):
        y = paragrafo(fig, 0.02, y, i, titolo, testo, 100, colore_n=BLU)

    # spettro Brillouin di un punto
    ax = fig.add_axes([0.645, 0.39, 0.33, 0.18])
    f = np.linspace(10.75, 10.95, 600)
    nu0, larghezza = 10.840, 0.030                       # GHz
    lor = lambda nu: 1 / (1 + ((f - nu) / (larghezza / 2)) ** 2)
    rng = np.random.default_rng(3)
    shift = EPS_1BAR * C_EPS / 1000                       # GHz
    ax.plot(f, lor(nu0), color=GRIGIO, lw=2.5, label="tubo a riposo")
    ax.plot(f, lor(nu0 + shift) + rng.normal(0, 0.03, f.size), color=ARANCIO, lw=1.2, alpha=0.8,
            label="+1 bar: misura con rumore")
    ax.plot(f, lor(nu0 + shift), color=ARANCIO, lw=2.5)
    ax.annotate("", xy=(nu0 + shift, 1.08), xytext=(nu0, 1.08),
                arrowprops=dict(arrowstyle="->", lw=2.5, color=ROSSO))
    ax.text(nu0 + shift / 2, 1.13, f"+{shift * 1000:.0f} MHz", color=ROSSO, ha="center", fontsize=14, fontweight="bold")
    ax.set_xlabel("\u0394\u03bd = differenza di frequenza tra impulso e luce di lettura [GHz]", fontsize=13)
    ax.set_ylabel("altezza del gradino letto in A", fontsize=12)
    ax.set_ylim(-0.1, 1.3)
    ax.set_yticks([])
    ax.legend(fontsize=12, loc="upper left", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Cosa misura lo strumento in UN punto della fibra", fontsize=15, fontweight="bold", color=TESTO)
    fig.text(0.645, 0.357,
             "La curva intera è il dato GREZZO (L0). La posizione del picco è ν_B (L1).\n"
             f"1 bar dilata il tubo in PE → l'elica si allunga di ~{EPS_1BAR:.0f} µε → il picco si sposta di ~{EPS_1BAR * C_EPS:.0f} MHz.",
             fontsize=13, color=TESTO, va="top", linespacing=1.4)

    # ================= 3. la fibra srotolata ========================================
    fig.text(0.02, 0.325, "Cosa riceve chi elabora i dati: la fibra \"srotolata\"",
             fontsize=22, fontweight="bold", color=TESTO, va="top")
    fig.text(0.02, 0.303, "Esempio: un tubo da 100 m, cavi da 15 m.  Lo strumento dà una curva come quella sopra "
             "per OGNI metro di fibra, a ogni misura (ogni pochi minuti).", fontsize=14.5, color=TESTO, va="top")
    ax = fig.add_axes([0.04, 0.12, 0.92, 0.165])
    ax.set_xlim(-12, Z_FINE + 12)
    ax.set_ylim(-3.3, 3.6)
    ax.set_axis_off()

    # il tubo (in alto, in metri di tubo, disegnato sotto i due tratti che lo coprono)
    def tubo_su(z_a, z_b, verso):
        ax.add_patch(Rectangle((z_a, 2.2), z_b - z_a, 0.55, fc="#d9dce1", ec=GRIGIO, lw=1.2))
        a, b = ("inizio tubo (0 m)", "fine tubo (100 m)") if verso > 0 else ("fine tubo (100 m)", "inizio tubo (0 m)")
        ax.text(z_a + 2, 2.47, a, fontsize=12, ha="left", va="center", color=GRIGIO)
        ax.text(z_b - 2, 2.47, b, fontsize=12, ha="right", va="center", color=GRIGIO)
    tubo_su(Z_ELICA0, Z_ELICA1, +1)
    tubo_su(Z_RIT0, Z_RIT1, -1)

    # i tratti della fibra
    tratti = [
        (0, CAVO, "#b9bec6", "cavo", ""),
        (Z_ELICA0, Z_ELICA1, ARANCIO, "tratto a ELICA sul tubo", "sente PRESSIONE + TEMPERATURA\n(100 m di tubo = 292 m di fibra)"),
        (Z_ELICA1, Z_RIT0, "#444", "", ""),
        (Z_RIT0, Z_RIT1, "#ffb37a", "tratto DRITTO nel tubicino", "sente SOLO TEMPERATURA\n(percorre il tubo al contrario)"),
        (Z_RIT1, Z_FINE, "#b9bec6", "cavo", ""),
    ]
    for a, b, c, nome, nota in tratti:
        ax.add_patch(Rectangle((a, 0), b - a, 1.0, fc=c, ec="white", lw=1.5))
        if nome:
            ax.text((a + b) / 2, 0.5, nome, ha="center", va="center", fontsize=13.5, fontweight="bold",
                    color="white" if c == ARANCIO else TESTO)
        if nota:
            ax.text((a + b) / 2, -0.25, nota, ha="center", va="top", fontsize=12.5, color=TESTO, linespacing=1.3)
    ax.annotate("giunzione", xy=((Z_ELICA1 + Z_RIT0) / 2, 1.0), xytext=((Z_ELICA1 + Z_RIT0) / 2, 1.75),
                ha="center", fontsize=12, arrowprops=dict(arrowstyle="->", color=TESTO))
    ax.text(0, -0.25, "porta A\nz = 0", ha="left", va="top", fontsize=12.5, fontweight="bold")
    ax.text(Z_FINE, -0.25, f"porta B\nz = {Z_FINE:.0f} m", ha="right", va="top", fontsize=12.5, fontweight="bold")
    ax.annotate("", xy=(Z_FINE, -2.05), xytext=(0, -2.05), arrowprops=dict(arrowstyle="->", lw=2, color=TESTO))
    ax.text(Z_FINE / 2, -2.25, "z = distanza lungo la fibra dalla porta A [m]  (asse dei dati)",
            ha="center", va="top", fontsize=13.5)

    # lo stesso punto del tubo compare due volte
    for z, testo in ((Z1, f"z₁ ≈ {Z1:.0f} m"), (Z2, f"z₂ ≈ {Z2:.0f} m")):
        ax.add_patch(FancyArrowPatch((z, 2.2), (z, 1.05), arrowstyle="-|>", mutation_scale=18, lw=2, color=ROSSO))
        ax.plot(z, 2.47, "o", ms=11, color=ROSSO)
        ax.text(z + 3, 1.6, testo, color=ROSSO, fontsize=14, fontweight="bold", va="center")
    ax.text((Z1 + Z2) / 2, 3.5, f"lo STESSO punto del tubo (a {X_P:.0f} m dall'inizio) compare DUE volte nei dati",
            ha="center", va="top", fontsize=14.5, fontweight="bold", color=ROSSO)

    # il conto
    box(fig.add_axes([0.02, 0.005, 0.96, 0.1]), 0, 0, 1, 1)
    fig.axes[-1].set_axis_off()
    righe = [
        ("Esempio: in quel punto la pressione sale di 1 bar e la temperatura di 1 °C.", True),
        (f"a z₂ (tratto dritto, solo temperatura): lo strumento vede +1 MHz   →   ΔT = 1 MHz / (1 MHz per °C) = 1 °C",
         False),
        (f"a z₁ (elica, pressione + temperatura): lo strumento vede +{EPS_1BAR * C_EPS + K_T_ELICA:.0f} MHz   →   "
         f"tolgo la parte della temperatura (1 °C × {K_T_ELICA:.0f} MHz per °C sull'elica*) = "
         f"{EPS_1BAR * C_EPS:.0f} MHz   →   {EPS_1BAR:.0f} µε   →   ≈ 1 bar", False),
        (f"* sull'elica il calore pesa di più: la fibra è solidale al PE, che col caldo si dilata e la tira. Secondo le fonti "
         f"tra circa 3,5 e 8 MHz/°C (qui {K_T_ELICA:.0f}): va calibrato in opera. Il simulatore fornisce anche i valori VERI "
         "di pressione, temperatura e allungamento.", False),
        ("Fonti: Bertulessi et al., Sensors 23, 6205 (2023), doi:10.3390/s23136205;  Stewart & Bilgin, PPI (2020);  schede tecniche OZ Optics "
         "DTS0115 e Prysmian DITEST.  Elenco completo e stato di verifica: docs/A-fonti.md", False),
    ]
    y = 0.1
    for testo, grassetto in righe:
        nota = testo.startswith(("*", "Fonti"))
        fig.text(0.035, y, testo, fontsize=12.5 if nota else 14, va="top", color=GRIGIO if testo.startswith("Fonti") else TESTO,
                 fontweight="bold" if grassetto else "normal", style="italic" if nota else "normal")
        y -= 0.019

    fig.savefig(USCITA, dpi=100, facecolor="white")
    print(f"scritto {USCITA}")


if __name__ == "__main__":
    main()
