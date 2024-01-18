# Simple Fire weather metric analysis using ERA5 and some BARPA data within GADI supercomputer

1. Read ERA5 and BARPA using xarray
      - code in fio.py, called by some notebooks (TODO: collapse into single 'summary' reading notebook)
      - used sometimes in notebooks, sometimes in bash scripts when creating intermediate data files
2. Create intermediate data files with just metrics of interest
      - Required to avoid massive file reading overheads
      - Coded mostly in bash scripts "make_....sh" called by qsub
      - TODO: simplify or summarise
3. Analyse data


# Environment

analysis3 on HH5 project:


# Data Access

### BARPA:
- project ia39
- folder:

### ERA5:


### BARRA:
