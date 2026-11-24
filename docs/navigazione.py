"""Navigazione della documentazione: aggiunge (o aggiorna) in cima e in fondo a ogni capitolo i collegamenti
"capitolo precedente · indice · capitolo successivo"; nelle appendici solo il ritorno all'indice.

    python docs/navigazione.py
"""
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent
CAPITOLI = [
    ("00-indice.md", "Indice"),
    ("01-introduzione.md", "1. Introduzione"),
    ("02-principio-di-misura.md", "2. Principio di misura (BOTDA)"),
    ("03-il-sensore-sul-tubo.md", "3. Configurazione del sensore"),
    ("04-rete-idraulica-e-scenari.md", "4. Rete idraulica e scenari"),
    ("05-meccanica-del-tubo.md", "5. Meccanica del tubo e della guaina"),
    ("06-strumento-e-dato-grezzo.md", "6. Modello dello strumento e dato grezzo"),
    ("07-temperatura-e-compensazione.md", "7. Temperatura e compensazione"),
    ("08-guida-all-uso.md", "8. Guida all'uso"),
    ("09-logica-del-simulatore.md", "9. Logica del simulatore"),
    ("10-parametri-del-simulatore.md", "10. Parametri del simulatore"),
    ("11-validazione.md", "11. Validazione"),
    ("12-risultati-e-questioni-aperte.md", "12. Risultati e questioni aperte"),
    ("A-fonti.md", "Appendice A. Fonti"),
    ("B-fibra-ottica-dfos.md", "Appendice B. Sensori distribuiti in fibra ottica"),
    ("C-diario-sessioni.md", "Appendice C. Diario delle sessioni"),
]
N_CAPITOLI = 12
TOP, BOTTOM = ("<!-- nav -->", "<!-- /nav -->"), ("<!-- nav-fondo -->", "<!-- /nav-fondo -->")


def _strip(testo: str) -> str:
    for a, b in (TOP, BOTTOM):
        testo = re.sub(re.escape(a) + r".*?" + re.escape(b) + r"\n*", "", testo, flags=re.S)
    return testo.strip() + "\n"


PARTI = {1: "Parte I — Problema e principio di misura", 4: "Parte II — I modelli", 8: "Parte III — Simulatore",
         12: "Parte IV — Conclusioni"}


def _parte(i: int) -> str:
    return next((t for k, t in sorted(PARTI.items(), reverse=True) if i >= k), "")


def _barra(i: int) -> str:
    """Barra a tre colonne: precedente | indice | successivo (tabella markdown, si allinea anche su GitHub)."""
    prev = f"[← {CAPITOLI[i - 1][1]}]({CAPITOLI[i - 1][0]})" if i > 0 else " "
    nxt = f"[{CAPITOLI[i + 1][1]} →]({CAPITOLI[i + 1][0]})" if i < len(CAPITOLI) - 1 else " "
    if i == 0:
        mezzo = "**Indice**"
    elif i <= N_CAPITOLI:
        mezzo = f"[📖 Indice](00-indice.md)<br><sub>capitolo {i} di {N_CAPITOLI} · {_parte(i)}</sub>"
    else:
        mezzo = "[📖 Indice](00-indice.md)<br><sub>appendici</sub>"
    return f"| {prev} | {mezzo} | {nxt} |\n|:---|:---:|---:|"


def _sigle(testo_fonti: str) -> list[str]:
    """Sigle delle fonti principali: nell'appendice A ognuna ha un titolo `### SIGLA` (ancora valida ovunque)."""
    i = testo_fonti.index("## Fonti principali")
    j = testo_fonti.index("\n## ", i + 5)
    return re.findall(r"^### ([A-Z0-9]+)\s*$", testo_fonti[i:j], flags=re.M)


def collega_fonti():
    """Ogni [SIGLA] nei documenti diventa un link al titolo della sua fonte nell'appendice A."""
    sigle = _sigle((DOCS / "A-fonti.md").read_text())
    alt = "|".join(sorted(sigle, key=len, reverse=True))
    pat = re.compile(r"(?<![\[\\*])\[(" + alt + r")\](?!\()")    # solo le sigle non già collegate
    files = [DOCS / f for f, _ in CAPITOLI] + [DOCS.parent / "README.md"]
    for p in files:
        t = p.read_text()
        dest = "" if p.name == "A-fonti.md" else ("docs/A-fonti.md" if p.name == "README.md" else "A-fonti.md")
        t2 = pat.sub(lambda m: f"[\\[{m.group(1)}\\]]({dest}#{m.group(1).lower()})", t)
        if t2 != t:
            p.write_text(t2)
    return sigle


def main():
    for i, (f, _) in enumerate(CAPITOLI):
        p = DOCS / f
        corpo = _strip(p.read_text())
        barra = _barra(i)
        p.write_text(f"{TOP[0]}\n{barra}\n{TOP[1]}\n\n{corpo}\n{BOTTOM[0]}\n\n{barra}\n{BOTTOM[1]}\n")
    print(f"navigazione aggiornata: {N_CAPITOLI} capitoli e {len(CAPITOLI) - N_CAPITOLI - 1} appendici")
    print(f"fonti collegate: {', '.join(collega_fonti())}")


if __name__ == "__main__":
    main()
