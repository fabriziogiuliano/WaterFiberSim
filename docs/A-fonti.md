<!-- nav -->
| [← 11. Risultati e questioni aperte](11-risultati-e-questioni-aperte.md) | [📖 Indice](00-indice.md)<br><sub>appendici</sub> | [Appendice B. Approfondimento sulla fibra →](B-fibra-ottica-dfos.md) |
|:---|:---:|---:|
<!-- /nav -->

# Appendice A — Fonti e stato di verifica

Questo file elenca le affermazioni tecniche usate nel progetto: nella figura [blender/tubo_fibra.png](../blender/tubo_fibra.png), nel README e nei parametri del simulatore. Per ognuna dice da dove viene e se è stata verificata.

Le fonti ammesse sono articoli scientifici, libri, schede tecniche di prodotti e norme. Non sono ammessi blog né pagine divulgative.

**Legenda dello stato:**
- ✅ **verificata**: letta nella fonte; la citazione è testuale;
- 🧮 **calcolo nostro**: derivata con formule e parametri presi da fonti verificate;
- ⚠️ **da verificare**: la fonte esiste ma non è stata letta, oppure il valore è citato a memoria.

Ultimo aggiornamento: 2026-11-23.

---

## Fonti principali

Ogni fonte ha un titolo con la sua sigla: i riferimenti nel libro portano qui.

### B23

M. Bertulessi, D. F. Bignami, I. Boschini, M. Longoni, G. Menduni, J. Morosi, "Experimental Investigations of Distributed Fiber Optic Sensors for Water Pipeline Monitoring", *Sensors* 23(13), 6205, 2023. DOI [10.3390/s23136205](https://doi.org/10.3390/s23136205). Politecnico di Milano + Cohaerentia S.r.l. Licenza CC BY  
Dove si trova: [docs/papers/sensors-23-06205-v2.pdf](papers/sensors-23-06205-v2.pdf)

### OZ

OZ Optics, *Fiber Optic Distributed Strain and Temperature Sensors (DSTS) – BOTDA Module*, scheda tecnica DTS0115, 1 marzo 2025  
Dove si trova: <https://www.ozoptics.com/ALLNEW_PDF/DTS0115.pdf>

### DIT

Prysmian, *DITEST – Distributed Temperature and Strain Interrogator*, scheda tecnica  
Dove si trova: <https://asean.prysmian.com/sites/asean.prysmian.com/files/media/documents/Prysmian_DITEST.pdf>

### ST13

M. A. Soto, L. Thévenaz, "Modeling and evaluating the performance of Brillouin distributed optical fiber sensors", *Opt. Express* 21(25), 31347–31366, 2013. DOI [10.1364/OE.21.031347](https://doi.org/10.1364/OE.21.031347). EPFL. Accesso libero  
Dove si trova: [docs/papers/oe-21-25-31347.pdf](papers/oe-21-25-31347.pdf)

### SB20

H. E. Stewart, Ö. Bilgin, *Thermal Stresses in HDPE Water Pipes*, Final Report to the Plastics Pipe Institute (PPI), agosto 2020  
Dove si trova: <https://conduitcalc.plasticpipe.org/pdf/ppi-stewart-and-bilgin-thermal-hdpe-final-report.pdf>

### AV17

C. M. Agudelo-Vera, M. Blokker, H. de Kater, R. Lafort, "Identifying (subsurface) anthropogenic heat sources that influence temperature in the drinking water distribution system", *Drink. Water Eng. Sci.* 10, 83–91, 2017. DOI [10.5194/dwes-10-83-2017](https://doi.org/10.5194/dwes-10-83-2017). Licenza CC BY 3.0  
Dove si trova: <https://dwes.copernicus.org/articles/10/83/2017/dwes-10-83-2017.pdf>

### PP814

Performance Pipe (Chevron Phillips Chemical), *Technical Note PP 814-TN: Engineering Considerations for Temperature Change*  
Dove si trova: <https://www.cpchem.com/sites/default/files/2020-04/PP%20814-TN%20Thermal%20Effects.pdf>

### BL24

E. J. M. Blokker, Q. Pan, K. van Laarhoven, "Validation of an Enhanced Drinking Water Temperature Model during Distribution", *Water* 16(19), 2796, 2024. DOI [10.3390/w16192796](https://doi.org/10.3390/w16192796). KWR / TU Delft. Licenza CC BY  
Dove si trova: [docs/papers/water-16-02796-v2.pdf](papers/water-16-02796-v2.pdf) (copia anche in [TU Delft](https://repository.tudelft.nl/file/File_f998b505-03bc-484a-8e61-77a60e311b3f))

### CI24

C. Cincotta, M. Blokker, C. Bragalli, Z. Kapelan, "Spatial Analysis of Water Temperature in a Drinking Water Distribution System for Climate Change Adaptation", *Eng. Proc.* 69, 127, 2024. DOI [10.3390/engproc2024069127](https://doi.org/10.3390/engproc2024069127). Licenza CC BY  
Dove si trova: <https://cris.unibo.it/bitstream/11585/987154/1/engproc-69-00127-v2.pdf>

### EPA

US EPA, *EPANET 2.2 User Manual* (autori e numero di rapporto da riportare dal frontespizio del PDF). Cap. 3 "The Network Model"  
Dove si trova: <https://epanet-manual.readthedocs.io/en/latest/3_network_model.html> · [PDF EPA](https://www.epa.gov/system/files/documents/2021-07/epanet_users_manual_2.2.0-1.pdf)

### NBX

Neubrex, *NBX-7031* (NEUBRESCOPE, PPP-BOTDA + TW-COTDR), pagina prodotto, aggiornata il 17/09/2026. Letti il 2026-11-24:
*"Highest spatial resolution 2cm"*, *"Readout Resolution 5 cm (default), 1 cm (minimum)"*, *"Distance range 50m ～
27km"*, *"Measurement time … 5 seconds（minimum）"*, *"Average count 2^5～2^23 times"*; impulsi di 0,2–10 ns per
risoluzioni di 2–100 cm.  
Dove si trova: <https://www.neubrex.com/products/NEUBRESCOPE/dtss_2/NBX-7031>

### UPO

Uponor Infra Oy, *PE100 pressure pipes – Technical factsheet*, 09/2020 (cita EN 12201, EN 1555)  
Dove si trova: <https://brandportal.uponor.com/m/20832399649c7390/original/PE100-2-page-factsheet_EN.pdf>

### ALX

Aliaxis UK, *GPS PE Blue pipe (PE100) – Product data sheet* (tabella "Pipe dimensions – water applications (BS EN 12201-2)")  
Dove si trova: <https://www.aliaxis.co.uk/en/downloads/getfile/399950>

### ECL

Electrosteel Castings Ltd., pagina prodotto *Ductile Iron Pipes*, tabella "Basic dimension of pipes – Pressure class (as per ISO 2531 and EN 545) and thickness class (as per IS 8329)" (pagina web, non catalogo PDF)  
Dove si trova: <https://www.electrosteel.com/products/ductile-iron-pipes>


[\[B23\]](#b23) è il riferimento più vicino a questo progetto. È un sistema BOTDA su tubi in HDPE con la fibra **avvolta a elica** e un tratto di **ritorno libero per compensare la temperatura**: la stessa architettura disegnata nella figura.

Differenza da tenere a mente: in [\[B23\]](#b23) la fibra è fissata **all'esterno** del tubo con nastro adesivo, mentre nel caso MATRIS è annegata nella guaina. Il trasferimento della deformazione alla fibra (blocco 3b) può quindi essere diverso.

---

## Affermazioni

### Architettura del sensore

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Fibra a elica incollata al tubo per lo strain, tratto di ritorno libero per la temperatura | ✅ | [\[B23\]](#b23), didascalia della Fig. 2: *"In yellow is the helically wrapped optical fiber bonded to the HDPE pipe for strain sensing, and in red is the returned fiber, loosely fixed to the pipe, for temperature compensation."* Nel testo, §2.1: *"a portion of the sensing cable returning to the interrogator is loosely fixed to the pipe for the thermal effect compensation on DFOS measurement"* |
| La BOTDA usa due laser in versi opposti nello stesso anello di fibra (uno a impulsi, uno continuo) | ✅ | [\[OZ\]](#oz): *"The typical DSTS BOTDA sensor configuration requires two lasers that are directed in opposite directions through the same loop of fiber (one laser operating continuously, the other pulsed)."* |
| La BOTDA richiede i due capi della fibra; la BOTDR ne usa uno solo | ✅ | [\[OZ\]](#oz), modulo d'ordine: *"BOTDA module (requires both ends of fiber to be connected to DSTS)"*. [\[OZ\]](#oz): *"the sensor fiber must be looped or mirrored"*. [\[DIT\]](#dit): *"Sensor configuration: Loop (2 fibers/channel) or Single-ended"* |
| La sonda continua entra dal capo lontano della fibra | ✅ | [\[B23\]](#b23), §2.1: *"a continuous-wave (CW) probe signal launched from the far end of the sensing fiber"* |
| Le due luci vengono dallo stesso laser, diviso da un accoppiatore 3 dB; la sonda è ottenuta con un modulatore Mach-Zehnder pilotato da un generatore RF | ✅ | [\[B23\]](#b23), §2.1: *"The light coming from a 1530 nm Distributed Feedback (DFB) laser is divided into two branches by a 3 dB optical coupler. The top branch is sinusoidally modulated by a Mach–Zehnder Modulator (MZM) driven by an RF generator to provide a continuous-wave (CW) probe signal"* |
| Impulsi di pompa di 20 ns (≈ 2 m di risoluzione), ripetuti a 30 kHz, amplificati da un EDFA | ✅ | [\[B23\]](#b23), §2.1: *"another Mach–Zehnder modulator, driven by a pulse generator and followed by an Erbium Doped Fiber Amplifier (EDFA), is used to generate 20 ns pump pulses (equivalent to a 2 m spatial resolution) with a 30 kHz repetition rate"* |
| La luce di lettura si legge al capo da cui partono gli impulsi, tramite un circolatore e un fotodiodo | ✅ | [\[B23\]](#b23), §2.1: *"launched into the sensing fiber from a second optical circulator. The same circulator also routs the probe signal to a 125 MHz photodetector (PD)"* |
| Campionamento a 125 MS/s = un campione ogni 0,8 m | ✅ | [\[B23\]](#b23), §2.1: *"a 125 MS/s Analog-to-Digital Converter (ADC) card (equivalent to an 80 cm spatial sampling)"* |
| La scansione di Δν su 1 GHz equivale a un intervallo di 20 mε | ✅ | [\[B23\]](#b23), §2.1: *"scanned over a 1 GHz range (equivalent to a dynamic range of 20 mε)"* |
| Per ogni posizione, la scansione in frequenza ricostruisce lo spettro di guadagno Brillouin, il cui massimo è la BFS | ✅ | [\[B23\]](#b23), §2.1: *"For each position along the sensing fiber, the frequency scan of the probe light allows us to reconstruct the Brillouin Gain Spectrum (BGS) … The specific frequency corresponding to the maximum of the BGS—called the Brillouin Frequency Shift (BFS)—depends on the local temperature and strain"* |
| Le due frequenze differiscono di circa lo 0,005 % (≈ 0,08 nm) | 🧮 | 10,8 GHz / (c / 1530 nm ≈ 196 THz) ≈ 5,5·10⁻⁵ |
| 1 MHz di errore su Δν vale circa 20 µε | 🧮 | 1 / C_ε, con C_ε ≈ 0,05 MHz/µε ([\[B23\]](#b23)) |
| L'impulso modula in ampiezza la luce di lettura; nel tempo, la potenza letta in A riproduce il profilo lungo la fibra | 🧮 | Riformulazione di [\[B23\]](#b23) §2.1 e [\[OZ\]](#oz) (amplificazione localizzata con campionamento di tipo OTDR: *"detected and localized using an OTDR-type sampling apparatus"*) |
| Lo scambio di energia avviene solo se Δν = ν_B per conservazione dell'energia (pompa → sonda + onda acustica) | ⚠️ | Fisica dello scattering Brillouin stimolato, da manuale; fonte da trovare (per esempio Hartog 2017 o Bao & Chen 2011) |
| Esiste anche la configurazione a perdita (sonda più alta della pompa, che cede energia) | ⚠️ | Da trovare una fonte |

### Parametri dello strumento: tempo e metri

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Lo strumento campiona nel **tempo**: [\[B23\]](#b23) usa un ADC a 125 MS/s, equivalente a 0,8 m lungo la fibra | ✅ | [\[B23\]](#b23) §2.1: *"a 125 MS/s Analog-to-Digital Converter (ADC) card (equivalent to an 80 cm spatial sampling)"* |
| La durata dell'impulso fissa la risoluzione spaziale: 20 ns ≈ 2 m | ✅ | [\[B23\]](#b23) §2.1: *"20 ns pump pulses (equivalent to a 2 m spatial resolution)"* |
| Conversione tempo → metri: Δz = c·t / (2n), per l'andata e ritorno della luce; campionamento Δz = c / (2 n f_ADC), risoluzione Δz = c·τ / (2n) | 🧮 | Tempo di volo. Con n = 1,5 riproduce esattamente i numeri di [\[B23\]](#b23) (0,80 m e 2,00 m); con n = 1,468 dà 0,82 e 2,04 m |
| Indice di gruppo della fibra monomodale standard a 1550 nm: n ≈ 1,468 | ⚠️ | **Citato a memoria.** Da verificare sulla scheda Corning SMF-28 (*"Effective Group Index of Refraction"*): corning.com blocca il download automatico, da scaricare a mano |
| Risoluzione lungo il tubo con l'elica: Δs = i·S/Lc (i = risoluzione dello strumento, S = passo dell'elica, Lc = lunghezza di una spira); con l'elica a 70° circa 2 m × cos 70° ≈ 0,7 m di tubo | ✅ formula, 🧮 numero | [\[B23\]](#b23) Eq. 2 e 3; Tab. 1: Δs = 0,45 e 0,72 m nelle loro prove |
| Altri parametri in [\[B23\]](#b23): finestra di scansione Δν (10,4–11,4 e 10,75–11,3 GHz), passo di frequenza νs (5 e 1 MHz), medie per passo N_avg (256), tempo di misura Δt (7 e 20 s) | ✅ | [\[B23\]](#b23) Tab. 1 e §2.1: *"The total measurement time ∆t has been tuned according to the experimental needs by properly setting the frequency scanning window ∆ν, the frequency step νs and the number of averages Navg per frequency step"* |
| Strumenti commerciali: campionamento e risoluzione sono impostazioni separate, date in metri | ✅ | [\[DIT\]](#dit): *"Spatial resolution (setting) 1-20 m (0.25 m increments)"*, *"Spatial sampling interval (setting) 0.25-10 m (0.25 m increments)"*. [\[OZ\]](#oz): *"Spatial Step as low as 5 cm"*, *"Averaging 1 to 65,000 scans"*. Neubrex NBX-7031 ([pagina prodotto](https://www.neubrex.com/products/NEUBRESCOPE/dtss_2/NBX-7031)): *"Readout Resolution 5 cm (default), 1 cm (minimum)"* |
| Il passo di calcolo del simulatore (`calc_step_m`, 0,1 m) non è un parametro dello strumento | — | Scelta del simulatore: abbastanza fine (≤ 1/10 della risoluzione) per simulare la media dello strumento al passo 3 |

### Fenomeno fisico (Brillouin)

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Lo spostamento Brillouin è di circa 10,8 GHz (a 1530–1550 nm) | ✅ | [\[B23\]](#b23), §2.1: *"Its frequency is downshifted by approximately 10.8 GHz from the pump frequency"* |
| Quando la differenza di frequenza tra i due laser è uguale alla frequenza Brillouin, la sonda viene amplificata; si scansiona la differenza e si cerca il picco | ✅ | [\[OZ\]](#oz): *"When the frequency difference between the two lasers is equal to the 'Brillouin frequency' of the fiber, there is a strong interaction … This interaction causes a strong amplification … it is necessary to map out the Brillouin spectrum by scanning the frequency difference … and fitting the peak"* |
| Δν_B = C_T·ΔT + C_ε·ε, con C_T ≈ 1 MHz/°C e C_ε ≈ 0,05 MHz/µε | ✅ con riserva | [\[B23\]](#b23), §2.1, Eq. 1: *"correspond to 1 MHz/°C and 0.05 MHz/µε, respectively [35]. However, these parameters are highly influenced by the cable coating properties and the bonding conditions, which can modify their value"*. La loro fonte primaria è V. Lanticq et al., "Brillouin sensing cable: Design and experimental validation", *IEEE Sensors J.* 8, 1194–1201, 2008 (⚠️ non letta) |
| La dipendenza lineare dello spostamento Brillouin dallo strain è nota dal 1989 | ⚠️ | T. Horiguchi, T. Kurashima, M. Tateda, "Tensile strain dependence of Brillouin frequency shift in silica optical fibers", *IEEE Photon. Technol. Lett.* 1(5), 107–108, 1989. La citazione esiste, il contenuto non è stato letto |
| La luce nella fibra percorre circa 1 m ogni 5 ns; 10 ns di andata e ritorno corrispondono a 1 m | 🧮 | Fisica di base: v = c/n con n ≈ 1,47, quindi v ≈ 2,04·10⁸ m/s, cioè circa 4,9 ns/m |
| "La fibra suona come una corda di chitarra" | — | Analogia didattica, non un'affermazione quantitativa |

### Prestazioni degli strumenti (rumore e accuratezza)

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Accuratezza dello strumento in [\[B23\]](#b23): meglio di 10 µε (0,5 MHz) e 0,5 °C. **Limite superiore** (*"better than"*), statistica (1σ, 2σ, massimo) **non dichiarata**, valida per quello strumento e quella configurazione | ✅ | [\[B23\]](#b23), §2.1: *"The measurement accuracy of the employed BOTDA interrogator has been verified to be better than 0.5 °C/10 µε."* |
| Accuratezza dichiarata da un costruttore: ±2 µε, ±0,1 °C (2σ) | ✅ | [\[OZ\]](#oz): *"Strain Accuracy (2σ) ± 2 με (Whole sensing range for BOTDA)"*, *"Temperature Accuracy (2σ) ± 0.1°C"* |
| Su lunghe distanze la ripetibilità peggiora molto | ✅ | [\[DIT\]](#dit): *"Temperature and Strain Repeatability, 1σ (typical): < 2 °C or < 40 με for 80 km, G652 fiber, 5 m spatial resolution and 20 minutes measurement time."* |
| **Errore usato nelle figure: ±0,5 MHz, solo indicativo.** Secondo le fonti varia da circa 0,1 MHz (OZ Optics, ±2 µε 2σ) a circa 2 MHz (DITEST, 40 µε 1σ a 80 km, 5 m, 20 min) | 🧮 | Conversione con C_ε = 0,05 MHz/µε. Al passo 3 diventa un parametro dello scenario, calcolato con il modello di Soto & Thévenaz 2013 (SNR, larghezza di riga, passo di scansione) |
| SNR dello spettro di guadagno Brillouin > 40 dB nell'esperimento | ✅ | [\[B23\]](#b23), §3.1: *"the Signal-to-Noise Ratio (SNR) of the BGS measurement is always greater than 40 dB"* |
| L'incertezza sul picco dipende da SNR, larghezza della campana e passo di scansione | ✅ | [\[ST13\]](#st13), letto per intero: vedi la sezione "Incertezza dello strumento" |

### Incertezza dello strumento ([\[ST13\]](#st13))

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Incertezza sul picco (fit parabolico dei punti sopra η × picco): σ_ν = (1/SNR)·√(3·δ·Δν_B / (8√2·(1−η)^{3/2})); con η = 0,5: σ_ν = (1/SNR)·√(¾·δ·Δν_B) | ✅ | [\[ST13\]](#st13) Eq. 7 e 8. δ = *"frequency sampling step"*, Δν_B = *"Brillouin full-width at half maximum (FWHM)"*, σ = rumore sulla curva normalizzata, *"directly representing the inverse of the local SNR"*. Validità: *"the validity is already good for 3 or more frequency points"* |
| La formula vale per qualunque sensore Brillouin che stima il picco con un fit (BOTDA, BOTDR, …) | ✅ | [\[ST13\]](#st13) §3: *"Eqs. (7) and (8) are valid not only for BOTDA systems"* |
| Validazione: SNR = 9,4 dB, δ = 1 MHz, Δν_B = 58 MHz, 200 medie → circa 0,75 MHz misurati; la formula dà 0,76 MHz (SNR lineare = 10^(dB/10)) | ✅ misura, 🧮 ricalcolo | [\[ST13\]](#st13) §3, Fig. 6–9: *"the frequency error obtained at 24.5 km distance with 10 time-averaged traces is 3.21 MHz, which is improved down to 0.75 MHz with 200 averages"* |
| Le medie migliorano l'SNR come √N_AV | ✅ | [\[ST13\]](#st13) §3: *"increasing the trace averaging in a factor of 20 results in a √20 ≈ 4.47 better SNR"* |
| L'SNR cresce con la risoluzione Δz (impulso più lungo) e cala con la distanza: SNR(z) = SNR₀·(Δz/Δz₀)·√(N_AV/N_AV₀)·e^(−αz) | ✅ forma, 🧮 riscrittura | [\[ST13\]](#st13) Eq. 4 e 9 |
| La risoluzione spaziale è metà durata dell'impulso per la velocità di gruppo (la nostra formula Δz = c·τ/(2n)) | ✅ | [\[ST13\]](#st13) §2: *"Δz is the interaction length, which is equivalent to the spatial resolution and determined by the pump pulse half duration multiplied by the group velocity of the guided mode"* |
| Valore realistico di partenza: SNR = 0 dB all'ingresso della fibra con risoluzione 2 m e una sola traccia | ✅ | [\[ST13\]](#st13) §3: *"assuming that a realistic SNR = 0 dB is measured at the input fiber end with a spatial resolution Δz₀ = 2 m and no averaging"* |
| Larghezza della campana: 58 MHz con risoluzione 2 m; si allarga con impulsi più corti | ✅ valore, ⚠️ legge | [\[ST13\]](#st13) §3: *"the FWHM at 58 MHz, which is obtained using a spatial resolution of 2 m"*; la larghezza è stata variata *"using different pump pulse widths (between 10 ns and 60 ns)"*. Nessuna formula tra larghezza e durata dell'impulso nell'articolo. Nell'esempio della figura di merito: *"a standard fiber with ΔνB = 27 MHz"* |
| Attenuazione della fibra a 1550 nm circa 0,2 dB/km | ✅ | [\[ST13\]](#st13) §2: *"α = 0.211 dB/km, which is in good agreement with standard values in single-mode fibers at 1550 nm"*; §3: α = 0,22 dB/km |
| Medie e passo di frequenza hanno effetto simile sull'incertezza; cambiare frequenza è lento | ✅ | [\[ST13\]](#st13) §3: *"time averaging and frequency scanning step have a similar impact on the accuracy. Since setting a new frequency on a microwave generator takes in general a much longer time than individual time averaging…"* |
| La potenza di pompa e sonda è limitata da effetti non lineari e svuotamento della pompa; con fibre corte si può usare più potenza | ✅ | [\[ST13\]](#st13) §2 e §4: regime *"ΔPs(z)/Ps(z) << 0.1"*; *"distributed sensing systems employing short fibers (L< α⁻¹) benefits from higher possible pump and probe signal powers"* |
| Con le impostazioni di [\[B23\]](#b23) (2 m, 256 medie, δ = 1 MHz, Δν_B = 58 MHz, SNR₀ = 0 dB) l'incertezza attesa all'inizio della fibra è circa 0,41 MHz (circa 0,03 bar sull'elica); con δ = 5 MHz circa 0,92 MHz | 🧮 | [\[ST13\]](#st13) Eq. 8 e 9; vicino all'accuratezza dichiarata da [\[B23\]](#b23) (*"better than … 10 µε"*, cioè 0,5 MHz) |
| Nelle nostre fibre (2–4 km) la distanza pesa poco: al massimo circa 0,8 dB di SNR in meno | 🧮 | α = 0,2 dB/km × 4 km |
| [\[B23\]](#b23) dichiara SNR > 40 dB: con [\[ST13\]](#st13) darebbe un'incertezza circa 500 volte più piccola dello 0,5 MHz dichiarato. Definizioni di SNR diverse, oppure l'accuratezza di [\[B23\]](#b23) contiene errori sistematici | ⚠️ da chiarire | [\[B23\]](#b23) §3.1 e §2.1. Nel simulatore si usa il modello di [\[ST13\]](#st13), validato |

### Temperatura

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| La temperatura si misura in modo distribuito come lo strain: ogni punto di campionamento è una media su 2 m | ✅ | [\[B23\]](#b23) §2.1: *"For each sampling point, strain and temperature variations are integrated on a spatial interval of 2 m"* |
| Il tratto libero misura solo la temperatura (1 MHz/°C); l'elica la sente in più attraverso la dilatazione del tubo | ✅ | [\[B23\]](#b23) Eq. 1 e Eq. 9 |
| [\[B23\]](#b23) modella la deformazione termica circonferenziale come α_HDPE·ΔT / K_T, con α_HDPE = 200 µε/°C e K_T = 4 empirico | ✅ | [\[B23\]](#b23) Eq. 9: *"KT is a scale temperature coefficient, empirically determined, for considering the thermal inertia of the pipe"*; Tab. 3: K_T = 4. Ricavato in prove di laboratorio di poche ore |
| Dilatazione termica del PE diversa nelle due direzioni: assiale 144 µε/°C per PE4XXX (classe del PE100), circonferenziale circa 65–70 % dell'assiale | ✅ | [\[SB20\]](#sb20) §2.4: *"the hoop CTE is roughly 65 to 70% of the axial CTE. Reported values for the axial CTE are … 144×10-6 per °C for … PE4XXX"*; *"the CTE in the hoop direction will be 65% of the axial value"*. [\[PP814\]](#pp814): *"8.0 x 10-5 in/in/°F"* (= 144 µε/°C) |
| Coefficiente di Poisson del PE da circa 0,42 a −7 °C a circa 0,49 a 49 °C; 0,45 a 23 °C | ✅ | [\[SB20\]](#sb20) §2.5. Nel simulatore oggi ν = 0,40 da [\[B23\]](#b23) Tab. 2 |
| Un tubo trattenuto alle estremità non si allunga: sviluppa uno sforzo assiale; il PE rilassa lo sforzo nel tempo (viscoelastico) | ✅ | [\[PP814\]](#pp814): *"Anchored or end restrained pipe will develop longitudinal stresses instead of undergoing a change in length"*; [\[SB20\]](#sb20): modello viscoelastico per tubi interrati *"restrained PE pipe"*, esponente di rilassamento n ≈ 0,1 |
| Sensibilità dell'elica (70°) alla temperatura, da [\[SB20\]](#sb20): tubo libero ≈ 0,883·94 + 0,117·144 ≈ 100 µε/°C → **≈ 6 MHz/°C**; tubo trattenuto in lunghezza (ε_z = 0, effetto Poisson sul cerchio, ν = 0,45) ≈ 0,883·(94 + 0,45·144) ≈ 140 µε/°C → **≈ 8 MHz/°C** | 🧮 | Conto mio con i coefficienti di [\[SB20\]](#sb20) e la formula dell'elica; quanto il terreno trattenga davvero il tubo (e quanto lo sforzo si rilassi) non è noto: forbice |
| Forbice complessiva della sensibilità dell'elica alla temperatura: da circa 3,5 ([\[B23\]](#b23) con K_T = 4) a circa 8 MHz/°C ([\[SB20\]](#sb20), tubo trattenuto); circa 11 con α = 200 senza K_T | ⚠️ | Righe sopra. **Va calibrata sul posto**: è il parametro più incerto del sistema |
| Variazione stagionale della temperatura alla profondità delle condotte: in 90 giorni circa 21→10 °C (zona calda), 18→4 °C (moderata), 16→1 °C (fredda), cioè circa 11–15 °C | ✅ | [\[SB20\]](#sb20), tabella *"Temperatures and stresses for representative design considerations"*: *"Seasonal cooling (90 days)"*, Warm *"70 to 50°F"*, Moderate *"65 to 40°F"*, Cold *"60 to 33°F"*; *"Soil temperatures are based on depths of cover associated with watermain installations"*. Valori per USA e Canada |
| L'acqua nelle condotte di distribuzione tende alla temperatura del terreno a 1 m (tubi di 60–200 mm, tempi di permanenza di 48 h o più) | ✅ (citazione secondaria) | [\[AV17\]](#av17) §1: *"the water temperature in distribution mains (pipes with a diameter of 60–200 mm, typical residence times of 48 h or more and located at a depth of 1 m) approaches the Tsoil around them (Blokker and Pieterse-Quirijns, 2013)"*. Il lavoro originale (JAWWA 105, 2013) non è stato letto |
| Lungo un percorso urbano la temperatura del terreno a 1 m può cambiare di circa 10 °C da un punto all'altro (punti caldi: fonti di calore, niente ombra, pavimentazione in cemento) | ✅ | [\[AV17\]](#av17) §3.3: *"a maximum SSUHI−1.0 m of 10 °C between the locations was measured"*; abstract: *"up to 7 °C warmer"* |
| Scenari S1t (raffreddamento uniforme di 8 °C dalla misura di base, deriva −0,15 °C/giorno, elica 6 MHz/°C) e S1th (in più un punto caldo di +3 °C su P6, tra 20 e 60 m) | ⚠️ scelte | Valori scelti per l'esperimento. Ordini di grandezza da [\[SB20\]](#sb20) (stagione) e [\[AV17\]](#av17) (variazioni locali); posizione, lunghezza e ampiezza del punto caldo scelte per mostrare l'effetto |
| Un afflusso rapido di acqua fredda (1–4 °C) cambia la temperatura del tubo in poco tempo | ✅ | [\[SB20\]](#sb20) §1: *"Additional stress changes can occur because of a rapid influx of cold water … The cold water temperature is between 33 and 40°F (1 and 4°C)"* |
| Equazione della temperatura del terreno con la profondità (onda annuale smorzata) | ⚠️ non letta | T. Kusuda, P. R. Achenbach, *Earth temperature and thermal diffusivity at selected stations in the United States*, NBS Report 8972, 1965, DOI [10.6028/NBS.RPT.8972](https://doi.org/10.6028/NBS.RPT.8972). PDF oltre 10 MB, non scaricato in automatico |

### Dato grezzo L0 (passo 3b)

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Lo spettro di guadagno Brillouin locale ha forma lorentziana | ✅ | [\[ST13\]](#st13) Fig. 5: *"The distribution maps a resonant Lorentzian profile and the peak gain frequency must be determined"* |
| Ogni punto dello strumento è una media su 2 m di fibra: nel simulatore lo spettro è la media degli spettri locali in una finestra centrata | ✅ principio, 🧮 finestra centrata | [\[B23\]](#b23) §2.1: *"strain and temperature variations are integrated on a spatial interval of 2 m"* |
| Rumore gaussiano indipendente su ogni frequenza, con σ = 1/SNR sulla curva normalizzata | ✅ | [\[ST13\]](#st13) Appendice: *"the measured Brillouin traces are affected by additive Gaussian uncorrelated noise"*; §3: σ *"directly representing the inverse of the local SNR"* |
| Fit di esempio: stima grezza, poi parabola ai minimi quadrati sui punti sopra metà picco, ricentrando la finestra | ✅ | [\[ST13\]](#st13) §3: *"discard all experimental points below a given fraction of the peak value (e.g. 50%)… parabolic fit"*; Appendice: *"an iterative multi-pass fitting procedure can be carried out to adjust recursively the frequency range"* |
| Con lorentziane, il fit parabolico dà un errore circa il 17 % più grande della formula (0,48 contro 0,41 MHz su spettri sintetici; 0,50 contro 0,43 su S1) | 🧮 | Calcolato dal simulatore. Coerente con [\[ST13\]](#st13) Appendice: *"Only the numerical factor √(3/4) can be reasonably taken as specific to the type of function fitted"* |
| Dove la finestra di 2 m prende tratti con frequenze diverse (giunzione, cambi di tratto) lo spettro ha più picchi e il fit può sbagliare di decine di MHz | 🧮 | Calcolato dal simulatore (S1: fino a 117 MHz alla giunzione) |
| Semplificazioni: ampiezza del guadagno normalizzata (l'attenuazione entra solo nell'SNR), niente polarizzazione, niente svuotamento della pompa, misura istantanea | — | Scelte del simulatore; [\[ST13\]](#st13) §2: regime di piccolo guadagno senza svuotamento |

### Temperatura dell'acqua (T1 per l'acqua)

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| L'acqua cambia temperatura in minuti od ore, il terreno intorno al tubo in giorni o settimane | ✅ | [\[BL24\]](#bl24) §1: *"The time it takes for the temperature of the soil around a drinking water main to change is in the order of days to weeks. The time it takes for the temperature of drinking water to change is in the order of minutes to hours."* |
| Nelle condotte di distribuzione l'acqua si avvicina in fretta alla temperatura del terreno, spesso più in fretta del tempo di permanenza | ✅ | [\[CI24\]](#ci24) §1: *"DWT in the distribution mains typically quickly approaches the undisturbed soil temperatures because pipe diameters are limited, so water heats up rapidly and often faster than the residence time"* |
| Modello: dT_acqua/dτ = k·(T_bordo − T_acqua), quindi T_acqua = T_bordo + (T_acqua,0 − T_bordo)·exp(−k·τ), con τ = tempo di permanenza | ✅ | [\[BL24\]](#bl24) Eq. 1 e 3: *"Tboundary is the temperature that the drinking water will eventually reach and k is the heat transfer rate (1/s)"* |
| k = 4·α_acqua / (D1²·[1/Nu + λ_acqua·ln(D2/D1)/(2λ_tubo) + λ_acqua·ln(D3/D2)/(2λ_terreno)]), con D3 = D2 + 2·TSoI·D1; Nu = 0,027·Re^0,8·Pr^0,33 (turbolento), 3,66 (laminare); α_acqua = 0,14·10⁻⁶ m²/s, λ_acqua = 0,57, λ_PVC = 0,16, λ_sabbia asciutta = 1,6 W/(m·K) | ✅ | [\[BL24\]](#bl24) Eq. 2 e §2.1 |
| Sfera di influenza termica: da una a due volte il raggio del tubo | ✅ | [\[BL24\]](#bl24) abstract: *"considering one to two times the radius of the drinking water pipe as the thermal sphere of influence"* |
| Di notte l'acqua nelle condotte è quasi ferma, di giorno scorre molto: le condizioni termiche cambiano nella giornata | ✅ | [\[BL24\]](#bl24) §2.2: *"the flow rate changes over the day with (almost) stagnant water during the night and high flow rates during peak hours"* |
| Differenza tra acqua in ingresso e temperatura di equilibrio nel caso misurato: circa 0,6–1,6 °C; nelle analisi di sensibilità 1–5 K | ✅ | [\[BL24\]](#bl24) §3: *"(Twater,0 − Tboundary) ≈ 0.6 to 1.6 °C during the test period"*; Tabella dei parametri: *"Tboundary − Twater,0 [K]"* tra 1 e 5 |
| Conducibilità termica del PE100: 0,38 W/(m·K) a 23 °C (DIN EN 12667); densità 0,96 g/cm³; modulo a trazione 1100 MPa; dilatazione lineare 1,8·10⁻⁴ /K | ✅ | Oadby Plastics, *PE - HD (100) Technical Properties* ([PDF](https://www.oadbyplastics.co.uk/wp-content/uploads/2025/11/PE-HD-100-Technical-Datasheet.pdf)): *"Thermal conductivity at 23°C W/mK DIN EN 12667 0.38"*, *"Specific gravity g/cm3 DIN EN ISO 1183 0.96"*. Calore specifico del PE100 non trovato in una scheda letta ⚠️ |
| Costante di tempo 1/k per il nostro tubo (PE DN110 SDR11, sabbia, λ_PE = 0,38): circa 0,6 h con acqua che scorre e sfera di influenza nulla, fino a circa 2,7 h con acqua ferma e sfera di influenza 2 | 🧮 | Calcolo con [\[BL24\]](#bl24) Eq. 2 |
| Nella strada S1 l'acqua impiega circa 20 minuti a percorrere 1 km al picco e ore di notte: di giorno porta gran parte della differenza tra serbatoio e terreno, di notte quasi nulla. La temperatura dell'acqua cambierebbe quindi **insieme ai consumi**, come la pressione | 🧮 | Velocità dal modello idraulico (0,83 m/s al picco all'inizio della strada), costante di tempo sopra |
| EPANET può simulare una grandezza che tende a un valore limite con legge del primo ordine (reazione con concentrazione limite), forma uguale a [\[BL24\]](#bl24) Eq. 1 | ⚠️ da verificare | Manuale EPANET, reazioni di qualità con *limiting concentration*: da leggere e citare prima di usarlo; [\[CI24\]](#ci24) usa invece EPANET-MSX |
| Il tubo in PE ha una sua inerzia termica: la parete (10 mm) segue l'acqua con un ritardo; il riferimento libero in un tubetto potrebbe seguire con un ritardo diverso dall'elica | ⚠️ da verificare | Conseguenza fisica; [\[B23\]](#b23) Eq. 9 introduce K_T *"for considering the thermal inertia of the pipe"*. Diffusività termica del PE da trovare |

### Guaina e modello a strati; validazione

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Perdita di carico Hazen-Williams: h = A·q^1,852, A = 4,727·C^−1,852·d^−4,871·L (piedi, cfs) | ✅ | [\[EPA\]](#epa) Tab. 3.1 *"Pipe Headloss Formulas for Full Flow (for headloss in feet and flow rate in cfs)"*. Il simulatore (EPANET) coincide con la formula (`validate`) |
| Modello a strati (Lamé, strati incollati, fondi chiusi): con uno strato coincide con la formula chiusa | 🧮 | Scienza delle costruzioni; verificato nei test |
| Guaina CIPP: modulo a flessione minimo 1724 MPa (250 000 psi) | ⚠️ | ASTM F1216 Tab. 1, letto solo nel riassunto di una ricerca (anteprima iteh); da leggere sulla norma |
| Guaina CIPP in vetro con resina UV: modulo a flessione circa 10 300 MPa (scheda di una guaina per fognature) | ⚠️ | Vortex, *EnviroCure UV* TDS (letta nel riassunto di una ricerca); per acquedotto servono dati del laminato MATRIS |
| Guaina in ghisa integra: circa 0,4–0,5 MHz/bar sull'elica; in ghisa con rigidezza ridotta a 1/10: 2,5–3,8; in PE: 3–10 | 🧮 | Modello a strati con i valori sopra (`validate`, [cap. 10](10-validazione.md)). **Corregge** il "circa 0,2 MHz/bar" detto prima a voce per P0 |
| Strato comprimibile di 10 mm con rigidezza confinata circa 70 MPa tra guaina e ghisa: circa 7 MHz/bar (pelle in feltro) o 3 (pelle in vetro) | 🧮, ⚠️ materiale ipotetico | Modello a strati; idea dell'utente |
| [\[B23\]](#b23) PN16 a 5 bar: 73 MHz misurati contro 69 MHz del modello con il rilassamento E2; a 10 bar 200 contro 138 | 🧮 | [\[B23\]](#b23) §3.1 e Tab. 2; il PE oltre i 5 bar non è lineare (creep) |

### Compensazione della temperatura (passo T3)

| Affermazione | Stato | Fonte o motivo |
|---|---|---|
| Compensazione: ΔT dal riferimento sullo stesso tubo nello stesso punto (ΔT = Δν_rif / C_T), poi Δν_pressione = Δν_elica − K·ΔT | ✅ principio, 🧮 formula | [\[B23\]](#b23): ritorno libero *"for the thermal effect compensation"*; formula dalla somma lineare di [\[B23\]](#b23) Eq. 1 |
| Errore sistematico se K è sbagliato: (K_vero − K_assunto)·ΔT / (MHz per bar); con 8 °C e K tra 3,5 e 8 invece di 6: da −1,4 a +1,1 bar | 🧮 | Calcolato dal simulatore (scenari S1t, S1th) |
| Errore casuale di una misura compensata: √2·√(σ_elica² + (K/C_T)²·σ_rif²/N_rif) / (MHz per bar), con N_rif = lunghezza della media / risoluzione | 🧮 | Propagazione degli errori; σ da [\[ST13\]](#st13) Eq. 7–9. Ipotesi: punti del riferimento indipendenti ogni risoluzione (2 m) |
| La media del riferimento su L metri sfuma le variazioni locali di temperatura: in S1th, con 74 m, errori fino a 0,58 bar ai bordi di un punto caldo di 40 m | 🧮 | Calcolato dal simulatore |
| Il riferimento va interpolato nel punto del tubo di ogni campione dell'elica: con il punto più vicino la griglia di calcolo dava scalini fino a 0,012 bar ai bordi del punto caldo; interpolando 0,001 bar | 🧮 | Calcolato dal simulatore (S1th) |
| Media adattiva del riferimento (filtro sigma: si mediano solo i vicini con temperatura entro una soglia da quella del punto): in S1th errore massimo 0,19 bar contro 0,58 della media mobile, sulla stessa lunghezza (74 m) | 🧮, ⚠️ soglia | Calcolato dal simulatore senza rumore. Soglia 0,5 °C scelta, dell'ordine del rumore del riferimento: da verificare con il rumore (passo 3b) e da cercare in letteratura un metodo consolidato |
| Sul dato rumoroso (spettri + fit, S1t/S1th) la compensazione con media mobile del riferimento su 74 m dà circa 0,06 bar per misura, in accordo con il modello del passo T3 (0,056) | 🧮 | Calcolato dal simulatore |
| Il rumore della misura di base è lo stesso in tutte le misure successive: errore fisso punto per punto, che la media nel tempo non riduce; mediando n misure di base cala come 1/√n (con 10: da 0,049 a 0,018 bar) | 🧮 | Calcolato dal simulatore; legge 1/√n come per le medie in [\[ST13\]](#st13) |
| Media adattiva robusta: confronto con la mediana del riferimento su 10 m, soglia = 2 × rumore del riferimento stimato dai dati (1,4826 × mediana delle differenze / √2); con soglia fissa 0,5 °C sul dato rumoroso non media quasi nulla | 🧮, ⚠️ parametri scelti | Calcolato dal simulatore; mediana su 10 m e soglia 2σ scelte. Stima robusta del rumore dalle differenze successive: tecnica statistica standard, fonte da citare in tesi ⚠️ |
| La sensibilità K va calibrata sul posto | ⚠️ da approfondire | Conseguenza delle righe sopra; metodo di calibrazione da cercare in letteratura |

### Meccanica del tubo in PE

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Deformazione circonferenziale sulla superficie esterna: ε_θ = (2−ν)·β²/(1−β²)·p/E, con β = raggio interno / raggio esterno | ✅ | [\[B23\]](#b23), Eq. 4–6 (fonte primaria: G. Petrucci, *Lezioni di Costruzione di Macchine*, Palermo, 2002) |
| HDPE: E₁ = 1050 MPa, ν = 0,4 | ✅ | [\[B23\]](#b23), Tab. 2 |
| HDPE: dilatazione termica α = 200 µε/°C | ✅ | [\[B23\]](#b23), Eq. 9: *"α_HDPE is assumed equal to 200 µε/°C"*. Le schede dei compound PE100 riportano 1,3–1,8·10⁻⁴ /K (ISO 11359-2) |
| Il PE ha comportamento viscoelastico (creep): modello di Burgers con E₁, E₂, η₂, η₃ | ✅ | [\[B23\]](#b23), Eq. 7–8 e Tab. 2 (per PN10: E₂ = 1,65·10³ MPa, η₂ = 2,04·10⁶ MPa·s, η₃ = 2,13·10⁸ MPa·s) |
| Tubo PE DN110, spessore 10 mm: ε_θ ≈ 309 µε per bar | 🧮 | Formula e parametri di [\[B23\]](#b23); β = 45/55 |
| Deformazione assiale con fondi chiusi: ε_z = (1−2ν)·β²/(1−β²)·p/E ≈ 39 µε per bar | 🧮 | Lamé, tubo a fondi chiusi (scienza delle costruzioni) |
| Fibra a elica: ε_f = ε_θ·sin²α + ε_z·cos²α; con α = 70° ≈ 277 µε per bar, cioè circa 14 MHz | 🧮 | Trasformazione della deformazione lungo una direzione (meccanica di base) |
| ~~Sull'elica la temperatura pesa circa 11 MHz/°C~~ **Correzione 2026-11-24:** il conto 1 + 0,05 × 200 usava α_HDPE di [\[B23\]](#b23) senza il suo K_T e senza la differenza tra direzione assiale e circonferenziale. Ora la sensibilità è una forbice (vedi "Temperatura") | ⚠️ | — |
| Ordine di grandezza misurato: 73 MHz a 5 bar e 200 MHz a 10 bar rispetto a 0 bar (tubo **PN16**, §3.1: *"BFS profiles and raw BGS measured by the BOTDA interrogator on the PN16 pipe"*) | ✅ | [\[B23\]](#b23), §3.1: *"a clear shift of 73 and 200 MHz due to increased hoop strain with respect to the reference 0 bar BGS is evident"* |

### Ipotesi del simulatore (passo 2)

| Affermazione | Stato | Fonte o motivo |
|---|---|---|
| La pressione varia linearmente lungo un tubo tra i due nodi | 🧮 | Con portata costante nel tubo la perdita di carico è uniforme lungo il tubo (Hazen-Williams: carico lineare); con quota lineare tra i nodi anche la pressione è lineare |
| 1 m di colonna d'acqua = 9,80665 kPa | — | ρ·g con ρ = 1000 kg/m³, g = 9,80665 m/s² |
| Il tratto di riferimento libero non si deforma con la pressione | ✅ principio | [\[B23\]](#b23): fibra di ritorno *"loosely fixed to the pipe for the thermal effect compensation"*; nella Fig. 7c il riferimento non si sposta con la pressione |
| La deformazione della parete si trasferisce alla fibra al 100 % | ⚠️ | Ipotesi. Il trasferimento dipende da rivestimento e incollaggio (Ansari & Libo 1998, da verificare) |
| Comportamento elastico istantaneo del PE | ⚠️ | Semplificazione: [\[B23\]](#b23) mostra il creep (modello di Burgers, Fig. 8) |
| ν_B0 = 10 880 MHz | ✅ forma, ⚠️ valore | [\[B23\]](#b23) Fig. 7a, fibra non tirata, letto a occhio; non cambia i Δν |
| Profilo a riposo nel simulatore: elica con valori in [105, 180] MHz, tratto libero +65 MHz, cavi 0, ondulazioni di circa 1 MHz su circa 8 m | ✅ valori di partenza, ⚠️ forma | Valori da [\[B23\]](#b23) Fig. 7a, letti a occhio (fibra fissata con nastro, **un solo tubo corto**, PN16). Per la fibra annegata (MATRIS) i valori sono solo un segnaposto |
| Lungo un'elica avvolta senza interruzioni il profilo a riposo cambia in modo **continuo** (punti di controllo casuali ogni ~300 m di fibra, uniti da segmenti); i nodi EPANET (rubinetti) non creano salti | ⚠️ ipotesi | Nessun dato su condotte lunghe. Motivo: la fibra è un filo unico tirato con continuità. Scelta del 2026-11-24, dopo che la versione precedente (valori estratti per ogni tubo EPANET) mostrava salti non fisici a ogni rubinetto |
| Il profilo a riposo **salta** dove la posa riparte da capo: dopo un cavo (per esempio in un pozzetto) o dove cambia il tubo (diametro esterno, materiale, guaina) | ⚠️ ipotesi | Lì la fibra viene riavvolta, quindi la tensione di posa può ripartire diversa. In [\[B23\]](#b23) Fig. 7a si vedono salti tra tratti con fissaggio diverso (elica, tratto libero, cavi) |


### Rete di prova: criteri di dimensionamento

| Affermazione | Stato | Fonte |
|---|---|---|
| Velocità di progetto nelle reti di distribuzione: tipica 1–1,5 m/s, minimo circa 0,4–0,6 m/s, massimo 1,5–3 m/s | ⚠️ | Corsi e manuali, non norme; trovati ma non letti per intero: [TU Delft, Distribution networks](https://ocw.tudelft.nl/wp-content/uploads/Distribution_networks.pdf), [TU Delft, Practical applications](https://ocw.tudelft.nl/wp-content/uploads/Practical_applications.pdf), [MoHUA (India), Manual Part A Ch. 12](https://mohua.gov.in/upload/uploadfiles/files/Part_A-Chapter-12-Service-Reservoir-and-Distribution-System.pdf), [Univ. Trieste, Pozzetto](https://moodle2.units.it/pluginfile.php/180266/mod_resource/content/1/28%20-%20Piping-Fluid%20distribution%20plants-Design%20of%20distribution%20networks.pdf) |
| Perdita di carico di progetto: ottimale 1–4 m/km, massimo 10 m/km; TU Delft: 1–2 m/km come valore comune, 2–5 per tubi piccoli e brevi | ⚠️ | Stesse fonti |
| Dimensioni PE100 SDR11 (PN16): DN110 × 10,0; DN125 × 11,4; DN160 × 14,6 mm | ✅ | [\[UPO\]](#upo), "Table: Wall thickness PE100", colonna *"SDR11 PN16 Wall thickness mm"*: righe *"110 … 10,0"*, *"125 … 11,4"*, *"160 … 14,6"*. Confermato da [\[ALX\]](#alx) (*"BS EN 12201-2"*), SDR 11: *"Min t"* 10 / 11,4 / 14,6 mm. Sono spessori **minimi** nominali |
| Diametro interno usato in EPANET = esterno − 2 × spessore minimo (90; 102,2; 130,8 mm) | 🧮 | Approssimazione. Il foro medio reale è circa 1 mm più piccolo, perché lo spessore effettivo sta tra minimo e massimo: [\[ALX\]](#alx) *"Mean Bore"* 89,3 (DN110), 101,3 (DN125), 129,7 (DN160). Effetto trascurabile sull'idraulica |
| Adduttrice in ghisa sferoidale DN200: diametro esterno 222 mm; spessore classe K9 6,3 mm (classe di pressione C40: 4,7 mm) | ✅ produttore, ⚠️ norma | [\[ECL\]](#ecl), riga DN200: *"200 mm \| 222 mm \| +1/-3.0 mm \| C40 \| 4.7 mm \| 6.3 mm \| 5 mm"* (colonne: DE, tolleranza, classe C preferita, spessore classe C, spessore K9, spessore K7). Tabella *"as per ISO:2531 and EN:545"*, ma il testo della EN 545 non è stato letto. Spessore del rivestimento interno in malta cementizia non dichiarato: **ignorato** (diametro interno 209,4 mm). P0 non ha la fibra, conta solo per l'idraulica |
| Modulo elastico della ghisa sferoidale ≈ 170 GPa | ⚠️ | [\[ECL\]](#ecl) riporta *"Modulus of Elasticity 1.7 x 10¹⁰ Kg/m²"*: unità scritta male (se kgf/m², ≈ 167 GPa). Coefficiente di Poisson 0,26 non trovato. Non usati nel calcolo (P0 senza fibra) |
| EPANET non contiene un catalogo di tubi né limiti di progetto: i dati di un tubo sono solo nodi, diametro, lunghezza, scabrezza, stato | ✅ | [\[EPA\]](#epa) §3.1: *"The principal hydraulic input parameters for pipes are:"* nodi di inizio e fine; diametro; lunghezza; coefficiente di scabrezza; stato |
| Coefficiente di Hazen-Williams per tubi nuovi: ghisa 130–140, plastica 140–150 (usati: PE 140, ghisa P0 130) | ✅ | [\[EPA\]](#epa), *"Table 3.2 Roughness Coefficients for New Pipe"*: *"Cast Iron \| 130 – 140"*, *"Plastic \| 140 – 150"* (anche *"Concrete or Concrete Lined \| 120 – 140"*). Avvertenza: *"Be aware that a pipe's roughness coefficient can change considerably with age."* |
| Norme di riferimento non lette (a pagamento, CEN/UNI): EN 12201-2 (tubi PE per acqua), EN 545 (ghisa sferoidale), EN 805 (requisiti dei sistemi di acquedotto) | ⚠️ | Da consultare in biblioteca (abbonamento UNI d'ateneo) se servono in tesi |
| Con tubi SDR11 la deformazione per bar non dipende dal diametro | 🧮 | β = r_int/r_est costante per SDR costante, quindi ε_θ (Lamé) uguale |
| Escursione giornaliera di pressione in reti reali | ❌ non trovata | Studi su distretti reali ([Starczewska et al., White Rose](https://eprints.whiterose.ac.uk/96459/1/1-s2.0-S1877705816000023-main.pdf); [US EPA, pressure management](https://www.epa.gov/system/files/documents/2021-12/ds-toolbox-fact-sheets_pressure-management.pdf)) senza un valore in bar nei riassunti |

### Pressione statica, quota e scenari semplici

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Il carico idraulico (*head*) è quota + altezza di pressione; quindi la pressione (in metri d'acqua) è carico − quota | ✅ | [\[EPA\]](#epa), Appendice C, [RESERVOIRS]: *"Head is the hydraulic head (elevation + pressure head) of water in the reservoir."* Per i nodi EPANET calcola *"hydraulic head (internal energy per unit weight of fluid)"* e *"pressure"* (§3.1, Junctions). In unità SI la pressione è in metri (Appendice A: *"Pressure \| pounds per square inch \| meter"*) |
| Il carico di un serbatoio è la quota del pelo dell'acqua, e non dipende da cosa succede nella rete | ✅ | [\[EPA\]](#epa) §3.1, Reservoirs: *"its hydraulic head (equal to the water surface elevation if the reservoir is not under pressure)"*; *"its head and water quality cannot be affected by what happens within the network"* |
| Senza prelievi la pressione in un punto è il dislivello tra il pelo dell'acqua del serbatoio e il punto (circa 0,098 bar per metro); conta l'altezza della colonna, non la quantità d'acqua (legge di Stevino) | 🧮 | Idrostatica di base (ρ·g·h). Testo di idraulica da citare in tesi ⚠️ |
| La pressione di EPANET è relativa (in più rispetto all'atmosfera), ed è quella che deforma la parete | 🧮 | Il manuale non lo dice esplicitamente (non trovato in §3 e Appendici). Ragionamento: l'atmosfera agisce sul pelo libero del serbatoio e all'esterno del tubo, quindi si annulla; la parete sente solo la differenza. Non dipende dalla quota sul livello del mare |
| Lungo una discesa la pressione cresce (circa +1 bar ogni 10 m) anche allontanandosi dal serbatoio; la perdita di carico la riduce solo nel verso del flusso | 🧮 | Dalle due righe sopra: carico che cala solo per attrito, quota che scende. Verificato negli scenari S0b e S2 con EPANET |
| Uno scenario con il serbatoio più in basso della strada richiederebbe una pompa di risalita: scartato | — | Decisione dell'utente (2026-11-24) |
| Scenari semplici: PE100 SDR11 DN110, prelievo totale 3,3 L/s (11 rubinetti da 0,3 L/s in S1/S2, uno solo in fondo in S0a/S0b), pendenza 2 %, pelo dell'acqua 50 m sopra l'inizio della strada | ⚠️ ipotesi | Valori scelti per stare nei criteri di progetto (velocità al picco 0,83 m/s, perdita di carico 8,5 m/km), vedi righe sopra; pendenza e pressione statica (circa 5 bar) scelte, non da norma (EN 805 da leggere) |

### Misura di base e minimo misurabile

| Affermazione | Stato | Fonte e citazione |
|---|---|---|
| Ogni metro di fibra ha una "nota di partenza" propria, dovuta anche alla pre-deformazione della posa: serve una misura di base | ✅ | [\[B23\]](#b23), §2.1: *"By considering the BFS with respect to a reference state, it is possible to eliminate the pre-strain component on the DFOS cable caused by the installation procedure."* §3.1: la differenza della curva a 0 bar sul tratto avvolto *"is clearly due to pre-strain induced during the installation"* |
| A riposo (0 bar) la frequenza Brillouin non è uguale lungo la fibra: sull'elica circa +180 MHz all'inizio e +105 MHz alla fine rispetto ai cavi (circa 10 880 MHz); sul tratto libero circa +65 MHz | ✅ forma, ⚠️ valori | [\[B23\]](#b23), Fig. 7a (tubo PN16), curva 0 bar. **Valori letti a occhio dal grafico.** Il motivo dell'aumento sull'elica è dichiarato (pre-deformazione della posa); quello sul tratto libero no. Disegno esplicativo: [img/frequenza-a-riposo.png](img/frequenza-a-riposo.png) |
| Nel caso MATRIS la fibra è annegata nella guaina, che polimerizza in opera: il profilo a riposo nasce soprattutto dalla deformazione residua di cura (ritiro chimico della resina + contrazione termica dopo la cura) | ⚠️ | Informazione di progetto (utente, 2026-11-23). Il fenomeno è misurato con fibre annegate in laminati compositi, anche con BOTDA: Ito, Takeda, Obo, Minakuchi, cure strain in laminati CFRP spessi con PPP-BOTDA ([record](https://katalog.lib.cas.cz/KNAV/EdsRecord/edsair,edsair.doi...........320e86439b22066e2bbdd261e391e72f)); laminati spessi con FBG + Luna OFDR, *"the chemical shrinkage is the dominant driver of residual stress build-up"* ([FPCM17](https://ecm-academics.plymouth.ac.uk/jsummerscales/fpcm/fpcm17/FPCM17_59_Tsavea.pdf)); [OSTI 226060](https://www.osti.gov/biblio/226060-measurement-process-induced-strains-composite-materials-using-embedded-fiber-optic-sensors). **Non letti**; nessuno riguarda tubi o guaine |
| Durante la cura di una guaina CIPP la fibra può misurare la temperatura e verificare la polimerizzazione | ⚠️ | Brevetti: [US12291944](https://patents.google.com/patent/US12291944), [US 2012/0261050](https://patents.justia.com/patent/20120261050). Non letti |
| Con un'accuratezza di 10 µε, in un tubo PN10 da 63 mm si misurano variazioni sopra 0,016 bar | ✅ | [\[B23\]](#b23), §4: *"The strain accuracy is 10 µε, which means that if we consider a PN10 HDPE pipe with an external diameter of 63 mm, all pressure variations higher than 0.016 bar produce a measurable hoop strain."* **Questo conto non include l'errore della compensazione di temperatura** |
| Compensare la temperatura è il limite pratico | ✅ in parte | [\[B23\]](#b23), §3.1: *"the loose part of the DFOS sensor layout measured a temperature variation of up to 4 °C. This variation involves thermal deformation that is not recovered in the unloading stage"* |
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
| Neubrex **NBX-7031** | Rayleigh TW-COTDR + Brillouin PPP-BOTDA | 50 m – 27 km; risoluzione fino a 2 cm | ✅ pagina del produttore letta (2026-11-24) | [\[NBX\]](#nbx) |
| Viavi **MTS-8000 DTSS** | BOTDR (un solo capo) | un solo capo | ⚠️ scheda trovata, non letta | [scheda](https://www.lasercomponents.com/fileadmin/user_upload/home/Datasheets/viavi/mts-8000-dtss.pdf) |
| **Cohaerentia** S.r.l. (Milano) | BOTDA | ad anello | ✅ è l'interrogatore usato in [\[B23\]](#b23) (*"provided by Cohaerentia Srl—relies on the standard BOTDA"*); ⚠️ nessuna pagina prodotto trovata | [\[B23\]](#b23) |

### Cavi sensore

Prysmian OptiStrain, Solifos BRUsens e Clearfield producono cavi per misure di strain e temperatura. ⚠️ Sono emersi dalla ricerca ma le schede non sono state lette: [Prysmian OptiStrain](https://na.prysmian.com/sites/na.prysmian.com/files/media/products/TLS-DS-D-701-DFS-Sensing-Cable-with-OptiStrain.pdf) · [Solifos](https://solifos.com/en/downloads-sensing/).

### Tubi con fibra integrata

| Caso | Cosa fa | Pressione dell'acqua? | Prodotto in vendita? | Fonte |
|---|---|---|---|---|
| Politecnico di Milano + Cohaerentia | fibra a elica fissata all'esterno di tubi HDPE, BOTDA | **sì** | **no**: §4, *"Future developments will be focused on … the industrial production of HDPE pipes 'natively smart,' in which DFOS cables are integrated into the pipeline surface during the extrusion process"* | [\[B23\]](#b23) ✅ |
| Aquaspira Ltd (UK) | fibra annegata con saldatura a caldo in HDPE su tubi compositi acciaio/plastica, *"either during the pipeline's manufacture or pre-/post-installation on site"*; Rayleigh OFDR (Luna ODiSI 6100) | no: carichi del traffico sul tubo interrato | non dichiarato; si parla di *"commercial trials"* | N. J. Cassidy et al., *Sensors* 24(4), 1298, 2024, DOI [10.3390/s24041298](https://doi.org/10.3390/s24041298) ✅ (letto tramite riassunto testuale, non dal PDF) |
| HBM FiberSensing | sensori FBG (puntuali) su una condotta forzata in acciaio a 100 bar | sì (deformazione della parete) | installazione su progetto | [nota applicativa](https://www.hbm.com/fileadmin/mediapool/files/technical-articles-technotes-white-papers/High_Pressure_Water_Pipe_-_Application_Note_en.pdf) ⚠️ non letta |
| UC Berkeley + EBMUD | cavo distribuito per lo strain, posato in trincea durante la costruzione | — | progetto di ricerca | [pagina](https://geomechanics.berkeley.edu/news/dms_ebmud/) ⚠️ non letta |

---

## Citate nel dump della sessione e ancora da verificare

Vengono dal [dump del 2026-11-23](C-diario-sessioni.md) e sono **citate a memoria**:

- [ ] E. Todini, S. Pilati, metodo del gradiente, 1988.
- [ ] L. A. Rossman, *EPANET 2 Users Manual*, US EPA.
- [ ] E. B. Wylie, V. L. Streeter, *Fluid Transients in Systems*, Prentice Hall, 1993.
- [ ] D. Covas et al., viscoelasticità nei transitori, *J. Hydraulic Research*, 2004–2005. Collegamento: [\[B23\]](#b23) usa il modello di Burgers con fonti diverse (Elleuch & Taktak 2006; Fathi-Moghadam & Kiani 2019).
- [ ] F. Ansari, Y. Libo, trasferimento di strain, *J. Lightwave Technology*, 1998.
- [ ] T. Kurashima et al., dipendenza termica dello spostamento Brillouin, *Applied Optics*, 1990.
- [ ] T. Kusuda, P. R. Achenbach, temperatura del suolo, ASHRAE, 1965.
- [ ] A. H. Hartog, *An Introduction to Distributed Optical Fibre Sensors*, CRC Press, 2017.
- [ ] X. Bao, L. Chen, "Recent Progress in Brillouin Scattering Based Fiber Sensors", *Sensors* 11(4), 4152–4187, 2011. Esiste ([PMC3231321](https://pmc.ncbi.nlm.nih.gov/articles/PMC3231321/)), non letta.

**Correzione rispetto al dump.** Il dump (§4.2) stima per un tubo in PE DN110 "~400 µε per bar" con la formula a parete sottile sul diametro medio. Con la formula di Lamé sulla superficie esterna usata da [\[B23\]](#b23) vengono circa 309 µε. Stesso ordine di grandezza, ma per il simulatore si usa la formula di [\[B23\]](#b23).

<!-- nav-fondo -->

| [← 11. Risultati e questioni aperte](11-risultati-e-questioni-aperte.md) | [📖 Indice](00-indice.md)<br><sub>appendici</sub> | [Appendice B. Approfondimento sulla fibra →](B-fibra-ottica-dfos.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
