# Simple Fire weather metric analysis using ERA5 and BARPA within GADI supercomputer

1. Read ERA5 and BARPA using xarray
      - code in fio.py, called by some notebooks (TODO: collapse into single 'summary' reading notebook)
      - used sometimes in notebooks, sometimes in bash scripts when creating intermediate data files
2. Create intermediate data files with just metrics of interest
      - Required to avoid massive file reading overheads
      - Coded mostly in bash scripts "make_....sh" called by qsub
      - TODO: simplify or summarise
3. Analyse data

# Environment

### GADI permissions
need to join several projects:
- ia39: BARPA data
- cj37: BARRA data
- py18: BARPA will be moving here soon
- hh5: python environments so we don't need to create our own

### Python environment setup

Running this code will plop you into a fully formed python environment within GADI
```
source /g/data/hh5/public/apps/miniconda3/etc/profile.d/conda.sh
conda activate /g/data/hh5/public/apps/miniconda3/envs/analysis3
```


# Examples:

## Simple grab and display of Data

### BARPA:

### ERA5:

## Create intermediate datasets


### BARRA:
