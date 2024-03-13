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

## Testing
if false; then
    gcm="CESM2"
    experiment="ssp370"
    realisation="r11i1p1f1"
    qsub -v y0=2015,y1=2016,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2016,y1=2018,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2018,y1=2023,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
fi


## CMCC-... only has ssp370 and historical
## 
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

if true; then
    gcm="CMCC-ESM2"
    experiment="ssp370"
    realisation="r1i1p1f1"
    for ((i=2015;i<=2100;i=i+2)); do
        y1=$(($i+2))
        qsub -v y0=$i,y1=$y1,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    done
    
fi

## CSIRO-ACCESS-ESM1-5
## different realisation than cmcc
if false; then
    gcm="ACCESS-ESM1-5"
    experiment="ssp370"
    realisation="r6i1p1f1"
    qsub -v y0=2015,y1=2020,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2020,y1=2025,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2025,y1=2030,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2030,y1=2035,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2035,y1=2040,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2040,y1=2045,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2045,y1=2050,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2050,y1=2055,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2055,y1=2060,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2060,y1=2065,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2065,y1=2070,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2070,y1=2075,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2075,y1=2080,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2080,y1=2085,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2085,y1=2090,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2090,y1=2095,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2095,y1=2101,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
fi

## CESM2
if false; then
    gcm="CESM2"
    experiment="ssp370"
    realisation="r11i1p1f1"
    qsub -v y0=2015,y1=2020,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2020,y1=2025,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2025,y1=2030,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2030,y1=2035,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2035,y1=2040,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2040,y1=2045,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2045,y1=2050,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2050,y1=2055,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2055,y1=2060,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2060,y1=2065,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2065,y1=2070,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2070,y1=2075,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2075,y1=2080,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2080,y1=2085,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2085,y1=2090,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2090,y1=2095,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
    qsub -v y0=2095,y1=2101,experiment=$experiment,gcm=$gcm,realisation=$realisation  ./subscripts/make_BARPA_monthly_max.sh
fi

