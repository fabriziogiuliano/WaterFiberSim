<!-- nav -->
| [← 4. Rete idraulica e scenari](04-rete-idraulica-e-scenari.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 5 di 11 · Parte II — I modelli</sub> | [6. Lo strumento e il dato grezzo →](06-strumento-e-dato-grezzo.md) |
|:---|:---:|---:|
<!-- /nav -->

# 5. Meccanica del tubo e della guaina

## 5.1 Tubo a un solo strato (Lamé)

La pressione p allarga il tubo. Sulla superficie esterna (dove sta la fibra nella rete di prova) ✅ [B23] Eq. 4–6:

  ε_θ = (2 − ν) β² / (1 − β²) · p / E,  ε_z = (1 − 2ν) β² / (1 − β²) · p / E  (fondi chiusi),  β = r_int / r_est

Per il PE100 SDR11 (E circa 1 GPa): circa 309 µε per bar sul giro, 277 µε sull'elica a 70°, **circa 14 MHz/bar**.
Con tubi SDR11 la sensibilità non dipende dal diametro 🧮.

## 5.2 L'elica

ε_fibra = ε_θ sin²α + ε_z cos²α (trasformazione della deformazione). A 70° la fibra raccoglie l'88 % della
deformazione del giro.

## 5.3 Più strati: tubo ospite + guaina

Con la guaina la fibra sta **dentro** la guaina, e la guaina sta dentro il tubo ospite. Il simulatore risolve Lamé a
N strati incollati (spostamento e pressione continui alle interfacce, fondi chiusi) 🧮; con uno strato coincide con
la formula sopra (verificato nei test).

Risultati (cap. 10, esperimenti), MHz per bar sull'elica:

| caso | MHz/bar |
|---|---|
| PE DN110 nudo, fibra fuori | 13,2 |
| guaina in feltro (1,7 GPa) in PE DN160 | 10,4 |
| guaina in vetro (10 GPa) in PE DN160 | 3,1 |
| guaina in ghisa degradata (rigidezza 1/10) | 2,5–3,8 |
| **guaina in ghisa integra** | **0,4–0,5** (pari al rumore di una misura) |

## 5.4 Perché il tubo rigido "spegne" la fibra

La guaina dentro un tubo rigido viene schiacciata nello spessore, ma la sua circonferenza non può crescere più di
quella del tubo: la fibra a elica, che misura l'allungamento del giro, non si allunga. Una gomma morbida non aiuta
perché è incomprimibile: conta la rigidezza **confinata**, non solo il modulo E.

## 5.5 Idea: lo strato comprimibile

Uno strato di 10 mm con rigidezza confinata circa 70 MPa tra una pelle sottile (con la fibra) e la ghisa restituisce
circa **7 MHz/bar** (pelle in feltro) o 3 (pelle in vetro) 🧮. Materiale, creep e durata da verificare (cap. 11).

## 5.6 Limiti del modello

Elastico: il PE ha creep ✅ [B23] (Burgers). A 5 bar il modello con il rilassamento torna con la misura di [B23]
entro il 6 %, a 10 bar sottostima (cap. 10). La temperatura dilata il tubo: cap. 7.

<!-- nav-fondo -->

| [← 4. Rete idraulica e scenari](04-rete-idraulica-e-scenari.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 5 di 11 · Parte II — I modelli</sub> | [6. Lo strumento e il dato grezzo →](06-strumento-e-dato-grezzo.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
