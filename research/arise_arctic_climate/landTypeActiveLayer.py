#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 14:45:21 2022

@author: Ariel L. Morrison

The 'irreversibility' of carbon loss from permafrost thaw depends on the ground
type: forests can resequester carbon during the growing season via photosynthesis
and carbon fixing, but peatland, as an anaerobic environment, cannot resequester
lost carbon on decadal time scales. As a result, carbon lost from thawing peatlands 
can be considered 'permanently' lost from the permafrost reservoir.
Here we make a simple calculation of how much thawing permafrost is in peatlands
each year from 2000-2070.
"""
import os; os.chdir('/Users/arielmor/Projects/actm-sai-csu/research/arise_arctic_climate')
dataDirSAI = '/Users/arielmor/Desktop/SAI/data/ARISE/data'
dataDirCESM = '/Users/arielmor/Desktop/SAI/data/CESM2'


def getLandType():
    import xarray as xr
    import numpy as np
    import pandas as pd
    
    ds = xr.open_dataset(dataDirCESM + '/surfdata_0.9x1.25_78pfts_CMIP6_simyr2000_c170824.nc')
    peatland = ds.peatf[107:,:]
    ds.close()
    
    ds = xr.open_dataset(dataDirCESM + '/gridareaNH.nc')
    gridArea = ds.cell_area
    ds.close()
    
    ''' Get total peatland area in sq km (>5% peatland in grid cell) '''
    peatlandArea = np.array(np.nansum((gridArea.where(peatland.values >= 0.05)/(1000**2)),axis=(0,1)))
    print(np.round(peatlandArea/1e6, decimals=2), "million km2")
    
    ''' Max active layer depth '''
    ens = ['001', '002', '003', '004', '006', '007', '008', '009']
    numEns = len(ens)
    ALTMAX_CONTROL = {}
    ALTMAX_FEEDBACK = {}
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.'\
                             + str(ens[i]) + '.clm2.h0.ALTMAX.201501-206412_NH.nc',
                             decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        ALTMAX_CONTROL[ens[i]] = (ds.ALTMAX).where(ds.ALTMAX <= 39.).groupby('time.year').max(dim='time')
        ds.close()
        
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.'\
                             + str(ens[i]) + '.clm2.h0.ALTMAX.203501-206912_NH.nc',
                             decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        ALTMAX_FEEDBACK[ens[i]] = (ds.ALTMAX).where(ds.ALTMAX <= 39.).groupby('time.year').max(dim='time')
        ds.close()
    
    ''' Each year, how much permafrost is in peatland? '''
    years = np.linspace(2035,2069,35)
    ALTMAX_FEEDBACK_PEAT = np.zeros((numEns,35,85,288))
    peatlandPFROST_FEEDBACK = np.zeros((numEns,35))
    totalPFROST_FEEDBACK = np.zeros((numEns,35))
    for i in range(numEns):
        for iyear in range(len(years)):
            ALTMAX_FEEDBACK_PEAT[i,iyear,:,:] = ALTMAX_FEEDBACK[ens[i]][iyear,:,:].where(peatland.values >= 0.05)
            totalPFROST_FEEDBACK[i,iyear] = np.array(np.nansum((gridArea.where(~np.isnan(ALTMAX_FEEDBACK[ens[i]][iyear,:,:]))/(1000**2)),
                                                             axis=(0,1)))
            peatlandPFROST_FEEDBACK[i,iyear] = np.array(np.nansum((gridArea.where(~np.isnan(ALTMAX_FEEDBACK_PEAT[i,iyear,:,:]))/(1000**2)),
                                                         axis=(0,1)))
    
    years = np.linspace(2015,2064,50)
    ALTMAX_CONTROL_PEAT = np.zeros((numEns,50,85,288))
    peatlandPFROST_CONTROL = np.zeros((numEns,50))
    totalPFROST_CONTROL = np.zeros((numEns,50))
    for i in range(numEns):
        for iyear in range(len(years)):
            ALTMAX_CONTROL_PEAT[i,iyear,:,:] = ALTMAX_CONTROL[ens[i]][iyear,:,:].where(peatland.values >= 0.05)
            totalPFROST_CONTROL[i,iyear] = np.array(np.nansum((gridArea.where(~np.isnan(ALTMAX_CONTROL[ens[i]][iyear,:,:]))/(1000**2)),
                                                            axis=(0,1)))
            peatlandPFROST_CONTROL[i,iyear] = np.array(np.nansum((gridArea.where(~np.isnan(ALTMAX_CONTROL_PEAT[i,iyear,:,:]))/(1000**2)),
                                                            axis=(0,1)))
    
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for i in range(numEns):
        plt.plot(
            (100 - (peatlandPFROST_FEEDBACK[i,0] - peatlandPFROST_FEEDBACK[i,:-5])/peatlandPFROST_FEEDBACK[i,0]*100),
            color='xkcd:cerulean',label='ARISE')
        plt.plot(
            (100 - (peatlandPFROST_CONTROL[i,20] - peatlandPFROST_CONTROL[i,20:])/peatlandPFROST_CONTROL[i,20]*100),
            color='xkcd:brick',label='SSP')
    plt.ylabel('% of 2035 peatland permafrost remaining')
    plt.xticks([0,5,10,15,20,25,30],['2035','2040','2045','2050','2055','2060','2065'])
    plt.xlim([0,30])
    display = (0,8)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend([handle for i,handle in enumerate(handles) if i in display],
      [label for i,label in enumerate(labels) if i in display], loc = 'best')
    plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/percent_peatland_permafrost_timeseries.jpg', 
                dpi=700, bbox_inches='tight')
    
    # print(np.round(totalPFROST_FEEDBACK[:-5]/1e6,decimals=2),"million km2")
    # print(np.round(peatlandPFROST_FEEDBACK[:-5]/1e6,decimals=2), "million km2")
    # print(np.round(totalPFROST_CONTROL[20:]/1e6,decimals=2),"million km2")
    # print(np.round(peatlandPFROST_CONTROL[20:]/1e6,decimals=2), "million km2")
    
    return peatlandPFROST_FEEDBACK,totalPFROST_FEEDBACK,peatlandPFROST_CONTROL,totalPFROST_CONTROL
