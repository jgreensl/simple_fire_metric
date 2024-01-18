import fio

import os

fname = '/scratch/en0/jwg574/ERA5/Aus_FFDI.nc'
if os.path.isfile(fname):
    print(fname, " Already exists")
    exit(0)

omg_large_ds = fio.ERA5_read_long( ['u10','v10','d2m','t2m'])

latrange=[-48,-9]
lonrange=[111,155]
## subset just AUS:
omg_large_ds = omg_large_ds.sel(latitude=slice(max(latrange),min(latrange)))
omg_large_ds = omg_large_ds.sel(longitude=slice(min(lonrange),max(lonrange)))


## Save ERA5_Aus?
omg_large_ds.to_netcdf(fname)



