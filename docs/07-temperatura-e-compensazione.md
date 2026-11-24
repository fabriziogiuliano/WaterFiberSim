<!-- nav -->
| [← 6. Modello dello strumento e dato grezzo](06-strumento-e-dato-grezzo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 7 di 13 · Parte II — I modelli</sub> | [8. Guida all'uso →](08-guida-all-uso.md) |
|:---|:---:|---:|
<!-- /nav -->

# 7. Temperatura e compensazione

## 7.1 Effetto della temperatura sulla misura

Il ritorno libero sente 1 MHz/°C. L'elica sente anche la **dilatazione del tubo**: tra circa 3,5 ([\[B23\]](A-fonti.md#b23) con K_T) e
8 MHz/°C ([\[SB20\]](A-fonti.md#sb20), tubo trattenuto dal terreno) (da verificare). Quindi **1 °C si legge come 0,25–0,55 bar**.

## 7.2 Temperatura del terreno

- Cambia lentamente: 11–15 °C in 90 giorni alla profondità delle condotte [\[SB20\]](A-fonti.md#sb20).
- Cambia da punto a punto: fino a 10 °C in città [\[AV17\]](A-fonti.md#av17) (punti caldi).
- Scenari S1t (raffreddamento uniforme) e S1th (+ punto caldo permanente su P6 e un evento di 3 ore su P3): senza
  compensare, −3,3 bar di errore con 8 °C; punto caldo ed evento sembrano anomalie di pressione. Nel waterfall della
  differenza dalla misura di base il punto caldo è una banda verticale, l'evento un rettangolo.

## 7.3 Temperatura dell'acqua

L'acqua tende alla temperatura del terreno con una legge esponenziale nel tempo di permanenza [\[BL24\]](A-fonti.md#bl24) Eq. 1–3;
costante di tempo 1,3–2,4 h nel tubo PE DN110 (calcolo nostro). Di giorno arriva veloce e "calda" in fondo alla strada, di notte si
porta al terreno: la temperatura segue i **consumi**. In S1w la variazione giornaliera della pressione letta senza
compensare ha il **segno sbagliato**.

## 7.4 Compensazione con la fibra di riferimento

Per ogni punto dell'elica si prende il ritorno sullo stesso tubo nello stesso punto (interpolato), $\Delta T$ = $\Delta\nu$_rif / $C_T$,
e si toglie K·$\Delta T$ dall'elica (calcolo nostro). Comandi: `compensate` (senza rumore) e `compensate --measured` (sul dato grezzo).

| fonte d'errore | entità | rimedio |
|---|---|---|
| K sbagliato (dentro la forbice) | ±1,1–1,4 bar con 8 °C: **sistematico** | calibrare K in opera |
| rumore del ritorno × K | 0,24 bar per misura | mediare il ritorno su circa 74 m → 0,056 bar |
| la media sfuma le variazioni locali | fino a 0,58–0,65 bar ai bordi di un punto caldo | media **adattiva** → 0,19–0,22 |
| rumore della misura di base | uguale in tutte le misure ("congelato") | mediare 10 misure di base → circa 3 volte meno |

Il modello degli errori coincide con il dato rumoroso (0,059 contro 0,055 bar, cap. 11). Gli esperimenti sugli scenari S1th e S1w, con figure e tabelle, sono nel cap. 12, §12.5–12.6.

## 7.5 Questioni aperte

Calibrazione di K; temperatura del serbatoio che cambia nel tempo; ritardo termico della parete (minuti, piccolo
rispetto alle ore (calcolo nostro)). Cap. 11.

<!-- nav-fondo -->

| [← 6. Modello dello strumento e dato grezzo](06-strumento-e-dato-grezzo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 7 di 13 · Parte II — I modelli</sub> | [8. Guida all'uso →](08-guida-all-uso.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
