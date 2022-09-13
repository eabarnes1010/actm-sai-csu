#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 14:45:07 2022

@author: Ariel L. Morrison
"""
import os
figureDir = '/Users/arielmor/Desktop/SAI/data/ARISE/figures/'
os.chdir('/Users/arielmor/Projects/actm-sai-csu/research/arise_arctic_climate')

def get_colormap(levs):
    from matplotlib import cm
    from matplotlib.colors import ListedColormap
    import numpy as np
    #########################################################
    # create discrete colormaps from existing continuous maps
    # first make default discrete blue-red colormap 
    # replace center colors with white at 0
    #########################################################
    ## brown-blue
    brbg = cm.get_cmap('BrBG', (levs+3))
    newcolors = brbg(np.linspace(0, 1, 256))
    newcolors[120:136, :] = np.array([1, 1, 1, 1])
    brbg_cmap = ListedColormap(newcolors)
    ## blue-red
    bwr = cm.get_cmap('RdBu_r', (levs+3))
    newcolors = bwr(np.linspace(0, 1, 256))
    newcolors[120:136, :] = np.array([1, 1, 1, 1])
    rdbu_cmap = ListedColormap(newcolors)
    ## rainbow
    jet = cm.get_cmap('turbo', (levs))
    magma = cm.get_cmap('magma', (levs))
    return brbg_cmap,rdbu_cmap,jet,magma


def make_maps(var,latitude,longitude,vmins,vmaxs,levs,mycmap,label,title,savetitle):
    import cartopy.crs as ccrs
    from cartopy.util import add_cyclic_point
    import matplotlib.pyplot as plt
    import matplotlib.path as mpath
    import matplotlib.colors as mcolors
    import numpy as np
    #########################################################
    # make single North Pole stereographic filled contour map
    #########################################################
    ## Add cyclic point
    var,lon = add_cyclic_point(var,coord=longitude)
    ## Create figure
    fig = plt.figure(figsize=(10,6))
    if vmins < 0. and vmins > 0.:
        norm = mcolors.TwoSlopeNorm(vmin=vmins, vcenter=0, vmax=vmaxs)
    else:
        norm = mcolors.Normalize(vmin=vmins, vmax=vmaxs)
    ## Create North Pole Stereo projection map with circle boundary
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.NorthPolarStereo())
    ax.set_extent([180, -180, 45, 90], crs=ccrs.PlateCarree())
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)
    ax.set_facecolor('0.94')
    ## Filled contour map
    cf1 = ax.pcolormesh(lon,latitude,var,transform=ccrs.PlateCarree(), 
                  norm=norm, cmap=mycmap)
    ax.coastlines(linewidth=0.8)
    if vmins < 0.:
        cbar = plt.colorbar(cf1, ax=ax, extend="both")
    else:
        cbar = plt.colorbar(cf1, ax=ax, extend="max")
    cbar.set_label(str(label), fontsize=10)
    plt.title(str(title), fontsize=11)
    ## Save figure
    plt.savefig(figureDir + str(savetitle) + '.jpg', dpi=950, bbox_inches='tight')
    return fig, ax
    
    