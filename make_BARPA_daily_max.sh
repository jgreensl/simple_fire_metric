#!/bin/bash
#PBS -P en0
#PBS -q normalbw
#PBS -N BARPA_DayMax
#PBS -l walltime=24:00:00
#PBS -l mem=240GB
#PBS -l ncpus=16
#PBS -l wd
#PBS -l storage=gdata/ia39+gdata/hh5+gdata/en0+scratch/en0

# Arguments required:
if [ -z ${y0} ] || [ -z ${y1} ] ; then
    echo "EG usage: qsub -v y0=2015,y1=2017 ${0}"
    echo "        : can also set: gcm=CMCC-CMCC-ESM2,experiment=ssp370"
    echo "NB: 20 years takes around 3 hours, 130GB RAM"
    exit 0
fi

# Default arguments
if [ -z ${gcm} ] ; then
    gcm="CMCC-CMCC-ESM2"
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

## ~ 30GB ram per year, takes a couple minutes
def run_some_years(
    years,
    gcm,experiment,realisation,):
    
                   
    folder_barpa_daily_max = fio.BARPA_daily_max_folder
    os.makedirs(folder_barpa_daily_max, exist_ok=True)
    
    for year in years:
        fname = folder_barpa_daily_max+fio.BARPA_intermediate_url(year,gcm,experiment,realisation)
        if os.path.isfile(fname):
            print("INFO: year %4d alread written at %s"%(year,fname))
            continue
        
        print("INFO: working on year ",year)
    
        # Read info for year
        ds = fio.BARPA_read_year(vars=['hurs','tas','uas','vas'], 
            year=year, 
            gcm=gcm, 
            experiment=experiment,
            realisation=realisation,
            )
        ds = fio.calc_Td(ds, t='tas',rh='hurs')
        ds = fio.calc_DWI_V(ds, d2m='Td',t2m='tas',u10='uas',v10='vas')
        ds = fio.calc_ffdi(ds, d2m='Td',t2m='tas',u10='uas',v10='vas')
        ds = fio.calc_ffdi_replacements(ds, d2m='Td',t2m='tas',u10='uas',v10='vas')
        
        # daily resampling
        # ffdi
        da_ffdi_max = ds.FFDI.resample(time='D').max()
        da_ffdif_max = ds.FFDI_F.resample(time='D').max()
        # calc dwi_v
        da_dwi_max = ds.DWI_V.resample(time='D').max()
        # keep driving vars for dwi_v
        
        # store the year
        ds_year = da_ffdi_max.to_dataset()
        ds_year = ds_year.merge(da_dwi_max)
        ds_year = ds_year.merge(da_ffdif_max)
        ds_year.to_netcdf(fname)
        print("INFO: file saved: ",fname)



### RUN SOME CODE
gcms = [
    ## evaluation/historical only
    "ECMWF-ERA5",
    "MPI-M-MPI-ESM1-2-HR", 
    ## with ssp projections:
    "CMCC-CMCC-ESM2",
    "CSIRO-ACCESS-ESM1-5",
    "CSIRO-ARCCSS-ACCESS-CM2", 
    "EC-Earth-Consortium-EC-Earth3",
    "NCAR-CESM2","CSIRO-ACCESS-ESM1-5",
    "NCC-NorESM2-MM",
    ]
experiments = [
    "evaluation", # 1979-2020
    "historical", # 1960-2014
    "ssp126", # 2015-2100
    "ssp370", # 2015-2100
    ]

#gcm = gcms[2]
#experiment = "ssp370"
#realisation = "r1i1p1f1"

run_some_years(years=YEARS,gcm=GCM,experiment=EXPERIMENT,realisation=REALISATION,)

EOF

echo "Finished: $gcm $experiment from $y0 to $y1"
echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
