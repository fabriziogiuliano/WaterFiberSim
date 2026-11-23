# WaterFiberSim

Simulatore di **sensori distribuiti in fibra ottica** (DFOS) posati su una rete idrica descritta in EPANET. Prende la rete (`.inp`), sovrappone una o più fibre ai tubi, trasforma pressione e temperatura dell'acqua in una grandezza ottica lungo tutta la fibra e produce il **segnale grezzo** che leggerebbe l'interrogatore. Il DSP su quel segnale è il lavoro di chi usa il simulatore.

Le tecniche di base: **DAS** (vibrazioni, Rayleigh), **DTS** (temperatura, Raman), **DSS** (deformazione + temperatura, Brillouin). Per misurare la pressione sulle pareti del tubo servono DSS + DTS. Il documento di contesto è [docs/fibra-ottica-dfos.md](docs/fibra-ottica-dfos.md). Decisioni, ricerca e piano della sessione iniziale: [docs/sessione-2026-11-23.md](docs/sessione-2026-11-23.md).

## INSTALL

> **Serve Python 3.11.** L'idraulica usa [owa-epanet](https://pypi.org/project/owa-epanet/) 2.3.5, la stessa versione di `edge-slm-emulator`, che ha pacchetti precompilati solo per:
>
> | Sistema | Python |
> |---|---|
> | Linux x86_64 | 3.11, 3.12 |
> | macOS Apple Silicon | 3.11 |
> | Windows | nessuno |
>
> Con altre versioni (per esempio 3.13) pip prova a compilarlo dai sorgenti e fallisce, perché mancano SWIG e CMake. Per questo `environment.yml` fissa `python=3.11`.

```bash
conda env create -f environment.yml
conda activate waterfibersim
pip install -e .
```

## Il piano

| Passo | Cosa | Uscita |
|---|---|---|
| **1** | **rete di prova, parametri dei tubi, percorso della fibra** | **mappa "metro di fibra → tubo" e disegno** |
| 2 | pressione lungo la fibra (EPANET, owa-epanet) → strain → frequenza Brillouin | ν_B(z, t), ancora senza ottica |
| 3 | segnale grezzo: spettro Brillouin con rumore + un fit di esempio | L0 e un primo DSP |
| 4 | eventi: perdita (idraulica), cedimento (meccanico) | etichette |
| 5 | temperatura (DTS) e separazione pressione/temperatura | |

I livelli del dato:

| Livello | Contenuto | Chi lo produce |
|---|---|---|
| **L0** | spettro Brillouin per ogni posizione e acquisizione (+ tracce Raman per il DTS), con rumore | simulatore |
| L1 | frequenza Brillouin ν_B(z, t) | DSP |
| L2 | strain ε(z, t) e temperatura T(z, t) | DSP |
| L3 | pressione stimata, eventi | DSP |

Il simulatore consegna L0 più le **etichette vere** di tutti i livelli.

---

## Passo 1 — rete, tubi, fibra

Obiettivo: descrivere **dove** sta la fibra. Niente fisica ancora: solo geometria e parametri.

### 1.1 La rete di prova

Una rete piccola, che si capisce a colpo d'occhio:

```
   R1 (serbatoio)
    │ P0  (adduttrice)
   J11 ── J12 ── J13
    │      │      │
   J21 ── J22 ── J23
    │      │      │
   J31 ── J32 ── J33
```

- **R1**: sorgente a carico fisso (serbatoio).
- **J11…J33**: griglia 3×3 di nodi, tubi da 100 m.
- **Utenze**: una domanda (con il suo andamento giornaliero) sui nodi del bordo, per esempio J13, J31, J33.

Il file è `rete/griglia_3x3.inp`, in formato EPANET standard: si apre anche con EPANET o QGIS.

### 1.2 I parametri dei tubi

L'`.inp` non si tocca: i parametri meccanici stanno in un file a parte, con valori di default e override per singolo tubo.

```yaml
# rete/tubi.yaml
default:
  materiale: PE100
  diametro_esterno_mm: 110
  spessore_mm: 10
  E_GPa: 1.0          # modulo elastico
  nu: 0.40            # coefficiente di Poisson
  profondita_m: 1.0   # interramento (serve per la temperatura)
tubi:
  P0:  {materiale: ghisa, diametro_esterno_mm: 160, spessore_mm: 8, E_GPa: 170, nu: 0.26}
  P12: {guaina: {spessore_mm: 6, E_GPa: 8}}   # tubo risanato con relining
```

### 1.3 La fibra in overlay

Una fibra **non si dirama**: è un percorso lineare. Il percorso è una lista ordinata di tratti, che possono essere tubi (in un verso) o **tratti morti**, cioè cavo che collega senza stare su un tubo.

```yaml
# fibre/fibra_A.yaml
interrogatore: {nodo: R1, tecnica: BOTDA}       # BOTDA: la fibra deve tornare all'interrogatore
avvolgimento: {tipo: elica, alfa_deg: 70}      # angolo rispetto all'asse del tubo
passo_campionamento_m: 0.5
percorso:
  - {morto: 15}                # cavo dall'interrogatore al primo tubo
  - {tubo: P0,  da: R1}
  - {tubo: P1,  da: J11}       # J11 → J12
  - {tubo: P2,  da: J12}       # J12 → J13
  - {morto: 5}
  - {tubo: P7,  da: J13}       # J13 → J23
  # ...
ritorno: {morto: 400}          # solo BOTDA: cavo che riporta all'interrogatore
```

Se la rete non si copre con un solo percorso, si usano più fibre, cioè più file (oppure più canali dello stesso interrogatore).

### 1.4 La mappa "metro di fibra → tubo"

È il prodotto del passo 1 e servirà a tutti i passi successivi. Per ogni campione lungo la fibra:

| z_fibra_m | tratto | tubo | s_tubo_m | x, y |
|---|---|---|---|---|
| 0.0 | morto | — | — | … |
| 15.0 | 1 | P0 | 0.00 | … |
| 15.5 | 1 | P0 | 0.17 | … |

Con l'avvolgimento a elica, **un metro di fibra copre meno di un metro di tubo**: s_tubo avanza di `passo · cos α` per ogni passo di fibra. Con α = 70° servono ~2,9 m di fibra per ogni metro di tubo.

### 1.5 Come si verifica il passo 1

- Disegno della rete con la fibra sopra, colorata per distanza dall'interrogatore.
- La lunghezza totale della fibra torna con la somma di tratti morti e tubi × 1/cos α.
- Ogni tubo coperto compare nella mappa con s_tubo che va da 0 alla sua lunghezza.

---

## Come si avvolge la fibra

**Sì, l'elica è la scelta corretta** quando si vuole misurare la pressione. Le possibilità principali:

| Posa | Cosa sente | Uso |
|---|---|---|
| **dritta lungo l'asse** (α = 0°) | deformazione assiale | flessione, cedimenti del terreno; con fibra libera, la temperatura |
| **ad anelli** (α ≈ 90°) | deformazione circonferenziale pura | massima sensibilità alla pressione, ma servono raccordi tra un anello e l'altro |
| **a elica** (0° < α < 90°) | una miscela delle due | **il compromesso usato in pratica** |

La deformazione che sente la fibra a elica:

**ε_fibra = ε_θ · sin²α + ε_z · cos²α**

dove ε_θ è la deformazione circonferenziale (quella grande, dovuta alla pressione) e ε_z quella assiale. Più α si avvicina a 90°, più la fibra "vede" la pressione.

Il prezzo è la lunghezza: un metro di tubo richiede **1 / cos α** metri di fibra.

| α | sensibilità alla pressione (sin²α) | fibra per metro di tubo | 1 m di risoluzione della fibra corrisponde a |
|---|---|---|---|
| 45° | 50 % | 1,4 m | 71 cm di tubo |
| 60° | 75 % | 2,0 m | 50 cm di tubo |
| 70° | 88 % | 2,9 m | 34 cm di tubo |
| 80° | 97 % | 5,8 m | 17 cm di tubo |

Più fibra per metro significa risoluzione migliore sul tubo, ma anche più attenuazione e meno metri di rete coperti dallo stesso interrogatore.

Altri due vincoli:
- **Curvatura:** l'elica ha raggio di curvatura R / sin²α, quindi non scende mai sotto il raggio del tubo. Per un DN110 (R = 55 mm) va bene anche una fibra standard; le fibre "insensibili alla curvatura" (ITU-T G.657) reggono fino a 7,5–10 mm.
- **Fibra di riferimento:** di solito accanto all'elica si posa una **fibra dritta in tubetto libero**, che non sente lo strain e misura solo la temperatura. Serve a compensare (vedi passo 5).

Nel caso MATRIS la fibra si annega nel composito della guaina durante la produzione. Se la guaina è fatta per avvolgimento di filamenti, l'elica viene naturale.

---

## Modello 3D e figura del sensore

![Il sensore in fibra ottica sul tubo](blender/tubo_fibra.png)

La figura spiega il sistema a chi non conosce la fibra: **una sola fibra ad anello**, i cui due capi arrivano allo **stesso interrogatore** (BOTDA).

- **Porta A** (z = 0): esce l'impulso laser ed entra la luce che lo strumento legge.
- **Andata a elica**, incollata nella guaina: sente pressione + temperatura.
- **Giunzione** in fondo al tratto.
- **Ritorno dritto** in un tubetto libero: sente solo temperatura.
- **Porta B**: entra il laser continuo, che percorre l'anello al contrario.

La figura spiega anche l'effetto Brillouin e la fibra "srotolata", in cui ogni punto del tubo compare due volte (z₁ sull'elica, z₂ sul ritorno). Per differenza tra i due punti si separano temperatura e pressione.

Si genera in due passi:

| Script | Cosa fa | Serve |
|---|---|---|
| [blender/tubo_fibra.py](blender/tubo_fibra.py) | spaccato 3D → `tubo_fibra_3d.png` + `tubo_fibra_3d.json` (posizione in pixel dei punti notevoli) e, a richiesta, il `.blend` | Blender (o il modulo `bpy`) |
| [blender/schema_sensore.py](blender/schema_sensore.py) | render + didascalie + pannelli → `tubo_fibra.png` | solo matplotlib |

```bash
# apre Blender con la scena pronta (le etichette 3D sono visibili nella vista, non nel render)
blender --python blender/tubo_fibra.py

# render senza interfaccia + file .blend, poi la figura finale
blender -b --python blender/tubo_fibra.py -- --render blender/tubo_fibra_3d.png --save blender/tubo_fibra.blend
python blender/schema_sensore.py
```

- Il `.blend` va generato con la **stessa versione di Blender** con cui lo si apre: un file salvato con Blender 5.0 non si apre con la 4.2. Per questo non è in git.
- Spessori e fibra sono **esagerati** per renderli visibili.
- I numeri dei pannelli (PE DN110, elica a 70°, coefficienti Brillouin) sono **indicativi**.
- I parametri della scena (angolo `ALFA_DEG`, raggi, lunghezza) sono in cima a `tubo_fibra.py`.
