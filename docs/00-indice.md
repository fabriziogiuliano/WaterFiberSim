<!-- nav -->
|   | **Indice** | [1. Introduzione →](01-introduzione.md) |
|:---|:---:|---:|
<!-- /nav -->

# WaterFiberSim — il libro del simulatore

Simulatore di sensori in fibra ottica (Brillouin, BOTDA) posati lungo i tubi di una rete idrica, per capire se e come
misurano la **pressione dell'acqua** metro per metro. Questo libro spiega il problema, la fisica, il simulatore, i
parametri, le verifiche e i risultati. Ogni capitolo rimanda agli altri; le fonti sono in appendice A.

> **In evidenza: gli strumenti BOTDA esistono già e si possono usare da subito** — Prysmian DITEST, OZ Optics DSTS,
> Neubrex NBX-7031, Cohaerentia: confronto e come impostarli nel simulatore nel [§2.5](02-principio-di-misura.md#25-strumenti-botda-in-commercio-utilizzabili-da-subito).

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
9. [I parametri del simulatore: analisi di tutte le variabili](09-parametri-del-simulatore.md)
10. [Validazione](10-validazione.md)

**Parte IV — Conclusioni**
11. [Risultati e questioni aperte](11-risultati-e-questioni-aperte.md)

**Appendici**
A. [Fonti e stato di verifica](A-fonti.md) — ogni affermazione con fonte e stato  
B. [Approfondimento sulla fibra ottica (DFOS)](B-fibra-ottica-dfos.md) — primo documento del progetto; §2.1 aggiornato  
C. [Diario delle sessioni e decisioni](C-diario-sessioni.md) — le decisioni in ordine di tempo

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
