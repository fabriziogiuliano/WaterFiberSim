<!-- nav -->
| [← 7. Temperatura e compensazione](07-temperatura-e-compensazione.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 8 di 12 · Parte III — Simulatore</sub> | [9. Logica del simulatore →](09-logica-del-simulatore.md) |
|:---|:---:|---:|
<!-- /nav -->

# 8. Guida all'uso del simulatore

Questo capitolo spiega come installare il simulatore, come descrivere una rete e una fibra, quali comandi lanciare,
che cosa producono e come leggere i risultati. I modelli fisici sono nei capitoli 4–7; il significato di ogni
parametro e il suo effetto sono nel cap. 10.

## 8.1 Installazione

Serve **Python 3.11**: la libreria idraulica owa-epanet 2.3.5 ha pacchetti precompilati solo per Linux x86_64
(Python 3.11 e 3.12) e macOS Apple Silicon (3.11); con versioni più recenti l'installazione fallisce.

```bash
conda env create -f environment.yml      # crea l'ambiente "waterfibersim" con Python 3.11
conda activate waterfibersim
pip install -e .                         # installa il pacchetto in modalità sviluppo
python -m pytest -q                      # verifica: tutti i test devono passare
```

## 8.2 Struttura del progetto

| cartella | contenuto |
|---|---|
| `network/` | reti idrauliche (file `.inp` di EPANET) e parametri meccanici dei tubi (`*.yaml`) |
| `scenario_paths/` | scenari: dove passa la fibra, lo strumento, la temperatura |
| `src/waterfibersim/` | il codice del simulatore |
| `tests/` | i test automatici |
| `out/` | i risultati delle simulazioni (non versionati) |
| `docs/` | questa documentazione |
| `blender/` | figure 3D del sensore |

## 8.3 I file di ingresso

Uno scenario è descritto da tre file: la **rete** (`.inp`), i **parametri dei tubi** (`.yaml`) e lo **scenario**
(`.yaml`), che richiama gli altri due.

### 8.3.1 La rete idraulica (`network/*.inp`)

È un file EPANET standard, apribile anche con EPANET o QGIS. Il simulatore usa:

| sezione | cosa serve |
|---|---|
| `[JUNCTIONS]` | nodi: quota [m], prelievo di base [L/s], andamento giornaliero |
| `[RESERVOIRS]` | serbatoi: quota del pelo dell'acqua [m] |
| `[PIPES]` | tubi: nodi di inizio e fine, lunghezza [m], diametro interno [mm], scabrezza di Hazen-Williams |
| `[PATTERNS]` | andamenti dei prelievi nel giorno (moltiplicatori orari) |
| `[COORDINATES]` | posizione dei nodi [m], per le figure |
| `[OPTIONS]` | unità: **devono essere SI** (per esempio `Units LPS`) |

Il diametro interno di ogni tubo deve essere coerente con `pipes.yaml` (§8.3.2).

### 8.3.2 I parametri meccanici dei tubi (`network/*pipes*.yaml`)

EPANET non conosce materiale e spessore; li dà questo file. Ogni tubo prende i valori di `default`, sostituiti da
quelli eventualmente elencati in `pipes`:

```yaml
default:
  material: PE100
  outer_diameter_mm: 110
  wall_thickness_mm: 10
  E_GPa: 1.0          # modulo elastico
  nu: 0.40            # coefficiente di Poisson
  depth_m: 1.0        # profondità di posa
pipes:
  P0:  {material: cast_iron, outer_diameter_mm: 222, wall_thickness_mm: 6.3, E_GPa: 170, nu: 0.26}
  P12: {outer_diameter_mm: 125, wall_thickness_mm: 11.4,
        liner: {thickness_mm: 6, E_GPa: 8, nu: 0.35}}     # tubo risanato: guaina dentro il tubo ospite
```

Controllo automatico: diametro esterno − 2 × spessore (− 2 × spessore della guaina) deve coincidere con il diametro
dell'`.inp` entro 0,5 mm.

### 8.3.3 Lo scenario (`scenario_paths/*.yaml`)

Esempio completo, con tutte le chiavi (scenario S1w):

```yaml
title: "S1w. Strada piana, acqua più calda del terreno"
description: "Testo libero, usato nelle figure"
network: network/street_flat.inp            # la rete
pipes: network/street_pipes.yaml            # i parametri dei tubi

temperature:                                # facoltativa: senza, la temperatura resta costante
  baseline_c: 12            # terreno quando si è fatta la misura di base [°C]
  soil_c: 12                # terreno all'inizio della simulazione [°C]
  drift_c_per_day: 0        # deriva stagionale [°C/giorno]
  helix_mhz_per_c: 6        # sensibilità dell'elica alla temperatura [MHz/°C]
  hotspots:                 # facoltativa: variazioni locali (non insieme a water)
    - {pipe: P6, from_m: 20, to_m: 60, delta_c: 3}                        # permanente
    - {pipe: P3, from_m: 30, to_m: 70, delta_c: 4, from_h: 14, to_h: 17}  # evento con orario
  water:                    # facoltativa: temperatura dell'acqua (modello di Blokker)
    source_c: 14            # acqua in uscita dal serbatoio [°C]
    soil_k_w_mk: 1.6        # conducibilità del terreno [W/(m·K)]
    pipe_k_w_mk: 0.38       # conducibilità del tubo [W/(m·K)]
    tsoi: 1                 # sfera di influenza termica

fibers:                                     # una o più fibre
  - id: S1w
    interrogator:
      node: N0                  # nodo vicino al quale sta lo strumento
      technique: BOTDA
      channel: 1                # canale dello strumento (fibre diverse, canali diversi)
      pulse_width_ns: 20        # durata dell'impulso → risoluzione
      adc_sample_rate_msps: 125 # frequenza dell'ADC → passo dei punti
      freq_step_mhz: 1          # passo della scansione in frequenza
      n_averages: 256           # medie per passo
      scan_window_ghz: [10.75, 11.3]
      linewidth_mhz: 58         # larghezza dello spettro Brillouin
      snr0_db: 0                # rapporto segnale/rumore di riferimento
      snr0_resolution_m: 2
    group_index: 1.468          # indice di gruppo della fibra
    attenuation_db_per_km: 0.2
    calc_step_m: 0.1            # passo di calcolo del simulatore (non dello strumento)
    sensing_leg:   {layout: helix, angle_deg: 70, bonding: bonded}   # andata: elica
    reference_leg: {layout: straight, bonding: loose_tube}           # ritorno: dritto, libero
    route:                      # percorso dell'andata, dalla porta A
      - {lead: 10, to: N0}      # cavo di 10 m fino al nodo N0
      - {pipe: P1, from: N0}    # tubo P1 percorso a partire da N0
      - {pipe: P2, from: N1}
      # ...
    junction_m: 2               # giunzione in fondo all'andata
```

Regole del percorso (`route`):
- è una sequenza **continua**: ogni tubo parte dal nodo in cui è finito il passo precedente;
- `pipe` + `from` percorre un tubo dal nodo indicato all'altro capo;
- `lead` è un tratto di cavo che non sta su un tubo (per esempio dalla cabina al primo tubo, o tra due pozzetti);
- una fibra non può passare due volte sullo stesso tubo;
- il ritorno (`reference_leg`) ripercorre automaticamente gli stessi tubi al contrario, fino alla porta B.

Valori consigliati per i parametri dello strumento: §2.5 (strumenti commerciali) e cap. 10.

## 8.4 I comandi

Tutti i comandi hanno la forma `python -m waterfibersim <comando> <scenario> [opzioni]`.

| comando | cosa fa | opzioni principali | tempo tipico (strada di 1 km) |
|---|---|---|---|
| `map` | mappa metro di fibra → tubo, figura del percorso | `--out` | 1 s |
| `run` | segnale vero nel tempo (pressione, deformazione, temperatura, frequenza Brillouin) | `--out`, `--hours`, `--step-min`, `--demand-multiplier`, `--seed`, `--no-rest-profile` | 6 s |
| `instrument` | incertezza attesa dello strumento lungo la fibra, tempo di misura, controllo della finestra | `--out` | 6 s |
| `measure` | dato grezzo L0: spettri con il rumore, più un fit di esempio | `--out`, `--hours`, `--every-min`, `--seed` | 30 s (24 h, una misura all'ora) |
| `compensate` | compensazione della temperatura sul segnale vero | `--out`, `--hour` | 3 s |
| `compensate --measured` | compensazione sul dato rumoroso | `--hours`, `--every-min`, `--baseline-repeats`, `--seed` | 60 s |
| `validate` | campagna di validazione (cap. 11) | `--out`, `--quick` | 15 s |
| `parameters` | studio di sensibilità dei parametri (figure del cap. 10) | `--out` | 10 s |

Opzioni comuni:
- `--out DIR`: cartella dei risultati (creata se manca);
- `--hours H`, `--step-min M`: durata della simulazione idraulica e passo (default 24 h, 15 min);
- `--every-min M`: ogni quanti minuti lo strumento fa una misura completa (default 60);
- `--seed N`: seme dei numeri casuali (profilo a riposo e rumore); stesso seme, stesso risultato;
- `--demand-multiplier X`: moltiplica tutti i prelievi (prove di sensibilità; la rete esce dai criteri di progetto).

Esempio di sessione completa sullo scenario S1:

```bash
python -m waterfibersim map        scenario_paths/S1_street_flat.yaml --out out/S1
python -m waterfibersim run        scenario_paths/S1_street_flat.yaml --out out/S1
python -m waterfibersim instrument scenario_paths/S1_street_flat.yaml --out out/S1
python -m waterfibersim measure    scenario_paths/S1_street_flat.yaml --out out/S1 --every-min 60
```

## 8.5 I file di uscita

| file | comando | contenuto |
|---|---|---|
| `fiber_map.csv` | `map`, `run` | una riga per punto di calcolo: `fiber`, `z_m` (distanza dalla porta A), `leg` (`lead`, `sensing`, `junction`, `reference`), `pipe`, `s_pipe_m` (posizione sul tubo dal suo nodo di inizio), `x`, `y` |
| `fiber_map.png` | `map` | percorso della fibra sulla rete e fibra "srotolata" |
| `signal_true.npz` | `run` | segnale vero (tabella sotto) |
| `signal_true_<fibra>.png` | `run` | 5 grafici: frequenza, differenza dalla misura di base, waterfall, variazione nel giorno, andamento per tubo |
| `uncertainty_<fibra>.png` | `instrument` | incertezza lungo la fibra |
| `raw_L0_<fibra>.npz` | `measure` | dato grezzo L0 (tabella sotto) |
| `fit_L1_<fibra>.npz` | `measure` | picchi stimati dal fit di esempio: `nu_fit_mhz` (misure × punti), `baseline_fit_mhz` |
| `raw_<fibra>.png` | `measure` | spettri di esempio, picco stimato contro vero, errore del fit |
| `compensation_<fibra>.png`, `compensation_measured_<fibra>.png` | `compensate` | pressione vera, letta e compensata; errori |

**`signal_true.npz`** (T istanti × Z punti di calcolo):

| campo | forma | unità | significato |
|---|---|---|---|
| `times_s` | T | s | istanti dall'inizio |
| `z_m`, `fiber`, `leg`, `pipe` | Z | m, — | posizione lungo la fibra e tratto di ogni punto |
| `nu_b_mhz` | T × Z | MHz | frequenza Brillouin vera (L1 vero) |
| `baseline_mhz`, `rest_mhz`, `nu_b0_mhz` | Z | MHz | misura di base vera, profilo a riposo, valore di riferimento |
| `pressure_bar` | T × Z | bar | pressione dell'acqua nel punto (vuoto su cavi e giunzione) |
| `strain_ue` | T × Z | µε | deformazione della fibra dovuta alla pressione |
| `delta_t_c` | T × Z | °C | variazione di temperatura dalla misura di base |
| `demand_multiplier`, `seed` | — | — | impostazioni della simulazione |

**`raw_L0_<fibra>.npz`** (M misure × P punti dello strumento × F frequenze):

| campo | forma | unità | significato |
|---|---|---|---|
| `freq_mhz` | F | MHz | frequenze della scansione |
| `z_m`, `leg`, `pipe`, `s_pipe_m` | P | m, — | punti dello strumento (ogni 0,82 m) |
| `times_s` | M | s | istanti delle misure |
| `spectra` | M × P × F | — | **dato grezzo**: guadagno Brillouin normalizzato, con rumore |
| `baseline_spectra` | P × F | — | dato grezzo della misura di base |
| `nu_true_center`, `nu_true_mean` | M × P | MHz | frequenza vera al centro del punto e media sulla risoluzione |
| `pressure_bar`, `delta_t_c` | M × P | bar, °C | etichette vere |
| `sigma_expected_mhz` | P | MHz | incertezza attesa di un fit |

## 8.6 Leggere i risultati in Python

```python
import numpy as np

# segnale vero
s = np.load("out/S1/signal_true.npz")
h = s["times_s"] / 3600                                # ore
elica_p5 = (s["leg"] == "sensing") & (s["pipe"] == "P5")
pressione = s["pressure_bar"][:, elica_p5].mean(axis=1)    # pressione media su P5, ora per ora
dnu = s["nu_b_mhz"] - s["baseline_mhz"]                # differenza dalla misura di base [MHz]

# dato grezzo
r = np.load("out/S1/raw_L0_S1.npz")
spettro = r["spectra"][8, 1000].astype(float)          # misura delle 08:00, punto 1000
frequenze = r["freq_mhz"]
vero = r["nu_true_mean"][8, 1000]                      # picco vero di quel punto
```

## 8.7 Flussi di lavoro tipici

**Nuovo scenario su una rete esistente.** Copiare uno scenario di `scenario_paths/`, cambiare `title`, `id` e il
percorso `route`; lanciare `map` e controllare la figura del percorso.

**Produrre il dato grezzo per chi sviluppa l'elaborazione.** Lanciare `measure` sullo scenario scelto; consegnare
`raw_L0_<fibra>.npz` (dato grezzo con le etichette vere) e `fiber_map.csv`. Per una misura più fitta nel tempo ridurre
`--every-min` (il file cresce di conseguenza: circa 5 MB per misura su 4 km).

**Simulare uno strumento commerciale.** Impostare `pulse_width_ns` e `adc_sample_rate_msps` dalla tabella del §2.5;
`n_averages` e `freq_step_mhz` secondo le impostazioni previste; controllare l'incertezza con `instrument`.

**Aggiungere temperatura o eventi.** Aggiungere la sezione `temperature` (§8.3.3): `soil_c` e `drift_c_per_day` per la
stagione, `hotspots` per variazioni locali (con `from_h`/`to_h` per un evento), `water` per la temperatura dell'acqua.
Verificare l'effetto con `compensate`.

**Studiare un parametro.** Cambiare il valore nello scenario e rilanciare `instrument` o `compensate --measured`;
per una panoramica, `parameters` rigenera le figure del cap. 10.

**Controllare il simulatore dopo una modifica.** `python -m pytest -q` e `python -m waterfibersim validate`.

## 8.8 Errori frequenti

Il simulatore controlla gli ingressi e si ferma con un messaggio che indica il punto:

| messaggio (in inglese) | causa | rimedio |
|---|---|---|
| `unknown keys [...]; allowed [...]` | chiave scritta male nello scenario o in `pipes.yaml` | correggere il nome |
| `SI flow units required` | `.inp` in unità americane | in `[OPTIONS]` usare `Units LPS` (o altre SI) |
| `inner diameter from YAML ... != diameter in the .inp` | diametro esterno, spessore o guaina incoerenti con l'`.inp` | allineare i due file |
| `pipes.yaml: pipes not in the .inp` | tubo elencato in `pipes.yaml` che non esiste nella rete | correggere il nome del tubo |
| `... starts at N but the route is at M (add a lead)` | percorso non continuo | aggiungere un `lead` o correggere `from` |
| `... already used: a fiber cannot pass twice on the same pipe` | tubo ripetuto nel percorso | usare una seconda fibra (altro canale) |
| `interrogator: missing [...]` | parametro dello strumento mancante | aggiungerlo (§8.3.3) |
| `calc_step_m ... too coarse` | passo di calcolo troppo grande rispetto alla risoluzione | ridurre `calc_step_m` |
| `temperature: hotspots together with water are not supported yet` | punti caldi e acqua insieme | usare uno dei due |
| `scan window ...: OUT OF WINDOW` (comando `instrument`) | qualche picco esce dalla finestra di scansione | allargare `scan_window_ghz` |

<!-- nav-fondo -->

| [← 7. Temperatura e compensazione](07-temperatura-e-compensazione.md) | [📖 Indice](00-indice.md)<br><sub>capitolo 8 di 12 · Parte III — Simulatore</sub> | [9. Logica del simulatore →](09-logica-del-simulatore.md) |
|:---|:---:|---:|
<!-- /nav-fondo -->
