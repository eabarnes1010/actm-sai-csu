"""Metrics for generic plotting.

Functions
---------
plot_metrics(history,metric)
plot_metrics_panels(history, settings)
plot_map(x, clim=None, title=None, text=None, cmap='RdGy')
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy as ct
import numpy.ma as ma
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import palettable
from matplotlib.colors import ListedColormap

mpl.rcParams["figure.facecolor"] = "white"
mpl.rcParams["figure.dpi"] = 150

def savefig(filename,dpi=300):
    for fig_format in (".png",".pdf"):
        plt.savefig(filename + fig_format, 
                    bbox_inches="tight",
                    dpi=dpi)

def get_qual_cmap():
    cmap = palettable.colorbrewer.qualitative.Accent_7.mpl_colormap
    cmap = ListedColormap(cmap(np.linspace(0,1,11)))
    cmap2 = cmap.colors
    cmap2[6,:] = cmap.colors[0,:]
    cmap2[2:6,:] = cmap.colors[5:1:-1,:]
    cmap2[1,:] = (.95,.95,.95,1)
    cmap2[0,:] = (1,1,1,1)
    cmap2[5,:] = cmap2[6,:]
    cmap2[6,:] = [0.7945098 , 0.49647059, 0.77019608, 1.]
    cmap2 = np.append(cmap2,[[.2,.2,.2,1]],axis=0)
    cmap2 = np.delete(cmap2, 0, 0)
    
    return ListedColormap(cmap2)   
        
    
def drawOnGlobe(ax, map_proj, data, lats, lons, cmap='coolwarm', vmin=None, vmax=None, inc=None, cbarBool=True, contourMap=[], contourVals = [], fastBool=False, extent='both'):

    data_crs = ct.crs.PlateCarree()
    data_cyc, lons_cyc = add_cyclic_point(data, coord=lons) #fixes white line by adding point#data,lons#ct.util.add_cyclic_point(data, coord=lons) #fixes white line by adding point
    data_cyc = data
    lons_cyc = lons
    
    
#     ax.set_global()
#     ax.coastlines(linewidth = 1.2, color='black')
#     ax.add_feature(cartopy.feature.LAND, zorder=0, scale = '50m', edgecolor='black', facecolor='black')    

    # ADD COASTLINES
    land_feature = cfeature.NaturalEarthFeature(
        category='physical',
        name='land',
        scale='50m',
        facecolor='None',
        edgecolor = 'k',
        linewidth=.5,
    )
    ax.add_feature(land_feature)
    
    # ADD COUNTRIES
    country_feature = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_0_countries',
        scale='50m',
        facecolor='None',
        edgecolor = 'k',
        linewidth=.25,
        alpha=.25,
    )
    ax.add_feature(country_feature)
    
    
    
#     ax.GeoAxes.patch.set_facecolor('black')
    
    if(fastBool):
        image = ax.pcolormesh(lons_cyc, lats, data_cyc, transform=data_crs, cmap=cmap)
#         image = ax.contourf(lons_cyc, lats, data_cyc, np.linspace(0,vmax,20),transform=data_crs, cmap=cmap)
    else:
        image = ax.pcolor(lons_cyc, lats, data_cyc, transform=data_crs, cmap=cmap,shading='auto')
    
    if(np.size(contourMap) !=0 ):
        contourMap_cyc, __ = add_cyclic_point(contourMap, coord=lons) #fixes white line by adding point
        ax.contour(lons_cyc,lats,contourMap_cyc,contourVals, transform=data_crs, colors='fuchsia')
    
    if(cbarBool):
        cb = plt.colorbar(image, shrink=.45, orientation="horizontal", pad=.02, extend=extent)
        cb.ax.tick_params(labelsize=6) 
    else:
        cb = None

    image.set_clim(vmin,vmax)
    
    return cb, image   

def add_cyclic_point(data, coord=None, axis=-1):

    # had issues with cartopy finding utils so copied for myself
    
    if coord is not None:
        if coord.ndim != 1:
            raise ValueError('The coordinate must be 1-dimensional.')
        if len(coord) != data.shape[axis]:
            raise ValueError('The length of the coordinate does not match '
                             'the size of the corresponding dimension of '
                             'the data array: len(coord) = {}, '
                             'data.shape[{}] = {}.'.format(
                                 len(coord), axis, data.shape[axis]))
        delta_coord = np.diff(coord)
        if not np.allclose(delta_coord, delta_coord[0]):
            raise ValueError('The coordinate must be equally spaced.')
        new_coord = ma.concatenate((coord, coord[-1:] + delta_coord[0]))
    slicer = [slice(None)] * data.ndim
    try:
        slicer[axis] = slice(0, 1)
    except IndexError:
        raise ValueError('The specified axis does not correspond to an '
                         'array dimension.')
    new_data = ma.concatenate((data, data[tuple(slicer)]), axis=axis)
    if coord is None:
        return_value = new_data
    else:
        return_value = new_data, new_coord
    return return_value    

def adjust_spines(ax, spines):
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', 5))
        else:
            spine.set_color('none')  
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        ax.yaxis.set_ticks([])
    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
        ax.xaxis.set_ticks([]) 

def format_spines(ax):
    adjust_spines(ax, ['left', 'bottom'])
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('dimgrey')
    ax.spines['bottom'].set_color('dimgrey')
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    ax.tick_params('both',length=4,width=2,which='major',color='dimgrey')
#     ax.yaxis.grid(zorder=1,color='dimgrey',alpha=0.35)   