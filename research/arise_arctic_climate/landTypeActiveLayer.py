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
    pft = ds.PCT_NAT_PFT[:,107:,:]; forest = np.nansum(pft[1:9,:,:],axis=0)
    ds.close()
    
    ds = xr.open_dataset(dataDirCESM + '/gridareaNH.nc')
    gridArea = ds.cell_area
    ds.close()
    
    ''' Get total peatland area in sq km (>5% peatland in grid cell) '''
    peatlandArea = np.array(np.nansum((gridArea.where(peatland.values >= 0.05)/(1000**2)),axis=(0,1)))
    print(np.round(peatlandArea/1e6, decimals=2), "million km2")
    
    ''' Max active layer depth '''
    ds = xr.open_dataset(dataDirSAI + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.001.clm2.h0.ALTMAX.201501-206412_NH.nc',
                         decode_times=False)
    units, reference_date = ds.time.attrs['units'].split('since')
    ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
    ALTMAX_CONTROL = (ds.ALTMAX).where(ds.ALTMAX <= 39.).groupby('time.year').max(dim='time')
    ds.close()
    
    ds = xr.open_dataset(dataDirSAI + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.001.clm2.h0.ALTMAX.203501-206912_NH.nc',
                         decode_times=False)
    units, reference_date = ds.time.attrs['units'].split('since')
    ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
    ALTMAX_FEEDBACK = (ds.ALTMAX).where(ds.ALTMAX <= 39.).groupby('time.year').max(dim='time')
    ds.close()
    
    ''' Each year, how much permafrost is in peatland? '''
    years = np.linspace(2035,2069,35)
    ALTMAX_FEEDBACK_PEAT = np.zeros((35,85,288))
    peatlandPFROST_FEEDBACK = np.zeros((35))
    totalPFROST_FEEDBACK = np.zeros((35))
    for iyear in range(len(years)):
        ALTMAX_FEEDBACK_PEAT[iyear,:,:] = ALTMAX_FEEDBACK[iyear,:,:].where(peatland.values >= 0.05)
        totalPFROST_FEEDBACK[iyear] = np.array(np.nansum((gridArea.where(~np.isnan(ALTMAX_FEEDBACK[iyear,:,:]))/(1000**2)),axis=(0,1)))
        peatlandPFROST_FEEDBACK[iyear] = np.array(np.nansum((gridArea.where(~np.isnan(ALTMAX_FEEDBACK_PEAT[iyear,:,:]))/(1000**2)),axis=(0,1)))
    
    years = np.linspace(2015,2064,50)
    ALTMAX_CONTROL_PEAT = np.zeros((50,85,288))
    peatlandPFROST_CONTROL = np.zeros((50))
    totalPFROST_CONTROL = np.zeros((50))
    for iyear in range(len(years)):
        ALTMAX_CONTROL_PEAT[iyear,:,:] = ALTMAX_CONTROL[iyear,:,:].where(peatland.values >= 0.05)
        totalPFROST_CONTROL[iyear] = np.array(np.nansum((gridArea.where(~np.isnan(ALTMAX_CONTROL[iyear,:,:]))/(1000**2)),axis=(0,1)))
        peatlandPFROST_CONTROL[iyear] = np.array(np.nansum((gridArea.where(~np.isnan(ALTMAX_CONTROL_PEAT[iyear,:,:]))/(1000**2)),axis=(0,1)))
    
    print(np.round(totalPFROST_FEEDBACK[:-5]/1e6,decimals=2),"million km2")
    print(np.round(peatlandPFROST_FEEDBACK[:-5]/1e6,decimals=2), "million km2")
    print(np.round(totalPFROST_CONTROL[20:]/1e6,decimals=2),"million km2")
    print(np.round(peatlandPFROST_CONTROL[20:]/1e6,decimals=2), "million km2")
    
    return peatlandPFROST_FEEDBACK,totalPFROST_FEEDBACK,peatlandPFROST_CONTROL,totalPFROST_CONTROL
