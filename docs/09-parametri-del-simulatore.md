<!-- nav -->
| [← 8. Logica del simulatore](08-logica-del-simulatore.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 9 di 11 · Parte III — Il simulatore</sub> | [10. Validazione →](10-validazione.md) |
|:---|:---:|---:|
<!-- /nav -->

# 9. I parametri del simulatore

Un **parametro** è una variabile che si può cambiare: un valore nel file della rete (`.inp`), nello scenario
(`scenario_paths/*.yaml`), nei parametri dei tubi (`pipes.yaml`) o, per poche scelte di modello, una costante nel
codice. Per ognuno questo capitolo dice: **cos'è**, **dove si imposta**, **come entra** nel modello, il **valore** con la
sua fonte, **cosa succede se lo cambi** (calcolato dal simulatore) e il **compromesso**.

I grafici si rigenerano con `python -m waterfibersim parameters` (modulo `parameters.py`): usano le stesse funzioni del
simulatore, su un tubo PE100 DN110 SDR11 e uno strumento con le impostazioni di [B23]. Quando un grafico è in MHz,
l'asse di destra dà l'equivalente in bar sull'elica in PE (1 bar ≈ 14,5 MHz). Simboli delle fonti come nell'appendice A.

## 9.1 I parametri dello strumento

![Parametri dello strumento](img/parametri_strumento.png)

Tutte entrano nell'incertezza di una misura attraverso il modello di Soto & Thévenaz ✅ [ST13] Eq. 7–9 (cap. 6):

  σ_ν = (1/SNR) · √(3·δ·Δν_B / (8√2·(1−η)^{3/2})),  SNR = SNR₀ · (Δz/Δz₀) · √N_AV · e^(−αz)

### 9.1.1 Durata dell'impulso `pulse_width_ns`

- **Cos'è.** Quanto dura ogni impulso di interrogazione (pompa). Lo strumento fa la media su tutta la fibra che
  l'impulso occupa: è la **risoluzione spaziale**, Δz = c·τ/(2n) ✅ [ST13] §2.
- **Valore.** 20 ns → 2,04 m ✅ [B23]. Gli strumenti commerciali vanno da 0,2 ns (2 cm, Neubrex) a centinaia di ns ✅.
- **Se lo cambi (grafico 2).** L'SNR è proporzionale a Δz: impulso di 10 ns → σ = 0,81 MHz (doppia); 50 ns → 0,16 MHz.
  Lungo il tubo, con l'elica a 70°, 2 m di fibra coprono circa 0,7 m di tubo ✅ [B23] Eq. 2.
- **Attenzione.** Il grafico tiene fissa la larghezza della campana (58 MHz); con impulsi più corti la campana si
  allarga ✅ [ST13] e l'incertezza peggiora ancora: sotto i 20 ns il grafico è ottimista ⚠️ (legge non nota).
- **Compromesso.** Risoluzione contro rumore. Per la pressione, che cambia lentamente lungo il tubo, 2 m bastano;
  servirebbe di più solo per localizzare eventi brevi (giunti, perdite).

### 9.1.2 Frequenza dell'ADC `adc_sample_rate_msps`

- **Cos'è.** Quante volte al secondo lo strumento legge il fotodiodo. Fissa il **passo dei punti**:
  Δz = c/(2·n·f_ADC) 🧮 (tempo di volo).
- **Valore.** 125 MS/s → 0,82 m ✅ [B23]; commerciali 0,01–10 m ✅ [DIT], [OZ], Neubrex.
- **Se lo cambi.** Più punti, non più informazione: due punti più vicini della risoluzione condividono gran parte della
  stessa fibra, quindi il loro rumore è **correlato** 🧮. Non cambia σ.
- **Consiglio.** Un passo di circa metà risoluzione (come 0,8 m su 2 m) è sufficiente.

### 9.1.3 Passo di frequenza `freq_step_mhz` (δ) e finestra `scan_window_ghz`

- **Cos'è.** Lo strumento costruisce la campana provando tante differenze di frequenza Δν, a passi di δ, dentro la
  finestra.
- **Valore.** δ = 1 MHz, finestra 10,75–11,3 GHz ✅ [B23] Tab. 1 (fase II).
- **Se lo cambi (grafico 1).** σ ∝ √δ: con δ = 5 MHz σ = 0,90 MHz contro 0,40. Il tempo di misura è proporzionale al
  numero di passi = finestra/δ.
- **La finestra** deve contenere tutti i picchi con mezza campana di margine: profilo a riposo (fino a +180 MHz),
  pressione (circa +100 MHz a 7 bar) e temperatura (6 MHz/°C sull'elica). Il comando `instrument` la controlla: oggi
  il margine è circa 120 MHz, cioè circa 20 °C sull'elica.
- **Compromesso.** δ e medie pesano allo stesso modo sull'incertezza; ma cambiare frequenza è lento per lo strumento
  ✅ [ST13] §3, quindi conviene un δ un po' più largo con più medie.

### 9.1.4 Medie `n_averages` (N_AV)

- **Cos'è.** Quante tracce lo strumento somma per ogni passo di frequenza.
- **Valore.** 256 ✅ [B23]; commerciali fino a 65 000 ✅ [OZ].
- **Se lo cambi (grafico 1).** σ ∝ 1/√N_AV ✅ [ST13]: 256 → 0,40 MHz; 4096 → 0,10 MHz (circa 0,007 bar).
- **Il prezzo (grafico 4).** Il tempo cresce come N_AV: con 256 medie su un anello di 4 km circa 5,5 s (senza tempi
  morti, [B23] dichiara 7–20 s); con 65 000 medie si superano i 15 minuti del passo idraulico.
- **Consiglio.** È il parametro più utile: il tempo c'è (la pressione cambia in ore). Fino a qualche migliaio di medie.

### 9.1.5 Qualità dello strumento: `snr0_db`, `snr0_resolution_m`, `linewidth_mhz`

- **Cos'è.** SNR₀ riassume potenze, rivelatore e perdite: SNR della traccia all'inizio della fibra con una sola media.
  `linewidth_mhz` è la larghezza della campana.
- **Valore.** SNR₀ = 0 dB a 2 m, *"realistic"* ✅ [ST13]; campana 58 MHz a 2 m ✅ [ST13].
- **Se lo cambi.** σ ∝ 1/SNR₀ e ∝ √Δν_B. Con questi valori il modello dà 0,40 MHz per le impostazioni di [B23], che
  dichiara meno di 0,5 MHz ✅ (cap. 10).
- **Da sapere.** [B23] dichiara SNR > 40 dB, che con [ST13] darebbe incertezze 500 volte più piccole: definizioni
  diverse ⚠️. Questo parametro va **tarato sullo strumento vero**, il giorno che lo si sceglie.

### 9.1.6 Fibra: `attenuation_db_per_km`, `group_index`, `calc_step_m`

- **Attenuazione** 0,2 dB/km ✅ [ST13]. Grafico 3: a 4 km σ passa da 0,40 a 0,49 MHz; a 50 km 4 MHz. Per i nostri
  anelli (≤ 4 km) è irrilevante.
- **Indice di gruppo** n = 1,468 ⚠️ (scheda Corning da leggere). Sposta i metri del 2 %, non le incertezze.
- **Passo di calcolo** 0,1 m: non è lo strumento, è la griglia su cui il simulatore calcola la verità; deve essere
  ≤ 1/10 della risoluzione (controllato).

## 9.2 I parametri meccaniche

![Parametri meccaniche](img/parametri_meccanica.png)

Entrano nella deformazione della fibra (cap. 5): Lamé (uno o più strati) e ε_fibra = ε_θ sin²α + ε_z cos²α, poi
Δν = C_ε · ε.

### 9.2.1 Angolo dell'elica `angle_deg`

- **Valore.** 70° ⚠️ scelto; [B23] circa 75°.
- **Se lo cambi (grafico 1).** 0° (fibra dritta): 2,0 MHz/bar; 45°: 9,1; 70°: 14,5; 80°: 15,8. Ma la fibra per metro
  di tubo cresce come 1/cos α: 2,9 m a 70°, 5,8 m a 80° (curva blu).
- **Compromesso.** Oltre 70° si guadagna poco segnale e si raddoppia la fibra (e quindi la lunghezza dell'anello,
  il tempo di misura e il costo). 70° è un buon punto.

### 9.2.2 Spessore del tubo (SDR) e diametro

- **Valore.** PE100 SDR11 ✅ schede Uponor, Aliaxis.
- **Se lo cambi (grafico 2).** La sensibilità dipende solo dal rapporto diametro/spessore: SDR11 14,5 MHz/bar, SDR17
  25 MHz/bar 🧮. A parità di SDR il diametro non conta.
- **Compromesso.** Tubi più sottili sentono di più ma reggono meno pressione (SDR17 = PN10). Il tubo lo sceglie
  l'acquedotto, non il sensore.

### 9.2.3 Modulo elastico `E_GPa` e Poisson `nu`

- **Valore.** E = 1,0 GPa (scenari), 1,05 [B23], 1,1 (scheda) ✅; ν = 0,40 [B23], 0,42–0,49 con la temperatura [SB20] ✅.
- **Se lo cambi (grafico 3).** MHz/bar ∝ 1/E: 1,0 → 14,5; 1,1 → 13,2. ν pesa pochi per cento.
- **Attenzione.** Il PE fa **creep**: sotto pressione costante E apparente cala nel tempo ✅ [B23]. È un errore
  sistematico sulla conversione MHz → bar se non calibrato (cap. 10: −20 % a 5 bar dopo minuti).

### 9.2.4 La guaina: `liner` (spessore, E, ν) e il tubo ospite

- **Valore.** 6 mm, 8 GPa, ν 0,35 ⚠️; letteratura: CIPP in feltro almeno 1,7 GPa (ASTM F1216), in vetro circa 10 GPa
  (scheda di una guaina per fognatura) ⚠️. I valori MATRIS veri vengono da OR1.
- **Se lo cambi (grafico 4).** È il parametro **decisivo**:
  - in un tubo ospite in PE la guaina lavora: 3–17 MHz/bar, più la guaina è morbida più si sente;
  - in ghisa degradata (rigidezza 1/10): 2–4 MHz/bar;
  - **in ghisa integra: 0,4–0,7 MHz/bar, qualunque sia la guaina**: la pressione la regge il tubo, la fibra quasi non
    si allunga (cap. 5).
- **Soglia pratica.** Con il rumore di [B23] servono almeno circa 4,5 MHz/bar per vedere 0,1 bar in una misura
  (linea rossa).

## 9.3 I parametri della temperatura e della compensazione

![Parametri della temperatura](img/parametri_temperatura.png)

### 9.3.1 Sensibilità dell'elica alla temperatura `helix_mhz_per_c` (K)

- **Cos'è.** Quanti MHz sposta l'elica per 1 °C: 1 MHz/°C della fibra più la dilatazione del tubo che la tira.
- **Valore.** 6 MHz/°C; forbice da fonti 3,5 ([B23] con K_T) – 8 ([SB20], tubo trattenuto) ⚠️.
- **Se lo cambi (grafico 1).** 1 °C non compensato vale 0,24–0,55 bar apparenti.
- **Se è sbagliata (grafico 2).** Errore sistematico = ΔK·ΔT / (MHz per bar): con 1 MHz/°C di errore e 10 °C dalla misura
  di base, 0,69 bar; con l'escursione stagionale (11–15 °C ✅ [SB20]) anche di più. Non cala con le medie.
- **Consiglio.** È il parametro più incerto e più pesante: va **calibrato in opera** (metodo da cercare, cap. 11).

### 9.3.2 Terreno: `baseline_c`, `soil_c`, `drift_c_per_day`, `hotspots`

- **Valore.** S1t: 18 → 10 °C, −0,15 °C/giorno ✅ [SB20] (11–15 °C in 90 giorni); punti caldi fino a 7–10 °C ✅ [AV17],
  posizione e ampiezza ⚠️ scelte. `delta_c` può essere positivo o negativo.
- **Eventi.** Un punto caldo può avere un orario (`from_h`, `to_h`): allora è un **evento**, presente solo in quelle ore
  (in S1th: +4 °C su P3 dalle 14 alle 17, scelto per mostrare l'effetto).
- **Effetto.** ΔT dalla misura di base, uguale per elica e ritorno nello stesso punto. Nel waterfall della differenza
  dalla misura di base (grafico 3 della figura del segnale) un punto caldo permanente è una banda verticale, un evento
  un rettangolo; nella variazione giornaliera (grafico 4) il punto caldo permanente sparisce, l'evento resta.

### 9.3.3 Acqua: `water.source_c`, `soil_k_w_mk`, `pipe_k_w_mk`, `tsoi`

- **Cos'è.** L'acqua esce dal serbatoio a `source_c` e si avvicina al terreno con il tempo di permanenza ✅ [BL24].
- **Valore.** +2 °C sul terreno ⚠️ ([BL24] misura 0,6–1,6 °C); PE 0,38 W/(m·K) ✅ scheda; sabbia 1,6 ✅ [BL24];
  sfera di influenza 1 ⚠️ ([BL24]: 1–2 raggi).
- **Se lo cambi (grafico 4).** Dopo 1 km a 0,8 m/s arriva ancora il 77 % della differenza serbatoio–terreno; a
  0,1 m/s (notte) solo il 13 %. La sfera di influenza sposta le curve, non la conclusione: **la temperatura dell'acqua
  segue i consumi** nelle reti piccole.

### 9.3.4 Media del riferimento (compensazione)

- **Cos'è.** Su quanti metri del ritorno si media la temperatura prima di toglierla dall'elica (`compensate`).
- **Se lo cambi (grafico 3).** Punto per punto: 0,14–0,32 bar di errore casuale (secondo K); mediata su 74 m:
  0,045–0,065 bar. Oltre circa 100 m si guadagna poco: resta il rumore dell'elica.
- **Compromesso.** La media **mobile** sfuma le variazioni locali (fino a 0,6 bar ai bordi di un punto caldo); la
  media **adattiva** (soglia 2σ, mediana su 10 m ⚠️) le conserva (0,2 bar), con poco rumore in più.
- **Misura di base.** Mediarne 10 riduce di circa 3 volte l'errore "congelato" (cap. 7).

## 9.4 I parametri idrauliche

![Parametri idrauliche](img/parametri_idraulica.png)

- **Prelievi, diametri, scabrezza** (`.inp`). Il segnale da misurare è l'escursione giornaliera di pressione: in fondo
  a una strada di 1 km con 11 rubinetti da 0,3 L/s in DN110 circa 0,28 bar (grafico 1, formula di Hazen-Williams
  ✅ [EPA] Tab. 3.1). Raddoppiando i prelievi l'escursione cresce di circa 3,6 volte (perdita ∝ Q^1,852).
- **Criteri di progetto** (grafico 2): una rete ben progettata tiene la velocità al picco tra 0,5 e 1,5 m/s ⚠️
  (manuali; EN 805 da leggere), e quindi **escursioni piccole**: 0,1–0,3 bar. È il motivo per cui il sensore deve
  arrivare a pochi centesimi di bar.
- **Quota e pendenza** (`Elev` dei nodi, testa del serbatoio): danno pressione statica (circa 0,1 bar/m), fissa nel
  tempo (cap. 4).

## 9.5 Riepilogo: tutti i parametri in tabella

### Rete e idraulica (file `.inp` di EPANET)

| parametro | default | intervallo | fonte | peso sul risultato |
|---|---|---|---|---|
| diametro interno dei tubi | da OD − 2·spessore (PE100 SDR11) | catalogo | ✅ schede Uponor, Aliaxis | perdita di carico ∝ D^−4,87: decide la variazione di pressione |
| scabrezza Hazen-Williams C | PE 140, ghisa 130 | 130–150 (nuovi) | ✅ [EPA] Tab. 3.2 | perdita ∝ C^−1,852 |
| consumi (`Demand`) e andamento giornaliero (`DAILY`) | 0,3 L/s per rubinetto (S1), 4 L/s per utenza (griglia); punte 1,6 × alle 8 e alle 19 | — | ⚠️ scelti per stare nei criteri di progetto | è il "segnale" idraulico: 0,04–0,8 bar di escursione |
| criteri di progetto (velocità 0,5–1,5 m/s, perdita ≤ 10 m/km) | — | — | ⚠️ corsi e manuali; EN 805 da leggere | servono a non inventare reti irrealistiche |
| quota del pelo dell'acqua del serbatoio | 50 m sul tubo (circa 4,9 bar) | — | ⚠️ scelta | pressione statica |
| pendenza della strada | 0 % o 2 % | — | ⚠️ scelta | +1 bar ogni 10 m di discesa, fisso nel tempo |
| passo idraulico | 15 min | — | scelta | i consumi cambiano a scalini di un'ora |

Verifica: la perdita di carico di EPANET coincide con la formula di [EPA] Tab. 3.1 (`validate`).

### Tubo e guaina (`pipes.yaml`, modello in `mechanics.py`)

| parametro | default | intervallo | fonte | peso |
|---|---|---|---|---|
| E del PE100 | 1,0 GPa | 1,05 ([B23]); 1,1 (scheda) | ✅ | MHz/bar ∝ 1/E |
| ν del PE | 0,40 | 0,42–0,49 con la temperatura | ✅ [B23], [SB20] | pochi % |
| creep del PE (Burgers E2, η2, η3) | non modellato | E2 = 1,65–4,47 GPa | ✅ [B23] Tab. 2 | +20 % a 5 bar dopo minuti; oltre a 10 bar molto di più |
| ghisa: E, ν | 170 GPa, 0,26 | — | ⚠️ (scheda con unità errata) | rende il tubo quasi indeformabile |
| guaina: spessore, E, ν | 6 mm, 8 GPa, 0,35 | E 1,7 (feltro, minimo ASTM F1216) – 10,3 GPa (vetro UV) | ⚠️ da laminato MATRIS OR1 | **decide se la pressione si vede** |
| posizione della fibra nella guaina | metà spessore | — | ⚠️ | piccolo |
| angolo dell'elica | 70° | 60–80° | ⚠️ scelto; [B23] 75° | ε_fibra = ε_θ sin²α + ε_z cos²α |

Sensibilità dell'elica alla pressione (modello a strati, `validate`): PE DN110 senza guaina circa 13–14 MHz/bar; guaina
in tubo in PE 3–10 MHz/bar; **guaina in ghisa integra circa 0,4–0,5 MHz/bar** (pari al rumore di una misura).

### Fibra e posa (`scenario_paths/*.yaml`, sezione della fibra)

| parametro | default | fonte | note |
|---|---|---|---|
| tratto di misura | elica, `bonded` (rete di prova) o `embedded` (MATRIS) | ✅ [B23]; decisione utente | sente pressione + temperatura |
| tratto di riferimento | dritto, libero in un tubetto | ✅ [B23] Fig. 7c; decisione MATRIS | sente solo temperatura |
| cavi (`lead`) e giunzione | lunghezze nello scenario | — | sentono la temperatura del terreno |
| indice di gruppo n | 1,468 | ⚠️ a memoria (scheda Corning da scaricare) | sposta i metri del 2 % |
| attenuazione | 0,2 dB/km | ✅ [ST13] | sotto i 4 km pesa poco |
| C_ε, C_T | 0,05 MHz/µε, 1 MHz/°C | ✅ [B23] Eq. 1 (dipendono dal cavo) | errore di calibrazione = errore sistematico |
| ν_B0 | 10 880 MHz | ⚠️ da [B23] Fig. 7a a occhio | non cambia le differenze |
| profilo a riposo | elica 105–180 MHz continuo, tubetto +65 MHz, ondulazioni 1 MHz | ✅ valori [B23], ⚠️ forma | si cancella con la misura di base |
| passo di calcolo `calc_step_m` | 0,1 m | scelta | ≤ 1/10 della risoluzione, non è lo strumento |

### Interrogatore (sezione `interrogator`)

| parametro | default | intervallo commerciale | fonte | effetto |
|---|---|---|---|---|
| durata dell'impulso | 20 ns → 2,04 m | 0,2 ns – 500 ns | ✅ [B23]; Neubrex, OZ, [DIT] | risoluzione; SNR ∝ Δz |
| campionamento ADC | 125 MS/s → 0,82 m | 0,01–10 m | ✅ [B23]; [DIT], [OZ] | passo dei punti |
| passo di frequenza δ | 1 MHz | 1–5 MHz | ✅ [B23] Tab. 1 | σ ∝ √δ; tempo ∝ 1/δ |
| medie N_AV | 256 | 1–65 000 | ✅ [B23], [OZ] | σ ∝ 1/√N_AV; tempo ∝ N_AV |
| finestra di scansione | 10,75–11,3 GHz | — | ✅ [B23] | deve contenere i picchi (margine circa 120 MHz ≈ 10 °C sull'elica) |
| larghezza della campana | 58 MHz a 2 m | 27–100 MHz | ✅ [ST13] | σ ∝ √Δν_B |
| SNR₀ | 0 dB a 2 m, 1 traccia | — | ✅ [ST13] "realistic" | σ ∝ 1/SNR |

Risultato (passo 3a, `instrument`): σ circa 0,40–0,46 MHz per misura (circa 0,03 bar sull'elica in PE); tempo minimo
circa 3–6 s per misura (tempi morti esclusi).

### Temperatura (sezione `temperature`)

| parametro | default (scenari) | fonte | effetto |
|---|---|---|---|
| terreno alla misura di base, oggi, deriva | 18 → 10 °C, −0,15 °C/giorno (S1t) | ✅ [SB20] 11–15 °C in 90 giorni | 1 °C ≈ 0,25–0,55 bar apparenti |
| sensibilità dell'elica alla temperatura K | 6 MHz/°C | ⚠️ forbice 3,5 ([B23] K_T) – 8 ([SB20]) | **parametro più incerto: va calibrato** |
| punti caldi locali | +3 °C su 40 m (S1th) | ✅ ordine di grandezza [AV17]; ⚠️ posizione scelta | sembrano anomalie di pressione |
| acqua: temperatura alla sorgente | +2 °C sul terreno (S1w) | ⚠️; [BL24] 0,6–1,6 misurati, 1–5 K nelle analisi | segue i consumi; può invertire il segno della variazione giornaliera |
| acqua: conducibilità PE e terreno, sfera di influenza | 0,38; 1,6 W/(m·K); 1 | ✅ scheda PE100; ✅ [BL24]; ⚠️ | costante di tempo 1,3–2,4 h |

### Elaborazione di esempio (fit e compensazione)

| parametro | default | fonte | effetto |
|---|---|---|---|
| fit: soglia η | 0,5 (±FWHM/2), 3 passate | ✅ [ST13] | +17 % di errore rispetto alla formula (forma lorentziana) |
| misura di base: numero di misure mediate | 1 | 🧮 | il suo rumore è "congelato": con 10 misure circa 3 volte meno |
| media del riferimento | 74 m (mobile o adattiva) | 🧮 | rumore 0,24 → 0,056 bar; la mobile sfuma i punti caldi |
| soglia della media adattiva | 2 σ del riferimento (dai dati), mediana su 10 m | ⚠️ scelte | conserva i punti caldi (0,22 contro 0,65 bar) |

<!-- nav-fondo -->

| [← 8. Logica del simulatore](08-logica-del-simulatore.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 9 di 11 · Parte III — Il simulatore</sub> | [10. Validazione →](10-validazione.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
