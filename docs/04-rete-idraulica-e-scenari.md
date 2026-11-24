<!-- nav -->
| [← 3. Configurazione del sensore](03-il-sensore-sul-tubo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 4 di 12 · Parte II — I modelli</sub> | [5. Meccanica del tubo e della guaina →](05-meccanica-del-tubo.md) |
|:---|:---:|---:|
<!-- /nav -->

# 4. Rete idraulica e scenari

## 4.1 Modello idraulico (EPANET)

L'idraulica è calcolata con EPANET 2.2 (libreria owa-epanet): pressione, carico, portate e velocità ogni 15 minuti.
EPANET non contiene catalogo di tubi né criteri di progetto [\[EPA\]](A-fonti.md#epa); la perdita di carico segue Hazen-Williams, e il
simulatore coincide con la formula ufficiale (cap. 11). Lungo un tubo la pressione è lineare tra i nodi.

## 4.2 Pressione statica e perdite di carico

- **Statica**: senza prelievi la pressione è il dislivello tra il pelo dell'acqua del serbatoio e il punto, circa
  0,1 bar per metro [\[EPA\]](A-fonti.md#epa) (carico = quota + altezza di pressione). È relativa all'atmosfera e non dipende dalla quota
  sul mare (calcolo nostro).
- **Perdita di carico**: l'acqua che scorre perde pressione nel verso del flusso; cresce con il quadrato circa della
  portata, quindi nelle ore di punta.
- Lungo una **discesa** la pressione cresce anche allontanandosi dal serbatoio (la quota vince sulla perdita).

## 4.3 Scenari

| scenario | cosa | per studiare |
|---|---|---|
| S0a / S0b | un tubo PE da 1 km, un solo prelievo in fondo; piano / in discesa 2 % | il caso più semplice: pressione lineare |
| S1 / S2 | strada di 1 km, un rubinetto ogni 100 m; piano / in discesa | la portata cala a ogni rubinetto |
| S1t / S1th | S1 con il terreno 8 °C più freddo; + punto caldo su P6 | temperatura del terreno (cap. 7) |
| S1w | S1 con l'acqua 2 °C più calda del terreno | temperatura dell'acqua (cap. 7) |
| A / B / C | griglia 3×3 con adduttrice in ghisa; tubo risanato P12 | reti con più tubi, guaina (cap. 5) |

Il serbatoio a valle è stato scartato: servirebbe una pompa (appendice C).

## 4.4 Criteri di dimensionamento

Le reti sono dimensionate con criteri di progetto (velocità 0,5–0,9 m/s, perdita ≤ 10 m/km (da verificare) da manuali, EN 805 da
leggere). Conseguenza: la pressione cambia nella giornata di **0,04–0,8 bar**, non di più. È il segnale da misurare.

Tutti i parametri della rete: cap. 10, sezione 1.

<!-- nav-fondo -->

| [← 3. Configurazione del sensore](03-il-sensore-sul-tubo.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 4 di 12 · Parte II — I modelli</sub> | [5. Meccanica del tubo e della guaina →](05-meccanica-del-tubo.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
