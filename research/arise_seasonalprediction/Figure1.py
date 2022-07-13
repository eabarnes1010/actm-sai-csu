#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 10:41:58 2022

@author: kmayer

Plot global/regional means of T2m and SST
for control and SAI runs
"""
import xarray as xr
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from cartopy import config
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from shapely.geometry.polygon import LinearRing

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

#%%
VAR = 'T2m'
DIR = 'data/'

#%% LOAD var vs time
landmask = xr.open_dataset('data/sftlf_fx_CESM2-WACCM_historical_r1i1p1f1_gn.nc')['sftlf']
landmask = xr.where(landmask>50,x=1,y=np.nan)

for ens in np.arange(1,11):
    
    FINAME = 'control_ens'+str(ens)+'_T2m_2015-2069.nc'
    cont = (xr.open_dataarray(DIR+FINAME) - 273.15)*landmask
    cont_sw = cont[:,122:139,188:201]
    cont_nw = cont[:,138:155,188:201]
    cont_al = cont[:,154:172,152:201]
    
    FINAME = 'SAI_ens'+str(ens)+'_T2m_2015-2069.nc'
    sai = (xr.open_dataarray(DIR+FINAME) - 273.15)*landmask
    sai_sw = sai[:,122:139,188:201]
    sai_nw = sai[:,138:155,188:201]
    sai_al = sai[:,154:172,152:201]
    
    weights = np.cos(np.deg2rad(cont.lat))
    weights.name = 'weights'
    
    # ------------------ CONTROL -----------------------
    cont_wgt = cont.weighted(weights)
    cont_sw_wgt = cont_sw.weighted(weights)
    cont_nw_wgt = cont_nw.weighted(weights)
    cont_al_wgt = cont_al.weighted(weights)
    
    cont_avg1 = cont_wgt.mean(('lat','lon'),skipna=True)
    cont_sw_avg1 = cont_sw_wgt.mean(('lat','lon'),skipna=True)
    cont_nw_avg1 = cont_nw_wgt.mean(('lat','lon'),skipna=True)
    cont_al_avg1 = cont_al_wgt.mean(('lat','lon'),skipna=True)

    cont_avg = cont_avg1.groupby('time.year').mean('time')
    cont_sw_avg = cont_sw_avg1.groupby('time.year').mean('time')
    cont_nw_avg = cont_nw_avg1.groupby('time.year').mean('time')
    cont_al_avg = cont_al_avg1.groupby('time.year').mean('time')
    
    # ------------------ SAI -----------------------
    sai_wgt = sai.weighted(weights)
    sai_sw_wgt = sai_sw.weighted(weights)
    sai_nw_wgt = sai_nw.weighted(weights)
    sai_al_wgt = sai_al.weighted(weights)
    
    sai_avg1 = sai_wgt.mean(('lat','lon'),skipna=True)
    sai_sw_avg1 = sai_sw_wgt.mean(('lat','lon'),skipna=True)
    sai_nw_avg1 = sai_nw_wgt.mean(('lat','lon'),skipna=True)
    sai_al_avg1 = sai_al_wgt.mean(('lat','lon'),skipna=True)

    sai_avg = sai_avg1.groupby('time.year').mean('time')
    sai_sw_avg = sai_sw_avg1.groupby('time.year').mean('time')
    sai_nw_avg = sai_nw_avg1.groupby('time.year').mean('time')
    sai_al_avg = sai_al_avg1.groupby('time.year').mean('time')
    
    
    # ------------------ COMBINE -----------------------
    if ens == 1:
        cont_all_gl = xr.DataArray(np.zeros(shape=(10,55),dtype='float'),
                                name=VAR,
                                dims=('ens','time'),
                                coords=[('ens',np.arange(1,11)),('time',cont_avg.year)])
        cont_all_sw = xr.DataArray(np.zeros(shape=(10,55),dtype='float'),
                                name=VAR,
                                dims=('ens','time'),
                                coords=[('ens',np.arange(1,11)),('time',cont_avg.year)])
        cont_all_nw = xr.DataArray(np.zeros(shape=(10,55),dtype='float'),
                                name=VAR,
                                dims=('ens','time'),
                                coords=[('ens',np.arange(1,11)),('time',cont_avg.year)])
        cont_all_al = xr.DataArray(np.zeros(shape=(10,55),dtype='float'),
                                name=VAR,
                                dims=('ens','time'),
                                coords=[('ens',np.arange(1,11)),('time',cont_avg.year)])
        #----------------------------------------------------------------------
        sai_all_gl = xr.DataArray(np.zeros(shape=(10,55),dtype='float'),
                                name=VAR,
                                dims=('ens','time'),
                                coords=[('ens',np.arange(1,11)),('time',sai_avg.year)])
        sai_all_sw = xr.DataArray(np.zeros(shape=(10,55),dtype='float'),
                                name=VAR,
                                dims=('ens','time'),
                                coords=[('ens',np.arange(1,11)),('time',sai_avg.year)])
        sai_all_nw = xr.DataArray(np.zeros(shape=(10,55),dtype='float'),
                                name=VAR,
                                dims=('ens','time'),
                                coords=[('ens',np.arange(1,11)),('time',sai_avg.year)])
        sai_all_al = xr.DataArray(np.zeros(shape=(10,55),dtype='float'),
                                name=VAR,
                                dims=('ens','time'),
                                coords=[('ens',np.arange(1,11)),('time',sai_avg.year)])
    
    cont_all_gl[ens-1,:] = cont_avg
    cont_all_sw[ens-1,:] = cont_sw_avg
    cont_all_nw[ens-1,:] = cont_nw_avg
    cont_all_al[ens-1,:] = cont_al_avg
    
    sai_all_gl[ens-1,:] = sai_avg
    sai_all_sw[ens-1,:] = sai_sw_avg
    sai_all_nw[ens-1,:] = sai_nw_avg
    sai_all_al[ens-1,:] = sai_al_avg

#%% LOAD MAP INFO
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

lon = np.asarray(cont.lon)
lat = np.asarray(cont.lat)
    
lons1 = [lon[left1_ilon]-360.0,lon[left1_ilon]-360.0,lon[right1_ilon]-360.0,lon[right1_ilon]-360.0]   
lats1 = [lat[lower1_ilat],lat[upper1_ilat],lat[upper1_ilat],lat[lower1_ilat]]  
ring1 = LinearRing(list(zip(lons1,lats1)))

lons2 = [lon[left2_ilon]-360.0,lon[left2_ilon]-360.0,lon[right2_ilon]-360.0,lon[right2_ilon]-360.0]   
lats2 = [lat[lower2_ilat],lat[upper2_ilat],lat[upper2_ilat],lat[lower2_ilat]]  
ring2 = LinearRing(list(zip(lons2,lats2)))

lons3 = [lon[left3_ilon]-360.0,lon[left3_ilon]-360.0,lon[right3_ilon]-360.0,lon[right3_ilon]-360.0]   
lats3 = [lat[lower3_ilat],lat[upper3_ilat],lat[upper3_ilat],lat[lower3_ilat]]  
ring3 = LinearRing(list(zip(lons3,lats3)))


#%% 2M TEMPERATURE PLOT
gs_kw = dict(width_ratios=[1, 1], height_ratios=[1, 1])

fig = plt.figure(figsize=(17,12),constrained_layout=False)
ax = fig.subplot_mosaic('''
                        AA
                        BC
                        ''', gridspec_kw = gs_kw)  

ax['B'] = plt.subplot(223,aspect=1.2)
ax['C'] = plt.subplot(224, projection = ccrs.PlateCarree(180),aspect=1.)
for loc in ['A','B']:                  
    adjust_spines(ax[loc], ['left', 'bottom'])
    ax[loc].spines['top'].set_color('none')
    ax[loc].spines['right'].set_color('none')
    ax[loc].spines['left'].set_color('dimgrey')
    ax[loc].spines['bottom'].set_color('dimgrey')
    ax[loc].spines['left'].set_linewidth(2)
    ax[loc].spines['bottom'].set_linewidth(2)
    ax[loc].tick_params('both',length=4,width=2,which='major',color='dimgrey')
    ax[loc].yaxis.grid(zorder=1,color='dimgrey',alpha=0.35)

ax['C'].coastlines(resolution='50m', color='dimgrey', linewidth=1)
ax['C'].set_ylim(24,72)
ax['C'].set_xlim(9.5,72)
ax['C'].axis("off")
gl = ax['C'].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=.2)
gl.top_labels = False
gl.right_labels = False
gl.ylocator = mticker.FixedLocator([30,40,50,60,70])
gl.xlocator = mticker.FixedLocator([-160,-140,-120,-100,-80,-60])
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 20, 'color': 'darkgrey'}
gl.ylabel_style = {'size': 20, 'color': 'darkgrey'}
ax['C'].add_geometries([ring1], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)
ax['C'].add_geometries([ring2], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)
ax['C'].add_geometries([ring3], ccrs.PlateCarree(), facecolor='none', edgecolor='k',linewidth=3)


ax['A'].set_ylim(9.5,12.5)
ax['B'].set_ylim(-5,22)


ax['A'].set_yticks(ticks = np.arange(10,13,1))
ax['B'].set_yticks(ticks = np.arange(-5,25,5))

ax['A'].set_yticklabels(labels = np.arange(10,13,1),fontsize=30,color='dimgrey')
ax['B'].set_yticklabels(labels = np.arange(-5,25,5),fontsize=30,color='dimgrey')

ax['A'].set_xticks(ticks = np.arange(0,60,5))
ax['A'].set_xticklabels(labels = np.arange(2015,2075,5),fontsize=30,rotation='0',color='dimgrey')
ax['B'].set_xticks(ticks = np.arange(0,60,10))
ax['B'].set_xticklabels(labels = np.arange(2015,2075,10),fontsize=30,rotation='0',color='dimgrey')

ax['A'].set_xlabel('year',fontsize=35,color='dimgrey')
ax['B'].set_xlabel('year',fontsize=35,color='dimgrey')

ax['A'].set_ylabel('temp (C)',fontsize=35,color='dimgrey')
ax['B'].set_ylabel('temp (C)',fontsize=35,color='dimgrey')

for ens in np.arange(0,10):
    ax['A'].plot(np.arange(0,55,1)[20:],sai_all_gl[ens][20:],'xkcd:dull teal',alpha=0.4,linewidth=2)
    ax['A'].plot(cont_all_gl[ens],'grey',alpha=0.5,linewidth=2)
    
    ax['B'].plot(np.arange(0,55,1)[20:],sai_all_al[ens][20:],'xkcd:dull teal',alpha=0.3)
    ax['B'].plot(cont_all_al[ens],'grey',alpha=0.5)
    
    ax['B'].plot(np.arange(0,55,1)[20:],sai_all_nw[ens][20:],'xkcd:dull teal',alpha=0.3)
    ax['B'].plot(cont_all_nw[ens],'grey',alpha=0.5)
    
    ax['B'].plot(np.arange(0,55,1)[20:],sai_all_sw[ens][20:],'xkcd:dull teal',alpha=0.3)
    ax['B'].plot(cont_all_sw[ens],'grey',alpha=0.5)
    
ax['A'].plot(cont_all_gl.mean('ens'),'k',alpha = 0.6,linewidth=5,label='CONTROL')
ax['B'].plot(cont_all_al.mean('ens'),'k',alpha = 0.6,linewidth=4)
ax['B'].plot(cont_all_nw.mean('ens'),'k',alpha = 0.6,linewidth=4)
ax['B'].plot(cont_all_sw.mean('ens'),'k',alpha = 0.6,linewidth=4)

ax['A'].plot(np.arange(0,55,1)[20:],sai_all_gl.mean('ens')[20:],'xkcd:dull teal',alpha = 0.9,linewidth=5,label='SAI')
ax['B'].plot(np.arange(0,55,1)[20:],sai_all_al.mean('ens')[20:],'xkcd:dull teal',alpha = 0.9,linewidth=4)
ax['B'].plot(np.arange(0,55,1)[20:],sai_all_nw.mean('ens')[20:],'xkcd:dull teal',alpha = 0.9,linewidth=4)
ax['B'].plot(np.arange(0,55,1)[20:],sai_all_sw.mean('ens')[20:],'xkcd:dull teal',alpha = 0.9,linewidth=4)

leg = ax['A'].legend(ncol=2,frameon=False,loc='upper left',title='GLOBAL',fontsize='25')
leg._legend_box.align = 'left'
leg.get_title().set_fontsize('30')
leg.get_title().set_color('dimgrey')
leg.get_texts()[0].set_color('dimgrey')
leg.get_texts()[1].set_color('xkcd:dull teal')

ax['A'].set_title('(a)',loc='left',fontsize=35,color='dimgrey')

ax['B'].set_title('(b)',loc='left',fontsize=35,color='dimgrey')
ax['B'].text(x=35,y=21.,s='SW COAST',fontsize=30,color='dimgrey',rotation=0)
ax['B'].text(x=35,y=11.,s='NW COAST',fontsize=30,color='dimgrey',rotation=0)
ax['B'].text(x=37,y=1.5,s='ALASKA',fontsize=30,color='dimgrey',rotation=0)

ax['C'].text(x=29,y=30.5,s='SW COAST',fontsize=30,color='dimgrey',rotation=0)
ax['C'].text(x=29,y=45.5,s='NW COAST',fontsize=30,color='dimgrey',rotation=0)
ax['C'].text(x=31,y=62.5,s='ALASKA',fontsize=30,color='dimgrey',rotation=0)

for loc in ['A','B']:
    ax[loc].vlines(x=20,ymin=-10,ymax=30,color='xkcd:dull teal',linestyle='--',linewidth=3)

plt.tight_layout()
# plt.show()

plt.savefig('figures/Figure1.png',bbox_inches='tight',dpi=300)
