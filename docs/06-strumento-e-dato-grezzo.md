<!-- nav -->
| [← 5. Meccanica del tubo e della guaina](05-meccanica-del-tubo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 6 di 13 · Parte II — I modelli</sub> | [7. Temperatura e compensazione →](07-temperatura-e-compensazione.md) |
|:---|:---:|---:|
<!-- /nav -->

# 6. Modello dello strumento e dato grezzo

## 6.1 Parametri temporali e risoluzione spaziale

Lo strumento si imposta in unità di tempo (durata dell'impulso, frequenza di campionamento). Le distanze lungo la fibra
si ricavano dal tempo di volo della luce, che percorre ogni tratto due volte, all'andata e al ritorno:

$$\Delta z_s = \frac{c}{2 \cdot n \cdot f_{ADC}} \qquad \Delta z = \frac{c \cdot \tau}{2 \cdot n}$$

dove:

| simbolo | nome | unità | valore |
|---|---|---|---|
| $\Delta z_s$ | distanza tra due punti consecutivi lungo la fibra | m | 0,82 (con 125 MS/s) |
| $\Delta z$ | tratto di fibra su cui lo strumento fa la media (risoluzione) | m | 2,04 (con 20 ns) |
| $c$ | velocità della luce nel vuoto | m/s | 299 792 458 |
| $n$ | indice di gruppo della fibra | — | 1,468 |
| $f_{ADC}$ | frequenza di campionamento dell'ADC | campioni/s | 125·10⁶ |
| $\tau$ | durata dell'impulso | s | 20·10⁻⁹ |

[\[B23\]](A-fonti.md#b23) dichiara 0,8 m e 2 m; la definizione di risoluzione è quella di [\[ST13\]](A-fonti.md#st13) §2.
Il valore n = 1,468 dell'indice di gruppo va confermato sulla scheda della fibra (da verificare).

## 6.2 Incertezza sulla frequenza Brillouin

Modello di Soto & Thévenaz [\[ST13\]](A-fonti.md#st13) Eq. 7–9, validato sui loro dati (cap. 11):

$$\sigma_\nu = \frac{1}{\mathrm{SNR}}\sqrt{\tfrac{3}{4} \cdot \delta \cdot \Delta\nu_B} \qquad \mathrm{SNR}(z) = \mathrm{SNR}_0 \cdot \frac{\Delta z}{\Delta z_0} \cdot \sqrt{N_{AV}} \cdot e^{-\alpha z}$$

dove:

| simbolo | nome | unità | valore (impostazioni di [\[B23\]](A-fonti.md#b23)) |
|---|---|---|---|
| $\sigma_\nu$ | incertezza (deviazione standard) della frequenza Brillouin stimata in una misura | MHz | circa 0,40 |
| $\mathrm{SNR}$ | rapporto segnale/rumore della traccia al picco (lineare) | — | circa 16 |
| $\delta$ | passo della scansione in frequenza | MHz | 1 |
| $\Delta\nu_B$ | larghezza a metà altezza dello spettro Brillouin | MHz | 58 |
| $\mathrm{SNR}_0$ | rapporto segnale/rumore all'inizio della fibra, con risoluzione $\Delta z_0$ e una sola traccia | — | 1 (0 dB) |
| $\Delta z$, $\Delta z_0$ | risoluzione usata e risoluzione a cui è dato $\mathrm{SNR}_0$ | m | 2,04 e 2 |
| $N_{AV}$ | numero di tracce mediate per ogni passo di frequenza | — | 256 |
| $\alpha$ | attenuazione della fibra | 1/m (da 0,2 dB/km) | 4,6·10⁻⁵ |
| $z$ | distanza lungo la fibra dalla porta A | m | — |

Con le impostazioni di [\[B23\]](A-fonti.md#b23): **σ ≈ 0,40–0,46 MHz per misura** (circa 0,03 bar sull'elica in PE). Medie e passo di
frequenza pesano allo stesso modo; la distanza pesa poco sotto i 4 km. Comando: `instrument`.

## 6.3 Dato grezzo (L0)

Comando `measure`: per ogni punto dello strumento e ogni misura, lo **spettro intero** (551 frequenze): media su 2 m
di campane lorentziane (58 MHz) [\[ST13\]](A-fonti.md#st13) Fig. 5, più rumore gaussiano 1/SNR [\[ST13\]](A-fonti.md#st13). Anche la misura di base è
rumorosa. File `raw_L0_<fibra>.npz` con le etichette vere.

## 6.4 Stima del picco (fit di esempio)

Parabola sui punti sopra metà picco, ricentrata in più passate [\[ST13\]](A-fonti.md#st13). Ritrova $\nu_B$ con circa il 17 % di errore in
più della formula (la campana è lorentziana, non una parabola: previsto da [\[ST13\]](A-fonti.md#st13)). Dove la finestra di 2 m prende
tratti diversi (giunzione, cavi) gli spettri hanno più picchi e il fit sbaglia: quei punti vanno scartati.

## 6.5 Tempo di misura

Tempo minimo di una misura: passi × medie × andata e ritorno sull'anello, 3–6 s (calcolo nostro); lo strumento reale ha tempi morti
([\[B23\]](A-fonti.md#b23): 7–20 s). Molto meno del passo idraulico (15 min).

Parametri: cap. 10, sezione 4. Effetto sulla compensazione: cap. 7. Esperimenti sullo scenario S1: cap. 12, §12.3–12.4.

<!-- nav-fondo -->

| [← 5. Meccanica del tubo e della guaina](05-meccanica-del-tubo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 6 di 13 · Parte II — I modelli</sub> | [7. Temperatura e compensazione →](07-temperatura-e-compensazione.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
