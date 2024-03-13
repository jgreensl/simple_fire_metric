# Simple Fire weather metric analysis using ERA5 and BARPA within GADI supercomputer

## Setting up GADI and Github for using this repo

### make an account on GADI
- sign up on my.nci.org.au
- Probably talk to Harvey for an account within the en0 project space

### good interface for GADI work
- go to are.nci.org.au, log in
- create a jupyterlab instance with these settings:
    - walltime: 8 (or however long you want to be able to access this window)
    - queue: normal
    - compute size: medium (may need large if doing anything heavy in the notebooks)
    - project: en0
    - storage: gdata/en0+gdata/hh5+gdata/ua8+gdata/py18+scratch/en0+gdata/ia39
    - software: python
    - (advanced option) module directories: /g/data/hh5/public/modules
    - (advanced option) modules: conda/analysis3


### Clone the repository in a directory on GADI
1. open a terminal
2. first time only: make a directory and clone the repository
```
mkdir /g/data/en0/<username>
cd /g/data/en0/<username>
git clone git@github.com:jgreensl/simple_fire_metric.git
```
3. any subsequent time: navigate to repository, run notebooks

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


## Summary of Repo

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


# Examples:

## Simple grab and display of Data

### BARPA:

### ERA5:

## Create intermediate datasets


### BARRA:
