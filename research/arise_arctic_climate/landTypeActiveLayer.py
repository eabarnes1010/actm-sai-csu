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


def getLandType(makeFigures):
    import xarray as xr
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
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
    ens = ['001', '002', '003', '004', '006', '007', '008', '009', '010']
    numEns = len(ens)
    ALTMAX_CONTROL = {}
    PFROST_CONTROL = {}
    ALTMAX_FEEDBACK = {}
    PFROST_FEEDBACK = {}
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.'\
                             + str(ens[i]) + '.clm2.h0.ALTMAX.201501-206412_NH.nc',
                             decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        PFROST_CONTROL[ens[i]] = (ds.ALTMAX[240:,:,:]).where(ds.ALTMAX[240:,:,:] <= 39.).groupby('time.year').mean(dim='time')
        ALTMAX_CONTROL[ens[i]] = (ds.ALTMAX).where(ds.ALTMAX <= 39.).groupby('time.year').max(dim='time')
        ds.close()
    print(np.nanmax(PFROST_CONTROL[ens[1]][:,29:-6,:]))
    print(" ")
    print(np.nanmax(ALTMAX_CONTROL[ens[1]][:,29:-6,:]))
        
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.'\
                             + str(ens[i]) + '.clm2.h0.ALTMAX.203501-206912_NH.nc',
                             decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        PFROST_FEEDBACK[ens[i]] = (ds.ALTMAX[:-60,:,:]).where(ds.ALTMAX[:-60,:,:] <= 39.).groupby('time.year').mean(dim='time')
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
    # x = xr.DataArray(np.arange(numEns*50*85*288).reshape(numEns,50,85,288))
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
            
    '''Soil respiration from permafrost soils'''
    soilRes_CONTROL        = {}
    soilResCum_CONTROL     = {}
    soilResCumPeat_CONTROL = {}
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + str(ens[i]) +
                             '.clm2.h0.ER.201501-206412_NH.nc', decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        lat = ds.lat
        lon = ds.lon
        time = ds.time[240:]
        '''
        Cumulative annual soil respiration from 2035 to 2064
        to see if model can detect a difference in 'irreversible'
        soil carbon loss
        1. Multiply monthly mean rate by days in month
        2. Multiply by seconds per day to get total land emissions
        3. Sum over year to get annual land emissions
        4. Cumulative sum over time
        '''
        soilRes_CONTROL[ens[i]]    = (ds['ER'][240:,:,:])
        soilRes_CONTROL[ens[i]]    = (soilRes_CONTROL[ens[i]] * time.dt.daysinmonth * 86400).groupby('time.year').sum(dim='time',skipna=True)
        soilResCum_CONTROL[ens[i]] = (soilRes_CONTROL[ens[i]].cumsum(axis=0)).where(PFROST_CONTROL[ens[i]].notnull())
        mx = np.ma.masked_invalid(ALTMAX_CONTROL_PEAT[i,20:,:,:])
        print(mx)
        soilResCumPeat_CONTROL[ens[i]] = (soilRes_CONTROL[ens[i]].cumsum(axis=0)).where(ALTMAX_CONTROL_PEAT[i,20:,:,:] != np.nan)
        ds.close()
        
    soilRes_FEEDBACK        = {}
    soilResCum_FEEDBACK     = {}
    soilResCumPeat_FEEDBACK = {}
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + str(ens[i]) +
                             '.clm2.h0.ER.203501-206912_NH.nc', decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        lat = ds.lat
        lon = ds.lon
        time = ds.time[:-60]
        soilRes_FEEDBACK[ens[i]]    = (ds['ER'][:-60,:,:])
        soilRes_FEEDBACK[ens[i]]    = (soilRes_FEEDBACK[ens[i]] * time.dt.daysinmonth*86400).groupby('time.year').sum(dim='time',skipna=True)
        soilResCum_FEEDBACK[ens[i]] = (soilRes_FEEDBACK[ens[i]].cumsum(axis=0)).where((PFROST_FEEDBACK[ens[i]].to_numpy()) != np.nan)
        soilResCumPeat_FEEDBACK[ens[i]] = (soilRes_FEEDBACK[ens[i]].cumsum(axis=0)).where(ALTMAX_FEEDBACK_PEAT[i,:-5,:,:] != np.nan)
        ds.close()
        
    ## ---- time series figures ---- ##
    if makeFigures:
        ## ---- cumulative carbon emitted from permafrost soils ---- ##
        from make_timeseries import make_timeseries
        ensMeanERCONTROL_ts, ensMembersERCONTROL_ts = make_timeseries(numEns,'ER',lat,lon,90,30,360,0,soilResCum_CONTROL)
        ensMeanERFEEDBACK_ts, ensMembersERFEEDBACK_ts = make_timeseries(numEns,'ER',lat,lon,90,30,360,0,soilResCum_FEEDBACK)
        ensMeanER_PEAT_CONTROL_ts, ensMembersER_PEAT_CONTROL_ts = make_timeseries(numEns,'ER',lat,lon,90,30,360,0,soilResCumPeat_CONTROL)
        ensMeanER_PEAT_FEEDBACK_ts, ensMembersER_PEAT_FEEDBACK_ts = make_timeseries(numEns,'ER',lat,lon,90,30,360,0,soilResCumPeat_FEEDBACK)
        fig = plt.figure(figsize=(10,4),dpi=900)
        for ensNum in range(len(ens)):
            plt.plot(ensMembersERCONTROL_ts[ens[ensNum]]/1000.,color='xkcd:light purple')
            plt.plot(ensMembersERFEEDBACK_ts[ens[ensNum]]/1000.,color='xkcd:light green')
            plt.plot(ensMembersER_PEAT_CONTROL_ts[ens[ensNum]]/1000.,linestyle='dotted',color='xkcd:light purple')
            plt.plot(ensMembersER_PEAT_FEEDBACK_ts[ens[ensNum]]/1000.,linestyle='dotted',color='xkcd:light green')
        plt.plot(ensMeanERCONTROL_ts/1000.,color='xkcd:dark purple',linewidth=2,label='CESM2-WACCM-SSP2-4.5')
        plt.plot(ensMeanERFEEDBACK_ts/1000.,color='g',linewidth=2,label='ARISE-SAI-1.5')
        plt.plot(ensMeanER_PEAT_CONTROL_ts/1000.,color='xkcd:dark purple',linestyle='dashed',linewidth=2)
        plt.plot(ensMeanER_PEAT_FEEDBACK_ts/1000.,color='g',linestyle='dashed',linewidth=2)
        plt.legend(fancybox=True)
        plt.xticks([0,5,10,15,20,25,29],['2035','2040','2045','2050','2055','2060','2064'])
        plt.xlim([0,29])
        # plt.ylim([0,10])
        plt.ylabel('Permafrost soil respiration (kgC/m2)', fontsize=11)
        plt.title('Cumulative respiration from total permafrost soils', fontsize=14, fontweight='bold')
        plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/nh_cumulative_ER_2035-2064.jpg',bbox_inches='tight',dpi=900)
        
        
        ## ---- peatland permafrost ---- ##
        fig, ax = plt.subplots()
        for i in range(numEns):
            plt.plot(
                (100 - (peatlandPFROST_FEEDBACK[i,0] - peatlandPFROST_FEEDBACK[i,:-5])/peatlandPFROST_FEEDBACK[i,0]*100),
                color='xkcd:cerulean',label='ARISE')
            plt.plot(
                (100 - (peatlandPFROST_CONTROL[i,20] - peatlandPFROST_CONTROL[i,20:])/peatlandPFROST_CONTROL[i,20]*100),
                color='xkcd:brick',label='SSP')
        plt.ylabel('% of 2035 peatland permafrost remaining')
        plt.xticks([0,5,10,15,20,25,29],['2035','2040','2045','2050','2055','2060','2064'])
        plt.xlim([0,30])
        display = (0,8)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend([handle for i,handle in enumerate(handles) if i in display],
          [label for i,label in enumerate(labels) if i in display], loc = 'best')
        plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/percent_peatland_permafrost_timeseries.jpg', 
                    dpi=700, bbox_inches='tight')
        
    return peatlandPFROST_FEEDBACK,totalPFROST_FEEDBACK,peatlandPFROST_CONTROL,\
        totalPFROST_CONTROL,soilResCum_CONTROL,soilResCum_FEEDBACK
