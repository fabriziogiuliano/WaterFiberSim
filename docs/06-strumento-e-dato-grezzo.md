<!-- nav -->
| [← 5. Meccanica del tubo e della guaina](05-meccanica-del-tubo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 6 di 11 · Parte II — I modelli</sub> | [7. Temperatura e compensazione →](07-temperatura-e-compensazione.md) |
|:---|:---:|---:|
<!-- /nav -->

# 6. Modello dello strumento e dato grezzo

## 6.1 Parametri temporali e risoluzione spaziale

Nello scenario i parametri dello strumento sono quelli reali, espressi nel tempo; i metri si ricavano con il tempo di volo:

  **passo dei punti: Δz_s = c / (2 · n · f_ADC)**  ·  **risoluzione spaziale: Δz = c · τ / (2 · n)**

dove:

| simbolo | nome | unità | valore |
|---|---|---|---|
| Δz_s | distanza tra due punti consecutivi lungo la fibra | m | 0,82 (con 125 MS/s) |
| Δz | tratto di fibra su cui lo strumento fa la media (risoluzione) | m | 2,04 (con 20 ns) |
| c | velocità della luce nel vuoto | m/s | 299 792 458 |
| n | indice di gruppo della fibra | — | 1,468 |
| f_ADC | frequenza di campionamento dell'ADC | campioni/s | 125·10⁶ |
| τ | durata dell'impulso | s | 20·10⁻⁹ |

Il **2 al denominatore** nasce dal percorso della luce. L'impulso parte dalla porta A e arriva al punto z; il segnale
che nasce lì torna indietro fino alla porta A, dove viene letto. Un punto più lontano di Δz costa quindi Δz in più
all'andata **e** Δz in più al ritorno: il suo segnale arriva dopo un tempo 2·Δz·n/c in più. Per questo 10 ns di tempo
corrispondono a circa 1 m di fibra, e non a 2 m.

✅ [\[B23\]](A-fonti.md#b23) dichiara 0,8 m e 2 m; la definizione di risoluzione è quella di [\[ST13\]](A-fonti.md#st13) §2.
L'indice di gruppo n = 1,468 è ⚠️ (scheda della fibra da leggere).

## 6.2 Incertezza sulla frequenza Brillouin

Modello di Soto & Thévenaz ✅ [\[ST13\]](A-fonti.md#st13) Eq. 7–9, validato sui loro dati (cap. 10):

  **σ_ν = (1 / SNR) · √(¾ · δ · Δν_B)**  ·  **SNR(z) = SNR₀ · (Δz / Δz₀) · √N_AV · e^(−α·z)**

dove:

| simbolo | nome | unità | valore (impostazioni di [\[B23\]](A-fonti.md#b23)) |
|---|---|---|---|
| σ_ν | incertezza (deviazione standard) della frequenza Brillouin stimata in una misura | MHz | circa 0,40 |
| SNR | rapporto segnale/rumore della traccia al picco (lineare) | — | circa 16 |
| δ | passo della scansione in frequenza | MHz | 1 |
| Δν_B | larghezza a metà altezza dello spettro Brillouin | MHz | 58 |
| SNR₀ | rapporto segnale/rumore all'inizio della fibra, con risoluzione Δz₀ e una sola traccia | — | 1 (0 dB) |
| Δz, Δz₀ | risoluzione usata e risoluzione a cui è dato SNR₀ | m | 2,04 e 2 |
| N_AV | numero di tracce mediate per ogni passo di frequenza | — | 256 |
| α | attenuazione della fibra | 1/m (da 0,2 dB/km) | 4,6·10⁻⁵ |
| z | distanza lungo la fibra dalla porta A | m | — |

Con le impostazioni di [\[B23\]](A-fonti.md#b23): **σ ≈ 0,40–0,46 MHz per misura** (circa 0,03 bar sull'elica in PE). Medie e passo di
frequenza pesano allo stesso modo; la distanza pesa poco sotto i 4 km. Comando: `instrument`.

## 6.3 Dato grezzo (L0)

Comando `measure`: per ogni punto dello strumento e ogni misura, lo **spettro intero** (551 frequenze): media su 2 m
di campane lorentziane (58 MHz) ✅ [\[ST13\]](A-fonti.md#st13) Fig. 5, più rumore gaussiano 1/SNR ✅ [\[ST13\]](A-fonti.md#st13). Anche la misura di base è
rumorosa. File `raw_L0_<fibra>.npz` con le etichette vere.

## 6.4 Stima del picco (fit di esempio)

Parabola sui punti sopra metà picco, ricentrata in più passate ✅ [\[ST13\]](A-fonti.md#st13). Ritrova ν_B con circa il 17 % di errore in
più della formula (la campana è lorentziana, non una parabola: previsto da [\[ST13\]](A-fonti.md#st13)). Dove la finestra di 2 m prende
tratti diversi (giunzione, cavi) gli spettri hanno più picchi e il fit sbaglia: quei punti vanno scartati.

## 6.5 Tempo di misura

Tempo minimo di una misura: passi × medie × andata e ritorno sull'anello, 3–6 s 🧮; lo strumento reale ha tempi morti
([\[B23\]](A-fonti.md#b23): 7–20 s). Molto meno del passo idraulico (15 min).

Parametri: cap. 9, sezione 4. Effetto sulla compensazione: cap. 7.

<!-- nav-fondo -->

| [← 5. Meccanica del tubo e della guaina](05-meccanica-del-tubo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 6 di 11 · Parte II — I modelli</sub> | [7. Temperatura e compensazione →](07-temperatura-e-compensazione.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
