#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 15:40:31 2022

@author: kmayer

Plot winter (NDJFM) 2m temperature variance 
for SSP & SAI and plot the difference (SSP-SAI)

"""
import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.colors as c
from cartopy import config
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from shapely.geometry.polygon import LinearRing

import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
plt.rc('text',usetex=True) 
plt.rcParams['font.family']='sans-serif'
plt.rcParams['font.sans-serif']=['Verdana']
plt.rcParams.update({'font.size': 15})
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
#%% VARIABLES
DIR = 'data/'
MEMstr = '1-10'

#'swcoast':
lower1_ilat = 122    
upper1_ilat = 139-1
left1_ilon  = 188    
right1_ilon = 201-1
#'nwcoast':
lower2_ilat = 138    
upper2_ilat = 155-1   
left2_ilon  = 188    
right2_ilon = 201-1
#'alaska'
lower3_ilat = 154    
upper3_ilat = 172-1
left3_ilon  = 152    
right3_ilon = 201-1

#%% LOAD
cont = xr.open_dataarray(DIR+'control_ens1-10_T2mvar_detrended_ensmean'+MEMstr+'.nc')
sai = xr.open_dataarray(DIR+'SAI_ens1-10_T2mvar_detrended_ensmean'+MEMstr+'.nc')

# ----- ensemble mean of variance -----
cont_mean = cont.mean('ens',skipna=True)
sai_mean = sai.mean('ens',skipna=True)

# ----- difference of ensemble mean of variance -----
diff = cont_mean - sai_mean

# ----- make region boxes -----
lon = np.asarray(sai.lon)
lat = np.asarray(sai.lat)
    
lons1 = [lon[left1_ilon]-360.0,lon[left1_ilon]-360.0,lon[right1_ilon]-360.0,lon[right1_ilon]-360.0]   
lats1 = [lat[lower1_ilat],lat[upper1_ilat],lat[upper1_ilat],lat[lower1_ilat]]  
ring1 = LinearRing(list(zip(lons1,lats1)))

lons2 = [lon[left2_ilon]-360.0,lon[left2_ilon]-360.0,lon[right2_ilon]-360.0,lon[right2_ilon]-360.0]   
lats2 = [lat[lower2_ilat],lat[upper2_ilat],lat[upper2_ilat],lat[lower2_ilat]]  
ring2 = LinearRing(list(zip(lons2,lats2)))

lons3 = [lon[left3_ilon]-360.0,lon[left3_ilon]-360.0,lon[right3_ilon]-360.0,lon[right3_ilon]-360.0]   
lats3 = [lat[lower3_ilat],lat[upper3_ilat],lat[upper3_ilat],lat[lower3_ilat]]  
ring3 = LinearRing(list(zip(lons3,lats3)))

#%% ------------------- PLOT -------------------------  

fig = plt.figure(figsize=(20,10))
ax = fig.subplot_mosaic('''
                        ABC
                        ''',subplot_kw={'projection':ccrs.PlateCarree(180)})
                        

for loc in ['A','B','C']:   
    ax[loc].coastlines(resolution='50m', color='dimgrey', linewidth=1)
    ax[loc].set_ylim(24,72)
    ax[loc].set_xlim(9.5,72)
    ax[loc].axis("off")
    ax[loc].add_geometries([ring1], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)
    ax[loc].add_geometries([ring2], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)
    ax[loc].add_geometries([ring3], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)

gl = ax['A'].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=.2)
gl.top_labels = False
gl.right_labels = False
gl.ylocator = mticker.FixedLocator([30,40,50,60,70])
gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 20, 'color': 'darkgrey'}
gl.ylabel_style = {'size': 20, 'color': 'darkgrey'}
    
for loc in ['B','C']:
    gl = ax[loc].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=.2)
    gl.top_labels = False
    gl.right_labels = False
    gl.left_labels = False
    gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.xlabel_style = {'size': 20, 'color': 'darkgrey'}
    
    
# ------------------- PLOT -------------------------    
cmap = 'bone_r'
csm=plt.get_cmap(cmap)
norm = c.BoundaryNorm(np.arange(0, 21, 1),csm.N)  

c1 = ax['A'].pcolormesh(cont.lon,cont.lat,cont_mean,cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=20.,norm=norm)
ax['A'].text(x=11,y=25,s='(a) SSP2-4.5',fontsize=30,color='dimgrey')

c2 = ax['B'].pcolormesh(sai.lon,sai.lat,sai_mean,cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=20.,norm=norm)
ax['B'].text(x=11,y=25,s='(b) SAI-1.5',fontsize=30,color='dimgrey')

cax = plt.axes([.125,0.25,0.5,0.03])
cbar = plt.colorbar(c2,cax=cax,orientation = 'horizontal', ticks=np.arange(0,22,2),shrink=0.5, pad=0.1)
cbar.ax.tick_params(size=0,labelsize=25)
cbar.ax.set_xticklabels(np.arange(0,22,2),color='darkgrey')
cbar.ax.set_xlabel('variance',fontsize=30,color='darkgrey')

# ------------------- PLOT DIFF -------------------------    
cmap = 'PuOr_r'
csm=plt.get_cmap(cmap)
norm = c.BoundaryNorm(np.arange(-5, 5.5, .5),csm.N)

c3 = ax['C'].pcolormesh(sai.lon,sai.lat,diff,cmap=csm,transform=ccrs.PlateCarree(),vmin=-5,vmax=5.,norm=norm)
ax['C'].text(x=11,y=25,s='(c) SSP - SAI',fontsize=30.,color='dimgrey')

cax2 = plt.axes([.675,0.25,0.225,0.03])
cbar2 = plt.colorbar(c3,cax=cax2,orientation = 'horizontal',fraction=0.04, ticks=np.arange(-5,7.5,2.5), pad=0.04)
cbar2.ax.tick_params(size=0,labelsize=25)
cbar2.ax.set_xticklabels(np.arange(-5,7.5,2.5),color='darkgrey')
cbar2.ax.set_xlabel('variance difference',fontsize=30,color='darkgrey')

# plt.show()

plt.savefig('figures/Figure2.png',bbox_inches='tight',dpi=300)
