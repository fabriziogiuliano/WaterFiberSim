<!-- nav -->
| [← 1. Introduzione](01-introduzione.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 2 di 11 · Parte I — Il problema e la fisica</sub> | [3. Il sensore sul tubo →](03-il-sensore-sul-tubo.md) |
|:---|:---:|---:|
<!-- /nav -->

# 2. Il principio di misura: la fibra Brillouin

La BOTDA è una tecnica di misura già esistente e disponibile in commercio (§2.5). Questo capitolo la presenta come la
descrivono le fonti, soprattutto la scheda di OZ Optics [\[OZ\]](A-fonti.md#oz) e l'articolo di Bertulessi et al. [\[B23\]](A-fonti.md#b23). Il simulatore usa
lo strumento così com'è e ne riproduce l'uscita: gli spettri e la loro incertezza (cap. 6).

## 2.1 La "nota" della fibra

Secondo [\[B23\]](A-fonti.md#b23) §2.1 la luce nella fibra interagisce con onde acustiche del vetro, e l'onda diffusa ha la frequenza
spostata: *"Its frequency is downshifted by approximately 10.8 GHz from the pump frequency"*. Lo spostamento, la
**frequenza Brillouin** ν_B, dipende da temperatura e deformazione ([\[B23\]](A-fonti.md#b23) Eq. 1):

  Δν_B = C_T · ΔT + C_ε · ε,  con C_T ≈ 1 MHz/°C e C_ε ≈ 0,05 MHz/µε

con l'avvertenza di [\[B23\]](A-fonti.md#b23): *"these parameters are highly influenced by the cable coating properties and the bonding
conditions"*. [\[OZ\]](A-fonti.md#oz): *"the Brillouin frequency at each point in the fiber is linearly related to the temperature and the
strain applied to the fiber"*.

## 2.2 Il principio BOTDA, con le parole del produttore

La descrizione di [\[OZ\]](A-fonti.md#oz) (scheda DTS0115), che è il riferimento di questo capitolo:

> *"The typical DSTS BOTDA sensor configuration requires two lasers that are directed in opposite directions through
> the same loop of fiber (one laser operating continuously, the other pulsed). When the frequency difference between the
> two lasers is equal to the 'Brillouin frequency' of the fiber, there is a strong interaction […]. This interaction
> causes a strong amplification to the Brillouin signal which can be detected and localized using an OTDR-type sampling
> apparatus. To make a strain or temperature measurement along the fiber, it is necessary to map out the Brillouin
> spectrum by scanning the frequency difference […] of the two laser sources and fitting the peak of the Brillouin
> spectrum"* — [\[OZ\]](A-fonti.md#oz)

Quindi, nelle parole che usiamo nel libro:
1. **una fibra ad anello**, con i due capi sullo strumento (porta A e porta B): [\[OZ\]](A-fonti.md#oz) *"requires both ends of fiber to be
   connected"*;
2. **due luci in versi opposti**: una a impulsi (in [\[B23\]](A-fonti.md#b23) chiamata *pump*, impulso di interrogazione), una continua
   (*probe*, luce di lettura);
3. dove la differenza di frequenza è uguale alla ν_B del punto, la luce continua viene **amplificata**;
4. la posizione si ricava dal tempo (*"OTDR-type sampling"*), circa 10 ns per metro di andata e ritorno 🧮;
5. la grandezza si ricava **scansionando** la differenza di frequenza e trovando il **picco** dello spettro.

[\[OZ\]](A-fonti.md#oz) spiega anche perché la BOTDA è preferita alla BOTDR (che usa un capo solo): *"Due to the strong signal strength the
strain and temperature measurements are more accurate and the measuring range is longer than that of BOTDR"*.

## 2.3 Com'è fatto dentro: lo schema di [\[B23\]](A-fonti.md#b23)

Lo schema a blocchi qui sotto è ridisegnato da [\[B23\]](A-fonti.md#b23) Fig. 2 e §2.1; i valori sono quelli del loro strumento (fornito da
Cohaerentia: *"The DFOS interrogator—provided by Cohaerentia Srl—relies on the standard BOTDA"*, [\[B23\]](A-fonti.md#b23)).

![Interrogatore BOTDA con fibra ad anello: schema a blocchi](img/dfos-interrogatore.drawio.svg)

*Schema modificabile in draw.io.*

| ramo | blocco | cosa fa, secondo [\[B23\]](A-fonti.md#b23) §2.1 |
|---|---|---|
| sorgente | laser DFB a 1530 nm | *"The light coming from a 1530 nm Distributed Feedback (DFB) laser is divided into two branches by a 3 dB optical coupler"* |
| luce di lettura (sonda) | modulatore + generatore RF | *"sinusoidally modulated by a Mach–Zehnder Modulator (MZM) driven by an RF generator to provide a continuous-wave (CW) probe signal"*, lanciata dal capo lontano della fibra |
| impulso (pompa) | modulatore + generatore di impulsi + EDFA | *"20 ns pump pulses (equivalent to a 2 m spatial resolution) with a 30 kHz repetition rate"* |
| ricezione | circolatore, fotodiodo, ADC | *"The same circulator also routs the probe signal to a 125 MHz photodetector"*; *"a 125 MS/s Analog-to-Digital Converter (ADC) card (equivalent to an 80 cm spatial sampling)"* |
| elaborazione | spettro e picco | *"For each position along the sensing fiber, the frequency scan of the probe light allows us to reconstruct the Brillouin Gain Spectrum (BGS)"*, il cui massimo è la ν_B |

## 2.4 Cosa prende il simulatore da qui

Il simulatore non riproduce i blocchi interni: parte da ν_B vera lungo la fibra e produce gli spettri che lo strumento
restituirebbe (dato grezzo L0), con la risoluzione, il passo, la scansione e il rumore impostati nello scenario. Il
modello dell'incertezza è quello di Soto & Thévenaz [\[ST13\]](A-fonti.md#st13) (cap. 6); ogni parametro è studiato nel **cap. 9**.

| livello | contenuto | chi lo produce |
|---|---|---|
| **L0** | per ogni punto e ogni misura, lo spettro (potenza in funzione della differenza di frequenza), con il rumore | il simulatore (cap. 6) |
| L1 | il picco ν_B(z, t) | l'elaborazione (fit, esempio nel cap. 6) |
| L2–L3 | allungamento, temperatura, pressione | l'elaborazione (esempio di compensazione nel cap. 7) |

## 2.5 Strumenti BOTDA in commercio: utilizzabili da subito

**Lo strumento non va sviluppato: esiste ed è in vendita.** Gli interrogatori qui sotto lavorano ad anello (BOTDA) e
misurano deformazione e temperatura su fibre di chilometri. Per il progetto servono la fibra posata nella guaina e uno
di questi strumenti; il resto (pressione, compensazione) è elaborazione dei dati.

| strumento | tecnica e configurazione | portata | risoluzione spaziale | passo dei punti | accuratezza / ripetibilità dichiarata | tempo di misura | dati in uscita | stato |
|---|---|---|---|---|---|---|---|---|
| **Prysmian DITEST** [\[DIT\]](A-fonti.md#dit) | BOTDA ad anello o BOTDR; 4 canali (fino a 20) | 80 km per canale (anello fino a 160 km) | 1–20 m | 0,25–10 m | *"< 2 °C or < 40 με"* (1σ) a 80 km, 5 m, 20 min | 1 s – 30 min | file txt/csv; protocolli Modbus, DNP3, IEC 61850 (opzioni) | ✅ scheda letta |
| **OZ Optics Foresight DSTS**, modulo BOTDA [\[OZ\]](A-fonti.md#oz) | BOTDA ad anello (combinazione con BOTDR opzionale); 2–251 canali | 100 km | 0,1–50 m (secondo il modello) | fino a 5 cm | ±2 µε, ±0,1 °C (2σ) | da 1 s (scansione completa) | — | ✅ scheda letta |
| **Neubrex NBX-7031** [\[NBX\]](A-fonti.md#nbx) | Brillouin PPP-BOTDA + Rayleigh TW-COTDR, su ordinazione | 50 m – 27 km (fino a 80 km nella versione UX) | fino a 2 cm (impulsi da 0,2 ns) | 5 cm (minimo 1 cm) | — | da 5 s | — | ✅ pagina prodotto letta |
| **Cohaerentia** (Milano) | BOTDA ad anello | — | 2 m in [\[B23\]](A-fonti.md#b23) | 0,8 m in [\[B23\]](A-fonti.md#b23) | *"better than 0.5 °C/10 µε"* in [\[B23\]](A-fonti.md#b23) | 7–20 s in [\[B23\]](A-fonti.md#b23) | — | ⚠️ usato in [\[B23\]](A-fonti.md#b23); nessuna scheda prodotto trovata |

Altri strumenti trovati ma **non** adatti così come sono, o non verificati: fibrisTerre fTB 5020 (BOFDA, nel dominio della
frequenza; scheda non letta ⚠️); Viavi MTS-8000 DTSS (BOTDR, un capo solo; scheda non letta ⚠️). Dettagli e link
nell'appendice A, sezione "Prodotti commerciali".

**Come impostare il simulatore per riprodurre uno strumento** (🧮, con Δz = c·τ/(2n) e Δz = c/(2·n·f), n = 1,468):

| impostazione dello strumento | `pulse_width_ns` | `adc_sample_rate_msps` |
|---|---|---|
| DITEST, 1 m di risoluzione, passo 0,25 m | 9,8 | 408 |
| [\[B23\]](A-fonti.md#b23) / Cohaerentia, 2 m, passo 0,8 m | 20 | 125 |
| OZ, 0,1 m di risoluzione, passo 5 cm | 0,98 | 2041 |
| Neubrex, 2 cm, passo 5 cm | 0,2 | 2041 |

Verifica incrociata: per Neubrex la scheda dichiara 2 cm di risoluzione con impulsi da 0,2 ns, e la formula del
simulatore dà 2,04 cm. Le accuratezze dichiarate non bastano da sole a fissare il rumore del simulatore (dipendono da
medie e tempo di misura): per uno strumento scelto, `snr0_db` va tarato sui suoi dati (cap. 9, §9.1.5).

<!-- nav-fondo -->

| [← 1. Introduzione](01-introduzione.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 2 di 11 · Parte I — Il problema e la fisica</sub> | [3. Il sensore sul tubo →](03-il-sensore-sul-tubo.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
