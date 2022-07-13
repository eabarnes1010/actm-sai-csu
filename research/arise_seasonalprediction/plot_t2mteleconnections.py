#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 26 12:51:40 2022

@author: kmayer

Plot map of the frequency of a positive anomaly following el nino/la nina

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

nino_cont = xr.open_dataarray(DIR+'control_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_cont = xr.open_dataarray(DIR+'control_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')

nino_sai = xr.open_dataarray(DIR+'SAI_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_sai = xr.open_dataarray(DIR+'SAI_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc') 

# ---- ensemble mean of freq of positive sign anomaly ----
nino_cont_mean = nino_cont.mean('ens',skipna=True)
nina_cont_mean = nina_cont.mean('ens',skipna=True)

nino_sai_mean = nino_sai.mean('ens',skipna=True)
nina_sai_mean = nina_sai.mean('ens',skipna=True)

# ---- load bootrapping data & calculate significance bounds ----
nino_diff_boot = xr.open_dataarray(DIR+'bootstrapping/bootdiff_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_diff_boot = xr.open_dataarray(DIR+'bootstrapping/bootdiff_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')

nino_sigup = np.percentile(nino_diff_boot,q=95,axis=0)
nino_siglow = np.percentile(nino_diff_boot,q=5,axis=0)

nina_sigup = np.percentile(nina_diff_boot,q=95,axis=0)
nina_siglow = np.percentile(nina_diff_boot,q=5,axis=0)

# ---- calculate differences & find significant locations for plotting
ninadiff = nina_cont_mean - nina_sai_mean
ninadiff_sig = ninadiff.where((ninadiff > nina_sigup) | (ninadiff < nina_siglow))

ninodiff = nino_cont_mean - nino_sai_mean
ninodiff_sig = ninodiff.where((ninodiff > nino_sigup) | (ninodiff < nino_siglow))

# ---- make regional boxes ----
lon = np.asarray(nino_sai.lon)
lat = np.asarray(nino_sai.lat)
    
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

fig = plt.figure(figsize=(20,11))
ax = fig.subplot_mosaic('''
                        ABC
                        DEF
                        ''',subplot_kw={'projection':ccrs.PlateCarree(180)})
                        
for loc in ['A','B','C','D','E','F']:   
    ax[loc].coastlines(resolution='50m', color='dimgrey', linewidth=1)
    ax[loc].set_ylim(24,72)
    ax[loc].set_xlim(9.5,72)
    ax[loc].axis("off")
    
    ax[loc].add_geometries([ring1], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)
    ax[loc].add_geometries([ring2], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)
    ax[loc].add_geometries([ring3], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)
    
for loc in ['A','D']:    
  gl = ax[loc].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=.2)
  gl.top_labels = False
  gl.right_labels = False
  if loc == 'A':
      gl.bottom_labels = False
  else:
      gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
      gl.xformatter = LONGITUDE_FORMATTER
      gl.xlabel_style = {'size': 25, 'color': 'darkgrey'}
  gl.ylocator = mticker.FixedLocator([30,40,50,60,70])
  gl.yformatter = LATITUDE_FORMATTER
  gl.ylabel_style = {'size': 25, 'color': 'darkgrey'}

for loc in ['B','C']:
   gl = ax[loc].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=.2)
   gl.top_labels = False
   gl.bottom_labels = False
   gl.right_labels = False
   gl.left_labels = False

for loc in ['E','F']:   
  gl = ax[loc].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=.2)
  gl.top_labels = False
  gl.right_labels = False
  gl.left_labels = False
  gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
  gl.xformatter = LONGITUDE_FORMATTER
  gl.xlabel_style = {'size': 25, 'color': 'darkgrey'}
    
# ------------------- PLOT LA NINA -------------------------    
cmap = 'RdBu_r'
csm=plt.get_cmap(cmap)
norm = c.BoundaryNorm(np.arange(0, 1.05, .05),csm.N)  

c1 = ax['A'].pcolormesh(nina_cont.lon,nina_cont.lat,nina_cont_mean,cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['A'].text(x=11,y=25,s='(a) SSP2-4.5',fontsize=30,color='dimgrey')
ax['A'].set_title('LA NINA',fontsize=40,color='dimgrey',loc='left')

c2 = ax['B'].pcolormesh(nina_sai.lon,nina_sai.lat,nina_sai_mean,cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['B'].text(x=11,y=25,s='(b) SAI-1.5',fontsize=30,color='dimgrey')

# ------------------- PLOT LA NINA DIFF -------------------------    
cmap = 'PuOr_r'
csm=plt.get_cmap(cmap)
norm = c.BoundaryNorm(np.arange(-.5, .55, .05),csm.N)

c3 = ax['C'].pcolormesh(nina_sai.lon,nina_sai.lat,ninadiff,cmap=csm,transform=ccrs.PlateCarree(),vmin=-1,vmax=1.,norm=norm)
ax['C'].text(x=11,y=25,s='(c) SSP - SAI',fontsize=30.,color='dimgrey')

ax['C'].pcolor(ninadiff_sig.lon,ninadiff_sig.lat,ninadiff_sig,hatch='/',alpha=0,linewidth=10,transform=ccrs.PlateCarree())

#------------------------------------------------------------------------------------------

# ------------------- PLOT EL NINO -------------------------
cmap = 'RdBu_r'
csm=plt.get_cmap(cmap)
norm = c.BoundaryNorm(np.arange(0, 1.05, .05),csm.N) 
 
c3 = ax['D'].pcolormesh(nino_cont.lon,nino_cont.lat,nino_cont_mean,cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['D'].text(x=11,y=25,s='(d) SSP2-4.5',fontsize=30,color='dimgrey')
ax['D'].set_title('EL NINO',fontsize=40,color='dimgrey',loc='left')

c5 = ax['E'].pcolormesh(nino_sai.lon,nino_sai.lat,nino_sai_mean,cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['E'].text(x=11,y=25,s='(e) SAI-1.5',fontsize=30,color='dimgrey')

cax = plt.axes([.125,0.05,0.5,0.03])
cbar = plt.colorbar(c5,cax=cax,orientation = 'horizontal', ticks=np.arange(0,1.25,.25),shrink=0.5, pad=0.1)
cbar.ax.tick_params(size=0,labelsize=28)
cbar.ax.set_xticklabels(np.arange(0,1.25,.25),color='darkgrey')
cbar.ax.set_xlabel('frequency (of positive sign)',fontsize=30,color='darkgrey')

# ------------------- PLOT EL NINO DIFF -------------------------   
cmap = 'PuOr_r'
csm=plt.get_cmap(cmap)
norm = c.BoundaryNorm(np.arange(-.5, .55, .05),csm.N)

c6 = ax['F'].pcolormesh(nino_sai.lon,nino_sai.lat,ninodiff,cmap=csm,transform=ccrs.PlateCarree(),vmin=-.5,vmax=.5,norm=norm)
ax['F'].text(x=11,y=25,s='(f) SSP - SAI',fontsize=30,color='dimgrey')

ax['F'].pcolor(ninodiff_sig.lon,ninodiff_sig.lat,ninodiff_sig,hatch='/',alpha=0,linewidth=10,transform=ccrs.PlateCarree())

cax2 = plt.axes([.675,0.05,0.225,0.03])
cbar2 = plt.colorbar(c6,cax=cax2,orientation = 'horizontal',fraction=0.04, ticks=np.arange(-.5,.75,.25), pad=0.04)
cbar2.ax.tick_params(size=0,labelsize=28)
cbar2.ax.set_xticklabels(np.arange(-.5,0.75,.25),color='darkgrey')
cbar2.ax.set_xlabel('frequency difference',fontsize=30,color='darkgrey')

# plt.show()

plt.savefig('figures/Figure3.png',bbox_inches='tight',dpi=300)
