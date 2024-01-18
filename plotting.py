import numpy as np
from datetime import datetime

## plotting modules
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib as mpl

# cartopy mapping
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point

#import iris
import iris.plot as iplt
import iris.quickplot as qplt

import warnings

# WESN
AUS_EXTENT=[120,150,-45,-12]

FFDI_cmap = (mpl.colors.ListedColormap(['yellow', 'orange','red']).with_extremes(over='purple', under='green'))
FFDI_cbounds = [25,50,75,100]
FFDI_cnorm = mpl.colors.BoundaryNorm(FFDI_cbounds, FFDI_cmap.N)


def add_coastlines(plot):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=DeprecationWarning)
        if hasattr(plot.axes,'flat'):
            for ax in plot.axes.flat:
                ax.coastlines()
        else:
            plot.axes.coastlines()

def plot_diff_quick(da_A,da_B,itimes=[0]):
    A = da_A.isel(time=itimes)
    B = da_B.isel(time=itimes)
    
    for da in [A,B,A-B]:
        p=da.plot(
            col='time',
            subplot_kws=dict(
                projection=ccrs.Orthographic(140, -10), # center somewhat australianly
                facecolor="gray"),
            transform=ccrs.PlateCarree(),
        )
        #p.axes.set_global()
        #p.axes.coastlines()
        add_coastlines(p)
        plt.suptitle(da.name)
        if da.name is None:
            plt.suptitle('A-B')
    plt.show()

def plot_ffdi(da, itimes=[0], lon0=140, lat0=-20):
    """
    like plot_quick, but with a specific colorbar
    green to 25, yellow to 50, orange to 75, red to 100, purple beyond
    """
    args = {}
    if len(itimes) > 1:
        args={'col':'time'}
    # FFDI stuff
    args['cmap']=FFDI_cmap
    args['norm']=FFDI_cnorm
    args['extend']='both'
    
    p=da.isel(time=itimes).plot(
        subplot_kws=dict(
            projection=ccrs.Orthographic(lon0, lat0), # center somewhat australianly
            facecolor="gray",
        ),
        transform=ccrs.PlateCarree(),
        **args,
    )
    add_coastlines(p)

def plot_quick(da, itimes=[0], lon0=140, lat0=-15):

    args = {}
    if len(itimes) > 1:
        args={'col':'time'}
    
    da0 = da
    if hasattr(da,'time'):
        da0 = da.isel(time=itimes)
        
    p=da0.plot(
        subplot_kws=dict(
            projection=ccrs.Orthographic(lon0, lat0), # center somewhat australianly
            facecolor="gray"),
        transform=ccrs.PlateCarree(),
        **args,
    )
    add_coastlines(p)


def plot_winds(ds, 
               u='u10',v='v10',
               vmax=None, # default to 90th percentile of windspeed
               itimes=[0],
               **kwargs):
    
    # create axis with subplot a project
    crs_latlon = ccrs.PlateCarree(central_longitude=140)
    for i in range(len(itimes)):
        fig = plt.figure()
        dsi = ds.isel(time=itimes[i])

        # set up plot and underlying coordinate system
        ax = fig.add_subplot(1, 1, 1, projection=crs_latlon)
        ax.coastlines()
        
        # plot windspeeds
        lat=dsi.latitude
        s = (dsi[u]**2+dsi[v]**2)**.5
        field, lon = add_cyclic_point(s, coord=dsi.longitude)

        if vmax is None:
            vmax = s.quantile(0.95) # get 95th percentile as vmax
        sweet_levels = np.arange(0, vmax, 1)
        
        cf = ax.contourf(lon, lat, field, 
                         levels=sweet_levels,
                         cmap='RdYlBu_r',
                         extend='max',
                         transform=ccrs.PlateCarree())
        
        # plot velocity field
        uvel, lonu = add_cyclic_point(dsi[u], coord=dsi.longitude)
        vvel, lonv = add_cyclic_point(dsi[v], coord=dsi.longitude)
        lonu = np.where(lonu>=180.,lonu-360.,lonu)
        
        sp = ax.streamplot(lonu, lat, uvel, vvel,
                           linewidth = 0.2,
                           arrowsize = 0.2,
                           density = 5,
                           color = 'k',
                           transform = ccrs.PlateCarree())
        plt.title(dsi.time.values)
        # add colorbar
        cb = plt.colorbar(cf,orientation='horizontal', pad=0.04, aspect=50)
        cb.ax.set_title('winds [%s]'%dsi[u].attrs['units']);
        
    