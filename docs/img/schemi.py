"""Schemi della documentazione (docs/), in .drawio.svg: interrogatore BOTDA (cap. 2), posa della fibra (cap. 3) e
catena del simulatore (README e cap. 9).

    python docs/img/schemi.py
"""
from pathlib import Path

from drawio_svg import Drawing

QUI = Path(__file__).resolve().parent
NERO, GRIGIO, ARANCIO, BLU, VERDE = "#1b1f24", "#868e96", "#ff6a00", "#1f5fbf", "#2b8a3e"


def posa_fibra():
    d = Drawing(1300, 520, nome="posa della fibra")
    d.label(30, 40, "Una sola fibra: andata a elica, ritorno dritto, due capi sullo stesso strumento", size=20,
            weight="bold", w=1200)
    # cabina con interrogatore
    d.box(30, 120, 230, 230, [], fill="#f1f3f5", stroke=GRIGIO, dashed=True)
    d.label(45, 145, "cabina / pozzetto", size=13, color=GRIGIO, w=200)
    d.box(60, 170, 170, 150, ["Interrogatore", "BOTDA"], fill=NERO, stroke=NERO, color="#ffffff", size=15)
    d.circle(230, 205, 11, ARANCIO, text="A", size=11)
    d.circle(230, 285, 11, BLU, text="B", size=11)
    # tubo
    x0, x1, yt, yb = 430, 1150, 150, 340
    d.box(x0, yt, x1 - x0, yb - yt, [], fill="#e9ecef", stroke=GRIGIO, radius=20, sw=2)
    d.label(x1 - 260, yb + 22, "tubo con la guaina (vista di lato)", size=13, color=GRIGIO, w=260)
    # cavi (lead)
    d.line([(241, 205), (330, 205), (330, 200), (x0 + 20, 200)], color=GRIGIO, sw=5)
    d.line([(241, 285), (330, 285), (330, 290), (x0 + 20, 290)], color=GRIGIO, sw=5)
    d.label(285, 380, ["cavi di collegamento (lead)", "nel terreno: temperatura del terreno"], size=13,
            color=GRIGIO, anchor="middle", w=260)
    d.line([(300, 362), (300, 292)], color=GRIGIO, sw=1.2, arrow=True)
    # elica (andata): zig-zag sopra
    pts, x, su = [(x0 + 20, 200)], x0 + 20, True
    while x < x1 - 60:
        x += 34
        pts.append((x, 170 if su else 235))
        su = not su
    pts.append((x1 - 40, 200))
    d.line(pts, color=ARANCIO, sw=3.5)
    d.label(x0 + 40, 128, "ANDATA: fibra a ELICA annegata nella guaina → sente PRESSIONE + TEMPERATURA", size=13,
            color=ARANCIO, weight="bold", w=700)
    # giunzione
    d.line([(x1 - 40, 200), (x1 - 15, 200), (x1 - 15, 290), (x1 - 40, 290)], color=NERO, sw=3)
    d.circle(x1 - 15, 245, 9, NERO)
    d.label(x1 + 5, 250, "giunzione", size=13, w=120)
    # ritorno dritto nel tubicino
    d.box(x0 + 20, 280, x1 - x0 - 60, 20, [], fill="#dbe4ff", stroke=BLU, radius=10, sw=1.2)
    d.line([(x1 - 40, 290), (x0 + 20, 290)], color=BLU, sw=3.5)
    d.label(x0 + 40, 330, "RITORNO: fibra DRITTA, libera in un tubicino nella stessa guaina → sente solo TEMPERATURA",
            size=13, color=BLU, weight="bold", w=720)
    # verso della luce
    d.line([(x0 + 150, 455), (x0 + 330, 455)], color=ARANCIO, sw=2.5, arrow=True)
    d.label(x0 + 340, 460, "impulsi da A (verso in cui cresce la distanza z)", size=12, w=360)
    d.line([(x0 + 330, 485), (x0 + 150, 485)], color=BLU, sw=2.5, arrow=True)
    d.label(x0 + 340, 490, "luce di lettura continua da B, si legge in A", size=12, w=360)
    d.save(QUI / "posa_fibra.drawio.svg")


def catena():
    """Catena del simulatore: sei passi in colonna (testo grande, leggibile anche ridotto nel README)."""
    X, W, H, G, Y0 = 20, 640, 76, 30, 20
    passi = [
        ("Rete idraulica", "EPANET calcola la pressione nei tubi", "cap. 4", NERO, "#ffffff"),
        ("Posa della fibra", "ogni metro di fibra va su un tubo", "cap. 3", NERO, "#ffffff"),
        ("Meccanica", "la pressione allunga la fibra", "cap. 5", NERO, "#ffffff"),
        ("Effetto Brillouin", "allungamento e calore spostano la frequenza", "cap. 2", ARANCIO, "#fff4e6"),
        ("Strumento BOTDA", "misura gli spettri, con il rumore", "cap. 6", NERO, "#ffffff"),
        ("Dato grezzo + verità", "spettri con rumore ed etichette vere", "cap. 8", BLU, "#e7f5ff"),
    ]
    d = Drawing(980, Y0 + 6 * H + 5 * G + 20, nome="catena del simulatore")
    for k, (titolo, riga, cap, col, fill) in enumerate(passi):
        y = Y0 + k * (H + G)
        d.box(X, y, W, H, [], fill=fill, stroke=col, sw=2)
        d.circle(X + 40, y + H / 2, 20, col, text=str(k + 1), size=20)
        d.label(X + 76, y + 33, titolo, size=21, weight="bold", w=440)
        d.label(X + 76, y + 61, riga, size=18, color="#343a40", w=480)
        d.label(X + W - 16, y + 33, cap, size=16, color=GRIGIO, anchor="end", w=80)
        if k:
            d.line([(X + W / 2, y - G + 2), (X + W / 2, y - 4)], color=NERO, sw=2.5, arrow=True)
    # temperatura: entra nel passo 4
    y4 = Y0 + 3 * (H + G)
    d.box(720, y4 - 10, 240, H + 20, ["Temperatura", "di terreno e acqua"], fill="#fff5f5", stroke="#c92a2a",
          size=19, sw=2)
    d.line([(718, y4 + H / 2), (X + W + 4, y4 + H / 2)], color="#c92a2a", sw=2.5, arrow=True)
    # elaborazione: uscita del passo 6, lavoro di chi usa il simulatore
    y6 = Y0 + 5 * (H + G)
    d.box(720, y6 - 10, 240, H + 20, ["Elaborazione", "dei dati (utente)"], fill="#ebfbee", stroke=VERDE, size=19,
          sw=2, dashed=True)
    d.line([(X + W + 2, y6 + H / 2), (716, y6 + H / 2)], color=VERDE, sw=2.5, arrow=True)
    d.save(QUI / "catena_simulatore.drawio.svg")


def interrogatore():
    """Schema a blocchi dell'interrogatore BOTDA ad anello, ridisegnato da Bertulessi et al. 2023, Fig. 2."""
    d = Drawing(1450, 640, nome="interrogatore BOTDA")
    d.label(30, 36, "Interrogatore BOTDA con fibra ad anello (da Bertulessi et al. 2023, Fig. 2)", size=18,
            weight="bold", w=1200)
    d.box(20, 60, 890, 520, [], fill="#f8f9fa", stroke=GRIGIO, dashed=True)
    d.label(36, 84, "interrogatore", size=13, color=GRIGIO, w=200)
    az, ar = "#e7f0ff", "#fff1e6"
    # sorgente
    d.box(40, 270, 150, 60, ["Laser DFB", "1530 nm"], fill="#ffffff")
    d.box(230, 270, 120, 60, ["Accoppiatore", "3 dB"], fill="#ffffff")
    d.line([(190, 300), (228, 300)], color=NERO, arrow=True)
    # ramo della luce di lettura (sonda)
    d.box(390, 70, 140, 40, ["Generatore RF"], fill=az, stroke=BLU)
    d.box(390, 130, 140, 60, ["Modulatore", "Mach-Zehnder"], fill=az, stroke=BLU)
    d.box(560, 130, 140, 60, ["Depolarizzatore"], fill=az, stroke=BLU)
    d.box(730, 130, 120, 60, ["Circolatore", "C1"], fill=az, stroke=BLU)
    d.line([(290, 270), (290, 160), (388, 160)], color=BLU, arrow=True)
    d.line([(460, 110), (460, 128)], color=BLU, arrow=True)
    d.line([(530, 160), (558, 160)], color=BLU, arrow=True)
    d.line([(700, 160), (728, 160)], color=BLU, arrow=True)
    d.line([(850, 160), (868, 160)], color=BLU, arrow=True)
    d.circle(882, 160, 14, BLU, text="B", size=13)
    # ramo degli impulsi (pompa)
    d.box(390, 318, 140, 40, ["Generatore impulsi"], fill=ar, stroke=ARANCIO)
    d.box(390, 380, 140, 60, ["Modulatore", "Mach-Zehnder"], fill=ar, stroke=ARANCIO)
    d.box(560, 380, 140, 60, ["Amplificatore", "EDFA"], fill=ar, stroke=ARANCIO)
    d.box(730, 380, 120, 60, ["Circolatore", "C2"], fill=ar, stroke=ARANCIO)
    d.line([(290, 330), (290, 410), (388, 410)], color=ARANCIO, arrow=True)
    d.line([(460, 358), (460, 378)], color=ARANCIO, arrow=True)
    d.line([(530, 410), (558, 410)], color=ARANCIO, arrow=True)
    d.line([(700, 410), (728, 410)], color=ARANCIO, arrow=True)
    d.line([(850, 410), (868, 410)], color=ARANCIO, arrow=True)
    d.circle(882, 410, 14, ARANCIO, text="A", size=13)
    # ricezione
    d.box(730, 490, 120, 54, ["Fotodiodo"], fill="#ebfbee", stroke=VERDE)
    d.box(560, 490, 140, 54, ["ADC"], fill="#ebfbee", stroke=VERDE)
    d.box(330, 490, 200, 54, ["Elaborazione"], fill="#ebfbee", stroke=VERDE)
    d.line([(790, 440), (790, 488)], color=VERDE, arrow=True)
    d.line([(730, 517), (702, 517)], color=VERDE, arrow=True)
    d.line([(560, 517), (532, 517)], color=VERDE, arrow=True)
    # fibra ad anello sul tubo
    x0, x1 = 1000, 1320
    d.box(x0 - 20, 225, x1 - x0 + 40, 110, [], fill="#e9ecef", stroke=GRIGIO, radius=16)
    d.label(x0 - 20, 360, "tubo", size=13, color=GRIGIO, w=100)
    d.line([(896, 410), (950, 410), (950, 305), (x0, 305)], color=NERO, sw=3)
    pts, x, su = [(x0, 305)], x0, False
    while x < x1 - 30:
        x += 26
        pts.append((x, 268 if su else 322))
        su = not su
    pts.append((x1, 305))
    d.line(pts, color=ARANCIO, sw=3)
    d.line([(x1, 305), (x1 + 15, 305), (x1 + 15, 245), (x1, 245)], color=NERO, sw=3)
    d.circle(x1 + 15, 275, 7, NERO)
    d.label(x1 + 28, 280, "giunzione", size=12, w=100)
    d.line([(x1, 245), (x0, 245)], color=BLU, sw=3)
    d.line([(x0, 245), (950, 245), (950, 160), (896, 160)], color=NERO, sw=3)
    d.label(1160, 215, "ritorno, dritto nel tubicino", size=12, color=BLU, anchor="middle", w=260)
    d.label(1160, 350, "andata, a elica", size=12, color=ARANCIO, anchor="middle", w=200)
    # versi delle due luci: frecce vere, nei due tratti
    d.line([(1040, 200), (1110, 200)], color=BLU, sw=2.5, arrow=True)          # sonda: da B verso la giunzione
    d.line([(1280, 200), (1210, 200)], color=ARANCIO, sw=2.5, arrow=True)      # impulsi: dalla giunzione verso B
    d.line([(1040, 372), (1110, 372)], color=ARANCIO, sw=2.5, arrow=True)      # impulsi: da A verso la giunzione
    d.line([(1280, 372), (1210, 372)], color=BLU, sw=2.5, arrow=True)          # sonda: dalla giunzione verso A
    # legenda
    d.line([(960, 470), (1010, 470)], color=ARANCIO, sw=2.5, arrow=True)
    d.label(1020, 475, "impulsi (pompa): da A, percorrono l'anello", size=12, w=360)
    d.line([(960, 500), (1010, 500)], color=BLU, sw=2.5, arrow=True)
    d.label(1020, 505, "luce di lettura (sonda): da B, si legge in A", size=12, w=360)
    d.line([(960, 530), (1010, 530)], color=VERDE, sw=2.5, arrow=True)
    d.label(1020, 535, "lettura: fotodiodo, ADC, elaborazione", size=12, w=360)
    d.save(QUI / "dfos-interrogatore.drawio.svg")


if __name__ == "__main__":
    interrogatore()
    posa_fibra()
    catena()
    print("scritti dfos-interrogatore.drawio.svg, posa_fibra.drawio.svg e catena_simulatore.drawio.svg")
