# Fonti e stato di verifica

Questo file elenca le affermazioni tecniche usate nel progetto: nella figura [blender/tubo_fibra.png](../blender/tubo_fibra.png), nel README e nei parametri del simulatore. Per ognuna dice da dove viene e se è stata verificata.

Le fonti ammesse sono articoli scientifici, libri, schede tecniche di prodotti e norme. Non sono ammessi blog né pagine divulgative.

**Legenda dello stato:**
- ✅ **verificata**: letta nella fonte; la citazione è testuale;
- 🧮 **calcolo nostro**: derivata con formule e parametri presi da fonti verificate;
- ⚠️ **da verificare**: la fonte esiste ma non è stata letta, oppure il valore è citato a memoria.

Ultimo aggiornamento: 2026-11-23.

---

## Fonti principali

| Sigla | Riferimento | Dove si trova |
|---|---|---|
| **[B23]** | M. Bertulessi, D. F. Bignami, I. Boschini, M. Longoni, G. Menduni, J. Morosi, "Experimental Investigations of Distributed Fiber Optic Sensors for Water Pipeline Monitoring", *Sensors* 23(13), 6205, 2023. DOI [10.3390/s23136205](https://doi.org/10.3390/s23136205). Politecnico di Milano + Cohaerentia S.r.l. Licenza CC BY | [docs/papers/sensors-23-06205-v2.pdf](papers/sensors-23-06205-v2.pdf) |
| **[OZ]** | OZ Optics, *Fiber Optic Distributed Strain and Temperature Sensors (DSTS) – BOTDA Module*, scheda tecnica DTS0115, 1 marzo 2025 | <https://www.ozoptics.com/ALLNEW_PDF/DTS0115.pdf> |
| **[DIT]** | Prysmian, *DITEST – Distributed Temperature and Strain Interrogator*, scheda tecnica | <https://asean.prysmian.com/sites/asean.prysmian.com/files/media/documents/Prysmian_DITEST.pdf> |

[B23] è il riferimento più vicino a questo progetto. È un sistema BOTDA su tubi in HDPE con la fibra **avvolta a elica** e un tratto di **ritorno libero per compensare la temperatura**: la stessa architettura disegnata nella figura.

Differenza da tenere a mente: in [B23] la fibra è fissata **all'esterno** del tubo con nastro adesivo, mentre nel caso MATRIS è annegata nella guaina. Il trasferimento della deformazione alla fibra (blocco 3b) può quindi essere diverso.

---

## Affermazioni

### Architettura del sensore

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Fibra a elica incollata al tubo per lo strain, tratto di ritorno libero per la temperatura | ✅ | [B23], didascalia della Fig. 2: *"In yellow is the helically wrapped optical fiber bonded to the HDPE pipe for strain sensing, and in red is the returned fiber, loosely fixed to the pipe, for temperature compensation."* Nel testo, §2.1: *"a portion of the sensing cable returning to the interrogator is loosely fixed to the pipe for the thermal effect compensation on DFOS measurement"* |
| La BOTDA usa due laser in versi opposti nello stesso anello di fibra (uno a impulsi, uno continuo) | ✅ | [OZ]: *"The typical DSTS BOTDA sensor configuration requires two lasers that are directed in opposite directions through the same loop of fiber (one laser operating continuously, the other pulsed)."* |
| La BOTDA richiede i due capi della fibra; la BOTDR ne usa uno solo | ✅ | [OZ], modulo d'ordine: *"BOTDA module (requires both ends of fiber to be connected to DSTS)"*. [OZ]: *"the sensor fiber must be looped or mirrored"*. [DIT]: *"Sensor configuration: Loop (2 fibers/channel) or Single-ended"* |
| La sonda continua entra dal capo lontano della fibra | ✅ | [B23], §2.1: *"a continuous-wave (CW) probe signal launched from the far end of the sensing fiber"* |
| Le due luci vengono dallo stesso laser, diviso da un accoppiatore 3 dB; la sonda è ottenuta con un modulatore Mach-Zehnder pilotato da un generatore RF | ✅ | [B23], §2.1: *"The light coming from a 1530 nm Distributed Feedback (DFB) laser is divided into two branches by a 3 dB optical coupler. The top branch is sinusoidally modulated by a Mach–Zehnder Modulator (MZM) driven by an RF generator to provide a continuous-wave (CW) probe signal"* |
| Impulsi di pompa di 20 ns (≈ 2 m di risoluzione), ripetuti a 30 kHz, amplificati da un EDFA | ✅ | [B23], §2.1: *"another Mach–Zehnder modulator, driven by a pulse generator and followed by an Erbium Doped Fiber Amplifier (EDFA), is used to generate 20 ns pump pulses (equivalent to a 2 m spatial resolution) with a 30 kHz repetition rate"* |
| La luce di lettura si legge al capo da cui partono gli impulsi, tramite un circolatore e un fotodiodo | ✅ | [B23], §2.1: *"launched into the sensing fiber from a second optical circulator. The same circulator also routs the probe signal to a 125 MHz photodetector (PD)"* |
| Campionamento a 125 MS/s = un campione ogni 0,8 m | ✅ | [B23], §2.1: *"a 125 MS/s Analog-to-Digital Converter (ADC) card (equivalent to an 80 cm spatial sampling)"* |
| La scansione di Δν su 1 GHz equivale a un intervallo di 20 mε | ✅ | [B23], §2.1: *"scanned over a 1 GHz range (equivalent to a dynamic range of 20 mε)"* |
| Per ogni posizione, la scansione in frequenza ricostruisce lo spettro di guadagno Brillouin, il cui massimo è la BFS | ✅ | [B23], §2.1: *"For each position along the sensing fiber, the frequency scan of the probe light allows us to reconstruct the Brillouin Gain Spectrum (BGS) … The specific frequency corresponding to the maximum of the BGS—called the Brillouin Frequency Shift (BFS)—depends on the local temperature and strain"* |
| Le due frequenze differiscono di circa lo 0,005 % (≈ 0,08 nm) | 🧮 | 10,8 GHz / (c / 1530 nm ≈ 196 THz) ≈ 5,5·10⁻⁵ |
| 1 MHz di errore su Δν vale circa 20 µε | 🧮 | 1 / C_ε, con C_ε ≈ 0,05 MHz/µε ([B23]) |
| L'impulso modula in ampiezza la luce di lettura; nel tempo, la potenza letta in A riproduce il profilo lungo la fibra | 🧮 | Riformulazione di [B23] §2.1 e [OZ] (amplificazione localizzata con campionamento di tipo OTDR: *"detected and localized using an OTDR-type sampling apparatus"*) |
| Lo scambio di energia avviene solo se Δν = ν_B per conservazione dell'energia (pompa → sonda + onda acustica) | ⚠️ | Fisica dello scattering Brillouin stimolato, da manuale; fonte da trovare (per esempio Hartog 2017 o Bao & Chen 2011) |
| Esiste anche la configurazione a perdita (sonda più alta della pompa, che cede energia) | ⚠️ | Da trovare una fonte |

### Fenomeno fisico (Brillouin)

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Lo spostamento Brillouin è di circa 10,8 GHz (a 1530–1550 nm) | ✅ | [B23], §2.1: *"Its frequency is downshifted by approximately 10.8 GHz from the pump frequency"* |
| Quando la differenza di frequenza tra i due laser è uguale alla frequenza Brillouin, la sonda viene amplificata; si scansiona la differenza e si cerca il picco | ✅ | [OZ]: *"When the frequency difference between the two lasers is equal to the 'Brillouin frequency' of the fiber, there is a strong interaction … This interaction causes a strong amplification … it is necessary to map out the Brillouin spectrum by scanning the frequency difference … and fitting the peak"* |
| Δν_B = C_T·ΔT + C_ε·ε, con C_T ≈ 1 MHz/°C e C_ε ≈ 0,05 MHz/µε | ✅ con riserva | [B23], §2.1, Eq. 1: *"correspond to 1 MHz/°C and 0.05 MHz/µε, respectively [35]. However, these parameters are highly influenced by the cable coating properties and the bonding conditions, which can modify their value"*. La loro fonte primaria è V. Lanticq et al., "Brillouin sensing cable: Design and experimental validation", *IEEE Sensors J.* 8, 1194–1201, 2008 (⚠️ non letta) |
| La dipendenza lineare dello spostamento Brillouin dallo strain è nota dal 1989 | ⚠️ | T. Horiguchi, T. Kurashima, M. Tateda, "Tensile strain dependence of Brillouin frequency shift in silica optical fibers", *IEEE Photon. Technol. Lett.* 1(5), 107–108, 1989. La citazione esiste, il contenuto non è stato letto |
| La luce nella fibra percorre circa 1 m ogni 5 ns; 10 ns di andata e ritorno corrispondono a 1 m | 🧮 | Fisica di base: v = c/n con n ≈ 1,47, quindi v ≈ 2,04·10⁸ m/s, cioè circa 4,9 ns/m |
| "La fibra suona come una corda di chitarra" | — | Analogia didattica, non un'affermazione quantitativa |

### Prestazioni degli strumenti (rumore e accuratezza)

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Accuratezza tipica: circa 10 µε (0,5 MHz) e 0,5 °C | ✅ | [B23], §2.1: *"The measurement accuracy of the employed BOTDA interrogator has been verified to be better than 0.5 °C/10 µε."* |
| Accuratezza dichiarata da un costruttore: ±2 µε, ±0,1 °C (2σ) | ✅ | [OZ]: *"Strain Accuracy (2σ) ± 2 με (Whole sensing range for BOTDA)"*, *"Temperature Accuracy (2σ) ± 0.1°C"* |
| Su lunghe distanze la ripetibilità peggiora molto | ✅ | [DIT]: *"Temperature and Strain Repeatability, 1σ (typical): < 2 °C or < 40 με for 80 km, G652 fiber, 5 m spatial resolution and 20 minutes measurement time."* |
| L'incertezza sul picco dipende da SNR, larghezza di riga e passo di scansione | ⚠️ | M. A. Soto, L. Thévenaz, "Modeling and evaluating the performance of Brillouin distributed optical fiber sensors", *Opt. Express* 21(25), 31347–31366, 2013, DOI 10.1364/OE.21.031347. Accesso libero: [EPFL Infoscience](https://infoscience.epfl.ch/record/191250/files/oe-21-25-31347.pdf?version=1). **Da leggere prima del passo 3** (modello del rumore) |

### Meccanica del tubo in PE

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Deformazione circonferenziale sulla superficie esterna: ε_θ = (2−ν)·β²/(1−β²)·p/E, con β = raggio interno / raggio esterno | ✅ | [B23], Eq. 4–6 (fonte primaria: G. Petrucci, *Lezioni di Costruzione di Macchine*, Palermo, 2002) |
| HDPE: E₁ = 1050 MPa, ν = 0,4 | ✅ | [B23], Tab. 2 |
| HDPE: dilatazione termica α = 200 µε/°C | ✅ | [B23], Eq. 9: *"α_HDPE is assumed equal to 200 µε/°C"*. Le schede dei compound PE100 riportano 1,3–1,8·10⁻⁴ /K (ISO 11359-2) |
| Il PE ha comportamento viscoelastico (creep): modello di Burgers con E₁, E₂, η₂, η₃ | ✅ | [B23], Eq. 7–8 e Tab. 2 (per PN10: E₂ = 1,65·10³ MPa, η₂ = 2,04·10⁶ MPa·s, η₃ = 2,13·10⁸ MPa·s) |
| Tubo PE DN110, spessore 10 mm: ε_θ ≈ 309 µε per bar | 🧮 | Formula e parametri di [B23]; β = 45/55 |
| Deformazione assiale con fondi chiusi: ε_z = (1−2ν)·β²/(1−β²)·p/E ≈ 39 µε per bar | 🧮 | Lamé, tubo a fondi chiusi (scienza delle costruzioni) |
| Fibra a elica: ε_f = ε_θ·sin²α + ε_z·cos²α; con α = 70° ≈ 277 µε per bar, cioè circa 14 MHz | 🧮 | Trasformazione della deformazione lungo una direzione (meccanica di base) |
| Sull'elica la temperatura pesa circa 1 + 0,05 × 200 ≈ 11 MHz/°C | 🧮 | Coefficienti di [B23]. La fibra solidale al tubo segue la dilatazione termica del PE, che è isotropa e quindi non dipende da α. [B23] aggiunge un coefficiente empirico K_T per l'inerzia termica del tubo |
| Ordine di grandezza misurato: 73 MHz a 5 bar e 200 MHz a 10 bar rispetto a 0 bar (tubo **PN16**, §3.1: *"BFS profiles and raw BGS measured by the BOTDA interrogator on the PN16 pipe"*) | ✅ | [B23], §3.1: *"a clear shift of 73 and 200 MHz due to increased hoop strain with respect to the reference 0 bar BGS is evident"* |

### Misura di base e minimo misurabile

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Ogni metro di fibra ha una "nota di partenza" propria, dovuta anche alla pre-deformazione della posa: serve una misura di base | ✅ | [B23], §2.1: *"By considering the BFS with respect to a reference state, it is possible to eliminate the pre-strain component on the DFOS cable caused by the installation procedure."* §3.1: la differenza della curva a 0 bar sul tratto avvolto *"is clearly due to pre-strain induced during the installation"* |
| A riposo (0 bar) la frequenza Brillouin non è uguale lungo la fibra: sull'elica circa +180 MHz all'inizio e +105 MHz alla fine rispetto ai cavi (circa 10 880 MHz); sul tratto libero circa +65 MHz | ✅ forma, ⚠️ valori | [B23], Fig. 7a (tubo PN16), curva 0 bar. **Valori letti a occhio dal grafico.** Il motivo dell'aumento sull'elica è dichiarato (pre-deformazione della posa); quello sul tratto libero no. Disegno esplicativo: [img/frequenza-a-riposo.png](img/frequenza-a-riposo.png) |
| Nel caso MATRIS la fibra è annegata nella guaina, che polimerizza in opera: il profilo a riposo nasce soprattutto dalla deformazione residua di cura (ritiro chimico della resina + contrazione termica dopo la cura) | ⚠️ | Informazione di progetto (utente, 2026-11-23). Il fenomeno è misurato con fibre annegate in laminati compositi, anche con BOTDA: Ito, Takeda, Obo, Minakuchi, cure strain in laminati CFRP spessi con PPP-BOTDA ([record](https://katalog.lib.cas.cz/KNAV/EdsRecord/edsair,edsair.doi...........320e86439b22066e2bbdd261e391e72f)); laminati spessi con FBG + Luna OFDR, *"the chemical shrinkage is the dominant driver of residual stress build-up"* ([FPCM17](https://ecm-academics.plymouth.ac.uk/jsummerscales/fpcm/fpcm17/FPCM17_59_Tsavea.pdf)); [OSTI 226060](https://www.osti.gov/biblio/226060-measurement-process-induced-strains-composite-materials-using-embedded-fiber-optic-sensors). **Non letti**; nessuno riguarda tubi o guaine |
| Durante la cura di una guaina CIPP la fibra può misurare la temperatura e verificare la polimerizzazione | ⚠️ | Brevetti: [US12291944](https://patents.google.com/patent/US12291944), [US 2012/0261050](https://patents.justia.com/patent/20120261050). Non letti |
| Con un'accuratezza di 10 µε, in un tubo PN10 da 63 mm si misurano variazioni sopra 0,016 bar | ✅ | [B23], §4: *"The strain accuracy is 10 µε, which means that if we consider a PN10 HDPE pipe with an external diameter of 63 mm, all pressure variations higher than 0.016 bar produce a measurable hoop strain."* **Questo conto non include l'errore della compensazione di temperatura** |
| Compensare la temperatura è il limite pratico | ✅ in parte | [B23], §3.1: *"the loose part of the DFOS sensor layout measured a temperature variation of up to 4 °C. This variation involves thermal deformation that is not recovered in the unloading stage"* |
| Con la compensazione termica, l'errore sul singolo metro e sulla singola misura è di circa 0,4 bar (PE DN110, elica a 70°) | 🧮 ⚠️ | Stima nostra: 0,5 MHz di rumore sul ritorno → 0,5 °C → 0,5 × 11 MHz sull'elica → circa 5,5 MHz, cioè circa 0,4 bar con 14 MHz/bar. **Da rifare con il simulatore** (passo 3) |
| Sull'acciaio la pressione è quasi impossibile da misurare | 🧮 ⚠️ | Stessa formula, con E = 210 GPa. Va ricontrollata con i parametri del tubo ospite MATRIS |

---

## Prodotti commerciali

Verificato il 2026-11-23. **I componenti si comprano; il sistema completo, cioè un tubo con fibra integrata letto da una BOTDA per misurare la pressione dell'acqua, non è risultato in vendita.** Oggi è a livello di ricerca e di prove pilota.

### Interrogatori Brillouin

| Prodotto | Tecnica | Configurazione | Stato | Fonte |
|---|---|---|---|---|
| Prysmian **DITEST** | BOTDA e BOTDR | *"Loop (2 fibers/channel) or Single-ended"*; BOTDA fino a 80 km (anello di 160 km) | ✅ scheda letta | [scheda](https://asean.prysmian.com/sites/asean.prysmian.com/files/media/documents/Prysmian_DITEST.pdf) |
| OZ Optics **Foresight DSTS**, modulo BOTDA | BOTDA (combinazione con BOTDR opzionale) | *"requires both ends of fiber to be connected"*; ±2 µε, ±0,1 °C (2σ); risoluzione da 0,1 a 50 m | ✅ scheda letta | [DTS0115](https://www.ozoptics.com/ALLNEW_PDF/DTS0115.pdf) |
| fibrisTerre **fTB 5020** (Polytec) | BOFDA (dominio della frequenza) | ad anello | ⚠️ solo dal riassunto della ricerca | [scheda](https://polytec.com/fileadmin/website/optical-systems/faseroptische-messtechnik/pdf/ftb5020-datenblatt.pdf) |
| Neubrex **NBX-7031** | Rayleigh TW-COTDR + Brillouin PPP-BOTDA | — | ⚠️ citato da un rivenditore, scheda del produttore non letta | [Solexperts](https://www.solexperts.com/files/downloads/FP_Mesures_fibre_optique_en.pdf) |
| Viavi **MTS-8000 DTSS** | BOTDR (un solo capo) | un solo capo | ⚠️ scheda trovata, non letta | [scheda](https://www.lasercomponents.com/fileadmin/user_upload/home/Datasheets/viavi/mts-8000-dtss.pdf) |
| **Cohaerentia** S.r.l. (Milano) | BOTDA | ad anello | ⚠️ è l'interrogatore usato in [B23]; nessuna pagina prodotto trovata | [B23] |

### Cavi sensore

Prysmian OptiStrain, Solifos BRUsens e Clearfield producono cavi per misure di strain e temperatura. ⚠️ Sono emersi dalla ricerca ma le schede non sono state lette: [Prysmian OptiStrain](https://na.prysmian.com/sites/na.prysmian.com/files/media/products/TLS-DS-D-701-DFS-Sensing-Cable-with-OptiStrain.pdf) · [Solifos](https://solifos.com/en/downloads-sensing/).

### Tubi con fibra integrata

| Caso | Cosa fa | Pressione dell'acqua? | Prodotto in vendita? | Fonte |
|---|---|---|---|---|
| Politecnico di Milano + Cohaerentia | fibra a elica fissata all'esterno di tubi HDPE, BOTDA | **sì** | **no**: §4, *"Future developments will be focused on … the industrial production of HDPE pipes 'natively smart,' in which DFOS cables are integrated into the pipeline surface during the extrusion process"* | [B23] ✅ |
| Aquaspira Ltd (UK) | fibra annegata con saldatura a caldo in HDPE su tubi compositi acciaio/plastica, *"either during the pipeline's manufacture or pre-/post-installation on site"*; Rayleigh OFDR (Luna ODiSI 6100) | no: carichi del traffico sul tubo interrato | non dichiarato; si parla di *"commercial trials"* | N. J. Cassidy et al., *Sensors* 24(4), 1298, 2024, DOI [10.3390/s24041298](https://doi.org/10.3390/s24041298) ✅ (letto tramite riassunto testuale, non dal PDF) |
| HBM FiberSensing | sensori FBG (puntuali) su una condotta forzata in acciaio a 100 bar | sì (deformazione della parete) | installazione su progetto | [nota applicativa](https://www.hbm.com/fileadmin/mediapool/files/technical-articles-technotes-white-papers/High_Pressure_Water_Pipe_-_Application_Note_en.pdf) ⚠️ non letta |
| UC Berkeley + EBMUD | cavo distribuito per lo strain, posato in trincea durante la costruzione | — | progetto di ricerca | [pagina](https://geomechanics.berkeley.edu/news/dms_ebmud/) ⚠️ non letta |

---

## Citate nel dump della sessione e ancora da verificare

Vengono dal [dump del 2026-11-23](sessione-2026-11-23.md) e sono **citate a memoria**:

- [ ] E. Todini, S. Pilati, metodo del gradiente, 1988.
- [ ] L. A. Rossman, *EPANET 2 Users Manual*, US EPA.
- [ ] E. B. Wylie, V. L. Streeter, *Fluid Transients in Systems*, Prentice Hall, 1993.
- [ ] D. Covas et al., viscoelasticità nei transitori, *J. Hydraulic Research*, 2004–2005. Collegamento: [B23] usa il modello di Burgers con fonti diverse (Elleuch & Taktak 2006; Fathi-Moghadam & Kiani 2019).
- [ ] F. Ansari, Y. Libo, trasferimento di strain, *J. Lightwave Technology*, 1998.
- [ ] T. Kurashima et al., dipendenza termica dello spostamento Brillouin, *Applied Optics*, 1990.
- [ ] T. Kusuda, P. R. Achenbach, temperatura del suolo, ASHRAE, 1965.
- [ ] A. H. Hartog, *An Introduction to Distributed Optical Fibre Sensors*, CRC Press, 2017.
- [ ] X. Bao, L. Chen, "Recent Progress in Brillouin Scattering Based Fiber Sensors", *Sensors* 11(4), 4152–4187, 2011. Esiste ([PMC3231321](https://pmc.ncbi.nlm.nih.gov/articles/PMC3231321/)), non letta.

**Correzione rispetto al dump.** Il dump (§4.2) stima per un tubo in PE DN110 "~400 µε per bar" con la formula a parete sottile sul diametro medio. Con la formula di Lamé sulla superficie esterna usata da [B23] vengono circa 309 µε. Stesso ordine di grandezza, ma per il simulatore si usa la formula di [B23].
