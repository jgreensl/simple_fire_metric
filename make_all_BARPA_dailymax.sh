#!/bin/bash
## run some intermediate data creation, change to false if gcm/experiment combo is done

## historical is 1960-2014
## ssp are 2015-2100

## CMCC-... only has ssp370 and historical
## 
if false; then
    gcm="CMCC-CMCC-ESM2"
    experiment="historical"
    qsub -v y0=1960,y1=1975,experiment=$experiment,gcm=$gcm  ./make_BARPA_daily_max.sh
    qsub -v y0=1975,y1=1990,experiment=$experiment,gcm=$gcm  ./make_BARPA_daily_max.sh
    qsub -v y0=1990,y1=2015,experiment=$experiment,gcm=$gcm  ./make_BARPA_daily_max.sh
fi

## CSIRO-ACCESS-ESM1-5
## different realisation than cmcc
if false; then
    gcm="CSIRO-ACCESS-ESM1-5"
    experiment="ssp126"
    realisation="r6i1p1f1"
    qsub -v y0=2015,y1=2030,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2030,y1=2045,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2045,y1=2060,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2060,y1=2075,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2075,y1=2090,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2090,y1=2101,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
fi

## CSIRO but different ssp
if false; then
    gcm="CSIRO-ACCESS-ESM1-5"
    experiment="ssp370"
    realisation="r6i1p1f1"
    qsub -v y0=2015,y1=2030,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2030,y1=2045,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2045,y1=2060,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2060,y1=2075,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2075,y1=2090,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
    qsub -v y0=2090,y1=2101,experiment=$experiment,gcm=$gcm,realisation=$realisation ./make_BARPA_daily_max.sh
fi

