#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:21:11 2022

@author: kmayer

Plot histogram of the frequency of a positive anomaly following el nino/la nina using all grid points in each of the 3 regions

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
            
#%% Define variables
DIR = 'data/'
MEMstr = '1-10'
RUN = 'control' # 'control', 'SAI', or 'base'
LEAD = 2

#'alaska':
lower_ilat1 = 154
upper_ilat1 = 172
left_ilon1  = 152
right_ilon1 = 201
#'nwcoast':
lower_ilat2 = 138
upper_ilat2 = 155
left_ilon2  = 188
right_ilon2 = 201
#'swcoast':
lower_ilat3 = 122
upper_ilat3 = 139
left_ilon3  = 188
right_ilon3 = 201

#%% LOAD & PLOT histogram of frequency of positive anomaly for each ENSO phase per scenario
for RUN in ['base','SAI','control']:
    nino = xr.open_dataarray(DIR+RUN+'_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
    nina = xr.open_dataarray(DIR+RUN+'_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')
    
    # FLATTEN for histogram plotting
    ninoflat_al = nino[:,lower_ilat1:upper_ilat1,left_ilon1:right_ilon1].values.ravel()
    ninaflat_al = nina[:,lower_ilat1:upper_ilat1,left_ilon1:right_ilon1].values.ravel()
    
    ninoflat_nw = nino[:,lower_ilat2:upper_ilat2,left_ilon2:right_ilon2].values.ravel()
    ninaflat_nw = nina[:,lower_ilat2:upper_ilat2,left_ilon2:right_ilon2].values.ravel()
    
    ninoflat_sw = nino[:,lower_ilat3:upper_ilat3,left_ilon3:right_ilon3].values.ravel()
    ninaflat_sw = nina[:,lower_ilat3:upper_ilat3,left_ilon3:right_ilon3].values.ravel()

    fig = plt.figure(figsize=(10,10),constrained_layout=False)  
    ax = fig.subplot_mosaic('''
                            A
                            B
                            C
                            ''')  
    for loc in ['A','B','C']:                  
        adjust_spines(ax[loc], ['left', 'bottom'])
        ax[loc].spines['top'].set_color('none')
        ax[loc].spines['right'].set_color('none')
        ax[loc].spines['left'].set_color('dimgrey')
        ax[loc].spines['bottom'].set_color('dimgrey')
        ax[loc].spines['left'].set_linewidth(2)
        ax[loc].spines['bottom'].set_linewidth(2)
        ax[loc].tick_params('both',length=4,width=2,which='major',color='dimgrey')
        ax[loc].yaxis.grid(zorder=1,color='dimgrey',alpha=0.35)
        ax[loc].set_xlim(0,1)
        ax[loc].set_xticks(np.arange(0,1.1,.1))
    
    ax['A'].set_xticklabels(labels = ['']*11,fontsize=18)
    ax['B'].set_xticklabels(labels = ['']*11,fontsize=18)
    ax['C'].set_xticklabels([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0],fontsize=18,color='dimgrey')
    ax['C'].set_xlabel('FREQUENCY',fontsize=20,color='dimgrey')
    
    ax['B'].set_ylabel('COUNT',fontsize=20,color='dimgrey')
    
    ax['A'].set_ylim(0,1500)
    ax['A'].set_yticks(np.arange(0,2000,500))
    ax['A'].set_yticklabels(np.arange(0,2000,500),fontsize=18,color='dimgrey')
    for loc in ['B','C']:
        ax[loc].set_ylim(0,500)
        ax[loc].set_yticks(np.arange(0,600,100))
        ax[loc].set_yticklabels(np.arange(0,600,100),fontsize=18,color='dimgrey')
    #--
    ax['A'].hist(ninaflat_al,bins=np.arange(0,1.05,.05),color='xkcd:ugly blue',edgecolor='white',linewidth=1,label = 'LA NINA',alpha=.75)
    ax['A'].vlines(x=np.nanmedian(ninaflat_al),ymin=0,ymax=1500,color='xkcd:navy',linestyle='--')

    ax['A'].hist(ninoflat_al,bins=np.arange(0,1.05,.05),color='rosybrown',edgecolor='white',linewidth=1,label = 'EL NINO',alpha=.75)
    ax['A'].vlines(x=np.nanmedian(ninoflat_al),ymin=0,ymax=1500,color='darkred',linestyle='--')
    #--
    ax['B'].hist(ninaflat_nw,bins=np.arange(0,1.05,.05),color='xkcd:ugly blue',edgecolor='white',linewidth=1,alpha=.75)
    ax['B'].vlines(x=np.nanmedian(ninaflat_nw),ymin=0,ymax=1500,color='xkcd:navy',linestyle='--')

    ax['B'].hist(ninoflat_nw,bins=np.arange(0,1.05,.05),color='rosybrown',edgecolor='white',linewidth=1,alpha=.75)
    ax['B'].vlines(x=np.nanmedian(ninoflat_nw),ymin=0,ymax=1500,color='darkred',linestyle='--')
    #--
    ax['C'].hist(ninaflat_sw,bins=np.arange(0,1.05,.05),color='xkcd:ugly blue',edgecolor='white',linewidth=1,alpha=.75)
    ax['C'].vlines(x=np.nanmedian(ninaflat_sw),ymin=0,ymax=1500,color='xkcd:navy',linestyle='--')

    ax['C'].hist(ninoflat_sw,bins=np.arange(0,1.05,.05),color='rosybrown',edgecolor='white',linewidth=1,alpha=.75)
    ax['C'].vlines(x=np.nanmedian(ninoflat_sw),ymin=0,ymax=1500,color='darkred',linestyle='--')
    #--
  
    leg1 = ax['A'].legend(frameon=False,ncol=2,title='ALASKA',title_fontsize=20,labelcolor='k',loc='upper left')
    leg1._legend_box.align = "left"
    leg2 = ax['B'].legend(frameon=False,ncol=2,title='NORTH-WEST COAST',title_fontsize=20,labelcolor='dimgrey',loc='upper left')
    leg2._legend_box.align = "left"
    leg3 = ax['C'].legend(frameon=False,ncol=2,title='SOUTH-WEST COAST',title_fontsize=20,labelcolor='dimgrey',loc='upper left')
    leg3._legend_box.align = "left"
    
    DIR_FIGSAVE = 'figures/'
    plt.savefig(DIR_FIGSAVE+RUN+'_posfreqhist.png',bbox_inches='tight',dpi=300)
    
    # plt.show()

#%% PLOT histogram of frequency of positive anomaly DIFFERENCE for each ENSO phase per scenario
nino_base = xr.open_dataarray(DIR+'base_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_base = xr.open_dataarray(DIR+'base_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')

nino_sai = xr.open_dataarray(DIR+'SAI_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_sai = xr.open_dataarray(DIR+'SAI_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')

nino_cont = xr.open_dataarray(DIR+'control_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
nina_cont = xr.open_dataarray(DIR+'control_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')

for DIFF in ['SAI-1.5 - BASE','SSP2-4.5 - BASE','SSP2-4.5 - SAI-1.5']:
    if DIFF == 'SAI-1.5 - BASE':
        diffnino = nino_sai - nino_base
        diffnina = nina_sai - nina_base
    elif DIFF == 'SSP2-4.5 - BASE':
        diffnino = nino_cont - nino_base
        diffnina = nina_cont - nina_base
    elif DIFF == 'SSP2-4.5 - SAI-1.5':
        diffnino = nino_cont - nino_sai
        diffnina = nina_cont - nina_sai
    # FLATTEN for histogram plotting
    
    diffnino_al = diffnino[:,lower_ilat1:upper_ilat1,left_ilon1:right_ilon1].values.ravel()
    diffnina_al = diffnina[:,lower_ilat1:upper_ilat1,left_ilon1:right_ilon1].values.ravel()
    
    diffnino_nw = diffnino[:,lower_ilat2:upper_ilat2,left_ilon2:right_ilon2].values.ravel()
    diffnina_nw = diffnina[:,lower_ilat2:upper_ilat2,left_ilon2:right_ilon2].values.ravel()
    
    diffnino_sw = diffnino[:,lower_ilat3:upper_ilat3,left_ilon3:right_ilon3].values.ravel()
    diffnina_sw = diffnina[:,lower_ilat3:upper_ilat3,left_ilon3:right_ilon3].values.ravel()

    fig = plt.figure(figsize=(10,10),constrained_layout=False)  
    ax = fig.subplot_mosaic('''
                            A
                            B
                            C
                            ''')  
    for loc in ['A','B','C']:                  
        adjust_spines(ax[loc], ['left', 'bottom'])
        ax[loc].spines['top'].set_color('none')
        ax[loc].spines['right'].set_color('none')
        ax[loc].spines['left'].set_color('dimgrey')
        ax[loc].spines['bottom'].set_color('dimgrey')
        ax[loc].spines['left'].set_linewidth(2)
        ax[loc].spines['bottom'].set_linewidth(2)
        ax[loc].tick_params('both',length=4,width=2,which='major',color='dimgrey')
        ax[loc].yaxis.grid(zorder=1,color='dimgrey',alpha=0.35)
        ax[loc].set_xlim(-.5,.5)
        ax[loc].set_xticks(np.arange(-0.5,0.75,.25))
    
    ax['A'].set_xticklabels(labels = ['']*5,fontsize=18)
    ax['B'].set_xticklabels(labels = ['']*5,fontsize=18)
    ax['C'].set_xticklabels(np.arange(-0.5,0.75,.25),fontsize=18,color='dimgrey')
    ax['C'].set_xlabel('FREQUENCY',fontsize=20,color='dimgrey')
    
    ax['B'].set_ylabel('COUNT',fontsize=20,color='dimgrey')
    
    ax['A'].set_ylim(0,1500)
    ax['A'].set_yticks(np.arange(0,2000,500))
    ax['A'].set_yticklabels(np.arange(0,2000,500),fontsize=18,color='dimgrey')
    for loc in ['B','C']:
        ax[loc].set_ylim(0,500)
        ax[loc].set_yticks(np.arange(0,600,100))
        ax[loc].set_yticklabels(np.arange(0,600,100),fontsize=18,color='dimgrey')
    
    ax['A'].hist(diffnina_al,bins=np.arange(-.5,.55,.05),color='xkcd:ugly blue',edgecolor='white',linewidth=1,label = 'LA NINA',alpha=.75)
    ax['A'].vlines(x=np.nanmedian(diffnina_al),ymin=0,ymax=1500,color='xkcd:navy',linestyle='--')

    ax['A'].hist(diffnino_al,bins=np.arange(-.5,.55,.05),color='rosybrown',edgecolor='white',linewidth=1,label = 'EL NINO',alpha=.75)
    ax['A'].vlines(x=np.nanmedian(diffnino_al),ymin=0,ymax=1500,color='darkred',linestyle='--')
    
    ax['B'].hist(diffnina_nw,bins=np.arange(-.5,.55,.05),color='xkcd:ugly blue',edgecolor='white',linewidth=1,alpha=.75)
    ax['B'].vlines(x=np.nanmedian(diffnina_nw),ymin=0,ymax=1500,color='xkcd:navy',linestyle='--')

    ax['B'].hist(diffnino_nw,bins=np.arange(-.5,.55,.05),color='rosybrown',edgecolor='white',linewidth=1,alpha=.75)
    ax['B'].vlines(x=np.nanmedian(diffnino_nw),ymin=0,ymax=1500,color='darkred',linestyle='--')
    
    ax['C'].hist(diffnina_sw,bins=np.arange(-.5,.55,.05),color='xkcd:ugly blue',edgecolor='white',linewidth=1,alpha=.75)
    ax['C'].vlines(x=np.nanmedian(diffnina_sw),ymin=0,ymax=1500,color='xkcd:navy',linestyle='--')

    ax['C'].hist(diffnino_sw,bins=np.arange(-.5,.55,.05),color='rosybrown',edgecolor='white',linewidth=1,alpha=.75)
    ax['C'].vlines(x=np.nanmedian(diffnino_sw),ymin=0,ymax=1500,color='darkred',linestyle='--')

    leg1 = ax['A'].legend(frameon=False,ncol=2,title='ALASKA',title_fontsize=20,labelcolor='k',loc='upper left')
    leg1._legend_box.align = "left"
    leg2 = ax['B'].legend(frameon=False,ncol=2,title='NORTH-WEST COAST',title_fontsize=20,labelcolor='dimgrey',loc='upper left')
    leg2._legend_box.align = "left"
    leg3 = ax['C'].legend(frameon=False,ncol=2,title='SOUTH-WEST COAST',title_fontsize=20,labelcolor='dimgrey',loc='upper left')
    leg3._legend_box.align = "left"
    
    DIR_FIGSAVE = 'figures/'
    plt.savefig(DIR_FIGSAVE+DIFF+'_posfreqhist.png',bbox_inches='tight',dpi=300)
    
    # plt.show()
