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
- this won't be necessary if you are working through the are.nci.org.au portal and have the advanced options noted above

## Summary of Repo

1. Read ERA5 and BARPA using xarray (Read_Raw_Models.ipynb)
    - some examples reading directly from the datasets is in this notebook
3. Create intermediate data files with just metrics of interest (fio.py)
      - Required to avoid massive file reading overheads
      - large intermediate dataset mostly created by running bash-script make_all_monthly_intermediates.sh
          - that script sends 'jobs' to the queue to be run independently by GADI
          - those jobs are defined in subscripts folder, with scripts calling code in the fio.py module
      - created files are monthly maximums for metrics and the metric components
      - The files are currently coded to go into my scratch directory
          - NB: scratch directory purges files that aren't touched for 90 days
      - The notebook "Intermediate_Data.ipynb" summarises and performs some small examples of reading the intermediate dataset
4. Analyse data (Analysis.ipynb)
    - run through some figure creation and analysis using the intermediate datasets


# Example Creating intermediate dataset
1. If you are not me (jwg574) you will need to change where you are writing the intermediate dataset to
    - inside fio.py there are three variables (BARPA_monthly_max_folder, ...) that define where the monthly maximum datasets will be saved
    - you might want to set this to your own scratch directory, or even in the data folder if Harvey hasn't told you to save space.
    - Note anywhere on /g/data/... is persistent until you delete it, anywhere on /scratch/... is purged after not being used for 90 days
3. Open the make_all_monthly_intermediates.sh
    - Depending which gcm and experiment you want to get monthly maximums for you will need to change one of the if-blocks to true, in order to run that if block when running that script.
4. on the command line run the script by typing `./make_all_monthly_intermediates.sh`
    - you should see a list of 'job ids' appear as the subscripts are 'sent to the queue' to be run by GADI
5. you can type `qstat` to see what jobs you are running on GADI
6. after a few hours, you can check that the jobs are done and the netcdf files are created in your outputdir
