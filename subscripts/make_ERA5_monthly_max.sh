#!/bin/bash
#PBS -P en0
#PBS -q normalbw
#PBS -N ERA5_MonthlyMax
#PBS -l walltime=8:00:00
#PBS -l mem=160GB
#PBS -l ncpus=16
#PBS -l wd
#PBS -l storage=gdata/rt52+gdata/hh5+gdata/en0+scratch/en0 

# Arguments required:
if [ -z ${y0} ] || [ -z ${y1} ] ; then
    echo "EG usage: qsub -v y0=2015,y1=2017 ${0}"
    echo "        : to create yearly files for monthly maximum ERA5 metrics and friends"
    echo "NB: 15 years takes around 3 hours, 100 GB RAM"
    exit 0
fi

## analysis 3 env for running python code
source /g/data/hh5/public/apps/miniconda3/etc/profile.d/conda.sh
conda activate /g/data/hh5/public/apps/miniconda3/envs/analysis3

echo "Starting: ERA5 Monthly max metric creation from $y0 to $y1"
echo "Starting: $(date '+%Y-%m-%d %H:%M:%S')"

# Run this python
python << EOF
import os
import fio

# what years are we looking at
YEARS=range(${y0},${y1})


for year in YEARS:
    print("info: starting %d"%year)
    fio.make_ERA5_monthly_maximum_intermediate(
        year,                                             
        force_renew = True,
        )

EOF

echo "Finished: ERA5 monthlies from $y0 to $y1"
echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
