<!-- nav -->
| [← Appendice A. Fonti](A-fonti.md) | [📖 Indice](00-indice.md)<br><sub>appendici</sub> | [Appendice C. Diario delle sessioni →](C-diario-sessioni.md) |
|:---|:---:|---:|
<!-- /nav -->

# Appendice B — Sensori distribuiti in fibra ottica su condotte idriche (approfondimento)

*Primo documento del progetto. Il §2.1 è aggiornato; il resto è il testo iniziale, in parte superato dai capitoli 2–7.*

Questo documento spiega come funziona un sensore distribuito in fibra ottica (DFOS, *Distributed Fibre Optic Sensing*), perché una perdita "si sente" lungo il tubo e come la fibra si inserisce nel Digital Twin dell'OR5 di MATRIS come tecnologia abilitante per un progetto successivo. Serve per capire prima di simulare: il codice verrà dopo, a piccoli passi.

**Contenuto**

1. [Il contesto: da MATRIS al follow-up](#1-il-contesto-da-matris-al-follow-up)
2. [Il principio: un cavo, migliaia di sensori](#2-il-principio-un-cavo-migliaia-di-sensori)
   - [2.1 Come funziona la BOTDA, passo per passo](02-principio-di-misura.md#22-il-principio-botda-panoramica)
3. [Tre fenomeni, tre sensori: DAS, DTS, DSS](#3-tre-fenomeni-tre-sensori-das-dts-dss)
4. [I numeri che contano](#4-i-numeri-che-contano)
5. [Perché una perdita "suona"](#5-perché-una-perdita-suona)
6. [Che dati produce: il waterfall](#6-che-dati-produce-il-waterfall)
7. [Fibra o MEMS nella guaina](#7-fibra-o-mems-nella-guaina)
8. [Come si aggancia al Digital Twin (OR5)](#8-come-si-aggancia-al-digital-twin-or5)
9. [Cosa simuleremo, e cosa no](#9-cosa-simuleremo-e-cosa-no)
10. [Glossario](#10-glossario)
11. [Da leggere](#11-da-leggere)

---

## 1. Il contesto: da MATRIS al follow-up

In MATRIS il monitoraggio "distribuito" è fatto da **accelerometri MEMS annegati nella guaina in composito** del relining (OR4), più **giunti smart** con sensori di pressione e portata usati come riferimento. Ogni nodo ha un microcontrollore che estrae feature spettrali (MFCC) dalle vibrazioni. È un sensore **quasi-distribuito**: tanti punti discreti, ognuno con la sua elettronica.

Il follow-up propone di sostituire o affiancare i nodi MEMS con una **fibra ottica posata o annegata lungo la condotta**: un sensore **realmente distribuito**, passivo, senza elettronica né alimentazione lungo il tubo. Il Digital Twin dell'OR5 deve poterla ospitare: per questo la simuliamo.

## 2. Il principio: un cavo, migliaia di sensori

Spostato e aggiornato nel **[capitolo 2](02-principio-di-misura.md)**: la diffusione Brillouin, lo schema a
blocchi dell'interrogatore BOTDA (blocco per blocco), come nascono posizione e misura. Il principio del tempo di volo
(z = c·t / (2n), circa 10 ns per metro) vale per tutte le tecniche di questa appendice.

## 3. Tre fenomeni, tre sensori: DAS, DTS, DSS

La luce di ritorno contiene tre "firme" fisiche diverse. Ognuna sensibile a una grandezza diversa:

| Fenomeno fisico | Tecnica | Cosa misura | Su una condotta serve per |
|---|---|---|---|
| **Rayleigh** (stessa frequenza del laser; si guarda la **fase**) | **DAS** — Distributed Acoustic Sensing | vibrazioni e suono, campionati a kHz | rumore delle **perdite**, colpi d'ariete, scavi e mezzi vicino al tubo |
| **Raman** (righe spostate in frequenza, intensità dipende dalla temperatura) | **DTS** — Distributed Temperature Sensing | temperatura assoluta | perdite su tubi interrati (il terreno bagnato cambia temperatura), intrusioni |
| **Brillouin** (riga spostata di ~11 GHz, lo spostamento dipende da deformazione e temperatura) | **DSS** — Distributed Strain Sensing (BOTDR/BOTDA) | deformazione (strain) + temperatura | cedimenti del terreno, deformazione del tubo, variazioni lente di pressione |

**Come funziona il DAS, in due righe.** Con un laser molto "puro" (coerente) la luce di ritorno da un tratto di fibra è la somma di tante onde che interferiscono: il risultato ha una certa fase. Se una vibrazione allunga o accorcia quel tratto di fibra di pochi nanometri, la fase cambia. Ripetendo l'impulso migliaia di volte al secondo si ricostruisce, per ogni canale, un segnale nel tempo che è proporzionale alla **deformazione dinamica** della fibra: un microfono lungo chilometri.

Per le perdite in una rete di distribuzione **il DAS è il candidato principale**, ed è quello che simuleremo per primo. DTS e DSS sono estensioni.

## 4. I numeri che contano

Ordini di grandezza tipici di un DAS commerciale (variano molto tra prodotti):

| Parametro | Valore tipico | Da cosa dipende |
|---|---|---|
| Portata (lunghezza leggibile) | fino a 40–50 km | potenza del laser, attenuazione della fibra (~0,2 dB/km) |
| Risoluzione spaziale (*gauge length*) | 1–10 m | durata dell'impulso e elaborazione; più corta = più dettaglio ma più rumore |
| Passo dei canali | 0,25–2 m | campionamento del rivelatore |
| Frequenza di ripetizione degli impulsi | fino a ~ c / (2·n·L) | un impulso deve tornare prima del successivo |
| Banda acustica | metà della frequenza di ripetizione | teorema del campionamento |

L'ultima riga è importante per le reti di distribuzione: **una fibra corta permette una banda alta**. Con L = 1 km la frequenza massima di ripetizione è ~100 kHz (banda fino a ~50 kHz); con L = 10 km è ~10 kHz (banda ~5 kHz). Per le perdite bastano poche centinaia di Hz – qualche kHz, quindi non è un vincolo.

**Il volume di dati** è il vero problema: 1000 canali × 10 000 campioni/s × 2 byte = **20 MB/s, circa 1,7 TB al giorno**. Nessuno trasmette questi dati grezzi: l'elaborazione si fa **accanto all'interrogatore** (edge) e verso il centro vanno solo eventi o indicatori compatti.

## 5. Perché una perdita "suona"

Quando l'acqua in pressione esce da una fessura, il getto turbolento genera **rumore a banda larga** (un sibilo). Questo rumore si propaga in due modi:

- **lungo il tubo**, soprattutto come onda di pressione nell'acqua accoppiata alla parete;
- **nel terreno** intorno, per brevi distanze.

Cosa determina quanto e come lo sente la fibra:

| Fattore | Effetto |
|---|---|
| **Pressione** e **portata persa** | più pressione e più portata = rumore più forte |
| **Materiale del tubo** | nei tubi **metallici** il rumore arriva lontano e ha frequenze più alte (fino a 1–2 kHz); nei tubi **plastici** (PE, PVC) e nei **compositi** è attenuato in pochi metri–decine di metri e concentrato a bassa frequenza (decine–centinaia di Hz) |
| **Distanza** dalla perdita | l'ampiezza decade con la distanza: il canale più vicino alla perdita è quello più "rumoroso" → **localizzazione** |
| **Accoppiamento** fibra–tubo | una fibra annegata nella guaina "sente" molto meglio di una posata nello scavo |
| **Rumore di fondo** | traffico stradale, pompe, flusso normale, rumore dell'interrogatore |

Altri eventi idraulici hanno firme diverse:

- **colpo d'ariete / arresto pompa**: un'onda di pressione che corre lungo il tubo a velocità costante (~1000–1400 m/s nei tubi metallici, ~300–500 m/s in quelli plastici): nel waterfall è una **diagonale**, e dalla sua pendenza si legge la velocità;
- **scavo vicino al tubo** (rischio di rottura per terzi): colpi ripetuti, localizzati, a orari lavorativi;
- **veicoli**: segnali che si spostano lungo la fibra dove una strada la costeggia, o un lampo breve dove la attraversa.

## 6. Che dati produce: il waterfall

L'uscita naturale di un DAS è una matrice **tempo × posizione**, detta *waterfall*: ogni colonna è un canale, ogni riga un istante, il colore è l'energia della vibrazione (di solito in una banda di frequenza).

Per la BOTDA del simulatore un esempio vero di matrice tempo × posizione è il grafico 3 della figura del segnale
(cap. 8; esempio: [A_signal_true.png](img/A_signal_true.png)). In un waterfall DAS gli eventi tipici si riconoscono così:

| evento | aspetto nel waterfall |
|---|---|
| perdita d'acqua | banda verticale che resta nel tempo, nella posizione della perdita |
| mezzo che passa lungo una strada parallela | traccia obliqua, che si sposta nel tempo |
| onda di pressione (transitorio) | diagonale sottile; la pendenza è la sua velocità |

Riconoscere eventi nel waterfall è un problema di **visione/segnali**: soglie, rilevamento di bande verticali, filtri, reti convoluzionali (CNN) sulle immagini tempo-posizione. È esattamente il tipo di "modello predittivo" previsto dall'att. 5.1 dell'OR5.

## 7. Fibra o MEMS nella guaina

| | MEMS nella guaina (MATRIS) | Fibra DAS (follow-up) |
|---|---|---|
| Tipo di copertura | punti discreti (un nodo ogni N metri o nei giunti) | continua, un canale ogni ~1 m |
| Elettronica lungo il tubo | sì: sensore + MCU + alimentazione + radio per ogni nodo | **nessuna**: la fibra è passiva |
| Dove si elabora | sul nodo (MFCC sul microcontrollore) | nell'interrogatore, a un'estremità |
| Costo | basso per nodo, cresce con il numero di nodi | interrogatore costoso (indicativamente decine di migliaia di euro), fibra economica; conviene su tratti lunghi |
| Vita utile | limitata dalla batteria/elettronica | la fibra dura quanto il tubo (decenni) |
| Localizzazione | tra due nodi, per correlazione | diretta, al canale più rumoroso (± qualche metro) |
| Integrazione nel relining | sensori e cavi annegati nel composito (OR2) | fibra annegata nel composito durante la produzione della guaina |
| Comunicazione | LoRaWAN da ogni nodo | un collegamento dall'interrogatore (IP o LoRaWAN per gli eventi) |

L'argomento per il follow-up: la guaina CIPP di MATRIS è **già un supporto ideale per annegare una fibra** durante la produzione, eliminando l'elettronica distribuita. I giunti smart restano utili come riferimento di pressione e portata per **calibrare** la fibra.

## 8. Come si aggancia al Digital Twin (OR5)

| livello | cosa fa |
|---|---|
| mondo fisico (simulato) | EPANET: pressioni, portate, perdite, guasti; modello del sensore (fibra, rumore, waterfall) |
| edge, accanto all'interrogatore | rilevatore: dal waterfall a eventi compatti ("perdita probabile a 1050 m, intensità alta, da 07:12"); regole, poi CNN |
| collegamento | pochi byte (LoRaWAN o IP) |
| Active Digital Twin (OR5) | il tubo "sa" dov'è la perdita; fusione con contatori di distretto e sensori di pressione; agenti che spiegano l'incidente e propongono azioni |

Quello che il repository ha già: la rete reale in EPANET con perdite e guasto pompa (`radio/hydraulics.py` nel progetto edge-slm-emulator), la pipeline LoRaWAN completa e gli agenti SLM. Quello che manca è il blocco centrale: **il modello acustico e il sensore in fibra**.

Questo arricchisce il tema del repository (la stessa informazione vista più volte): una perdita la vedono il contatore di distretto (portata in aumento), i sensori di pressione (calo) e ora la fibra (rumore localizzato). Gli agenti devono riconoscere che sono **lo stesso evento**.

## 9. Cosa simuleremo, e cosa no

Un DAS reale campiona a kHz: simulare i campioni grezzi di migliaia di canali per 24 ore produrrebbe terabyte di dati inutili. Simuleremo invece **ciò che l'interrogatore calcola dopo la prima elaborazione**: per ogni canale e ogni intervallo (es. 1 s), l'**energia della vibrazione in alcune bande di frequenza**. È anche la rappresentazione usata in letteratura per rilevare gli eventi.

| Simuliamo | Non simuliamo (per ora) |
|---|---|
| tracciato della fibra lungo tubi reali della rete EPANET | l'ottica (fase, interferenza, laser) |
| energia per banda per canale, nel tempo | i campioni acustici grezzi a kHz |
| perdite come sorgenti con ampiezza legata alla portata persa da EPANET | la vibroacustica dettagliata del tubo |
| attenuazione con la distanza dipendente dal materiale | DTS e DSS (estensioni) |
| rumore di fondo, *fading*, traffico, transitori della pompa | |
| un rilevatore edge semplice, valutato contro la verità di EPANET | |

I parametri (attenuazione, livelli di rumore, risoluzione) verranno da letteratura e, appena disponibili, da misure reali: il modello deve essere **calibrabile**, non "giusto" a priori.

## 10. Glossario

| Termine | Significato |
|---|---|
| **DFOS** | Distributed Fibre Optic Sensing: la fibra stessa è il sensore, lungo tutta la sua lunghezza |
| **Interrogatore** | l'apparecchio a un'estremità della fibra che manda gli impulsi e analizza il ritorno |
| **Backscattering** | la piccola parte di luce rimandata indietro da ogni punto della fibra |
| **OTDR** | misurare la posizione dal tempo di ritorno della luce |
| **DAS / DTS / DSS** | sensori distribuiti di vibrazione / temperatura / deformazione |
| **Canale** | il tratto di fibra che corrisponde a un sensore virtuale |
| **Gauge length** | lunghezza di fibra su cui il DAS misura una deformazione; fissa la risoluzione spaziale |
| **Waterfall** | la matrice tempo × posizione prodotta dal DAS |
| **Fading** | canali che a tratti diventano "sordi" per un effetto casuale di interferenza della luce |
| **CIPP / relining** | risanamento senza scavo: una guaina impregnata di resina indurita dentro il tubo esistente |
| **MEMS** | sensori microscopici su chip (es. accelerometri), quelli previsti da MATRIS |
| **Strain** | deformazione relativa (allungamento / lunghezza); in µε = milionesimi |

## 11. Da leggere

In ordine di utilità per iniziare (verificare i riferimenti esatti prima di citarli in tesi):

1. A. H. Hartog, *An Introduction to Distributed Optical Fibre Sensors*, CRC Press, 2017 — il manuale di riferimento su DAS, DTS e DSS.
2. P. Lu et al., "Distributed optical fiber sensing: Review and perspective", *Applied Physics Reviews* 6, 041302, 2019 — rassegna, buona per lo stato dell'arte.
3. P. Stajanca et al., "Detection of leak-induced pipeline vibrations using fiber-optic distributed acoustic sensing", *Sensors* 18(9), 2841, 2018 — DAS applicato proprio alle perdite in condotta.
4. O. Hunaidi, W. T. Chu, "Acoustical characteristics of leak signals in plastic water distribution pipes", *Applied Acoustics* 58, 1999 — come "suona" una perdita nei tubi plastici.
5. Y. Gao, M. J. Brennan, P. F. Joseph, J. M. Muggleton, O. Hunaidi, "A model of the correlation function of leak noise in buried plastic pipes", *Journal of Sound and Vibration* 277, 2004 — modello di propagazione e attenuazione del rumore di perdita: la base del nostro modello acustico.
6. K. A. Klise et al., Water Network Tool for Resilience (WNTR), Sandia National Laboratories — il simulatore idraulico citato nell'att. 5.1.

<!-- nav-fondo -->

| [← Appendice A. Fonti](A-fonti.md) | [📖 Indice](00-indice.md)<br><sub>appendici</sub> | [Appendice C. Diario delle sessioni →](C-diario-sessioni.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
