<!-- nav -->
| [← Indice](00-indice.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 1 di 11 · Parte I — Problema e principio di misura</sub> | [2. Principio di misura (BOTDA) →](02-principio-di-misura.md) |
|:---|:---:|---:|
<!-- /nav -->

# 1. Introduzione

## 1.1 Obiettivo

Misurare la **pressione sulle pareti dei tubi** di una rete idrica, **metro per metro**, con una fibra ottica posata
lungo il tubo e letta da uno strumento Brillouin (cap. 2). Il simulatore produce:
- il **dato grezzo L0** che darebbe lo strumento (spettri Brillouin con il rumore, cap. 6);
- le **etichette vere**: pressione, deformazione, temperatura in ogni punto e in ogni istante.

Chi elabora i dati (L1–L3) può così sviluppare e verificare i suoi algoritmi sapendo la verità.

### Livelli di elaborazione del dato

Nel documento i dati sono indicati per livello di elaborazione:

| livello | contenuto | esempio |
|---|---|---|
| **L0** — dato grezzo | per ogni punto della fibra e ogni misura, lo spettro Brillouin (potenza in funzione della frequenza), con il rumore | 551 valori per punto |
| **L1** — frequenza Brillouin | il picco dello spettro in ogni punto, $\nu_B(z,t)$ | 11 095,3 MHz |
| **L2** — grandezze fisiche della fibra | deformazione e temperatura, dopo la sottrazione della misura di base e la compensazione | 277 µε; +1,2 °C |
| **L3** — informazione sulla rete | pressione dell'acqua lungo i tubi ed eventuali anomalie | 4,7 bar in P5 alle 08:00 |

Il simulatore produce L0 e le etichette vere di tutti i livelli; il passaggio da L0 a L3 è l'elaborazione dei dati.

## 1.2 Contesto

Il lavoro si colloca nel risanamento delle condotte con guaine polimerizzate in opera e nello sviluppo di gemelli
digitali delle reti idriche. L'idea è annegare la fibra nella guaina di risanamento, così che il tubo risanato diventi
anche un sensore (cap. 3). Il riferimento scientifico più vicino è Bertulessi et al. 2023 [\[B23\]](A-fonti.md#b23) (Politecnico di Milano,
Cohaerentia), che ha provato lo stesso schema su tubi in PE in laboratorio.

## 1.3 Domande di ricerca

1. Quanto si sposta la frequenza della fibra per 1 bar, su quale tubo e con quale posa? (cap. 5)
2. Con quale errore lo strumento la misura? (cap. 6)
3. Quanto disturba la temperatura del terreno e dell'acqua, e come si toglie? (cap. 7)
4. Le ipotesi reggono il confronto con i dati veri? (cap. 10)

Le risposte, con i loro limiti, sono riassunte nel cap. 11.

## 1.4 Ambito e limiti

Non è l'elaborazione dei dati: il fit e la compensazione inclusi sono **esempi** per verificare che dal dato grezzo
si torni alla pressione (cap. 6 e 7). Non è un progetto di installazione: i parametri dei materiali della guaina non sono
ancora noti (cap. 9).

<!-- nav-fondo -->

| [← Indice](00-indice.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 1 di 11 · Parte I — Problema e principio di misura</sub> | [2. Principio di misura (BOTDA) →](02-principio-di-misura.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
