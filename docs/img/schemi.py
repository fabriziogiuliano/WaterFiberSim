"""Schemi della documentazione (docs/), in .drawio.svg: posa della fibra (cap. 3) e catena del simulatore (cap. 8).

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
    # ritorno dritto nel tubetto
    d.box(x0 + 20, 280, x1 - x0 - 60, 20, [], fill="#dbe4ff", stroke=BLU, radius=10, sw=1.2)
    d.line([(x1 - 40, 290), (x0 + 20, 290)], color=BLU, sw=3.5)
    d.label(x0 + 40, 330, "RITORNO: fibra DRITTA, libera in un tubetto nella stessa guaina → sente solo TEMPERATURA",
            size=13, color=BLU, weight="bold", w=720)
    # verso della luce
    d.line([(x0 + 150, 455), (x0 + 330, 455)], color=ARANCIO, sw=2.5, arrow=True)
    d.label(x0 + 340, 460, "impulsi da A (verso in cui cresce la distanza z)", size=12, w=360)
    d.line([(x0 + 330, 485), (x0 + 150, 485)], color=BLU, sw=2.5, arrow=True)
    d.label(x0 + 340, 490, "luce di lettura continua da B, si legge in A", size=12, w=360)
    d.save(QUI / "posa_fibra.drawio.svg")


def catena():
    d = Drawing(1200, 1060, nome="catena del simulatore")
    d.label(30, 40, "La catena del simulatore: dall'acqua al dato grezzo", size=20, weight="bold", w=1100)
    W, X = 560, 60

    def blocco(y, titolo, testo, modulo, fill="#ffffff", stroke=NERO):
        d.box(X, y, W, 96, [titolo, *testo], fill=fill, stroke=stroke, size=13, align="left")
        d.label(X + W + 20, y + 52, modulo, size=13, color=GRIGIO, w=300)

    def freccia(y):
        d.line([(X + W / 2, y), (X + W / 2, y + 28)], color=NERO, sw=2, arrow=True)

    y = 80
    blocco(y, "1. Rete idraulica (EPANET)", ["pressione, carico, portate, velocità nei tubi, ogni 15 min"],
           "hydraulics.py · cap. 4"); freccia(y + 96); y += 124
    blocco(y, "2. Pressione lungo ogni tubo", ["lineare tra i due nodi, per ogni punto della fibra (mappa fibra → tubo)"],
           "simulate.py, fibermap.py · cap. 3"); freccia(y + 96); y += 124
    blocco(y, "3. Meccanica", ["Lamé a 1 o N strati (tubo ospite + guaina); elica: ε_θ sin²α + ε_z cos²α"],
           "mechanics.py · cap. 5"); freccia(y + 96); y += 124
    blocco(y, "4. Frequenza Brillouin vera ν_B(z, t)", ["ν_B0 + profilo a riposo + C_ε·ε + temperatura  →  etichette vere"],
           "brillouin.py, rest_profile.py · cap. 2, 3", fill="#fff4e6", stroke=ARANCIO); freccia(y + 96); y += 124
    blocco(y, "5. Strumento BOTDA", ["media su 2 m, un punto ogni 0,82 m, scansione a 1 MHz, rumore 1/SNR"],
           "instrument.py, measure.py · cap. 6"); freccia(y + 96); y += 124
    blocco(y, "6. Dato grezzo L0", ["uno spettro per punto e per misura + misura di base + etichette"],
           "raw_L0_<fibra>.npz", fill="#e7f5ff", stroke=BLU); freccia(y + 96); y += 124
    blocco(y, "7. Elaborazione di esempio", ["fit del picco, differenza dalla base, compensazione con il ritorno"],
           "compensation.py · cap. 7 (non è il compito del simulatore)", fill="#ebfbee", stroke=VERDE)
    # temperatura, a lato
    d.box(X + W + 20, 400, 340, 110, ["Temperatura", "terreno: stagione, punti caldi", "acqua: segue i consumi (Blokker)"],
          fill="#fff5f5", stroke="#c92a2a", size=13, align="left")
    d.label(X + W + 30, 530, "temperature.py · cap. 7", size=13, color=GRIGIO, w=300)
    d.line([(X + W + 20, 455), (X + W, 455), (X + W, 470), (X + W - 2, 470)], color="#c92a2a", sw=2, arrow=True)
    d.label(X, 1020, "Verifiche di ogni anello: `python -m waterfibersim validate` (cap. 10)", size=13, color=GRIGIO,
            w=900)
    d.save(QUI / "catena_simulatore.drawio.svg")


if __name__ == "__main__":
    posa_fibra()
    catena()
    print("scritti posa_fibra.drawio.svg e catena_simulatore.drawio.svg")
