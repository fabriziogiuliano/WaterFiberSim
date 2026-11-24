![WaterFiberSim](docs/img/logo-scuro.png)

# WaterFiberSim

Simulatore di una misura in fibra ottica della **pressione dell'acqua sulle pareti dei tubi** di una rete idrica
descritta in EPANET. Una fibra è annegata a elica nella guaina di risanamento del tubo ed è letta da uno strumento
Brillouin (BOTDA). Il simulatore produce:

- il **dato grezzo L0** che darebbe lo strumento: spettri Brillouin con il rumore, punto per punto lungo la fibra;
- le **etichette vere**: pressione, deformazione, temperatura e frequenza Brillouin in ogni punto e in ogni istante.

L'elaborazione dei dati (da L0 alla pressione stimata) è il lavoro di chi usa il simulatore.

**Documentazione: [indice](docs/00-indice.md).** Per usare il simulatore basta la
[guida all'uso (cap. 8)](docs/08-guida-all-uso.md). Cosa è dimostrato e quali sono i limiti:
[validazione (cap. 11)](docs/11-validazione.md) e [risultati e questioni aperte (cap. 12)](docs/12-risultati-e-questioni-aperte.md).

## Installazione

Serve **Python 3.11**: l'idraulica usa [owa-epanet](https://pypi.org/project/owa-epanet/) 2.3.5, che ha pacchetti
precompilati solo per Linux x86_64 (Python 3.11 e 3.12) e macOS Apple Silicon (Python 3.11); per Windows nessuno.

```bash
conda env create -f environment.yml
conda activate waterfibersim
pip install -e .
pytest -q
```

## Esempio

```bash
python -m waterfibersim map        scenario_paths/S1_street_flat.yaml --out out/S1   # metro di fibra -> tubo
python -m waterfibersim run        scenario_paths/S1_street_flat.yaml --out out/S1   # segnale vero nel tempo
python -m waterfibersim instrument scenario_paths/S1_street_flat.yaml --out out/S1   # incertezza dello strumento
python -m waterfibersim measure    scenario_paths/S1_street_flat.yaml --out out/S1   # dato grezzo L0
```

Tutti i comandi, i file di ingresso e di uscita e la lettura dei risultati in Python sono nel
[cap. 8](docs/08-guida-all-uso.md).
