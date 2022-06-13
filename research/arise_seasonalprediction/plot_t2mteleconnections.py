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
upper3_ilat = 171    
left3_ilon  = 152    
right3_ilon = 201-1

#%% LOAD
nino_base = xr.open_dataarray(DIR+'base_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_base = xr.open_dataarray(DIR+'base_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')

nino_cont = xr.open_dataarray(DIR+'control_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_cont = xr.open_dataarray(DIR+'control_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')

nino_sai = xr.open_dataarray(DIR+'SAI_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_sai = xr.open_dataarray(DIR+'SAI_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc') 
   

#grab lats & lons to make boxes around the 3 regions
lon = np.asarray(nino_base.lon)
lat = np.asarray(nino_base.lat)
    
lons1 = [lon[left1_ilon]-360.0,lon[left1_ilon]-360.0,lon[right1_ilon]-360.0,lon[right1_ilon]-360.0]   
lats1 = [lat[lower1_ilat],lat[upper1_ilat],lat[upper1_ilat],lat[lower1_ilat]]  
ring1 = LinearRing(list(zip(lons1,lats1)))

lons2 = [lon[left2_ilon]-360.0,lon[left2_ilon]-360.0,lon[right2_ilon]-360.0,lon[right2_ilon]-360.0]   
lats2 = [lat[lower2_ilat],lat[upper2_ilat],lat[upper2_ilat],lat[lower2_ilat]]  
ring2 = LinearRing(list(zip(lons2,lats2)))

lons3 = [lon[left3_ilon]-360.0,lon[left3_ilon]-360.0,lon[right3_ilon]-360.0,lon[right3_ilon]-360.0]   
lats3 = [lat[lower3_ilat],lat[upper3_ilat],lat[upper3_ilat],lat[lower3_ilat]]  
ring3 = LinearRing(list(zip(lons3,lats3)))

#%% ------------------- PLOT map of frequency of positive sign T2m anomaly following ENSO -------------------------
cmap = 'RdBu_r'
csm=plt.get_cmap(cmap)
norm = c.BoundaryNorm(np.arange(0, 1.05, .05),csm.N)

fig = plt.figure(figsize=(10,15))
ax = fig.subplot_mosaic('''
                        A
                        B
                        C
                        ''',subplot_kw={'projection':ccrs.PlateCarree(180)})
                        
for loc in ['A','B','C']:   
    ax[loc].coastlines(resolution='50m', color='dimgrey', linewidth=1)
    ax[loc].set_ylim(24,72)
    ax[loc].set_xlim(9.5,125)
    ax[loc].axis("off")
    gl = ax[loc].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=0)
    gl.top_labels = False
    gl.right_labels = False
    gl.ylocator = mticker.FixedLocator([30,40,50,60,70])
    gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 20, 'color': 'darkgrey'}
    gl.ylabel_style = {'size': 20, 'color': 'darkgrey'}
    ax[loc].add_geometries([ring1], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    ax[loc].add_geometries([ring2], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    ax[loc].add_geometries([ring3], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    
    
c1 = ax['A'].pcolormesh(nino_base.lon,nino_base.lat,nino_base[0],cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['A'].text(x=11,y=25,s='BASE',fontsize=30,color='dimgrey')

c2 = ax['B'].pcolormesh(nino_sai.lon,nino_sai.lat,nino_sai[0],cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['B'].text(x=11,y=25,s='SAI-1.5',fontsize=30,color='dimgrey')

c3 = ax['C'].pcolormesh(nino_cont.lon,nino_cont.lat,nino_cont[0],cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['C'].text(x=11,y=25,s='SSP2-4.5',fontsize=30,color='dimgrey')

cax = plt.axes([0.125,0.07,0.775,0.015])
cbar = plt.colorbar(c3,cax=cax,orientation = 'horizontal', ticks=np.arange(0,1.25,.25),shrink=0.75)
cbar.ax.tick_params(size=0,labelsize=22)
cbar.ax.set_xticklabels(np.arange(0,1.25,.25),color='darkgrey')
cbar.ax.set_xlabel('$<$ Negative $|$ Positive $>$',fontsize=22,color='dimgrey')

# plt.show()
DIR_FIGSAVE = 'figures/'
plt.savefig(DIR_FIGSAVE+'posfreq_ElNino_testmember10.png',bbox_inches='tight',dpi=300)

   
# ------------------- PLOT LA NINA -------------------------      
fig = plt.figure(figsize=(10,15))#,constrained_layout=True)  
ax = fig.subplot_mosaic('''
                        A
                        B
                        C
                        ''',subplot_kw={'projection':ccrs.PlateCarree(180)})
                        
for loc in ['A','B','C']:
    ax[loc].coastlines(resolution='50m', color='dimgrey', linewidth=1)
    ax[loc].set_ylim(24,72)
    ax[loc].set_xlim(9.5,125)
    ax[loc].axis("off")
    gl = ax[loc].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=0)
    gl.top_labels = False
    gl.right_labels = False
    gl.ylocator = mticker.FixedLocator([30,40,50,60,70])
    gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 20, 'color': 'darkgrey'}
    gl.ylabel_style = {'size': 20, 'color': 'darkgrey'}
    ax[loc].add_geometries([ring1], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    ax[loc].add_geometries([ring2], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    ax[loc].add_geometries([ring3], ccrs.PlateCarree(), facecolor='none', edgecolor='k')


c1 = ax['A'].pcolormesh(nina_base.lon,nina_base.lat,nina_base[0],cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['A'].text(x=11,y=25,s='BASE',fontsize=30,color='dimgrey')

c2 = ax['B'].pcolormesh(nina_sai.lon,nina_sai.lat,nina_sai[0],cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['B'].text(x=11,y=25,s='SAI-1.5',fontsize=30,color='dimgrey')

c3 = ax['C'].pcolormesh(nina_cont.lon,nina_cont.lat,nina_cont[0],cmap=csm,transform=ccrs.PlateCarree(),vmin=0,vmax=1.,norm=norm)
ax['C'].text(x=11,y=25,s='SSP2-4.5',fontsize=30,color='dimgrey')

cax = plt.axes([0.125,0.07,0.775,0.015])
cbar = plt.colorbar(c3,cax=cax,orientation = 'horizontal', ticks=np.arange(0,1.25,.25),shrink=0.75)
cbar.ax.tick_params(size=0,labelsize=22)
cbar.ax.set_xticklabels(np.arange(0,1.25,.25),color='darkgrey')
cbar.ax.set_xlabel('$<$ Negative $|$ Positive $>$',fontsize=22,color='dimgrey')

# plt.show()

DIR_FIGSAVE = 'figures/'
plt.savefig(DIR_FIGSAVE+'posfreq_LaNina_testmember10.png',bbox_inches='tight',dpi=300)
    

#%% Plot the difference between SAI - BASE, SSP - BASE & SSP - SAI
cmap = 'RdBu_r'
csm=plt.get_cmap(cmap)
norm = c.BoundaryNorm(np.arange(-.5, .55, .05),csm.N)

# ------------------- PLOT EL NINO -------------------------
diff1 = nino_cont[0] - nino_sai[0]
diff2 = nino_sai[0] - nino_base[0]
diff3 = nino_cont[0] - nino_base[0]

fig = plt.figure(figsize=(10,15))
ax = fig.subplot_mosaic('''
                        A
                        B
                        C
                        ''',subplot_kw={'projection':ccrs.PlateCarree(180)})
                        
for loc in ['A','B','C']:
    ax[loc].coastlines(resolution='50m', color='dimgrey', linewidth=1)
    ax[loc].set_ylim(24,72)
    ax[loc].set_xlim(9.5,125)
    ax[loc].axis("off")
    gl = ax[loc].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=0)
    gl.top_labels = False
    gl.right_labels = False
    gl.ylocator = mticker.FixedLocator([30,40,50,60,70])
    gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 20, 'color': 'darkgrey'}
    gl.ylabel_style = {'size': 20, 'color': 'darkgrey'}
    ax[loc].add_geometries([ring1], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    ax[loc].add_geometries([ring2], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    ax[loc].add_geometries([ring3], ccrs.PlateCarree(), facecolor='none', edgecolor='k')


c1 = ax['A'].pcolormesh(nino_base.lon,nino_base.lat,diff1,cmap=csm,transform=ccrs.PlateCarree(),vmin=-.5,vmax=.5,norm=norm)
ax['A'].text(x=11,y=25,s='SSP2-4.5 - SAI-1.5',fontsize=25,color='dimgrey')
c2 = ax['B'].pcolormesh(nino_base.lon,nino_base.lat,diff2,cmap=csm,transform=ccrs.PlateCarree(),vmin=-.5,vmax=.5,norm=norm)
ax['B'].text(x=11,y=25,s='SAI-1.5 - BASE',fontsize=25,color='dimgrey')
c3 = ax['C'].pcolormesh(nino_base.lon,nino_base.lat,diff3,cmap=csm,transform=ccrs.PlateCarree(),vmin=-.5,vmax=.5,norm=norm)
ax['C'].text(x=11,y=25,s='SSP2-4.5 - BASE',fontsize=25,color='dimgrey')


cax = plt.axes([0.125,0.07,0.775,0.015])
cbar = plt.colorbar(c3,cax=cax,orientation = 'horizontal',fraction=0.04, ticks=np.arange(-.5,.75,.25), pad=0.07)
cbar.ax.tick_params(size=0,labelsize=20)
cbar.ax.set_xticklabels(np.arange(-.5,0.75,.25),color='darkgrey')
cbar.ax.set_xlabel('Frequency of Positive Sign: Difference',fontsize=22,color='dimgrey')


# plt.show()
DIR_FIGSAVE = 'figures/'
plt.savefig(DIR_FIGSAVE+'posfreqdiff_ElNino_testmember10.png',bbox_inches='tight',dpi=300)

# ------------------- PLOT LA NINA -------------------------      
diff1 = nina_cont[0] - nina_sai[0]
diff2 = nina_sai[0] - nina_base[0]
diff3 = nina_cont[0] - nina_base[0]

fig = plt.figure(figsize=(10,15))#,constrained_layout=True)
ax = fig.subplot_mosaic('''
                        A
                        B
                        C
                        ''',subplot_kw={'projection':ccrs.PlateCarree(180)})
                        
for loc in ['A','B','C']:
    ax[loc].coastlines(resolution='50m', color='dimgrey', linewidth=1)
    ax[loc].set_ylim(24,72)
    ax[loc].set_xlim(9.5,125)
    ax[loc].axis("off")
    gl = ax[loc].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=0)
    gl.top_labels = False
    gl.right_labels = False
    gl.ylocator = mticker.FixedLocator([30,40,50,60,70])
    gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 20, 'color': 'darkgrey'}
    gl.ylabel_style = {'size': 20, 'color': 'darkgrey'}
    ax[loc].add_geometries([ring1], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    ax[loc].add_geometries([ring2], ccrs.PlateCarree(), facecolor='none', edgecolor='k')
    ax[loc].add_geometries([ring3], ccrs.PlateCarree(), facecolor='none', edgecolor='k')


c1 = ax['A'].pcolormesh(nina_base.lon,nina_base.lat,diff1,cmap=csm,transform=ccrs.PlateCarree(),vmin=-1,vmax=1.,norm=norm)
ax['A'].text(x=11,y=25,s='SSP2-4.5 - SAI-1.5',fontsize=25,color='dimgrey')
c2 = ax['B'].pcolormesh(nina_base.lon,nina_base.lat,diff2,cmap=csm,transform=ccrs.PlateCarree(),vmin=-1,vmax=1.,norm=norm)
ax['B'].text(x=11,y=25,s='SAI-1.5 - BASE',fontsize=25,color='dimgrey')
c3 = ax['C'].pcolormesh(nina_base.lon,nina_base.lat,diff3,cmap=csm,transform=ccrs.PlateCarree(),vmin=-1,vmax=1.,norm=norm)
ax['C'].text(x=11,y=25,s='SSP2-4.5 - BASE',fontsize=25,color='dimgrey')


cax = plt.axes([0.125,0.07,0.775,0.015])
cbar = plt.colorbar(c3,cax=cax,orientation = 'horizontal',fraction=0.04, ticks=np.arange(-.5,.75,.25), pad=0.07)
cbar.ax.tick_params(size=0,labelsize=20)
cbar.ax.set_xticklabels(np.arange(-.5,.75,.25),color='darkgrey')
cbar.ax.set_xlabel('Frequency of Positive Sign: Difference',fontsize=22,color='dimgrey')


# plt.show()

DIR_FIGSAVE = 'figures/'
plt.savefig(DIR_FIGSAVE+'posfreqdiff_LaNina_testmember10.png',bbox_inches='tight',dpi=300)
