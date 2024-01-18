
### IMPORTS
###
import xarray as xr
import numpy as np
import pandas as pd
from glob import glob
import regionmask
import pickle,warnings

__VERBOSE__=False
AU_LATRANGE = [-48,-9]
AU_LONRANGE = [111,155]

## CONSTANTS

BARPA_daily_max_folder = '/scratch/en0/jwg574/BARPA/daily_maximums/'
BARPA_base_url = "/g/data/ia39/australian-climate-service/release/CORDEX-CMIP6/output/AUS-15/BOM/%s/%s/%s/BOM-BARPA-R/v1/%s/%s/"

# map metric names to folder names
ERA5_varmap={
    'u10':'10u','v10':'10v',  # 10m winds
    'd2m':'2d','t2m':'2t', # 2m temperature and dewpoint temperature
   }

TIMESERIES_LOCATIONS = { # "loc" : [lat,lon]
    "Melb":{
        "latlon":[-37.6722, 144.8503], # airport latlon
        "yx_barpa":[103,368],
        "yx_era":[115, 135],
        "color":"magenta",
    },
    "Adel":{
        "latlon":[-34.9063, 138.8397], # hills latlon
        "yx_barpa":[121,329],
        "yx_era":[104, 111],
        "color":"yellow",
    },
    "Sydn":{
        "latlon":[-33.8, 150.7], # west sydney
        "yx_barpa":[128,406],
        "yx_era":[99, 159],
        "color":"orange",
    },
    "Darw":{
        "latlon":[-12.464,130.85], # Darwin
        "yx_barpa":[266, 277],
        "yx_era":[14, 79],
        "color":"red",
    },
    "Dar2":{
        "latlon":[-12.71,131.1], #darwin+.25 southeast
        "yx_barpa":[265, 279],
        "yx_era":[15, 80],
        "color":"grey",
    }, # Test darwin inland
}

def print_info(msg):
    if __VERBOSE__:
        print("INFO: ",msg)
    
def BARPA_intermediate_url(year,
                            gcm = "CMCC-CMCC-ESM2",
                            experiment = "ssp370",
                            realisation = "r1i1p1f1",
                            #freq = "1hr", I don't think I'll use things other than 1hr
                           ):
    # year_gcm_experiment_realisation.nc
    return "%s_%s_%s_%s.nc"%(str(year),gcm,experiment,realisation)

def BARPA_read_intermediate_years(ystr,
                                  gcm = "CMCC-CMCC-ESM2",
                                  experiment = "ssp370",
                                  realisation = "r1i1p1f1",
                                 ):
    regex_urls = BARPA_daily_max_folder + BARPA_intermediate_url(ystr,gcm,experiment,realisation)
    urls = glob(regex_urls)
    urls.sort()
    print("INFO: Reading %d BARPA dailymax files matching year %s"%(len(urls),ystr))
    ds = xr.open_mfdataset(urls)
    return ds

def BARPA_read_year(vars, year, 
                    gcm = "CMCC-CMCC-ESM2",
                    experiment = "ssp370",
                    realisation = "r1i1p1f1",
                    freq = "1hr",):
    year = str(year)
    
    ds = None
    for var in vars:        
        url_barpa_folder = BARPA_var_folder(var,gcm,experiment,realisation,freq)
        url_barpa_files = glob(url_barpa_folder+"*%s01-*.nc"%year)
        if len(url_barpa_files) < 1:
            print("ERROR: No Files Found:",url_barpa_folder)
        url_barpa_file = url_barpa_files[0]
        print("INFO: reading from ",url_barpa_file)

        dsnew = xr.open_dataset(url_barpa_file,chunks='auto')
        
        # make height an attribute, not a coordinate
        if hasattr(dsnew[var],'height'):
            dsnew[var].attrs.update({'height':dsnew[var].height.values})
            dsnew = dsnew.drop_vars('height')
            
        # store in ds
        if ds is None:
            ds = dsnew
        else:
            # combining messes with coordinates
            # just force them to match
            ds = xr.merge([ds,dsnew],compat='override',join='override',combine_attrs='override')
        #print("DEBUG: TIME[:3]",ds.time[:3])
    return ds

def BARPA_var_folder(var,
                     gcm = "CMCC-CMCC-ESM2",
                     experiment = "ssp370",
                     realisation = "r1i1p1f1",
                     freq = "1hr",
                    ):
    url_barpa_folder = BARPA_base_url%(gcm,experiment,realisation,freq,var)
    return url_barpa_folder

def BARPA_var_url(var, year,
                   gcm = "CMCC-CMCC-ESM2",
                   experiment = "ssp370",
                   realisation = "r1i1p1f1",
                   freq = "1hr",
                  ):
    year = str(year)
    url_barpa_folder = BARPA_var_folder(var,gcm,experiment,realisation,freq)
    url_barpa_file = glob(url_barpa_folder+"*%s01-*.nc"%year)[0]
    return url_barpa_file

def calc_DWI_V(ds,d2m='d2m',t2m='t2m',u10='u10',v10='v10'):

    print_info("WARNING: DWI_V calculated assuming period 1 always")
    
    if not hasattr(ds,'s10'):
        ds = calc_s10(ds,u10,v10)
    S10 = ds.s10 * 3.6 # m/s -> km/h
    DPD = ds[t2m] - ds[d2m] # Celcius (identical to Kelvin)
    
    ## DWI_V
    # TODO: split into 3 periods
    DWI_V = (S10/25.0) * (DPD+5)/20.0
    ds['DWI_V'] = DWI_V
    ds.DWI_V.attrs['units']='dry windy index'
    ds.DWI_V.attrs['long_name'] = "dry windy index for Vesta"
    ds.DWI_V.attrs['description']='U10(km/h)/25 * (DPD(Celcius)+5)/20'

    return ds

def calc_ffdi(ds,d2m='d2m',t2m='t2m',u10='u10',v10='v10',DF=10):
    """
    input units: Kelvin and m/s
    Mark 5 FFDI calculation
    """
    # T in celcius
    T = ds[t2m] - 273.15 # K -> C 
    
    # relhum
    if hasattr(ds,'rh2m'):
        RH = ds['rh2m']
    elif hasattr(ds,'hurs'):
        RH = ds['hurs']
    else:    
        ds = calc_rh(ds,d2m=d2m,t2m=t2m)
        RH = ds.rh2m

    # 10m winds
    if not hasattr(ds,'s10'):
        ds = calc_s10(ds,u10=u10,v10=v10)
    S10 = ds.s10 * 3.6 # m/s -> km/h

    # mark 5 ffdi uses T [Celcius], RH [%], 10m winds [km/h], and drought factor (unitless)
    ds['FFDI'] = 2*np.e**(-.45 + .987 * np.log(DF) - .0345 * RH + .0338 * T + .0234 * S10)
    ds.FFDI.attrs['units']='danger index'
    ds.FFDI.attrs['long_name'] = "forest fire danger index mk. 5"
    ds.FFDI.attrs['description']='2*e**(-.45 + .987 * np.log(DF) - .0345 * RH + .0338 * T + .0234 * S10)'
    
    return ds

def calc_ffdi_replacements(ds,d2m='d2m',t2m='t2m',u10='u10',v10='v10',DF=10):
    """
    Psuedo, and Faux FFDI calculated using km/h 10m winds, %RH at 2m, 2m T Celcius, and assuming DF of 10
    Based on DWI_V (Kevin's Dry Windy Index)
    Period 1: midday to 1700, 1 Oct -> 31 Mar
    Period 2: all other daytime hours (0600 - 1800)
    Period 3: nightime (1800-0600)
    
    Currently just assuming we are always in period 1 (worst case)
    
    """
    
    T = ds[t2m] - 273.15 # K -> C
    # relhum
    if hasattr(ds,'rh2m'):
        RH = ds['rh2m']
    elif hasattr(ds,'hurs'):
        RH = ds['hurs']
    else:    
        ds = calc_rh(ds,d2m=d2m,t2m=t2m)
        RH = ds.rh2m
    if not hasattr(ds,'DWI_V'):
        ds = calc_DWI_V(ds,d2m,t2m,u10,v10)
    DWI_V = ds.DWI_V # ?? units
    
    ## faux ffdi
    ds['FFDI_F'] = DF * (T+12)/20.0 * DWI_V
    ds.FFDI_F.attrs['units']='danger index'
    ds.FFDI_F.attrs['long_name'] = "faux forest fire danger index"
    ds.FFDI_F.attrs['description']='DF * (T+12)/20 * DWI_V'

    ## faux ffdi
    ds['FFDI_P'] = 5/3 * DF * DWI_V
    ds.FFDI_P.attrs['units']='danger index'
    ds.FFDI_P.attrs['long_name'] = "pseudo forest fire danger index"
    ds.FFDI_P.attrs['description']='5/3 * DF * DWI_V'
    
    return ds

def calc_rh(ds,d2m='d2m',t2m='t2m'):
    '''
        return ds with 'rh2m' dataarray from d2m and t2m
        RH = 100 × {exp[17.625 × Dp/(243.04 + Dp)]/exp[17.625 × T/(243.04 + T)]}
        assumed: d2m and t2m in Celcius
    '''
    
    Dp = ds[d2m] - 273.15 # Kelvin to C
    T = ds[t2m] - 273.15 #
    rh = 100 * np.exp( 17.625 * Dp/(243.04 + Dp)) / np.exp( 17.625 * T/(243.04 + T))
    ds['rh2m'] = rh
    ds.rh2m.attrs['units']='%'
    ds.rh2m.attrs['description']='100 * np.exp( 17.625 * Dp/(243.04 + Dp)) / np.exp( 17.625 * T/(243.04 + T))'
    ds.rh2m.attrs['long_name']='2 metre relative humidity'
    return ds

def calc_s10(ds,u10='u10',v10='v10'):
    #return ds with 's10' dataarray
    
    ds['s10'] = (ds[v10]**2+ds[u10]**2)**0.5
    ds.s10.attrs['units']=ds[u10].units
    ds.s10.attrs['description']='sqrt(u10**2+v10**2)'
    ds.s10.attrs['long_name'] ='10 metre wind speed'
    
    return ds

def calc_Td(ds,t='tas',rh='hurs'):
    ''' Td = T - ((100 - RH)/5.) 
        T in celcius
        RH in pct
    '''
    Td = ds[t] - (100-ds[rh])/5.0
    ds['Td'] = Td
    ds.Td.attrs['units']=ds[t].units
    ds.Td.attrs['description']='Td = T - ((100 - RH)/5.)'
    ds.Td.attrs['long_name'] ='Dewpoint Temperature'
    
    return ds

def ERA5_read_dailymaximums():
    ds_dm = xr.open_dataset("/scratch/en0/jwg574/ERA5/daily_maximums.nc")
    #ausmask = get_landmask(pre_2000.FFDI)
    return ds_dm

def ERA5_read_yearlymaximums():
    ds_ym = xr.open_dataset("/scratch/en0/jwg574/ERA5/yearly_maximums.nc")
    #ausmask = get_landmask(pre_2000.FFDI)
    return ds_ym

def ERA5_read_long(varlist,latrange=[-60,20]):
    ''' 
    read full ERA5 1960-2020
    ARGS:
        varlist=['u10','v10',...]
        years=[list of years]
    '''
    ## 20x20x744 = 1.14 MB
    ## 30x30x10000 should be better
    #chunks={'time':2000,'latitude':40,'longitude':40}
    
    ## first figure out paths from day and varlist
    ds = None
    
    for var in varlist:
        varfolder = var
        if var in ERA5_varmap.keys():
            varfolder = ERA5_varmap[var]
        varpath = "/g/data/rt52/era5/single-levels/reanalysis/%s/*/*01-*.nc"%(varfolder)
        filename = glob(varpath)

        if len(filename) == 0:
            print('ERROR: no netcdf files found:',varpath)
        
        print('INFO: reading %d files for %s'%(len(filename),var))
        
        # store in ds
        if ds is None:
            ds = xr.open_mfdataset(filename,
                                   #chunks=chunks
                                  )
        else:
            dsnew = xr.open_mfdataset(filename,
                                      #chunks=chunks
                                     )
            ds[var] = dsnew[var]
    
    if latrange is not None:
        # descending latitude
        ds=ds.sel(latitude=slice(max(latrange),min(latrange)))
    
    return ds 

def ERA5_read_month(varlist,day,latrange=[-60,20]):
    ''' varlist=['u10','v10',...], day=datetime(yyyy,m,d) '''

    ## how to chunk data
    chunks={'time':50}
    
    ## first figure out paths from day and varlist
    pdday = pd.to_datetime(str(day))
    yyyy,mm =  pdday.strftime('%Y,%m').split(',')
    ds = None
    
    
    
    # read month file for each var
    for var in varlist:
        varfolder = var
        if var in ERA5_varmap.keys():
            varfolder = ERA5_varmap[var]
        varpath = "/g/data/rt52/era5/single-levels/reanalysis/%s/%s/*%s%s01-*.nc"%(varfolder,yyyy,yyyy,mm)
        filename = glob(varpath)
        if len(filename) == 0:
            print('ERROR: no netcdf files found:',varpath)
            
        print_info('INFO: reading %s'%filename)
        # store in ds
        if ds is None:
            ds = xr.open_dataset(filename[0])
        else:
            dsnew = xr.open_dataset(filename[0])
            ds[var] = dsnew[var]
    
    if latrange is not None:
        # descending latitude
        ds=ds.sel(latitude=slice(max(latrange),min(latrange)))

    ds = ds.chunk(chunks={'time':50})
    
    return ds

def get_landmask(da):
    
    landmask = regionmask.defined_regions.natural_earth_v5_0_0.land_110.mask(da)
    # this is zeros where land is, nans elsewhere
    # lets change it to True where land is, False elsewhere
    return landmask == 0

def get_time_series(locname, force_renew=False, verbose=False):
    """ Pass in locname from TIMESERIES_LOCATIONS keys 
        reads FFDI, FFDI_F, DWI_V time series from ERA5 and several BARPA runs
        uses intermediate pickle file if possible, otherwise requires barpa daily maximum intermediates to have been created
    """
    assert locname in TIMESERIES_LOCATIONS.keys(), "%s not in list: %s"%(locname, str(TIMESERIES_LOCATIONS.keys()))
    
    # first check if file already created
    fname = 'data/timeseries_%s.pickle'%(locname)
    if not force_renew and os.path.isfile(fname):
        # read and return file data
        print("INFO: %s found, reading data"%fname)
        with open(fname,'rb') as ts_file:
            ts_dict = pickle.load(ts_file)
        return ts_dict

    # Otherwise we create the time series
    ## READ ERA5
    # rename lon,lat to match BARPA
    ds_ERA5 = ERA5_read_dailymaximums().rename({'longitude':'lon','latitude':'lat'})
    
    ## READ BARPA
    ## Read ssp370, and historical for CMCC GCM
    ds_cmcc = BARPA_read_intermediate_years("*",experiment='ssp370')
    ds_cmcc_hist = BARPA_read_intermediate_years("*",experiment='historical')
    
    ## Read ssp370 and ssp126, and historical for CMCC GCM
    ds_esm1_126 = BARPA_read_intermediate_years("*",
                                                gcm="CSIRO-ACCESS-ESM1-5",
                                                experiment="ssp126",
                                                realisation="r6i1p1f1",)
    ds_esm1_370 = BARPA_read_intermediate_years("*",
                                                 gcm="CSIRO-ACCESS-ESM1-5",
                                                 experiment="ssp370",
                                                 realisation="r6i1p1f1",
                                                )
    
    y_era,x_era = TIMESERIES_LOCATIONS[locname]['yx_era']
    y_barpa,x_barpa = TIMESERIES_LOCATIONS[locname]['yx_barpa']
    ts_places = {}
    
    ## Loop over metric here: FFDI, FFDI_F, DWI_V
    for metric in ['FFDI','DWI_V' ,'FFDI_F']: # for now not ffdi_f
        ## Can loop over barpa models
        for barpa_model, descriptor in zip([ds_cmcc_hist, ds_cmcc, ds_esm1_370, ds_esm1_126],
                                           ["%s_%s_CMCC_hist","%s_%s_CMCC_370",'%s_%s_CSIRO_ESM_370','%s_%s_CSIRO_ESM_126']):
            ts_name = descriptor%(locname,metric)
            if verbose:
                print("INFO: Loading ",ts_name)
            TS = barpa_model[metric][:,y_barpa,x_barpa].load()
            ## some barpa data uses no leap years, non-standard calendar
            ## may be slightly out of sync with reality, I think that is why null values get put in?
            if isinstance(TS.indexes['time'],xr.CFTimeIndex):
                with warnings.catch_warnings(): # ignore calendar conversion warnings
                    warnings.simplefilter("ignore")
                    TS_dti = TS.indexes['time'].to_datetimeindex()
            else:
                TS_dti=TS.indexes['time']
            ## Store as pandas time series, removing nans
            TS_pd = pd.Series(TS.values,index=TS_dti)
            if verbose:
                print("INFO: dropping %d null values from %s"%(TS_pd.isnull().sum(),ts_name))
            ts_places[ts_name] = TS_pd.dropna()
    
        if verbose:
            print("Loading ERA_5")
        TSE=ds_ERA5[metric][:,y_era,x_era].load()
        ts_places['%s_%s_ERA5'%(locname,metric)] = pd.Series(TSE.values,TSE.indexes['time'])

    with open(fname,'wb') as ts_file:
        print("INFO: Saving %s"%fname)
        pickle.dump(ts_places,ts_file)
    
    return ts_places

def read_enso_rolling3m():
    """https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"""
    oni = pd.read_csv("https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",delim_whitespace=True)
    oni['Monthstr'] = oni.SEAS.str[1]
    oni['Month'] = (oni.index%12)+1
    oni['Date'] = pd.to_datetime(dict(year=oni.YR, month=oni.Month, day=1))
    oni=oni.set_index(pd.DatetimeIndex(oni['Date'])).drop(['Date'],axis=1)
    return oni

def select_australia(ds,latrange=AU_LATRANGE,lonrange=AU_LONRANGE):
    """
    return subset of DS that is within lat and lon range
    """
    ds = ds.sel(latitude=slice(max(latrange),min(latrange)))
    ds = ds.sel(longitude=slice(min(lonrange),max(lonrange)))
    return ds
