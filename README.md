# Simple Fire weather metric analysis using ERA5 and BARPA within GADI supercomputer

1. Read ERA5 and BARPA using xarray
2. Create intermediate data files with just metrics of interest
      - Required to avoid massive file reading overheads
      - Coded mostly in bash scripts "make_....sh"
      - created files will be monthly maximums for metrics and the metric components
      - The files are currently coded to go into my scratch directory
          - NB: scratch directory purges files that aren't touched for 90 days
      - TODO: simplify and summarise
      - The notebook "Intermediate_Data.ipynb" summarises and performs some small examples of reading the intermediate dataset
3. Analyse data

# Environment

### GADI permissions
need to join several projects:
- cj37: BARRA data (currently unused)
- py18: BARPA moved here in Jan/Feb 2024, group managed by Chun Hsu
- hh5: python environments so we don't need to create our own

### Python environment setup

Running this code on the command line will plop you into a fully formed python environment within GADI
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
