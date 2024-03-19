
### IMPORTS
###
import xarray as xr
import numpy as np
import pandas as pd
from glob import glob
import regionmask
import pickle,warnings, os
from datetime import timedelta

__VERBOSE__=False
AU_LATRANGE = [-48,-9]
AU_LONRANGE = [111,155]

## CONSTANTS

BARPA_daily_max_folder = '/scratch/en0/jwg574/BARPA/daily_maximums/'
BARPA_monthly_max_folder = '/scratch/en0/jwg574/BARPA/monthly_maximums/'
ERA5_monthly_max_folder = '/scratch/en0/jwg574/ERA5/monthly_maximums/'
# /g/data/py18/BARPA/output/CMIP6/DD/AUS-15/BOM/<GCM>/<experiment>/<realisation>/BARPA-R/v1-r1/<freq>/<variable>/V20231001/<yearly netcdf files>
BARPA_base_url = "/g/data/py18/BARPA/output/CMIP6/DD/AUS-15/BOM/%s/%s/%s/BARPA-R/v1-r1/%s/%s/%s/"
BARPA_base_url_OLD_ia39 = "/g/data/ia39/australian-climate-service/release/CORDEX-CMIP6/output/AUS-15/BOM/%s/%s/%s/BOM-BARPA-R/v1/%s/%s/"


# map metric names to folder names
ERA5_varmap={
    'u10':'10u','v10':'10v',  # 10m winds
    'd2m':'2d','t2m':'2t', # 2m temperature and dewpoint temperature
   }

TIMESERIES_LOCATIONS = { # "loc" : [lat,lon]
    "Melb":{
        "latlon":[-37.6722, 144.8503], # airport latlon
        "yx_barpa":[66, 219],
        "yx_era":[115, 135],
        "color":"magenta",
    },
    "Adel":{
        "latlon":[-34.9063, 138.8397], # hills latlon
        "yx_barpa":[84, 180],
        "yx_era":[104, 111],
        "color":"yellow",
    },
    "Sydn":{
        "latlon":[-33.8, 150.7], # west sydney
        "yx_barpa":[91, 257],
        "yx_era":[99, 159],
        "color":"orange",
    },
    "Darw":{
        "latlon":[-12.464,130.85], # Darwin
        "yx_barpa":[229, 128],
        "yx_era":[14, 79],
        "color":"red",
    },
    "Dar2":{
        "latlon":[-12.71,131.1], #darwin+.25 southeast
        "yx_barpa":[228, 130],
        "yx_era":[15, 80],
        "color":"grey",
    }, # Test darwin inland
}

def print_info(msg):
    if __VERBOSE__:
        print("INFO: ",msg)
    
def BARPA_intermediate_url(year,
                            gcm = "CMCC-ESM2",
                            experiment = "ssp370",
                            realisation = "r1i1p1f1",
                            #freq = "1hr", I don't think I'll use things other than 1hr
                           ):
    # year_gcm_experiment_realisation.nc
    return "%s_%s_%s_%s.nc"%(str(year),gcm,experiment,realisation)

def BARPA_read_intermediate_years(ystr,
                                  gcm = "CMCC-ESM2",
                                  experiment = "ssp370",
                                  realisation = "r1i1p1f1",
                                 ):
    regex_urls = BARPA_monthly_max_folder + BARPA_intermediate_url(ystr,gcm,experiment,realisation)
    urls = glob(regex_urls)
    urls.sort()
    print("INFO: Reading %d BARPA years (of monthly maximums) matching year %s"%(len(urls),ystr))
    print("    :  ",gcm,experiment,realisation)
    if len(urls) == 0:
        print("ERROR: no urls in ",regex_urls)
    ds = xr.open_mfdataset(urls)
    return ds

def BARPA_read_year(vars, year, 
                    gcm = "CMCC-ESM2",
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
            print("ERROR: var,year,...:",var,year,gcm,experiment,realisation)
        url_barpa_file = url_barpa_files[0]
        print("INFO: reading %s from %s"%(var,url_barpa_file))

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
                     gcm = "CMCC-ESM2",
                     experiment = "ssp370",
                     realisation = "r1i1p1f1",
                     freq = "1hr",
                     version = 'v20231001',
                    ):
    """
    For any variable name return the folder holding all the netcdf data
    
    Inputs: (all strings)
        var = variable name in BARPA
        gcm = global climate model eg: 'CMCC-ESM2', or 'ACCESS-ESM1-5'
        experiment = barpa model experiment eg: 'ssp370', or 'historical'
        freq = output time frequency eg: '1hr', or '6hr'
        version = barpa output version, currently seems to be just v20231001
    """
    url_barpa_folder = BARPA_base_url%(gcm,experiment,realisation,freq,var,version)
    return url_barpa_folder

def BARPA_var_url(var, year,
                   gcm = "CMCC-ESM2",
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

def calc_monthly_components(da,metric,components):
    """
    monthly loop over <metric>, picking out maximum, and the components producing that maximum
    new da with variables: [metric, metric_component1,... ]
    ARGUMENTS:
        da, # DataArray with both metrics, and components, as data variables on time,lat,lon coords
        metric, # "FFDI", "DWI_V", or "FFDI_F" 
        components, #["tas","s10", "Td", ...]
    """
    
    # Resample the data array input to get monthly data
    # 'ME' means monthly groups with time label on End of month
    # Currently (20240312) 'ME' fails, 'M' throws warning but OK
    # I think ME works OK when running through qsub, just not from jupyterlab instance (?)
    da_r = da[metric].resample(time='ME')
    
    ds_months = None
    for time_stamp, da_month in da_r:
        dict_month = {}
        
        da_max = da_month.compute().max(dim='time')
        da_imax = da_month==da_max # indices where da_month == da_max value
        
        for component in components:
            # min collapses time dimension to first instance where da matches da_max
            # there should only be one instance anyway, but the time dim will be there until we collapse it
            component_max = da[component].where(da_imax).min("time")
            dict_month["%s_%s"%(metric,component)] = component_max
        
        dict_month[metric] = da_max
        ds_month = xr.Dataset(dict_month)
        if ds_months is None:
            ds_months=ds_month
        else:
            ds_months = xr.concat([ds_months,ds_month],dim='time')

    return ds_months

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

def ERA5_read_intermediate(ystr='*'):
    regex_urls = '%s%s.nc'%(ERA5_monthly_max_folder,ystr)
    urls = glob(regex_urls)
    urls.sort()
    print("INFO: Reading %d ERA5 monthly max files matching year %s"%(len(urls),ystr))
    if len(urls) == 0:
        print("ERROR: no urls in ",regex_urls)
    ds = xr.open_mfdataset(urls)
    return ds

def ERA5_read_dailymaximums():
    ds_dm = xr.open_dataset("./data/ERA5/daily_maximums.nc")
    #ausmask = get_landmask(pre_2000.FFDI)
    return ds_dm
    
def ERA5_read_yearlymaximums():
    ds_ym = xr.open_dataset("./data/ERA5/yearly_maximums.nc")
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



def make_BARPA_monthly_maximum_intermediate(year, 
                                            force_renew = False, 
                                            gcm = "CMCC-ESM2", # climate model
                                            experiment = "ssp370",
                                            realisation = "r1i1p1f1",
                                            freq = "1hr",
                                            debug=False,
                                           ):
    """
    Arguments:
        year, # which year to create the files for
        force_renew, # overwrite yearly maximum file if it already exists
        gcm = "CMCC-ESM2", # climate model
        experiment = "ssp370",
        realisation = "r1i1p1f1",
        freq = "1hr"
    Returns nothing, file will be created in fio.BARPA_montly_max_folder
    """

    # Read data unless it's already done
    fname = BARPA_monthly_max_folder+BARPA_intermediate_url(year,gcm,experiment,realisation)
    if os.path.isfile(fname):
        print("INFO: year %4d alread written at %s"%(year,fname))
        # don't overwrite the file
        if not force_renew:
            return xr.load_dataset(fname)

    # Read year of barpa data
    print("INFO: Reading and calculating FFDI and friends for %4d"%year)
    #vars, year, gcm = "CMCC-ESM2", experiment = "ssp370", realisation = "r1i1p1f1", freq = "1hr",
    barpa0 = BARPA_read_year(vars=['hurs','tas','ps','uas','vas'], 
                            year=year, 
                            gcm=gcm,
                            experiment=experiment,
                            realisation=realisation,
                            freq=freq,
                           )
    
    # Subset to AUS
    barpa = barpa0.where(barpa0.lat < AU_LATRANGE[1],drop=True)
    barpa = barpa.where(barpa.lat > AU_LATRANGE[0],drop=True)
    barpa = barpa.where(barpa.lon > AU_LONRANGE[0],drop=True)
    barpa = barpa.where(barpa.lon < AU_LONRANGE[1],drop=True)
    
    # calculate FFDI_F, FFDI, DWI_V
    barpa = calc_Td(barpa,t='tas',rh='hurs')
    barpa = calc_ffdi(barpa,d2m='Td',t2m='tas',u10='uas',v10='vas')
    barpa = calc_ffdi_replacements(barpa ,d2m='Td',t2m='tas',u10='uas',v10='vas')

    # Calculate monthly maximum fire metrics, and the contributing components
    monthlies = []
    monthlies.append(calc_monthly_components(barpa,'FFDI',['tas','s10']))
    monthlies.append(calc_monthly_components(barpa,'FFDI_F',['tas','s10','Td']))
    monthlies.append(calc_monthly_components(barpa,'DWI_V',['tas','s10','Td']))
    
    # combine into single dataset
    DS_monthlies = xr.combine_by_coords(monthlies)

    # Update timestamps
    mid_month_stamp = pd.date_range(start='%d-01-01'%year,periods=12,freq='MS')+timedelta(days=14)
    DS_monthlies = DS_monthlies.assign_coords({"time": mid_month_stamp})
    
    # Save these monthly maximums to a file
    os.makedirs(BARPA_monthly_max_folder,exist_ok=True)
    print("INFO: Saving file %s"%fname)
    DS_monthlies.to_netcdf(fname)
    #return DS_monthlies

def make_ERA5_monthly_maximum_intermediate(
    year, 
    force_renew = False, ):
    """
    Arguments:
        year, # which year to create the files for
        force_renew, # overwrite yearly maximum file if it already exists
    Returns nothing, file will be created in fio.ERA_montly_max_folder
    """
    
    vars_for_ffdi = ['u10','v10','d2m','t2m']
    
    # Don't bother if data already exists
    fname = ERA5_monthly_max_folder + "%4d.nc"%year
    if os.path.isfile(fname):
        print("INFO: year %4d alread written at %s"%(year,fname))
    
        if not force_renew:
            return None

    print("INFO: Reading and calculating FFDI and friends for %4d"%year)
    monthlies = []
    # first we build up a year of data
    ds = None
    for month in np.arange(12)+1:
        # read month
        month_str='%4d-%02d'%(year,month)
        ds_month = ERA5_read_month(vars_for_ffdi, month_str)
        
        # combine along time axis
        if ds is None:
            ds = ds_month
        else:
            ds = xr.concat([ds,ds_month],'time')
    
    # subset to AUS
    ds = ds.sel(latitude=slice(max(AU_LATRANGE),min(AU_LATRANGE)))
    ds = ds.sel(longitude=slice(min(AU_LONRANGE),max(AU_LONRANGE)))
    
    # calculate FFDI_F, FFDI, DWI_V
    ds = calc_ffdi(ds,d2m='d2m',t2m='t2m',u10='u10',v10='v10')
    ds = calc_ffdi_replacements(ds ,d2m='d2m',t2m='t2m',u10='u10',v10='v10')

    #print(ds)
    # Calculate monthly maximum fire metrics, and the contributing components
    monthlies.append(calc_monthly_components(ds,'FFDI',['t2m','s10']))
    monthlies.append(calc_monthly_components(ds,'FFDI_F',['t2m','s10','d2m']))
    monthlies.append(calc_monthly_components(ds,'DWI_V',['t2m','s10','d2m']))
    
    # combine into single dataset
    DS_monthlies = xr.combine_by_coords(monthlies)

    # Update timestamps
    mid_month_stamp = pd.date_range(start='%d-01-01'%year,periods=12,freq='MS')+timedelta(days=14)
    DS_monthlies = DS_monthlies.assign_coords({"time": mid_month_stamp})
    
    # Save these monthly maximums to a file
    os.makedirs(ERA5_monthly_max_folder,exist_ok=True)
    print("INFO: Saving file %s"%fname)
    DS_monthlies.to_netcdf(fname,mode='w')
    #return DS_monthlies
    

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
    if 'lat' in ds.coords:
        ds = ds.where(ds.lat < latrange[1],drop=True)
        ds = ds.where(ds.lat > latrange[0],drop=True)
        ds = ds.where(ds.lon > lonrange[0],drop=True)
        ds = ds.where(ds.lon < lonrange[1],drop=True)
    else:
        ds = ds.where(ds.latitude < latrange[1],drop=True)
        ds = ds.where(ds.latitude > latrange[0],drop=True)
        ds = ds.where(ds.longitude > lonrange[0],drop=True)
        ds = ds.where(ds.longitude < lonrange[1],drop=True)
    return ds
