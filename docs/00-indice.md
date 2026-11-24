<!-- nav -->
|   | **Indice** | [1. Introduzione →](01-introduzione.md) |
|:---|:---:|---:|
<!-- /nav -->

![WaterFiberSim](img/logo.png)

# WaterFiberSim — Documentazione tecnica

Simulatore di sensori in fibra ottica (Brillouin, BOTDA) posati lungo i tubi di una rete idrica, per capire se e come
misurano la **pressione dell'acqua** metro per metro. Questo documento descrive il problema, la fisica, il simulatore, i
parametri, le verifiche e i risultati. Ogni capitolo rimanda agli altri; le fonti sono in appendice A.

> **Interrogatori BOTDA commerciali** — Prysmian DITEST, OZ Optics DSTS,
> Neubrex NBX-7031, Cohaerentia: confronto e come impostarli nel simulatore nel [§2.5](02-principio-di-misura.md#25-interrogatori-botda-commerciali).

## Indice

**Parte I — Problema e principio di misura**
1. [Introduzione](01-introduzione.md)
2. [Principio di misura (BOTDA)](02-principio-di-misura.md)
3. [Configurazione del sensore](03-il-sensore-sul-tubo.md)

**Parte II — I modelli**
4. [Rete idraulica e scenari](04-rete-idraulica-e-scenari.md)
5. [Meccanica del tubo e della guaina](05-meccanica-del-tubo.md)
6. [Modello dello strumento e dato grezzo](06-strumento-e-dato-grezzo.md)
7. [Temperatura e compensazione](07-temperatura-e-compensazione.md)

**Parte III — Simulatore**
8. [Logica del simulatore](08-logica-del-simulatore.md)
9. [Parametri del simulatore](09-parametri-del-simulatore.md)
10. [Validazione](10-validazione.md)

**Parte IV — Conclusioni**
11. [Risultati e questioni aperte](11-risultati-e-questioni-aperte.md)

**Appendici**
A. [Fonti e stato di verifica](A-fonti.md) — ogni affermazione con fonte e stato  
B. [Sensori distribuiti in fibra ottica (DFOS)](B-fibra-ottica-dfos.md) — primo documento del progetto; §2.1 aggiornato  
C. [Diario delle sessioni e decisioni](C-diario-sessioni.md) — le decisioni in ordine di tempo

## Guida alla lettura

- Chi deve **usare** il simulatore: capitoli 4, 8, 9 (e il README del repository per l'installazione).
- Chi vuole capire **la fisica**: capitoli 2, 3, 5, 6, 7.
- Chi vuole sapere **se funziona**: capitoli 10 e 11.

Accanto alle affermazioni, nei capitoli: la fonte citata tra parentesi quadre (link all'appendice A); "(calcolo
nostro)" per i risultati ricavati da noi con formule o con il simulatore; "(da verificare)" per i valori scelti o
non ancora confermati da una fonte. Nell'appendice A lo stato di ogni affermazione è indicato con ✅ (verificato su
una fonte letta), 🧮 (calcolo nostro), ⚠️ (scelto o da verificare).

La navigazione in cima e in fondo a ogni capitolo si rigenera con `python docs/navigazione.py`.

<!-- nav-fondo -->

|   | **Indice** | [1. Introduzione →](01-introduzione.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
