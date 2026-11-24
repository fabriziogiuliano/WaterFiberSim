<!-- nav -->
|   | **Indice** | [1. Introduzione →](01-introduzione.md) |
|:---|:---:|---:|
<!-- /nav -->

# WaterFiberSim — il libro del simulatore

Simulatore di sensori in fibra ottica (Brillouin, BOTDA) posati lungo i tubi di una rete idrica, per capire se e come
misurano la **pressione dell'acqua** metro per metro. Questo libro spiega il problema, la fisica, il simulatore, i
parametri, le verifiche e i risultati. Ogni capitolo rimanda agli altri; le fonti sono in appendice A.

## Indice

**Parte I — Il problema e la fisica**
1. [Introduzione: obiettivo e contesto](01-introduzione.md)
2. [Il principio di misura: la fibra Brillouin](02-principio-di-misura.md)
3. [Il sensore sul tubo: posa della fibra](03-il-sensore-sul-tubo.md)

**Parte II — I modelli**
4. [Rete idraulica e scenari](04-rete-idraulica-e-scenari.md)
5. [Meccanica del tubo e della guaina](05-meccanica-del-tubo.md)
6. [Lo strumento e il dato grezzo](06-strumento-e-dato-grezzo.md)
7. [Temperatura e compensazione](07-temperatura-e-compensazione.md)

**Parte III — Il simulatore**
8. [Logica del simulatore](08-logica-del-simulatore.md)
9. [Scheda tecnica dei parametri](09-scheda-tecnica.md)
10. [Validazione](10-validazione.md)

**Parte IV — Conclusioni**
11. [Risultati e questioni aperte](11-risultati-e-questioni-aperte.md)

**Appendici**
- A. [Fonti e stato di verifica](fonti.md)
- B. [Approfondimento sulla fibra ottica (DFOS)](fibra-ottica-dfos.md) — §2.1 aggiornato, il resto è il testo iniziale
- C. [Diario delle sessioni e decisioni](sessione-2026-11-23.md)

## Come si legge

- Chi deve **usare** il simulatore: capitoli 4, 8, 9 (e il README del repository per l'installazione).
- Chi vuole capire **la fisica**: capitoli 2, 3, 5, 6, 7.
- Chi vuole sapere **se funziona**: capitoli 10 e 11.

Simboli usati per le affermazioni (come nell'appendice A): ✅ verificato su una fonte letta · 🧮 calcolato ·
⚠️ scelto o da verificare.

La navigazione in cima e in fondo a ogni capitolo si rigenera con `python docs/libro.py`.

<!-- nav-fondo -->

|   | **Indice** | [1. Introduzione →](01-introduzione.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
