<!-- nav -->
| [← 10. Parametri del simulatore](10-parametri-del-simulatore.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 11 di 12 · Parte III — Simulatore</sub> | [12. Risultati e questioni aperte →](12-risultati-e-questioni-aperte.md) |
|:---|:---:|---:|
<!-- /nav -->

# 11. Validazione del simulatore

*Pagina generata da `python -m waterfibersim validate` (poi `python docs/navigazione.py` per la navigazione).*

Ogni riga confronta un risultato del simulatore con un dato indipendente. Esiti: **OK** entro la tolleranza; **DIFF** differenza capita e spiegata nella nota; **KO** da indagare. Commento e conclusioni nel [capitolo 9](09-logica-del-simulatore.md) e nel [capitolo 12](12-risultati-e-questioni-aperte.md).
## 11.1 Confronto con riferimenti indipendenti

| area | cosa | simulatore | riferimento | fonte | esito | nota |
|---|---|---|---|---|---|---|
| idraulica | perdita di carico, tubo PE DN110 da 1 km alle 08:00 (S0a) | 8.504 m | 8.504 m | EPANET 2.2, Tab. 3.1 (h = A q^1,852, A = 4,727 C^-1,852 d^-4,871 L) | **OK** | differenza 0.00 % |
| meccanica | spostamento Brillouin sull'elica, PN16 OD 63, 5 bar (α = 75.4°) | 56 MHz elastico; 69 MHz con E2 (Burgers) | 73 MHz misurati | [\[B23\]](A-fonti.md#b23) §3.1 e Tab. 2 | **OK** | con il rilassamento viscoelastico (E2) il modello torna entro il 15 %; il solo elastico sottostima |
| meccanica | spostamento Brillouin sull'elica, PN16 OD 63, 10 bar (α = 75.4°) | 112 MHz elastico; 138 MHz con E2 (Burgers) | 200 MHz misurati | [\[B23\]](A-fonti.md#b23) §3.1 e Tab. 2 | **DIFF** | misurato 1.4 volte il modello: a 10 bar il PE esce dal comportamento lineare (creep, termine η3 di Burgers, non modellato); il simulatore è elastico |
| meccanica | minima variazione di pressione misurabile, PN10 OD 63, accuratezza 10 µε | 0.023 bar (Lamé, superficie esterna) | 0,016 bar | [\[B23\]](A-fonti.md#b23) §4 | **OK** | stesso ordine di grandezza; [\[B23\]](A-fonti.md#b23) non dice con quale formula lo ricava |
| strumento | incertezza sul picco, SNR 9,4 dB, δ 1 MHz, Δν_B 58 MHz, 200 medie | 0.76 MHz | 0,75 MHz misurati | [\[ST13\]](A-fonti.md#st13) §3, Fig. 6–9 | **OK** |  |
| strumento | incertezza con le impostazioni di [\[B23\]](A-fonti.md#b23) (20 ns, 1 MHz, 256 medie), SNR0 = 0 dB | 0.40 MHz | migliore di 0,5 MHz (10 µε) | [\[B23\]](A-fonti.md#b23) §2.1; [\[ST13\]](A-fonti.md#st13) Eq. 8–9 | **OK** | il valore dichiarato è un limite superiore |
| strumento | passo di campionamento da 125 MS/s; risoluzione da 20 ns | 0.82 m; 2.04 m | 0,8 m; 2 m | [\[B23\]](A-fonti.md#b23) §2.1 | **OK** | con n = 1.468 (da verificare sulla scheda della fibra); con n = 1,5 i valori coincidono |
| dato grezzo | fit parabolico su spettri lorentziani sintetici (SNR 16, δ 1 MHz, 58 MHz) | 0.484 MHz | 0.412 MHz (Eq. 8) | [\[ST13\]](A-fonti.md#st13) Eq. 8 e Appendice | **DIFF** | +17 %: la formula assume una parabola; [\[ST13\]](A-fonti.md#st13): il fattore √(3/4) dipende dalla funzione fittata |
| temperatura | costante di tempo acqua–terreno, PE DN110 in sabbia, acqua ferma / 0,2 / 0,8 m/s | 2.4 h / 1.3 h / 1.3 h | "minutes to hours" | [\[BL24\]](A-fonti.md#bl24) §1, Eq. 2 | **OK** |  |
| compensazione | errore di una misura compensata, riferimento mediato su 74 m (S1t) | 0.059 bar (spettri rumorosi + fit) | 0.055 bar (formula di propagazione) | coerenza interna: [\[ST13\]](A-fonti.md#st13) + propagazione degli errori | **OK** | il fit fa circa il 17 % peggio della formula di [\[ST13\]](A-fonti.md#st13): atteso un valore un po' più alto |

## 11.2 Sensibilità della fibra nella guaina (modello multistrato)

Spostamento Brillouin sull'elica a 70° per 1 bar; fibra a metà guaina (o della pelle). Rumore di una misura con le impostazioni di [\[B23\]](A-fonti.md#b23): circa 0,4–0,5 MHz, quindi per vedere 0,1 bar servono almeno circa 4–5 MHz/bar.

| caso | MHz per bar | 0,1 bar visibile in una misura? | nota |
|---|---|---|---|
| PE DN110 SDR11, fibra sulla superficie esterna (rete di prova, [\[B23\]](A-fonti.md#b23)) | 13.22 | sì | riferimento |
| CIPP feltro 6 mm (E 1,7 GPa) in ghisa DN200 integra (E 170 GPa) | 0.46 | no |  |
| CIPP vetro UV 6 mm (E 10,3 GPa) in ghisa DN200 integra (E 170 GPa) | 0.40 | no |  |
| CIPP feltro 6 mm (E 1,7 GPa) in ghisa DN200 degradata (E ridotto a 1/10) | 3.80 | no |  |
| CIPP vetro UV 6 mm (E 10,3 GPa) in ghisa DN200 degradata (E ridotto a 1/10) | 2.48 | no |  |
| CIPP feltro 6 mm (E 1,7 GPa) in PE DN160 SDR11 (E 1,1 GPa) | 10.35 | sì |  |
| CIPP vetro UV 6 mm (E 10,3 GPa) in PE DN160 SDR11 (E 1,1 GPa) | 3.10 | no |  |
| ghisa integra + strato comprimibile 10 mm (E 50 MPa, confinato circa 67 MPa) + pelle in feltro 3 mm | 6.69 | sì | ipotesi (idea dell'utente) |
| ghisa integra + strato comprimibile 10 mm (E 500 MPa, confinato circa 673 MPa) + pelle in feltro 3 mm | 1.15 | no | ipotesi (idea dell'utente) |
| ghisa integra + strato comprimibile 10 mm (E 50 MPa, confinato circa 67 MPa) + pelle in vetro 6 mm | 3.21 | no | ipotesi (idea dell'utente) |
| ghisa integra + strato comprimibile 10 mm (E 500 MPa, confinato circa 673 MPa) + pelle in vetro 6 mm | 0.96 | no | ipotesi (idea dell'utente) |

<!-- nav-fondo -->

| [← 10. Parametri del simulatore](10-parametri-del-simulatore.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 11 di 12 · Parte III — Simulatore</sub> | [12. Risultati e questioni aperte →](12-risultati-e-questioni-aperte.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
