<!-- nav -->
| [← 1. Introduzione](01-introduzione.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 2 di 11 · Parte I — Il problema e la fisica</sub> | [3. Il sensore sul tubo →](03-il-sensore-sul-tubo.md) |
|:---|:---:|---:|
<!-- /nav -->

# 2. Il principio di misura: la fibra Brillouin

## 2.1 La "nota" della fibra

Il vetro della fibra vibra con onde sonore minuscole; la luce che le incontra torna indietro con la frequenza
spostata di circa **10,8 GHz** ✅ [B23]. Questo spostamento, la frequenza Brillouin ν_B, cambia con l'allungamento e
con la temperatura della fibra ✅ [B23] Eq. 1:

  Δν_B = C_ε · ε + C_T · ΔT,  con C_ε ≈ 0,05 MHz/µε e C_T ≈ 1 MHz/°C

I coefficienti dipendono dal cavo e da come è fissato ✅ [B23]: vanno calibrati (cap. 7).

## 2.2 La BOTDA: leggere ogni metro

Lo strumento (interrogatore) manda **impulsi** da un capo della fibra (porta A) e una **luce continua** dall'altro capo
(porta B): la fibra è un **anello** ✅ [OZ], [DIT]. Dove la differenza di frequenza tra le due luci è uguale alla nota
del punto, l'impulso cede energia alla luce continua; il ritardo dice **dove** (circa 10 ns per metro, andata e
ritorno), la frequenza a cui succede dice **quanto**. Scansionando la differenza di frequenza si ricostruisce in ogni
punto una **campana** (spettro di guadagno), il cui picco è ν_B ✅ [B23] §2.1.

Spiegazione passo per passo con lo schema a blocchi: appendice B, §2.1, e lo schema
[dfos-interrogatore.drawio.svg](img/dfos-interrogatore.drawio.svg).

## 2.3 Le manopole e i limiti

Risoluzione spaziale (durata dell'impulso, circa 2 m), passo dei punti (frequenza dell'ADC, circa 0,8 m), passo di
frequenza, numero di medie: decidono incertezza e tempo di misura. Sono trattate nel cap. 6.

## 2.4 Strumenti reali

Esistono interrogatori commerciali con queste caratteristiche: Prysmian DITEST (80 km), OZ Optics DSTS (100 km),
Neubrex (fino a 2 cm di risoluzione) ✅ (appendice A, sezione "Manopole dello strumento").

<!-- nav-fondo -->

| [← 1. Introduzione](01-introduzione.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 2 di 11 · Parte I — Il problema e la fisica</sub> | [3. Il sensore sul tubo →](03-il-sensore-sul-tubo.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
