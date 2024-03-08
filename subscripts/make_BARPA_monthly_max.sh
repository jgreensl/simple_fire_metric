#!/bin/bash
#PBS -P en0
#PBS -q normal
#PBS -N BARPA_MonthlyMax
#PBS -l walltime=12:00:00
#PBS -l mem=100GB
#PBS -l ncpus=16
#PBS -l wd
#PBS -l storage=gdata/py18+gdata/hh5+gdata/en0+scratch/en0 

# Arguments required:
if [ -z ${y0} ] || [ -z ${y1} ] ; then
    echo "EG usage: qsub -v y0=2015,y1=2017 ${0}"
    echo "        : can also set: gcm=CMCC-ESM2,experiment=ssp370,realisation=r1i1p1f1"
    echo "NB: X years takes around X hours, X RAM"
    exit 0
fi

# Default arguments
if [ -z ${gcm} ] ; then
    gcm="CMCC-ESM2"
fi
if [ -z ${experiment} ] ; then
    experiment="ssp370"
fi
if [ -z ${realisation} ] ; then
    realisation="r1i1p1f1"
fi

## analysis 3 env for running python code
source /g/data/hh5/public/apps/miniconda3/etc/profile.d/conda.sh
conda activate /g/data/hh5/public/apps/miniconda3/envs/analysis3

echo "Starting: $gcm $experiment $realisation from $y0 to $y1"
echo "Starting: $(date '+%Y-%m-%d %H:%M:%S')"

# Run this python
python << EOF
import os
import fio

# what years are we looking at
YEARS=range(${y0},${y1})
GCM="${gcm}"
EXPERIMENT="${experiment}"
REALISATION="${realisation}"

#make_BARPA_monthly_maximum_intermediate(
#year, 
#force_renew = False, 
#gcm = "CMCC-ESM2", # climate model
#experiment = "ssp370",
#realisation = "r1i1p1f1",
#freq = "1hr"):

for year in YEARS:
    print("info: starting %d"%year)
    data = fio.make_BARPA_monthly_maximum_intermediate(
        year,                                             
        force_renew = True,
        gcm = GCM,
        experiment = EXPERIMENT,
        realisation = REALISATION,
        )

EOF

echo "Finished: $gcm $experiment from $y0 to $y1"
echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
