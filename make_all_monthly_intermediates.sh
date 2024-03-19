#!/bin/bash
## run some intermediate data creation, change to false if gcm/experiment combo is done

## historical is 1960-2014
## ssp are 2015-2100

## ERA5 is another source of historical info 1960 - 2020?
if false; then
    qsub -v y0=1950,y1=1975 ./subscripts/make_ERA5_monthly_max.sh
    qsub -v y0=1975,y1=2000 ./subscripts/make_ERA5_monthly_max.sh
    qsub -v y0=2000,y1=2023 ./subscripts/make_ERA5_monthly_max.sh
fi

## Subset to rerun due to failures
if false; then
    gcm="CMCC-ESM2"
    experiment="historical"
    realisation="r1i1p1f1"
    qsub -v y0=1964,y1=1966,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=1974,y1=1976,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
fi


## CMCC-... only has ssp370 and historical
if false; then
    gcm="CMCC-ESM2"
    experiment="historical"
    realisation="r1i1p1f1"
    # submit 2 years at a time
    for ((i=1960;i<=2010;i=i+2)); do
        y1=$(($i+2))
        qsub -v y0=$i,y1=$y1,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    done
    # final 3 years
    qsub -v y0=2012,y1=2015,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
fi
## CMCC SSP370
if false; then
    gcm="CMCC-ESM2"
    experiment="ssp370"
    realisation="r1i1p1f1"
    for ((i=2015;i<=2100;i=i+2)); do
        y1=$(($i+2))
        qsub -v y0=$i,y1=$y1,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    done
    
fi

## ACCESS-ESM1-5
## different realisation than cmcc
if false; then
    gcm="ACCESS-ESM1-5"
    experiment="ssp370"
    realisation="r6i1p1f1"
    for ((i=2015;i<=2100;i=i+2)); do
        y1=$(($i+2))
        qsub -v y0=$i,y1=$y1,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    done
fi

## CESM2
if false; then
    gcm="CESM2"
    experiment="ssp370"
    realisation="r11i1p1f1"
    for ((i=2015;i<=2100;i=i+2)); do
        y1=$(($i+2))
        qsub -v y0=$i,y1=$y1,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    done
    
fi

