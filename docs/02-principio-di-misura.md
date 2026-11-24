<!-- nav -->
| [← 1. Introduzione](01-introduzione.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 2 di 11 · Parte I — Il problema e la fisica</sub> | [3. Il sensore sul tubo →](03-il-sensore-sul-tubo.md) |
|:---|:---:|---:|
<!-- /nav -->

# 2. Il principio di misura: la fibra Brillouin

## 2.1 La "nota" della fibra

Il vetro della fibra vibra con onde sonore minuscole. La luce che le incontra torna indietro con la frequenza
spostata di circa **10,8 GHz** ✅ [\[B23\]](A-fonti.md#b23): è la **frequenza Brillouin** ν_B, una specie di "nota" del vetro. Come una
corda di chitarra, la nota cambia se la fibra viene tirata o scaldata ✅ [\[B23\]](A-fonti.md#b23) Eq. 1:

  Δν_B = C_ε · ε + C_T · ΔT,  con C_ε ≈ 0,05 MHz/µε e C_T ≈ 1 MHz/°C

(1 µε = un micrometro di allungamento per metro). I coefficienti dipendono dal cavo e da come è fissato ✅ [\[B23\]](A-fonti.md#b23):
vanno calibrati (cap. 7). Misurare ν_B lungo la fibra significa quindi misurare allungamento e temperatura metro per
metro.

## 2.2 Lo strumento: schema a blocchi

La tecnica usata è la **BOTDA** (*Brillouin Optical Time-Domain Analysis*). La fibra fa un **anello**: parte dalla
**porta A** dello strumento (l'interrogatore), percorre il tubo (andata a elica, cap. 3) e torna alla **porta B** dello
stesso strumento ✅ [\[OZ\]](A-fonti.md#oz): *"requires both ends of fiber to be connected"*.

![Interrogatore BOTDA con fibra ad anello: schema a blocchi](img/dfos-interrogatore.drawio.svg)

*Schema ricavato da [\[B23\]](A-fonti.md#b23) Fig. 2 e §2.1; modificabile in draw.io.*

Lo schema, blocco per blocco (valori di [\[B23\]](A-fonti.md#b23) §2.1, citazioni nell'appendice A):

| ramo | blocco | cosa fa |
|---|---|---|
| sorgente | **laser DFB** a 1530 nm, continuo | una sola luce, da cui nascono entrambe le luci di misura |
| | **accoppiatore 3 dB** | divide la luce in due rami uguali |
| ramo blu: **luce di lettura** (*sonda*) | **generatore RF** + **modulatore Mach-Zehnder** | sposta la frequenza di Δν ≈ 10,8 GHz: la sonda è un tono continuo a frequenza laser − Δν. Il generatore RF è **il parametro**: cambiandolo si sceglie Δν |
| | **depolarizzatore** | rende la misura indipendente dalla polarizzazione della luce |
| | **circolatore C1 → porta B** | manda la sonda nell'anello dal capo B |
| ramo arancione: **impulso di interrogazione** (*pompa*) | **generatore di impulsi** + **modulatore** | impulsi di 20 ns, 30 000 al secondo |
| | **amplificatore EDFA** | rende gli impulsi forti |
| | **circolatore C2 → porta A** | manda gli impulsi nell'anello dal capo A |
| ramo verde: **ricezione** | **circolatore C2 → fotodiodo** (125 MHz) | la sonda, dopo aver fatto tutto l'anello, rientra da A e C2 la devia al fotodiodo: **qui si legge** |
| | **ADC** (125 milioni di campioni al secondo) | campiona la potenza letta: un campione ogni 0,8 m di fibra |
| | **elaborazione** | per ogni posizione costruisce lo spettro e ne trova il picco ν_B(z) |

Le due luci vengono dallo **stesso laser**, quindi la loro differenza di frequenza è fissata elettronicamente e con
precisione: serve, perché 1 MHz di errore su Δν vale circa 20 µε 🧮.

## 2.3 Come nasce la misura

1. **Le due luci si incrociano.** Gli impulsi (pompa) partono da A, la luce di lettura (sonda) parte da B: percorrono
   l'anello in versi opposti. Gli impulsi arrivati in B non si leggono; la sonda rientra in A e si legge.
2. **Lo scambio di energia.** Dove un impulso incrocia la sonda **e** Δν coincide con la ν_B di quel punto, l'impulso
   cede energia alla sonda ✅ [\[OZ\]](A-fonti.md#oz): *"When the frequency difference between the two lasers is equal to the 'Brillouin
   frequency' of the fiber, there is a strong interaction"*. L'impulso "scrive", la sonda "porta" fino ad A: in A
   arriva un **gradino** di potenza in più.
3. **Il tempo dà la posizione.** Il gradino nato nel punto z arriva in A dopo t = 2·z·n/c, circa 10 ns per metro
   (andata dell'impulso, ritorno della sonda). La durata dell'impulso fissa la **risoluzione** (20 ns ≈ 2 m), il
   campionamento dell'ADC fissa il **passo** (125 MS/s ≈ 0,8 m) ✅ [\[B23\]](A-fonti.md#b23). Formule e valori: cap. 6.
4. **La frequenza dà la grandezza.** Lo strumento ripete la misura per tanti valori di Δν (in [\[B23\]](A-fonti.md#b23) una scansione di
   1 GHz). Per ogni punto ottiene una **campana**, lo spettro di guadagno Brillouin, il cui **picco** è ν_B(z) ✅ [\[B23\]](A-fonti.md#b23).
5. **Dal picco alle grandezze.** ν_B(z), confrontata con una **misura di base** a tubo vuoto, dà allungamento e
   temperatura (§2.1); dall'allungamento dell'elica si ricava la pressione (cap. 5), dalla temperatura del ritorno si
   compensa (cap. 7).

| livello | contenuto | chi lo produce |
|---|---|---|
| **L0** | per ogni punto e ogni misura, lo spettro (potenza in funzione di Δν), con il rumore | il simulatore (cap. 6) |
| L1 | il picco ν_B(z, t) | l'elaborazione (fit, esempio nel cap. 6) |
| L2–L3 | allungamento, temperatura, pressione | l'elaborazione (esempio di compensazione nel cap. 7) |

⚠️ *Variante:* in [\[B23\]](A-fonti.md#b23) la sonda ha frequenza **più bassa** degli impulsi e **riceve** energia (gradino in su). Esiste
anche la configurazione opposta, in cui la sonda perde energia; il principio è lo stesso (fonte da trovare).

## 2.4 I parametri e i limiti

Durata dell'impulso, frequenza dell'ADC, passo di frequenza, numero di medie: decidono incertezza e tempo di misura.
Il modello dell'incertezza è nel cap. 6; ogni parametro è studiato in dettaglio, con i grafici, nel **cap. 9**.

## 2.5 Strumenti reali

Esistono interrogatori commerciali con queste caratteristiche: Prysmian DITEST (80 km), OZ Optics DSTS (100 km),
Neubrex (fino a 2 cm di risoluzione) ✅ (appendice A, sezione "Parametri dello strumento").

<!-- nav-fondo -->

| [← 1. Introduzione](01-introduzione.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 2 di 11 · Parte I — Il problema e la fisica</sub> | [3. Il sensore sul tubo →](03-il-sensore-sul-tubo.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
