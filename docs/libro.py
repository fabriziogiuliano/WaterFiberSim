"""Navigazione del libro: aggiunge (o aggiorna) in cima e in fondo a ogni capitolo i collegamenti
"capitolo precedente · indice · capitolo successivo"; nelle appendici solo il ritorno all'indice.

    python docs/libro.py
"""
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent
CAPITOLI = [
    ("00-indice.md", "Indice"),
    ("01-introduzione.md", "1. Introduzione"),
    ("02-principio-di-misura.md", "2. Il principio di misura"),
    ("03-il-sensore-sul-tubo.md", "3. Il sensore sul tubo"),
    ("04-rete-idraulica-e-scenari.md", "4. Rete idraulica e scenari"),
    ("05-meccanica-del-tubo.md", "5. Meccanica del tubo e della guaina"),
    ("06-strumento-e-dato-grezzo.md", "6. Lo strumento e il dato grezzo"),
    ("07-temperatura-e-compensazione.md", "7. Temperatura e compensazione"),
    ("08-logica-del-simulatore.md", "8. Logica del simulatore"),
    ("09-scheda-tecnica.md", "9. Scheda tecnica dei parametri"),
    ("10-validazione.md", "10. Validazione"),
    ("11-risultati-e-questioni-aperte.md", "11. Risultati e questioni aperte"),
]
APPENDICI = ["fonti.md", "fibra-ottica-dfos.md", "sessione-2026-11-23.md"]
TOP, BOTTOM = ("<!-- nav -->", "<!-- /nav -->"), ("<!-- nav-fondo -->", "<!-- /nav-fondo -->")


def _strip(testo: str) -> str:
    for a, b in (TOP, BOTTOM):
        testo = re.sub(re.escape(a) + r".*?" + re.escape(b) + r"\n*", "", testo, flags=re.S)
    return testo.strip() + "\n"


PARTI = {1: "Parte I — Il problema e la fisica", 4: "Parte II — I modelli", 8: "Parte III — Il simulatore",
         11: "Parte IV — Conclusioni"}


def _parte(i: int) -> str:
    return next((t for k, t in sorted(PARTI.items(), reverse=True) if i >= k), "")


def _barra(i: int) -> str:
    """Barra a tre colonne: precedente | indice | successivo (tabella markdown, si allinea anche su GitHub)."""
    prev = f"[← {CAPITOLI[i - 1][1]}]({CAPITOLI[i - 1][0]})" if i > 0 else " "
    nxt = f"[{CAPITOLI[i + 1][1]} →]({CAPITOLI[i + 1][0]})" if i < len(CAPITOLI) - 1 else " "
    mezzo = "**Indice**" if i == 0 else f"[📖 Indice](00-indice.md)<br><sub>capitolo {i} di {len(CAPITOLI) - 1} · {_parte(i)}</sub>"
    return f"| {prev} | {mezzo} | {nxt} |\n|:---|:---:|---:|"


def main():
    for i, (f, _) in enumerate(CAPITOLI):
        p = DOCS / f
        corpo = _strip(p.read_text())
        barra = _barra(i)
        p.write_text(f"{TOP[0]}\n{barra}\n{TOP[1]}\n\n{corpo}\n{BOTTOM[0]}\n\n{barra}\n{BOTTOM[1]}\n")
    for f in APPENDICI:
        p = DOCS / f
        corpo = _strip(p.read_text())
        p.write_text(f"{TOP[0]}\n| [📖 Indice del libro](00-indice.md) · appendice |\n|:---:|\n{TOP[1]}\n\n{corpo}")
    print(f"navigazione aggiornata: {len(CAPITOLI)} capitoli, {len(APPENDICI)} appendici")


if __name__ == "__main__":
    main()
