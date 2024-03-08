#!/bin/bash
## run some intermediate data creation, change to false if gcm/experiment combo is done

## historical is 1960-2014
## ssp are 2015-2100

## ERA5 is another source of historical info 1960 - 2020?
if true; then
    qsub -v y0=1950,y1=1975 ./subscripts/make_ERA5_monthly_max.sh
    qsub -v y0=1975,y1=2000 ./subscripts/make_ERA5_monthly_max.sh
    qsub -v y0=2000,y1=2023 ./subscripts/make_ERA5_monthly_max.sh
fi

## CMCC-... only has ssp370 and historical
## 
if false; then
    gcm="CMCC-ESM2"
    experiment="historical"
    #qsub -v y0=1960,y1=1965,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=1960,y1=1975,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=1975,y1=1990,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=1990,y1=2015,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
fi

if false; then
    gcm="CMCC-ESM2"
    experiment="ssp370"
    qsub -v y0=2015,y1=2020,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2020,y1=2030,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
    #qsub -v y0=2030,y1=2050,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
    #qsub -v y0=2050,y1=2070,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
    #qsub -v y0=2070,y1=2090,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
    #qsub -v y0=2090,y1=2101,experiment=$experiment,gcm=$gcm  ./subscripts/make_BARPA_monthly_max.sh
fi

## CSIRO-ACCESS-ESM1-5
## different realisation than cmcc
if false; then
    gcm="CSIRO-ACCESS-ESM1-5"
    experiment="ssp126"
    realisation="r6i1p1f1"
    qsub -v y0=2015,y1=2030,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2030,y1=2045,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2045,y1=2060,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2060,y1=2075,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2075,y1=2090,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2090,y1=2101,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
fi

## CSIRO but different ssp
if false; then
    gcm="CSIRO-ACCESS-ESM1-5"
    experiment="ssp370"
    realisation="r6i1p1f1"
    qsub -v y0=2015,y1=2030,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2030,y1=2045,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2045,y1=2060,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2060,y1=2075,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2075,y1=2090,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2090,y1=2101,experiment=$experiment,gcm=$gcm,realisation=$realisation ./subscripts/make_BARPA_monthly_max.sh
fi

