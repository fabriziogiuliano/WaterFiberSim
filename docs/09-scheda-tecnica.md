<!-- nav -->
| [← 8. Logica del simulatore](08-logica-del-simulatore.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 9 di 11 · Parte III — Il simulatore</sub> | [10. Validazione →](10-validazione.md) |
|:---|:---:|---:|
<!-- /nav -->

# 9. Scheda tecnica dei parametri

Ogni parametro: dove si imposta, valore di default, intervallo plausibile, da dove viene, quanto pesa sul risultato.
Stato delle fonti come in `docs/fonti.md`: ✅ verificato su fonte letta · 🧮 calcolato · ⚠️ scelto o da verificare.
Sigle delle fonti: [B23] Bertulessi 2023 · [ST13] Soto & Thévenaz 2013 · [BL24] Blokker 2024 · [SB20] Stewart & Bilgin 2020 ·
[AV17] Agudelo-Vera 2017 · [EPA] manuale EPANET 2.2 · [DIT]/[OZ] schede degli interrogatori.

## 1. Rete e idraulica (file `.inp` di EPANET)

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

## 2. Tubo e guaina (`pipes.yaml`, modello in `mechanics.py`)

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

## 3. Fibra e posa (`scenario_paths/*.yaml`, sezione della fibra)

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

## 4. Interrogatore (sezione `interrogator`)

| manopola | default | intervallo commerciale | fonte | effetto |
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

## 5. Temperatura (sezione `temperature`)

| parametro | default (scenari) | fonte | effetto |
|---|---|---|---|
| terreno alla misura di base, oggi, deriva | 18 → 10 °C, −0,15 °C/giorno (S1t) | ✅ [SB20] 11–15 °C in 90 giorni | 1 °C ≈ 0,25–0,55 bar apparenti |
| sensibilità dell'elica alla temperatura K | 6 MHz/°C | ⚠️ forbice 3,5 ([B23] K_T) – 8 ([SB20]) | **parametro più incerto: va calibrato** |
| punti caldi locali | +3 °C su 40 m (S1th) | ✅ ordine di grandezza [AV17]; ⚠️ posizione scelta | sembrano anomalie di pressione |
| acqua: temperatura alla sorgente | +2 °C sul terreno (S1w) | ⚠️; [BL24] 0,6–1,6 misurati, 1–5 K nelle analisi | segue i consumi; può invertire il segno della variazione giornaliera |
| acqua: conducibilità PE e terreno, sfera di influenza | 0,38; 1,6 W/(m·K); 1 | ✅ scheda PE100; ✅ [BL24]; ⚠️ | costante di tempo 1,3–2,4 h |

## 6. Elaborazione di esempio (fit e compensazione)

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
