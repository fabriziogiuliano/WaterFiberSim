<!-- nav -->
| [← Appendice B. Approfondimento sulla fibra](B-fibra-ottica-dfos.md) | [📖 Indice](00-indice.md)<br><sub>appendici</sub> |   |
|:---|:---:|---:|
<!-- /nav -->

# Appendice C — Diario delle sessioni: decisioni, ricerca e piano

Raccolta di tutto ciò che è stato formulato nella sessione di lavoro del 23/11/2026, per riprendere il lavoro in un altro ambiente senza perdere il filo. Le parti sono in ordine logico, non cronologico.

**Indice**

1. [Obiettivo e decisioni prese](#1-obiettivo-e-decisioni-prese)
2. [Stato dei repository](#2-stato-dei-repository)
3. [Concetti: DFOS, DAS, DTS, DSS](#3-concetti-dfos-das-dts-dss)
4. [Dalla pressione alla fibra](#4-dalla-pressione-alla-fibra)
5. [Modelli matematici assodati](#5-modelli-matematici-assodati)
6. [Framework e strumenti esistenti](#6-framework-e-strumenti-esistenti)
7. [Architettura del simulatore](#7-architettura-del-simulatore)
8. [Piano a passi](#8-piano-a-passi)
9. [Integrazione futura con LoRaWAN](#9-integrazione-futura-con-lorawan)
10. [Domande aperte e cose da fare](#10-domande-aperte-e-cose-da-fare)
11. [Note tecniche sull'ambiente](#11-note-tecniche-sullambiente)
12. [Fonti](#12-fonti)
13. [Seconda parte della sessione: decisioni e correzioni](#13-seconda-parte-della-sessione-decisioni-e-correzioni)

---

## 1. Obiettivo e decisioni prese

**Contesto.** Il progetto nasce dall'OR5 di MATRIS (Active Digital Twin). In MATRIS il monitoraggio è fatto da MEMS annegati nella guaina in composito del relining (OR4); il follow-up propone la **fibra ottica** come sensore realmente distribuito.

**Obiettivo (rivisto durante la sessione).** Non le perdite via acustica (DAS), ma **misurare la pressione sulle pareti del tubo** con un sensore distribuito in fibra: **DSS (Brillouin) + DTS (Raman)**, con il DAS eventualmente per i transitori veloci.

**Decisioni:**

| Decisione | Motivo |
|---|---|
| Tutto **in simulazione** | non ci sono misure reali disponibili |
| Il simulatore è un **prodotto per un utente informatico**: lui lancia scenari, prende dati e fa esperimenti (DSP, ML) senza dover conoscere la fisica | la fisica resta dentro, con default dalla letteratura e poche parametri documentati |
| Non si simula l'ottica impulso per impulso: si simula il **segnale grezzo già mediato** (spettro Brillouin con il rumore corretto) | statisticamente equivalente e molto meno costoso |
| Il simulatore si ferma a **L0 (grezzo)** e fornisce le **etichette vere** di tutti i livelli; L1–L3 sono DSP dell'utente | vedi §7 |
| **Wrapper su EPANET `.inp`**: l'`.inp` non si tocca, i parametri meccanici per tubo stanno in un YAML a parte | separare idraulica e meccanica |
| Si parte da una **rete minima** (serbatoio + griglia 3×3 + utenze) | capibile a colpo d'occhio |
| Fibra in **overlay** sulla rete, avvolta **a elica** | vedi §4.3 |
| Nome del progetto: **WaterFiberSim** | |
| **Progetto indipendente** da `edge-slm-emulator`, gestito in modo ortogonale; integrazione solo quando entrambi saranno maturi | |

---

## 2. Stato dei repository

**`~/WaterFiberSim`** (questo repo), branch `main`:

| Commit | Contenuto |
|---|---|
| `93a58ad` | README con piano e passo 1; modello 3D Blender (`blender/tubo_fibra.py` + render `.png`); `.gitignore` |
| `4ca8674` | `docs/B-fibra-ottica-dfos.md` (documento di contesto) + `docs/img/dfos-interrogatore.drawio.svg` |
| (questo file) | dump della sessione |

**Push non ancora fatto.** Il remote è `git@github.com:fabriziogiuliano/WaterFiberSim.git` e la chiave SSH autentica correttamente come `fabriziogiuliano`, ma il push risponde *Repository not found*: il repo su GitHub non esiste ancora (o ha un nome/owner diverso). Da fare: crearlo vuoto e privato su https://github.com/new, poi `git push -u origin main`.

**`~/edge-slm-emulator`**, branch `dt_matris` (solo locale, non pushato):
- `194f85c Add MATRIS docs`: aggiunta `docs/MATRIS/`;
- `f9f39b1 Move DFOS document to the WaterFiberSim project`: tolto il documento DFOS (ora vive qui);
- in `docs/MATRIS/` resta solo `Allegato n 4_Piano di Sviluppo.doc.docx`.

Il repo `edge-slm-emulator` è privato su GitHub; il branch `dt_matris` non esiste ancora su `origin`.

---

## 3. Concetti: DFOS, DAS, DTS, DSS

**DFOS** = *Distributed Fibre Optic Sensing* (a volte DOFS): la fibra stessa è il sensore lungo tutta la sua lunghezza. Un interrogatore a un capo manda impulsi laser; ogni punto della fibra rimanda indietro un po' di luce (*backscattering*); il **tempo di ritorno** dice da dove arriva la luce: **z = c·t / (2n)**, con n ≈ 1,47, cioè circa **10 ns = 1 m**. Ogni "fetta" di tempo è un **canale** (sensore virtuale).

| Grandezza | Tecnica | Fenomeno | Velocità | Numeri tipici |
|---|---|---|---|---|
| vibrazioni / suono | **DAS** | Rayleigh (fase) | kHz | gauge 1–10 m, banda fino a kHz, fino a 40–50 km |
| temperatura | **DTS** | Raman (rapporto anti-Stokes/Stokes) | secondi–minuti | ~0,1 °C, ~1 m, decine di km; insensibile allo strain |
| deformazione + temperatura | **DSS** | Brillouin (spostamento ~11 GHz) | secondi–minuti | 2–10 µε, 0,5–1 m, decine di km |

**DAS.** Una vibrazione allunga e accorcia la fibra di nanometri e cambia la fase della luce di ritorno; con migliaia di impulsi al secondo ogni metro diventa un "microfono". Sente ciò che tocca la fibra (terreno, tubo), soprattutto lungo l'asse. Usi: cavi telecom come sismometri, balene (DAS4Whales), treni e traffico, intrusioni, perdite. Per la pressione serve solo per le **variazioni rapide** (colpi d'ariete), non per il valore assoluto.

**DTS.** Il rapporto tra le righe Raman anti-Stokes e Stokes dipende dalla temperatura (∝ exp(−h·Δν / k·T)). Usi: pozzi, cavi di alta tensione, incendi in galleria, dighe e argini.

**DSS.** La luce interagisce con le onde acustiche del vetro; lo spostamento di frequenza Brillouin dipende da strain e temperatura:
- **Δν_B = C_ε·Δε + C_T·ΔT**, con C_ε ≈ 0,05 MHz/µε e C_T ≈ 1 MHz/°C;
- quindi **1 °C ≈ 20 µε**: la temperatura va compensata;
- **BOTDR**: un solo capo, meno preciso; **BOTDA**: due fasci dai due capi, più preciso, la fibra deve tornare all'interrogatore (anello);
- **OFDR Rayleigh**: risoluzione al mm e < 1 µε, ma solo su tratti corti;
- **FBG**: punti molto precisi, quasi-distribuito.

**Condizione chiave:** la fibra misura lo strain della struttura solo se è **solidale** (incollata o annegata). Una fibra in tubetto libero sente solo la temperatura e fa da **riferimento**. Nel caso MATRIS la fibra annegata nel composito della guaina è solidale per costruzione.

**Combinazione scelta:** DSS (pressione + temperatura) + DTS o fibra libera (solo temperatura) → per differenza la pressione. Eventualmente DAS per i transitori.

---

## 4. Dalla pressione alla fibra

### 4.1 La catena

```
pressione p(x,t) → deformazione della parete ε(x,t) → fibra → ε misurata → p stimata
   (EPANET)          (formula del tubo)                (DSS)   (rumore,       (DSP dell'utente)
                                                                temperatura)
```

Il tubo lo deforma la **pressione**, non il flusso; il flusso conta perché crea le perdite di carico, cioè le variazioni di pressione lungo il tubo. Lungo un tubo la pressione si interpola tra i due nodi EPANET.

### 4.2 Deformazione della parete

Tubo a parete sottile, fondi chiusi:
- circonferenziale: **ε_θ ≈ p·D·(2 − ν) / (4·t·E)**;
- assiale: ε_z ≈ p·D·(1 − 2ν) / (4·t·E), molto più piccola.

| Tubo | ε per 1 bar | Misurabile con DSS? |
|---|---|---|
| PE (DN110, t = 10 mm, E ≈ 1 GPa, ν ≈ 0,4) | ~ 400 µε | sì, molto bene |
| acciaio (DN100, t = 6 mm, E = 210 GPa, ν = 0,3) | ~ 4 µε | quasi no: vicino alla risoluzione Brillouin |

Sull'acciaio 1 °C (≈ 20 µε) vale come ~5 bar: la compensazione termica è critica.

**Attenzione relining (MATRIS):** la guaina è appoggiata al tubo ospite che la sostiene; la sua deformazione la decide soprattutto il tubo ospite. Se l'ospite è metallico o in cemento, la fibra nella guaina si deforma pochissimo. **Da verificare con OR2/OR4.**

### 4.3 Avvolgimento: l'elica è corretta

**ε_fibra = ε_θ·sin²α + ε_z·cos²α** (α = angolo rispetto all'asse del tubo)

| Posa | Cosa sente | Uso |
|---|---|---|
| dritta (α = 0°) | assiale | flessione, cedimenti; in tubetto libero, temperatura |
| ad anelli (α ≈ 90°) | circonferenziale pura | massima sensibilità, ma servono raccordi |
| **a elica** | miscela | il compromesso usato in pratica |

| α | sensibilità alla pressione (sin²α) | fibra per metro di tubo (1/cos α) | 1 m di fibra = |
|---|---|---|---|
| 45° | 50 % | 1,4 m | 71 cm di tubo |
| 60° | 75 % | 2,0 m | 50 cm |
| 70° | 88 % | 2,9 m | 34 cm |
| 80° | 97 % | 5,8 m | 17 cm |

- Passo dell'elica: p = 2πR / tan α.
- Raggio di curvatura dell'elica: R / sin²α ≥ R; per DN110 (R = 55 mm) va bene; le fibre G.657 reggono fino a 7,5–10 mm.
- Accanto all'elica si posa di solito una fibra dritta in tubetto libero (riferimento di temperatura).
- Se la guaina MATRIS è fatta per avvolgimento di filamenti, l'elica viene naturale.

---

## 5. Modelli matematici assodati

Ogni blocco è una funzione pura; il simulatore le compone.

| # | Blocco | Modello | Riferimento |
|---|---|---|---|
| 1 | pressione in regime | metodo del gradiente (EPANET) | Todini & Pilati 1988; Rossman (EPANET) |
| 1b | transitori | metodo delle caratteristiche (TSNet) | Wylie & Streeter, *Fluid Transients in Systems*, 1993 |
| 2 | pressione → parete | Lamé (parete spessa) / Barlow (sottile) | scienza delle costruzioni |
| 2b | PE viscoelastico | Kelvin–Voigt generalizzato (ritardo, creep) | Covas et al., *J. Hydraulic Research* 2004–2005 |
| 2c | guaina + tubo ospite | Lamé multistrato con contatto; laminazione classica | elasticità + teoria dei laminati |
| 3 | parete → fibra a elica | ε_f = ε_θ sin²α + ε_z cos²α | meccanica di base |
| 3b | trasferimento strain al vetro | shear-lag dell'interfaccia | Ansari & Libo, *J. Lightwave Technol.* 1998 |
| 4 | fibra → Brillouin | Δν_B = C_ε Δε + C_T ΔT | Horiguchi et al. 1989; Kurashima et al. 1990 |
| 4b | rumore DSS | incertezza in frequenza da SNR, larghezza di riga, passo di scansione; media sulla lunghezza dell'impulso | Soto & Thévenaz, *Optics Express* 2013 |
| 5 | DTS Raman | rapporto anti-Stokes/Stokes ∝ exp(−hΔν / kT) | Hartog 2017 |
| 6 | temperatura del tubo interrato | profondità + stagione | Kusuda & Achenbach 1965 |
| 7 | separare p e T | sistema lineare 2×2 | letteratura DSS |

```python
p      = idraulica(rete, t)                 # 1   EPANET / TSNet
eps_w  = parete(p, tubo)                    # 2   Lamé (+ viscoelasticità, + guaina)
eps_f  = fibra(eps_w, alfa, trasferimento)  # 3   elica + trasferimento
T      = temperatura(t, profondita)         # 6   Kusuda
nu_B   = brillouin(eps_f, T) + rumore_dss() # 4   misura DSS
T_m    = raman(T) + rumore_dts()            # 5   misura DTS
# l'utente riceve nu_B, T_m (anzi: L0 grezzo); le etichette sono p e T veri
```

**Meno solidi:** 2c (parametri della guaina MATRIS e del contatto con l'ospite), 2b (coefficienti del PE specifico), 4 (C_ε, C_T dipendono da fibra e rivestimento: si calibrano). **Tutti i riferimenti sono stati citati a memoria: verificarli prima di metterli in tesi.**

---

## 6. Framework e strumenti esistenti

**Conclusione: nessun framework fa tutta la catena** (rete idrica → misura DSS/DTS → LoRaWAN). Esistono pezzi. Questo è anche un argomento di originalità per la tesi.

**Elaborare dati DAS (Python, open source):** xdas (Xarray + Dask, dati più grandi della memoria), DASCore (base dell'ecosistema DASDAE, *Seismica* 2024), DASPy, Lightguide (pyrocko, beta), FiLark (streaming, preprint 2026).
→ Far uscire i dati in un formato compatibile con xdas/DASCore, così gli stessi script gireranno su dati reali.

**ML su DAS:** SeisBench DAS (da v0.12).

**Generare DAS sintetico:** Salvus (commerciale) e SPECFEM (open source) per onde sismiche; Rapagnani et al. (EGU24, codice non trovato); microsimulazione del traffico → DAS (Applied Sciences 2025: U-Net addestrate solo su sintetico funzionano su dati reali — buon precedente da citare).

**Brillouin / ottica:** codice MATLAB BOTDA/COTDR dell'Università di Cambridge (miglior riferimento per il modello di rumore BOTDA, da tradurre in Python); NumBAT (Brillouin in guide d'onda, troppo basso livello); OptiSystem (commerciale, nessun esempio BOTDA pronto); simulatore φ-OTDR (tesi Univ. of Manitoba).

**Idraulica:** EPANET/WNTR (regime), TSNet (transitori, su WNTR).

**Meccanica:** FEniCS, CalculiX, Code_Aster (open source), COMSOL, Abaqus (commerciali): servono solo per geometrie complesse; per un tubo bastano le formule.

**Lavori vicini da citare come stato dell'arte:** BAM (SMSI 2025, recipienti a pressione per idrogeno: strain misurato vs atteso dalla pressione → indicatore di danno; il più vicino concettualmente); Politecnico di Milano 2026 (fibra → campo di tensione con FE e surrogati); tesi Aalborg 2023 (sensore in fibra virtuale in FE, separazione strain/temperatura); FEM statistico con FBG.

**Dati reali:** nessun dataset DAS pubblico su perdite idriche trovato; dataset Mendeley (DOI 10.17632/tbrnp6vrnj.1) con accelerometri/idrofoni/pressione su banco perdite; due banchi DAS su tubi d'acqua in laboratorio (arXiv 2307.15374, 2508.04316), disponibilità dati da verificare.

---

## 7. Architettura del simulatore

### 7.1 Ingressi

- **Rete**: file EPANET `.inp` standard (si apre anche con EPANET/QGIS).
- **Parametri dei tubi**: YAML con default e override per tubo (materiale, diametro esterno, spessore, E, ν, profondità, eventuale guaina con spessore ed E).
- **Fibre**: un YAML per fibra:
  - `interrogatore`: nodo e tecnica (BOTDA, BOTDR, DTS, DAS);
  - `avvolgimento`: elica con `alfa_deg`;
  - `passo_campionamento_m`;
  - `percorso`: lista **ordinata** di tratti, ciascuno un tubo con verso (`{tubo: P1, da: J11}`) oppure un **tratto morto** (`{morto: 15}`, cavo che non sta su un tubo);
  - `ritorno`: solo per BOTDA, il cavo che riporta all'interrogatore.
- **Scenario**: durata, eventi, rumore, seed.

### 7.2 Regole della fibra (chiarite nella sessione)

- **Invio e lettura avvengono nello stesso punto**: l'interrogatore a un capo. Eccezione BOTDA: servono entrambi i capi, la fibra fa un anello e torna allo stesso strumento.
- **La fibra non si dirama**: è un percorso lineare. Per coprire una griglia: un percorso che ripassa su alcuni tratti, più fibre (una per ramo) o tratti morti.
- **La fibra non "manda" un segnale quando succede qualcosa**: l'interrogatore misura continuamente il profilo; un evento è una variazione locale alla distanza z; accorgersene è compito del DSP.

### 7.3 Prodotto del passo 1: la mappa

Per ogni campione lungo la fibra: `z_fibra_m, tratto, tubo, s_tubo_m, x, y`. Con l'elica, s_tubo avanza di `passo · cos α` per ogni passo di fibra.

### 7.4 Il segnale grezzo ha due assi temporali

Ogni impulso produce una **traccia** (luce di ritorno in funzione del tempo, cioè della posizione); il campionamento della traccia (centinaia di MHz) fissa il passo spaziale: 100 MHz ≈ 1 m. Le tracce si ripetono nel tempo → matrice **(tempo lento × posizione)**. Per la DSS c'è un asse in più: per ogni posizione si scansiona la **frequenza** e si ottiene lo spettro Brillouin (una curva lorentziana il cui picco si sposta con lo strain).

| Livello | Contenuto | Chi lo produce |
|---|---|---|
| **L0** | spettro Brillouin per posizione e acquisizione (+ tracce Stokes/anti-Stokes per il DTS), con rumore | simulatore |
| L1 | ν_B(z, t) | DSP: fit del picco |
| L2 | ε(z, t), T(z, t) | DSP: sistema 2×2 |
| L3 | pressione stimata, eventi | DSP: inversione + rilevamento |

### 7.5 Eventi

- **Idraulici** (perdita, rottura, manovra pompa): li calcola EPANET/WNTR (che sa spezzare un tubo e mettere una perdita a metà); i picchi improvvisi richiederanno TSNet.
- **Meccanici** (cedimento del terreno, schiacciamento): non idraulici, si sommano direttamente allo strain nel tratto.

### 7.6 Il "contratto" verso l'utente (bozza, da adattare a DSS/DTS)

```python
from waterfibersim import Simulator          # nome del pacchetto da decidere

ds = Simulator.from_yaml("scenari/base.yaml", seed=1).run()
ds.raw          # L0
ds.labels       # verità: p, T, ε, ν_B per canale e tempo; eventi
ds.channels     # canale → tubo, metri, x/y
ds.plot(); ds.save("out/")
```

```
python -m waterfibersim generate scenari/base.yaml --seed 1 --out out/
python -m waterfibersim batch    scenari/base.yaml --n 200 --randomize --out dataset/
```

Poi: `evaluate(stime, ds.labels)` con metriche (errore di pressione, precision/recall degli eventi, errore di localizzazione in m, ritardo di rilevamento) e `sim.stream()` per l'uso online.

Nota storica: la prima bozza del contratto era pensata per DAS/perdite (`waterfall [tempo, canale, banda]`, generatore "procedurale" con perdita = banda verticale, camion = macchia in movimento, colpo d'ariete = diagonale, fading = canali muti). Resta valida per un'eventuale estensione DAS.

---

## 8. Piano a passi

| Passo | Cosa | Uscita | Stato |
|---|---|---|---|
| **1** | rete di prova (serbatoio R1, adduttrice P0, griglia 3×3 J11…J33 con tubi da 100 m, utenze su J13, J31, J33), `tubi.yaml`, `fibra_A.yaml` | mappa metro di fibra → tubo + disegno rete con fibra | **progettato** nel README; file `.inp`/YAML e codice ancora da creare |
| 2 | pressione lungo la fibra da WNTR → strain → ν_B(z, t) | L1 vero, senza ottica | |
| 3 | L0: spettro Brillouin con rumore + fit del picco come DSP di esempio | verifica: dal grezzo si ritrova ν_B | |
| 4 | eventi: perdita (idraulica), cedimento (meccanico) | etichette | |
| 5 | temperatura (Kusuda) + DTS, separazione p/T | | |
| poi | DAS + transitori (TSNet); integrazione LoRaWAN | | |

**Verifiche del passo 1:** disegno della rete con la fibra colorata per distanza dall'interrogatore; lunghezza totale della fibra = tratti morti + tubi × 1/cos α; ogni tubo coperto compare con s_tubo da 0 alla sua lunghezza.

**Modo di lavorare:** un passo alla volta, ognuno verificabile da solo.

---

## 9. Integrazione futura con LoRaWAN

Da fare solo quando i due progetti saranno maturi. Schema emerso nella sessione:
- l'interrogatore diventa un nuovo tipo di dispositivo nell'emulatore (`radio/devices.py` + codec JS in `radio/codecs/`), come gli altri;
- trasmette **eventi compatti**, mai il dato grezzo: es. `t_sim` (4 B) + posizione (2 B) + classe (1 B) + intensità (1 B) + durata (2 B) ≈ 10 B, entro i 51 B di SF12 EU868;
- trasmissione su evento + heartbeat periodico, per il duty cycle dell'1 %: l'elaborazione pesante sta all'edge, accanto all'interrogatore;
- gli agenti dell'emulatore correlano la stessa anomalia vista da contatori di distretto, sensori di pressione e fibra.

Ordine di grandezza del grezzo DAS, per ricordare perché si fa edge: 1000 canali × 10 000 campioni/s × 2 B = 20 MB/s ≈ 1,7 TB/giorno.

---

## 10. Domande aperte e cose da fare

- [x] **Creare il repo su GitHub** e fare il push (fatto dall'utente).
- [ ] **Materiale del tubo ospite nel caso MATRIS**: decide se la misura di pressione nella guaina ha senso (§4.2). Chiedere a OR2/OR4 anche rigidezza del composito e tipo di produzione della guaina (avvolgimento di filamenti?).
- [ ] **Riallineare `docs/B-fibra-ottica-dfos.md`** all'obiettivo pressione/DSS+DTS (oggi è impostato su perdite/DAS). Precisare che Stajanca et al. 2018 riguarda perdite di **gas**.
- [ ] Schemi del documento in `.drawio.svg`: fatto quello dell'interrogatore; restano il waterfall (§6) e l'architettura DT (§8), da ripensare dopo il riallineamento.
- [ ] Passo 1: creare `rete/griglia_3x3.inp`, `rete/tubi.yaml`, `fibre/fibra_A.yaml` e il codice della mappa.
- [x] Decidere il nome del pacchetto Python e la struttura delle cartelle (vedi §13).
- [ ] Verificare tutti i riferimenti bibliografici prima della tesi: avviato, stato in [A-fonti.md](A-fonti.md).

---

## 11. Note tecniche sull'ambiente

- **Blender**: non installato sul sistema; lo script è stato verificato con `bpy` 5.0.1 (Blender come modulo Python) in un ambiente conda temporaneo con Python 3.11 (`pip install bpy`). Lo script gestisce i nomi che cambiano tra versioni (input del Principled BSDF, `surface_render_method` vs `blend_method`) e usa Cycles su CPU per il render senza display.
  - aprire la scena: `blender --python blender/tubo_fibra.py`
  - render: `blender -b --python blender/tubo_fibra.py -- --render out.png --save out.blend`
  - con il modulo: `python blender/tubo_fibra.py -- --render out.png`
- **Formato `.drawio.svg`**: SVG normale con il sorgente draw.io nell'attributo `content`; si vede come immagine e si modifica in draw.io / app.diagrams.net o con l'estensione VS Code *Draw.io Integration* (`hediet.vscode-drawio`). È stato generato con un piccolo script Python (stesso elenco di forme → SVG + XML mxGraph), non incluso nel repo.
- **WNTR**: non era installato nell'ambiente di sistema; `edge-slm-emulator` usa `owa-epanet` nell'env conda `cn`. Per WaterFiberSim servirà un ambiente proprio con `wntr`, `numpy`, `scipy`, `matplotlib`, `pyyaml`.
- Preferenze di lavoro: passi piccoli e verificati; i comandi di push/sudo/docker li lancia l'utente; nessuna riga di attribuzione a Claude nei commit.

---

## 12. Fonti

Strumenti e dati:
- [xdas](https://xdas.readthedocs.io/en/stable/) · [DASCore (Seismica)](https://seismica.library.mcgill.ca/article/view/1184) · [DASCore su PyPI](https://pypi.python.org/pypi/dascore) · [DASPy](https://www.github.com/HMZ-03/DASPy) · [Lightguide](https://github.com/pyrocko/lightguide) · [FiLark (arXiv 2605.20132)](https://arxiv.org/pdf/2605.20132)
- [SeisBench DAS (arXiv 2609.07558)](https://arxiv.org/pdf/2609.07558)
- [Salvus per DAS (EGU23)](https://meetingorganizer.copernicus.org/EGU23/EGU23-6915.html) · [SPECFEM per DAS (tesi Utrecht)](https://studenttheses.uu.nl/handle/20.500.12932/36981) · [Rapagnani et al. (EGU24)](https://meetingorganizer.copernicus.org/EGU24/EGU24-5936.html) · [DAS sintetico da microsimulazione del traffico](https://sumlab.unican.es/publicaciones/method-to-use-transport-microsimulation-models-to-create-synthetic-distributed-acoustic-sensing-datasets/)
- [Cambridge – codice MATLAB BOTDA/COTDR](https://www.repository.cam.ac.uk/handle/1810/248986) · [NumBAT](https://arxiv.org/pdf/1811.10219) · [OptiSystem + MATLAB per BOTDA](https://optiwave.com/forums/topic/joint-simulation-of-botda-system-by-optisystem-and-matlab/) · [OptiSystem](https://optiwave.com/?p=51107) · [Simulatore φ-OTDR (Univ. of Manitoba)](https://mspace.lib.umanitoba.ca/items/13cab5a6-2c31-4a0b-ace4-7a8ffb210c9e/full)
- [BAM – digital twin recipienti H₂ con DFOS](https://www.ama-science.org/proceedings/details/5962) · [Politecnico di Milano – fibra → campo di tensione](https://re.public.polimi.it/retrieve/878f750a-8ef9-42bd-bdfb-08cfeb7c6955/1-s2.0-S0045794926001550-main.pdf) · [Aalborg – simulazione termo-meccanica per fibra](https://projekter.aau.dk/projekter/files/537432842/Jensen__N.__2023____Thermo_mechanical_simulation_for_fiber_optic_measurement_systems.pdf) · [FEM statistico con FBG](https://arxiv.org/pdf/2103.13729)
- [Water pipe leak detection con fibra e AI (arXiv 2307.15374)](https://arxiv.org/pdf/2307.15374) · [Foundation model DAS (arXiv 2508.04316)](https://arxiv.org/pdf/2508.04316) · [Dataset perdite idriche, Data in Brief 2023](https://par.nsf.gov/servlets/purl/10407599) · [Stajanca et al. 2018 (gas)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6164018)

Bibliografia citata a memoria (da verificare):
- A. H. Hartog, *An Introduction to Distributed Optical Fibre Sensors*, CRC Press, 2017.
- P. Lu et al., "Distributed optical fiber sensing: Review and perspective", *Applied Physics Reviews* 6, 2019.
- E. Todini, S. Pilati, metodo del gradiente, 1988.
- E. B. Wylie, V. L. Streeter, *Fluid Transients in Systems*, 1993.
- D. Covas et al., viscoelasticità nei transitori idraulici, *J. Hydraulic Research*, 2004–2005.
- F. Ansari, Y. Libo, trasferimento di strain nei sensori in fibra, *J. Lightwave Technology*, 1998.
- T. Horiguchi et al., dipendenza dello spostamento Brillouin dallo strain, *IEEE Photonics Technology Letters*, 1989.
- T. Kurashima et al., effetti termici sullo spostamento Brillouin, *Applied Optics*, 1990.
- M. A. Soto, L. Thévenaz, modellazione delle prestazioni dei sensori Brillouin distribuiti, *Optics Express*, 2013.
- T. Kusuda, P. R. Achenbach, temperatura del suolo, ASHRAE, 1965.
- O. Hunaidi, W. T. Chu, 1999; Y. Gao et al., 2004 (acustica delle perdite in tubi plastici).
- K. A. Klise et al., WNTR, Sandia National Laboratories.

---

## 13. Seconda parte della sessione: decisioni e correzioni

### 13.1 Codice e ambiente

| Decisione | Motivo |
|---|---|
| Pacchetto `waterfibersim` in `src/`; **API Python e file di ingresso (nomi e chiavi YAML) in inglese**: `network/grid_3x3.inp`, `network/pipes.yaml`, `fibers/fiber_A.yaml`; commenti e documenti in italiano. (Prima si era deciso "dati in italiano": cambiato su richiesta dell'utente.) | l'utente finale è un informatico; un solo vocabolario tra file e codice |
| **owa-epanet 2.3.5 al posto di WNTR** | stessa libreria e versione di `edge-slm-emulator`, per non dover raccordare due motori idraulici |
| **Python 3.11** | owa-epanet 2.3.5 ha pacchetti precompilati solo per 3.11 (Linux anche 3.12); con 3.13 la compilazione fallisce per mancanza di SWIG. Scritto nella sezione INSTALL del README |
| `CLAUDE.md` resta **fuori da git** | richiesta dell'utente |
| Il `.blend` si genera con la **stessa versione di Blender** con cui lo si apre (l'utente ha la 4.2.19 LTS) | un file salvato con Blender 5.0 non si apre con la 4.2 |

Fatto: `rete/griglia_3x3.inp` (P12 ha diametro 78 mm per via della guaina), `rete/tubi.yaml`, `network.py` con i controlli di coerenza. La rete è verificata: pressioni tra 4,70 e 4,90 bar, portata in P0 tra 2,1 e 9,6 L/s.

### 13.2 Architettura del sensore (decisa)

- **Una sola fibra ad anello** sull'interrogatore BOTDA: porta A → **tratto a elica incollato** (sente ε + T) → giunzione → **tratto dritto libero in un tubetto** (sente solo T) → porta B. È la stessa architettura di Bertulessi et al. 2023 (fonte [\[B23\]](A-fonti.md#b23) in [A-fonti.md](A-fonti.md)).
- **Impulsi di interrogazione (pompa)** escono da A. **Luce di lettura (sonda)**, un tono ottico continuo a frequenza laser − Δν (Δν ≈ 10,8 GHz, scelta dal generatore RF), esce da B. **Si legge in A**, tramite il circolatore C2 e il fotodiodo.
- L'impulso **modula in ampiezza** la luce di lettura, punto per punto: il tempo dà la posizione, l'altezza del gradino in funzione di Δν dà lo spettro. Spiegazione completa in [B-fibra-ottica-dfos.md §2.1](B-fibra-ottica-dfos.md#21-come-funziona-la-botda-passo-per-passo).
- **L0 = P(z, Δν)**: lo spettro di guadagno Brillouin per ogni metro e ogni misura, con rumore. **L1 = picco ν_B(z, t)**.
- Ogni punto del tubo compare **due volte** nei dati: z₁ sull'elica e z₂ sul tratto dritto. La differenza tra i due separa pressione e temperatura.

**Formato della fibra (deciso):** si scrive solo il percorso di andata (`route`), con cavi di collegamento `lead` (prima "tratti morti"). Il tratto di riferimento ripercorre **sempre gli stessi tubi al contrario**, quindi non c'è più un `ritorno: {morto: …}`. Formato nel README §1.3.

### 13.3 Numeri corretti con le fonti

| Grandezza | Prima (a memoria) | Ora | Fonte |
|---|---|---|---|
| ε_θ per 1 bar, PE DN110 sp. 10 | ~400 µε (parete sottile) | ~309 µε (Lamé, superficie esterna) | formula e parametri di [\[B23\]](A-fonti.md#b23) |
| fibra a elica a 70° per 1 bar | ~360 µε → 18 MHz | ~277 µε → ~14 MHz | calcolo nostro |
| peso della temperatura sull'elica | 8 MHz/°C | ≈ 11 MHz/°C (α_HDPE = 200 µε/°C) | [\[B23\]](A-fonti.md#b23) |
| minimo misurabile per metro, con compensazione termica | ~0,2 bar | ~0,4 bar | calcolo nostro, **da rifare con il simulatore** |

Altri punti dalla fonte [\[B23\]](A-fonti.md#b23), utili per i passi successivi:
- il PE è viscoelastico, con un modello di Burgers e i suoi parametri in Tab. 2 (blocco 2b);
- la posa lascia una **pre-deformazione** diversa per ogni metro, quindi serve una misura di base.

### 13.4 Proposte in attesa di conferma

- Simulare una **"nota di partenza" diversa per ogni metro** di fibra (offset fisso, più alto sull'elica per la pre-deformazione della posa: in [\[B23\]](A-fonti.md#b23) Fig. 7a circa +105…+180 MHz, letti a occhio), fornire una **misura di base** a tubo vuoto e mettere l'offset vero nelle etichette. Spiegata con il disegno `docs/img/frequenza-a-riposo.png`.
- Valutare un contatto con Politecnico di Milano / Cohaerentia (autori di [\[B23\]](A-fonti.md#b23)) per avere dati reali di confronto.

### 13.4b La guaina MATRIS polimerizza in opera (informazione dell'utente)

La guaina arriva **floscia**, viene posizionata nel tubo e **polimerizza in opera** durante il relining, diventando rigida come la plastica. La fibra è **annegata** nel composito e viene ancorata dalla polimerizzazione: non è incollata né fissata col nastro come in [\[B23\]](A-fonti.md#b23). Conseguenze:
- il profilo a riposo nasce soprattutto dalla **deformazione residua di cura** (ritiro chimico + contrazione termica), non dalla tensione della posa. I valori di [\[B23\]](A-fonti.md#b23) Fig. 7a sono solo un **riferimento provvisorio**;
- la **misura di base** si può fare solo **dopo la cura**, a guaina rigida e a temperatura di esercizio;
- ogni installazione avrà il suo profilo a riposo;
- in più (da verificare), la stessa fibra potrebbe controllare la cura misurando la temperatura.

Nel formato della fibra: `bonding: embedded` (MATRIS) oppure `bonded` (fissata all'esterno, come in [\[B23\]](A-fonti.md#b23)).

**Domande per l'OR4:**
1. tipo di resina, ciclo e temperatura di cura;
2. quando la guaina floscia viene gonfiata contro il tubo, **si allarga**? Se sì, l'elica cambia angolo e tensione già in posa. **Non lo sappiamo**: l'angolo α di progetto potrebbe non essere quello finale;
3. materiale e rigidezza del tubo ospite (già in §10);
4. è possibile misurare il profilo a riposo dopo la cura su un campione?

### 13.4c Profilo a riposo nel simulatore (proposta)

Non una forma fissa, ma una somma di componenti per tratto: scostamento medio, pendenza (in salita, in discesa o piatta), ondulazioni lente, gradini ai giunti, e una deriva lenta opzionale. Solo lo scostamento medio ha un riferimento ([\[B23\]](A-fonti.md#b23)); il resto è un'**ipotesi** dichiarata. Disegno esplicativo: `docs/img/frequenza-a-riposo.png`.

### 13.4d Scenari di percorso (decisi)

I percorsi della fibra sono **scenari** conservati in `scenario_paths/` e usati per esperimenti diversi: A_main_line (1 fibra, 5 tubi, per collaudare il codice), B_serpentine (1 fibra, 10 tubi su 13, il massimo senza ripassi), C_two_fibers (2 fibre su 2 canali, 13 su 13). Uno scenario contiene la lista `fibers:`; ogni fibra ha `interrogator` (con `channel`), `sensing_leg`, `reference_leg`, `route` (tubi con `from`, cavi `lead` con `to`/`from`) e `junction_m`. Una fibra non passa due volte sullo stesso tubo. Figura `docs/img/scenario_paths.png` + `.drawio.svg`, generate dai YAML. Nella rete di prova `bonding: bonded` (fibra fissata all'esterno, come [\[B23\]](A-fonti.md#b23)); `embedded` per il caso MATRIS.

### 13.4e Simulazione: passi 1 e 2 fatti sullo scenario A

- `python -m waterfibersim map …`: mappa z → tubo (scenario A: 2001,5 m, 4004 campioni; ogni tubo due volte).
- **P0 (adduttrice in ghisa) non ha l'elica in nessuno scenario**: la fibra ci passa come cavo (`lead: 215`). Decisione dell'utente: sulla ghisa la fibra non misurerebbe niente (circa 0,2 MHz/bar).
- `python -m waterfibersim run …`: segnale vero ν_B(z, t) per 24 h ogni 15 min (`out/A/signal_true.npz`, matrici tempo × posizione). Fibra a elica sui tubi in PE circa +70 MHz (circa 4,8 bar), variazione giornaliera 2–3 MHz (circa 14,5 MHz/bar con E = 1,0 GPa), al limite dell'errore di una singola misura; riferimento 0.
- Il segnale è **ideale**: tabella "Cosa il simulatore non fa ancora" nel README §Passo 2.
- Moduli: `fiber.py`, `fibermap.py`, `hydraulics.py`, `mechanics.py` (Lamé + elica; i tubi risanati danno errore esplicito), `brillouin.py`, `simulate.py`, `plot.py`; 9 test.

**Piano MATRIS (Allegato 4, Piano di Sviluppo)**, letto il 2026-11-23:
- la rigidezza del laminato della guaina la progetta l'OR1 (Att. 1.2, Teoria Classica dei Laminati; deliverable D1.1);
- EKSO risana tubi di ogni materiale (acciaio, PVC, PRFV, PEAD, calcestruzzo);
- la guaina è CIPP con cura ad acqua, vapore o UV;
- l'OR7 prevede anche tubi nuovi in composito con sensori integrati, cioè senza tubo ospite.

Tre casi per il simulatore: tubo nuovo in composito / relining su ospite flessibile / relining su ospite rigido. Da chiedere: E e spessore del laminato (D1.1), materiali dei tubi ospite dei dimostratori. **In sospeso:** se citare testualmente il Piano (documento interno) in `A-fonti.md`.

### 13.4f Figura del segnale, consumi e profilo a riposo

- **`--demand-multiplier`**: moltiplica i consumi (EPANET *Demand Multiplier*). Con ×1 la rete di prova è poco carica (variazione giornaliera 0,1–0,2 bar, velocità massima 0,77 m/s); con ×3 la variazione è 0,7–1,5 bar. Per valutare il sensore servono consumi realistici o una rete reale (da decidere).
- **Profilo a riposo** (`rest_profile.py`, `--seed`, `--no-rest-profile`): elica, per ogni tubo, da inizio a fine con valori a caso in [105, 180] MHz; tratto libero +65 MHz; cavi 0; ondulazioni di circa 1 MHz. Valori da [\[B23\]](A-fonti.md#b23) Fig. 7a, forma per tubo = ipotesi. Etichette `rest_mhz`, `baseline_mhz` in `signal_true.npz`.
- **Figura `signal_true_<fibra>.png`** con 4 grafici: 1 frequenza assoluta a vuoto e con carico (con le annotazioni in bar per tubo), 2 differenza dalla misura di base, 3 mappa tempo × posizione, 4 andamento nel tempo a metà di **ogni** tubo coperto dall'elica. Il grafico "si vede o no?" è stato tolto su richiesta dell'utente (non diceva niente di utile). **Asse destro in bar su tutti i grafici in MHz** (preferenza dell'utente); nel grafico 1 annotazioni per tubo, perché lì la base cambia metro per metro.
- **Due calibrazioni** (chiarito con l'utente): la misura di base toglie la nota a riposo; il rapporto MHz → bar va calibrato a parte. Oggi il simulatore è ideale su entrambe; incertezze di misura volutamente escluse per ora.
- **Idee** per i passi 3–4: la notte (consumi minimi, pressione vicina alla statica) come momento in cui una perdita si vede meglio, e come possibile riferimento per verificare il rapporto MHz → bar in opera. Da verificare in letteratura (minimo flusso notturno).

### 13.4g Rete di prova ridimensionata (2026-11-24)

Né consumi ×1 né ×3 erano realistici: con ×1 velocità troppo basse (0,37 m/s di media al picco), con ×3 perdite di carico fino a 56 m/km (limite di progetto: 10 m/km). Il difetto era il dimensionamento dei tubi. Nuova rete: utenze 4 L/s ciascuna; P1, P11 DN160; P2, P12 DN125 (P12 risanato, guaina 6 mm); altri DN110 (PE100 SDR11); P0 ghisa con diametro interno 209,2 mm. Al picco: velocità 0,5–0,9 m/s nei tubi principali, perdita di carico ≤ 9,2 m/km, escursione di pressione circa 0,2 bar. Risultato: una rete ben progettata ha poca variazione di pressione da perdite di carico. `--demand-multiplier` resta solo per esperimenti di sensibilità; `out/A_x3` tolto. Sensibilità della fibra uguale su tutti i tubi (SDR costante).

**Scenari annotati:** A2 (tutta la domanda in fondo alla linea) e uno con quote diverse dei nodi. Superati dagli scenari semplici S0a/S0b/S1/S2 (§13.4i).

Fonti per i tubi (2026-11-24): manuale EPANET Tab. 3.2 (C dei tubi nuovi: P0 portato da 100 a 130), schede Uponor e Aliaxis (PE100 SDR11 ✅), Electrosteel (ghisa EN 545 DN200 K9: spessore 6,3 mm, diametro interno 209,4 mm). Norme EN 805, EN 12201-2, EN 545 a pagamento: l'utente chiederà l'accesso alla banca dati UNI della Biblioteca di ingegneria UniPA.

### 13.4h Profilo a riposo continuo (2026-11-24)

L'utente ha notato che, nella strada, il profilo a riposo saltava a ogni nodo EPANET: non fisico, perché la strada è un tubo solo e la fibra è avvolta senza interruzioni. Ora il profilo è continuo lungo un tratto di posa (punti di controllo casuali ogni ~300 m di fibra, `REST_KNOT_M`), e salta solo dove la posa riparte: dopo un cavo (pozzetto) o dove cambia il tubo (diametro esterno, materiale, guaina). Ipotesi ⚠️, nessun dato su condotte lunghe; accettate dall'utente in attesa di dati empirici. Nel pozzetto basta lo stesso interrogatore: le fibre si giuntano (nel simulatore: un `lead` tra due tubi).

### 13.4i Scenari semplici S0a, S0b, S1, S2 (2026-11-24)

Su richiesta dell'utente ("facciamo un passo indietro"): linea di 1 km, PE100 SDR11 DN110, interrogatore all'inizio, stessa fibra in tutti. S0a/S0b un tubo con un solo prelievo in fondo (3,3 L/s), in piano / in discesa 2 % con serbatoio in cima; S1/S2 strada con un rubinetto ogni 100 m (11 × 0,3 L/s), in piano / in discesa. Scenario con serbatoio a valle **scartato**: servirebbe una pompa di risalita.

Concetti chiariti con l'utente: pressione statica = dislivello tra pelo dell'acqua del serbatoio e punto (Stevino, conta l'altezza della colonna), pressione relativa (l'atmosfera si annulla), indipendente dal livello del mare; lungo una discesa la pressione cresce anche allontanandosi dal serbatoio; la quota dà una pendenza fissa, la perdita di carico la variazione nel tempo.

Figure: nuova mappa per le reti in linea (profilo con quote, pelo dell'acqua, rubinetti, interrogatore; fibra srotolata con cavi e giunzione etichettati); nel grafico 1 del segnale, con più di 5 tubi solo i bar su due livelli; titolo del grafico 4 corretto. `Network` legge anche quota, tipo e prelievo di base dei nodi.

### 13.4j Parametri dello strumento e incertezza attesa (2026-11-24)

- L'utente ha chiesto di ragionare sull'incertezza della strumentazione prima di tutto, partendo dalle **parametri**. Ha corretto due cose: il vecchio `sampling_step_m: 0.5` era un passo di calcolo scelto da me, non lo strumento ("non ci prendiamo in giro"); e i parametri veri sono **nel tempo**, non in metri.
- Ora nello scenario: `pulse_width_ns` e `adc_sample_rate_msps` (i metri si ricavano con Δz = c·t/(2n), stampati dal CLI); `freq_step_mhz`, `n_averages`, `scan_window_ghz` ([\[B23\]](A-fonti.md#b23) Tab. 1, fase II); `linewidth_mhz: 58`, `snr0_db: 0` a 2 m ([\[ST13\]](A-fonti.md#st13)); `attenuation_db_per_km: 0.2` ([\[ST13\]](A-fonti.md#st13)); `group_index: 1.468` (⚠️ a memoria: scheda Corning SMF-28 non scaricabile in automatico); `calc_step_m: 0.1` (passo di calcolo, ≤ 1/10 della risoluzione).
- Letto per intero Soto & Thévenaz 2013 [\[ST13\]](A-fonti.md#st13) (PDF fornito dall'utente, in `.gitignore`: licenza non verificata). Formula dell'incertezza sul picco (Eq. 7–9) validata contro i loro dati; con le impostazioni di [\[B23\]](A-fonti.md#b23) dà 0,41 MHz, vicino allo 0,5 MHz dichiarato. Incongruenza ⚠️: [\[B23\]](A-fonti.md#b23) dichiara SNR > 40 dB, che con [\[ST13\]](A-fonti.md#st13) darebbe incertezze 500 volte più piccole.
- Nuovo comando `instrument` (`instrument.py`): incertezza lungo la fibra in MHz, bar sull'elica e °C sul riferimento; tempo minimo di misura; controllo della finestra di scansione; figura `uncertainty_<fibra>.png`. Risultato: circa 0,03 bar per misura sull'elica, 0,045 bar dopo la sottrazione della base; la distanza conta poco sotto i 4 km.
- **Questione aperta principale:** compensazione della temperatura (errore del riferimento × circa 11 MHz/°C sull'elica ≈ 0,36 bar). Da decidere se affrontarla prima dello spettro con rumore (passo 3b).

### 13.4k Temperatura: fonti, segnale e compensazione (2026-11-24)

- L'utente ha scelto di affrontare la temperatura prima dello spettro con rumore, e di partire dal **terreno** (l'acqua dopo).
- **T1, fonti:** Stewart & Bilgin 2020 (PPI: dilatazione del PE assiale 144 µε/°C, circonferenziale circa 65 %; Poisson 0,42–0,49; stagione 11–15 °C in 90 giorni); Agudelo-Vera et al. 2017 (acqua alla temperatura del terreno a 1 m con permanenze ≥ 48 h; fino a 10 °C di differenza tra punti di una città); Performance Pipe PP 814 (144 µε/°C, tubo trattenuto). **Corretto** l'11 MHz/°C dell'elica: forbice 3,5 ([\[B23\]](A-fonti.md#b23) con K_T = 4) – 8 MHz/°C ([\[SB20\]](A-fonti.md#sb20), tubo trattenuto), da calibrare. Kusuda & Achenbach 1965 non letto (PDF troppo grande).
- **T2, segnale:** sezione `temperature` facoltativa nello scenario (`temperature.py`); scenari **S1t** (raffreddamento uniforme di 8 °C) e **S1th** (+ punto caldo di +3 °C su P6, scelto per mostrare l'effetto; l'utente ha chiesto due scenari separati). Il punto caldo è solo termico, non cambia la pressione; `delta_c` può essere anche negativo. Figure: pressione "APPARENTE" quando la temperatura non è compensata.
- **T3, compensazione** (`compensation.py`, comando `compensate`): senza compensare −3,3 bar di errore; con K giusto circa 0; con K agli estremi della forbice ±1,1–1,4 bar sistematici; errore casuale 0,24 bar per misura con il riferimento punto per punto, 0,056 bar mediandolo su 74 m, ma la media sfuma i punti caldi (fino a 0,58 bar ai bordi).
- **Raffinamento (su osservazione dell'utente dei "saltini"):** riferimento interpolato nel punto del tubo (prima: punto più vicino, scalini di 0,012 bar, ora 0,001); media mobile più corta (20 m: 0,47 bar ai bordi); media **adattiva** (filtro sigma, soglia 0,5 °C ⚠️): 0,19 bar, solo nelle rampe. Tutto senza rumore: la soglia va verificata al passo 3b.
- **Conclusioni:** il parametro critico è K (calibrazione in opera, metodo da cercare); la lunghezza della media del riferimento è un compromesso con l'uniformità del terreno; le variazioni nella giornata restano leggibili anche senza compensare.
- **Prossimo:** temperatura dell'acqua che segue i consumi (permanenze brevi nelle nostre reti), oppure passo 3b (spettro con rumore). Da decidere con l'utente.

### 13.4l Passo 3b: dato grezzo L0 (2026-11-24)

- `measure.py`, comando `measure`: spettri Brillouin rumorosi per ogni punto dello strumento (ogni 0,82 m), media su 2 m (finestra centrata), lorentziana di 58 MHz, rumore gaussiano σ = 1/SNR, misura di base rumorosa, etichette; una misura ogni `--every-min` (default 60). S1, 24 h: 25 × 4831 × 551, circa 130 MB (float16).
- Fit di esempio di Soto (parabola su ±FWHM/2, multi-passata): errore 0,50 MHz sull'elica contro 0,43 previsti; circa +17 % anche su spettri sintetici, attribuito alla forma lorentziana (il fattore √(3/4) dipende dalla funzione, [\[ST13\]](A-fonti.md#st13)). Alla giunzione spettri con più picchi: errori fino a 117 MHz (effetto reale della risoluzione).
- **Prossimo:** compensazione della temperatura sul dato rumoroso (S1t, S1th), per verificare la media adattiva e la sua soglia; poi la temperatura dell'acqua.

### 13.4m Compensazione sul dato rumoroso (2026-11-24)

- `compensate --measured`: compensazione sui picchi stimati dagli spettri rumorosi (S1t, S1th), con esclusione automatica dei punti a finestra mista (16 su S1).
- Media mobile 74 m: circa 0,06 bar per misura (modello T3 confermato). Media adattiva: con soglia fissa 0,5 °C non regge il rumore (prototipo: 0,24 bar); corretta con mediana su 10 m come confronto e soglia 2σ stimata dai dati: 0,050 bar casuale e conserva il punto caldo (0,22 contro 0,65 bar).
- **Scoperta:** il rumore della misura di base è congelato (stesso in ogni misura, non si media nel tempo): 0,049 bar con una misura di base, 0,018 con la media di 10. Indicazione pratica: misura di base come media di più misure (`--baseline-repeats`).
- **Prossimo:** temperatura dell'acqua che segue i consumi; restano aperti la calibrazione di K e l'indice di gruppo della fibra.

### 13.4n Posa MATRIS della fibra: decisione (2026-11-24)

Informazione e decisione dell'utente: nella realizzazione MATRIS **l'elica è annegata nella guaina polimerizzata** e **la fibra di ritorno è annegata nello stesso modo, ma dentro un tubetto in cui è libera di muoversi** (loose tube). Conseguenze:
- elica e ritorno stanno nello stesso materiale alla stessa distanza dall'acqua: vedono la stessa temperatura nello stesso istante (niente ritardi diversi);
- il ritorno, libero nel tubetto, non si deforma con la pressione e sente solo la temperatura (principio verificato in [\[B23\]](A-fonti.md#b23) Fig. 7c sul tratto libero); limiti da verificare su una scheda di cavo: lasco della fibra nel tubetto, attrito;
- la compensazione resta quella già simulata (S1t, S1th).
Opzione scartata: ritorno dritto e ancorato (sentirebbe anche la deformazione assiale, sistema 2×2).

### 13.4o Temperatura dell'acqua, S1w (2026-11-24)

- Fonti: Blokker et al. 2024 [\[BL24\]](A-fonti.md#bl24) (modello validato, Eq. 1–3, PDF CC BY in `docs/papers/`), Cincotta et al. 2024 [\[CI24\]](A-fonti.md#ci24); conducibilità del PE100 0,38 W/(m·K) da scheda (Oadby Plastics).
- Implementazione nel nostro codice (l'utente non è interessato a farlo fare a EPANET): `hydraulics.py` legge carichi, portate e velocità; `temperature.py` propaga la temperatura nodo per nodo, da monte a valle, quasi stazionario ora per ora.
- S1w: +2 °C alla sorgente; in fondo alla strada +0,13 °C di notte, +1,02 °C al picco; la variazione giornaliera della pressione apparente ha segno invertito; la compensazione la toglie.
- Chiarimenti con l'utente: i cavi (`lead`) misurano la temperatura del terreno, il ritorno quella del tubo/acqua; il ritardo termico della parete (minuti) è piccolo rispetto alle ore; con la posa MATRIS elica e ritorno vedono la stessa temperatura. Figura del sensore aggiornata (voce 10 "Cavi di collegamento", elica 6 MHz/°C).
- **Rischio principale individuato:** guaina dentro un ospite rigido e integro: la fibra a elica sente pochissimo la pressione (circa 0,05–0,2 MHz/bar). Idea dell'utente: strato comprimibile tra guaina e ospite; servirebbe una rigidezza confinata di circa 70 MPa (circa 100 volte meno di una guaina CIPP). Prossimo: modello a N strati e campagna di validazione.

### 13.4p Idea scartata (2026-11-24)

"La fibra che si sveglia" (su ospite rigido la fibra sente la pressione solo dove il tubo dietro cede, come indicatore di degrado): **scartata dall'utente**, troppo povera; segnala il cedimento quando è tardi e non misura la pressione, che è l'obiettivo. Per il tubo rigido resta da cercare una soluzione costruttiva (strato comprimibile o altro).

### 13.5 Documenti prodotti

- `blender/tubo_fibra.py` (spaccato 3D) + `blender/schema_sensore.py` → `blender/tubo_fibra.png`: figura con didascalie, fenomeno fisico, fibra "srotolata" e fonti.
- `docs/img/dfos-interrogatore.drawio.svg`: schema a blocchi BOTDA ad anello, ricavato da [\[B23\]](A-fonti.md#b23) Fig. 2.
- `docs/A-fonti.md`: ogni affermazione con fonte, citazione testuale e stato; prodotti commerciali.
- `docs/papers/sensors-23-06205-v2.pdf`: [\[B23\]](A-fonti.md#b23), licenza CC BY.

### 13.6 Prossimo passo

Passo 3b e compensazione sul dato rumoroso fatti (§13.4l, §13.4m). Prossimo: temperatura dell'acqua che segue i consumi.

<!-- nav-fondo -->

| [← Appendice B. Approfondimento sulla fibra](B-fibra-ottica-dfos.md) | [📖 Indice](00-indice.md)<br><sub>appendici</sub> |   |
|:---|:---:|---:|
<!-- /nav-fondo -->
