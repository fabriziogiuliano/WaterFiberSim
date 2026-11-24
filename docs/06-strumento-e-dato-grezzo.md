<!-- nav -->
| [← 5. Meccanica del tubo e della guaina](05-meccanica-del-tubo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 6 di 11 · Parte II — I modelli</sub> | [7. Temperatura e compensazione →](07-temperatura-e-compensazione.md) |
|:---|:---:|---:|
<!-- /nav -->

# 6. Lo strumento e il dato grezzo

## 6.1 I parametri sono nel tempo

Nello scenario i parametri dello strumento sono quelle vere, nel tempo; i metri si ricavano con il tempo di volo:

  passo dei punti Δz = c / (2 n f_ADC)  (125 MS/s → 0,82 m)   ·   risoluzione Δz = c τ / (2 n)  (20 ns → 2,04 m)

✅ [B23] dichiara 0,8 m e 2 m; [ST13]: risoluzione = *"pump pulse half duration multiplied by the group velocity"*.
L'indice di gruppo n = 1,468 è ⚠️ (scheda della fibra da leggere).

## 6.2 L'incertezza sul picco

Modello di Soto & Thévenaz ✅ [ST13] Eq. 7–9, validato sui loro dati (cap. 10):

  σ_ν = (1/SNR) · √(¾ · δ · Δν_B),   SNR(z) = SNR₀ · (Δz/Δz₀) · √N_AV · e^(−αz)

Con le impostazioni di [B23]: **σ ≈ 0,40–0,46 MHz per misura** (circa 0,03 bar sull'elica in PE). Medie e passo di
frequenza pesano allo stesso modo; la distanza pesa poco sotto i 4 km. Comando: `instrument`.

## 6.3 Il dato grezzo L0

Comando `measure`: per ogni punto dello strumento e ogni misura, lo **spettro intero** (551 frequenze): media su 2 m
di campane lorentziane (58 MHz) ✅ [ST13] Fig. 5, più rumore gaussiano 1/SNR ✅ [ST13]. Anche la misura di base è
rumorosa. File `raw_L0_<fibra>.npz` con le etichette vere.

## 6.4 Il fit di esempio

Parabola sui punti sopra metà picco, ricentrata in più passate ✅ [ST13]. Ritrova ν_B con circa il 17 % di errore in
più della formula (la campana è lorentziana, non una parabola: previsto da [ST13]). Dove la finestra di 2 m prende
tratti diversi (giunzione, cavi) gli spettri hanno più picchi e il fit sbaglia: quei punti vanno scartati.

## 6.5 Tempi

Tempo minimo di una misura: passi × medie × andata e ritorno sull'anello, 3–6 s 🧮; lo strumento reale ha tempi morti
([B23]: 7–20 s). Molto meno del passo idraulico (15 min).

Parametri: cap. 9, sezione 4. Effetto sulla compensazione: cap. 7.

<!-- nav-fondo -->

| [← 5. Meccanica del tubo e della guaina](05-meccanica-del-tubo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 6 di 11 · Parte II — I modelli</sub> | [7. Temperatura e compensazione →](07-temperatura-e-compensazione.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
