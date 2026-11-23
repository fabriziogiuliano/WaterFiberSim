"""
Disegno esplicativo: perché ogni metro di fibra ha una sua frequenza "a riposo" e perché serve la misura di base.

I profili imitano Bertulessi et al., Sensors 23, 6205 (2023), Fig. 7a (tubo PN16, 0 e 5 bar).
I valori sono letti A OCCHIO dal grafico: servono a dare forma e ordini di grandezza, non sono dati.
Uso:  python docs/img/frequenza_a_riposo.py   ->  docs/img/frequenza-a-riposo.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ARANCIO, BLU, GRIGIO, ROSSO, VERDE, TESTO = "#ff6a00", "#1f5fbf", "#6b6f76", "#c92a2a", "#2b8a3e", "#1b1f24"
z = np.linspace(0, 22, 1101)
EL0, EL1 = 4.6, 12.3            # tratto a elica (Fig. 7a: circa 4-12,5 m)
LI0, LI1 = 18.0, 20.0           # tratto libero per la temperatura (Fig. 7a: 18-20 m)
BASE = 10880.0                  # MHz, fibra non tirata (Fig. 7a, fuori dall'elica)

rng = np.random.default_rng(7)
piccole = np.convolve(rng.normal(0, 1.2, z.size), np.ones(15) / 15, mode="same")   # piccole differenze tra metri


def sul(a, b, larghezza=0.4):
    """1 dentro [a, b], 0 fuori, con bordi morbidi (la risoluzione dello strumento è ~1-2 m)."""
    return 1 / (1 + np.exp(-(z - a) / larghezza * 4)) * 1 / (1 + np.exp((z - b) / larghezza * 4))


# a riposo: fibra tirata dalla posa sull'elica (non uniforme: da ~+180 a ~+105 MHz), un po' anche sul tratto libero
pre_elica = sul(EL0, EL1) * np.interp(z, [EL0, EL1], [180, 105])
pre_libero = sul(LI0, LI1) * 65
riposo = BASE + pre_elica + pre_libero + piccole
pressione = sul(EL0, EL1) * 73                    # 5 bar: +73 MHz sull'elica (Bertulessi 2023, §3.1)
cinque_bar = riposo + pressione + np.convolve(rng.normal(0, 1.2, z.size), np.ones(15) / 15, mode="same")

fig, axs = plt.subplots(3, 1, figsize=(16.5, 15.5), dpi=100, sharex=True,
                        gridspec_kw=dict(hspace=0.55, top=0.9, bottom=0.14, left=0.08, right=0.66))
fig.suptitle("Perché ogni metro di fibra ha una sua frequenza \"a riposo\" e serve la misura di base",
             fontsize=19, fontweight="bold", color=TESTO, x=0.05, ha="left")
fig.text(0.05, 0.935, "Forme e valori imitano un esperimento reale: Bertulessi et al., Sensors 23, 6205 (2023), "
         "Fig. 7a (tubo PN16), letti a occhio dal grafico.", fontsize=12.5, color=GRIGIO)


def sfondo(ax):
    ax.axvspan(EL0, EL1, color=ARANCIO, alpha=0.09, lw=0)
    ax.axvspan(LI0, LI1, color=BLU, alpha=0.09, lw=0)
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=11.5)


# 1. a riposo
ax = axs[0]
sfondo(ax)
ax.axhline(BASE, color=GRIGIO, ls="--", lw=1.5)
ax.plot(z, riposo, color=TESTO, lw=2.4)
ax.set_ylim(10840, 11180)
ax.set_ylabel("ν_B [MHz]", fontsize=13)
ax.set_title("1. A RIPOSO: tubo vuoto (0 bar), temperatura uguale ovunque", fontsize=15, fontweight="bold",
             loc="left", color=TESTO)
ax.text((EL0 + EL1) / 2, 11160, "tratto a ELICA", ha="center", fontsize=12.5, color=ARANCIO, fontweight="bold")
ax.text((LI0 + LI1) / 2, 11160, "tratto\nLIBERO", ha="center", va="top", fontsize=12, color=BLU, fontweight="bold")
ax.text(1.0, BASE - 25, "quello che ci si aspetterebbe: una linea piatta", fontsize=11.5, color=GRIGIO)
ax.annotate("la posa ha lasciato la fibra TIRATA,\ne non in modo uniforme: +180 MHz qui...",
            xy=(EL0 + 0.6, BASE + 178), xytext=(-0.2, 11095), fontsize=11.5,
            arrowprops=dict(arrowstyle="->", color=TESTO))
ax.annotate("...+105 MHz qui", xy=(EL1 - 0.4, BASE + 108), xytext=(12.8, 11040), fontsize=11.5,
            arrowprops=dict(arrowstyle="->", color=TESTO))

# 2. con 5 bar
ax = axs[1]
sfondo(ax)
ax.plot(z, riposo, color=TESTO, lw=1.8, label="a riposo (misura di base)")
ax.plot(z, cinque_bar, color=ROSSO, lw=2.4, label="con 5 bar")
ax.set_ylim(10840, 11260)
ax.set_ylabel("ν_B [MHz]", fontsize=13)
ax.set_title("2. CON 5 bar: lo strumento vede la curva rossa", fontsize=15, fontweight="bold", loc="left", color=TESTO)
ax.legend(fontsize=12, loc="upper right", frameon=False)
x0 = 8.5
i = np.argmin(abs(z - x0))
ax.annotate("", xy=(x0, cinque_bar[i]), xytext=(x0, riposo[i]),
            arrowprops=dict(arrowstyle="<->", color=VERDE, lw=2.2))
ax.text(x0 + 0.3, riposo[i] - 45, "\u2191 +73 MHz:\nquesta è la pressione", fontsize=11.5,
        color=VERDE, va="center", fontweight="bold")
ax.annotate("", xy=(x0 - 1.2, cinque_bar[i - 60]), xytext=(x0 - 1.2, BASE),
            arrowprops=dict(arrowstyle="<->", color=ROSSO, lw=1.8))
ax.text(x0 - 1.6, BASE + 60, "~+220 MHz rispetto\nalla linea piatta:\npressione + posa\nMESCOLATE",
        fontsize=11, color=ROSSO, ha="right", va="center")

# 3. differenza
ax = axs[2]
sfondo(ax)
diff = cinque_bar - riposo
ax.axhline(0, color=GRIGIO, lw=1)
ax.plot(z, diff, color=VERDE, lw=2.6)
ax.set_ylim(-25, 110)
ax.set_ylabel("Δν_B [MHz]", fontsize=13)
ax.set_xlabel("z = posizione lungo la fibra [m]", fontsize=13)
ax.set_title("3. CON 5 bar MENO A RIPOSO: resta solo l'effetto della pressione", fontsize=15, fontweight="bold",
             loc="left", color=TESTO)
ax.text((EL0 + EL1) / 2, 88, "+73 MHz uniforme sull'elica = 5 bar", ha="center", fontsize=12.5, color=VERDE,
        fontweight="bold")
ax.text((LI0 + LI1) / 2, 18, "0: il tratto libero\nnon sente la pressione", ha="center", fontsize=11, color=BLU)

# spiegazione a destra
spieg = [
    ("Cosa succede", True),
    ("Ogni metro di fibra ha la sua \"nota\" a riposo.\nSull'elica è molto più alta, perché\n"
     "avvolgendola la si tira, e non tutta allo\nstesso modo. Anche il tratto libero ha la\n"
     "sua (+65 MHz): l'articolo non dice perché.", False),
    ("Senza misura di base", True),
    ("Se l'informatico confronta la curva rossa\ncon la linea piatta, vede ~+220 MHz e li\n"
     "attribuisce alla pressione: ~15 bar invece\ndi 5. In più la \"pressione\" sembrerebbe\n"
     "diversa da un punto all'altro del tubo.", False),
    ("Con la misura di base", True),
    ("Si registra il profilo a riposo una volta,\nall'installazione. Poi ogni misura si\n"
     "confronta con quello, metro per metro:\nla posa si cancella e resta la pressione.\n"
     "Bertulessi 2023 fa così (§2.1): \"By con-\nsidering the BFS with respect to a reference\n"
     "state, it is possible to eliminate the\npre-strain component\".", False),
    ("Nel simulatore", True),
    ("• ogni metro riceve una sua \"nota\" a riposo\n  (fissa nel tempo, più alta sull'elica);\n"
     "• si consegna la misura di base;\n• le note vere a riposo stanno nelle etichette.", False),
]
y = 0.89
for testo, titolo in spieg:
    fig.text(0.69, y, testo, fontsize=14 if titolo else 12, fontweight="bold" if titolo else "normal",
             color=TESTO, va="top", linespacing=1.35)
    y -= 0.03 if titolo else 0.022 * (testo.count("\n") + 1) + 0.03

fig.text(0.05, 0.035, "Arancione: tratto a elica (sente pressione + temperatura).  Blu: tratto libero (solo temperatura).  "
         "Fuori dalle bande: cavi.\nIl numero di bar per MHz dipende dal tubo: qui 73 MHz = 5 bar vale per il tubo PN16 "
         "dell'esperimento.\nNell'esperimento la fibra è fissata all'esterno del tubo con nastro adesivo. Nel caso MATRIS è "
         "annegata nella guaina che polimerizza in opera:\nil profilo a riposo nasce soprattutto dalla polimerizzazione, "
         "e forma e valori sono DA VERIFICARE.", fontsize=11.5, color=GRIGIO, linespacing=1.4)
out = Path(__file__).with_name("frequenza-a-riposo.png")
fig.savefig(out, dpi=100, facecolor="white")
print("scritto", out)
