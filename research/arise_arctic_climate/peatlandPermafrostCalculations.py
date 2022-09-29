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
    altmaxControl = {}
    pfrostControl = {}
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.'\
                             + str(ens[i]) + '.clm2.h0.ALTMAX.201501-206412_NH.nc',
                             decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        altmaxControl[ens[i]] = (ds.ALTMAX).where(ds.ALTMAX <= 39.)
        pfrostControl[ens[i]] = altmaxControl[ens[i]][240:,:,:].groupby('time.year').mean(dim='time',skipna=True)
        ds.close()
        
    altmaxFeedback = {}
    pfrostFeedback = {}
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.'\
                             + str(ens[i]) + '.clm2.h0.ALTMAX.203501-206912_NH.nc',
                             decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        lat = ds.lat; lon = ds.lon
        altmaxFeedback[ens[i]] = (ds.ALTMAX).where(ds.ALTMAX <= 39.)
        pfrostFeedback[ens[i]] = altmaxFeedback[ens[i]][:-60,:,:].groupby('time.year').mean(dim='time',skipna=True)
        ds.close()

        
    ''' Each year, how much permafrost is in peatland? '''
    years                      = np.linspace(2035,2064,30)
    pfrostInPeatlandFeedback   = {}
    pfrostInPeatlandControl    = {}
    peatlandPfrostFeedbackArea = np.zeros((numEns,30))
    totalPfrostFeedbackArea    = np.zeros((numEns,30))
    peatlandPfrostControlArea  = np.zeros((numEns,30))
    totalPfrostControlArea     = np.zeros((numEns,30))
    
    for i in range(numEns):
        pfrostInPeatlandFeedback[ens[i]] = np.zeros((30,85,288))
        pfrostInPeatlandControl[ens[i]]  = np.zeros((30,85,288))
        for iyear in range(len(years)):
            ## pfrostFeedback = annual average (30x85x288)
            ## altmaxFeedback = every month (420x85x288)
            pfrostInPeatlandFeedback[ens[i]][iyear,:,:] = pfrostFeedback[ens[i]][iyear,:,:].where(
                                                                                    peatland.values >= 0.05)
            pfrostInPeatlandControl[ens[i]][iyear,:,:]  = pfrostControl[ens[i]][iyear,:,:].where(
                                                                                    peatland.values >= 0.05)
            
            ## add grid area for permafrost soils
            totalPfrostFeedbackArea[i,iyear] = np.array(np.nansum((gridArea.where(
                                                    ~np.isnan(pfrostFeedback[ens[i]][iyear,:,:]))/(
                                                        1000**2)),axis=(0,1)))
            totalPfrostControlArea[i,iyear]  = np.array(np.nansum((gridArea.where(
                                                    ~np.isnan(pfrostControl[ens[i]][iyear,:,:]))/(
                                                    1000**2)),axis=(0,1)))
            
            ## add grid area for permafrost soils in peatland
            peatlandPfrostFeedbackArea[i,iyear] = np.array(np.nansum((gridArea.where(
                                                      ~np.isnan(pfrostInPeatlandFeedback[ens[i]][iyear,:,:]))/(
                                                      1000**2)),axis=(0,1)))
            peatlandPfrostControlArea[i,iyear]  = np.array(np.nansum((gridArea.where(
                                                      ~np.isnan(pfrostInPeatlandControl[ens[i]][iyear,:,:]))/(
                                                      1000**2)),axis=(0,1)))
    
            
    '''Soil respiration from permafrost soils'''
    soilResControl        = {}
    soilResCumControl     = {}
    soilResCumPeatControl = {}
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + str(ens[i]) +
                             '.clm2.h0.ER.201501-206412_NH.nc', decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        lat = ds.lat
        lon = ds.lon
        time = ds.time[240:]
        '''
        Cumulative annual soil respiration from 2035 to 2064 to see if model can 
        detect a difference in 'irreversible' soil carbon loss
        1. Multiply monthly mean rate by days in month
        2. Multiply by seconds per day to get total land emissions
        3. Sum over year to get annual land emissions
        4. Cumulative sum over time
        '''
        soilResControl[ens[i]]        = ds['ER'][240:,:,:]
        soilResControl[ens[i]]        = (soilResControl[ens[i]] * time.dt.daysinmonth * 86400).groupby(
                                                                    'time.year').sum(dim='time',skipna=True)
        soilResCumControl[ens[i]]     = soilResControl[ens[i]].cumsum(
                                                                    axis=0)
        soilResCumControl[ens[i]]     = soilResCumControl[ens[i]].where(
                                                                    ~np.isnan(pfrostControl[ens[i]]))
        soilResCumPeatControl[ens[i]] = soilResCumControl[ens[i]].where(
                                                                    ~np.isnan(pfrostInPeatlandControl[ens[i]]))
        ds.close()
        
    '''Soil respiration from permafrost soils'''
    soilResFeedback        = {}
    soilResCumFeedback     = {}
    soilResCumPeatFeedback = {}
    for i in range(numEns):
        ds = xr.open_dataset(dataDirSAI + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + str(ens[i]) +
                             '.clm2.h0.ER.203501-206912_NH.nc', decode_times=False)
        units, reference_date = ds.time.attrs['units'].split('since')
        ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
        lat = ds.lat
        lon = ds.lon
        time = ds.time[:-60]
        soilResFeedback[ens[i]]        = ds['ER'][:-60,:,:]
        soilResFeedback[ens[i]]        = (soilResFeedback[ens[i]] * time.dt.daysinmonth * 86400).groupby(
                                                                    'time.year').sum(dim='time',skipna=True)
        soilResCumFeedback[ens[i]]     = soilResFeedback[ens[i]].cumsum(
                                                                    axis=0)
        soilResCumFeedback[ens[i]]     = soilResCumFeedback[ens[i]].where(
                                                                    ~np.isnan(pfrostFeedback[ens[i]]))
        soilResCumPeatFeedback[ens[i]] = soilResCumFeedback[ens[i]].where(
                                                                    ~np.isnan(pfrostInPeatlandFeedback[ens[i]]))
        ds.close()
     
        
    ## ---- time series figures ---- ##
    if makeFigures:
        ## ---- cumulative carbon emitted from permafrost soils, 2035-2065 ---- ##
        from make_timeseries import make_timeseries
        import matplotlib.pyplot as plt
        ensMeanERCONTROL_ts, ensMembersERCONTROL_ts = make_timeseries(numEns,'ER',lat,lon,90,40,360,0,soilResCumControl)
        ensMeanERFEEDBACK_ts, ensMembersERFEEDBACK_ts = make_timeseries(numEns,'ER',lat,lon,90,40,360,0,soilResCumFeedback)
        ensMeanER_PEAT_CONTROL_ts, ensMembersER_PEAT_CONTROL_ts = make_timeseries(numEns,'ER',lat,lon,90,40,360,0,soilResCumPeatControl)
        ensMeanER_PEAT_FEEDBACK_ts, ensMembersER_PEAT_FEEDBACK_ts = make_timeseries(numEns,'ER',lat,lon,90,40,360,0,soilResCumPeatFeedback)
        
        peatlandEnsMeanFeedbackArea = 0
        for val in peatlandPfrostFeedbackArea:
            peatlandEnsMeanFeedbackArea += val
        peatlandEnsMeanFeedbackArea = peatlandEnsMeanFeedbackArea/numEns 
        
        peatlandEnsMeanControlArea = 0
        for val in peatlandPfrostControlArea:
            peatlandEnsMeanControlArea += val
        peatlandEnsMeanControlArea = peatlandEnsMeanControlArea/numEns 
        
        pfrostEnsMeanFeedbackArea = 0
        for val in totalPfrostFeedbackArea:
            pfrostEnsMeanFeedbackArea += val
        pfrostEnsMeanFeedbackArea = pfrostEnsMeanFeedbackArea/numEns 
        
        pfrostEnsMeanControlArea = 0
        for val in totalPfrostControlArea:
            pfrostEnsMeanControlArea += val
        pfrostEnsMeanControlArea = pfrostEnsMeanControlArea/numEns 
        
        fig = plt.figure(figsize=(10,4.5),dpi=900)
        for ensNum in range(len(ens)):
            plt.plot(((ensMembersERCONTROL_ts[ens[ensNum]]/1000.)*totalPfrostControlArea[ensNum,:])/1e6,
                     color='xkcd:pale red',linewidth=0.9)
            plt.plot(((ensMembersERFEEDBACK_ts[ens[ensNum]]/1000.)*totalPfrostFeedbackArea[ensNum,:])/1e6,
                     color='xkcd:cerulean',linewidth=0.9)
            plt.plot(((ensMembersER_PEAT_CONTROL_ts[ens[ensNum]]/1000.)*peatlandPfrostControlArea[ensNum,:])/1e6,
                     linestyle='dotted',color='xkcd:pale red',linewidth=0.9)
            plt.plot(((ensMembersER_PEAT_FEEDBACK_ts[ens[ensNum]]/1000.)*peatlandPfrostFeedbackArea[ensNum,:])/1e6,
                     linestyle='dotted',color='xkcd:cerulean',linewidth=0.9)
        plt.plot(((ensMeanERCONTROL_ts/1000.)*pfrostEnsMeanControlArea)/1e6,
                     color='xkcd:dark red',linewidth=2,
                     label='CESM2-WACCM-SSP2-4.5 total permafrost')
        plt.plot(((ensMeanERFEEDBACK_ts/1000.)*pfrostEnsMeanFeedbackArea)/1e6,
                     color='xkcd:cobalt blue',linewidth=2,
                     label='ARISE-SAI total permafrost')
        plt.plot(((ensMeanER_PEAT_CONTROL_ts/1000.)*peatlandEnsMeanControlArea)/1e6,
                     color='xkcd:dark red',linestyle='dashed',linewidth=2,
                     label='CESM2-WACCM-SSP2-4.5 peat permafrost')
        plt.plot(((ensMeanER_PEAT_FEEDBACK_ts/1000.)*peatlandEnsMeanFeedbackArea)/1e6,
                      color='xkcd:cobalt blue',linestyle='dashed',linewidth=2,
                      label='ARISE-SAI peat permafrost')
        plt.legend(fancybox=True)
        plt.xticks([0,5,10,15,20,25,29],['2035','2040','2045','2050','2055','2060','2064'])
        plt.xlim([0,29])
        plt.ylim(bottom=0)
        plt.ylabel('Permafrost soil respiration (metric kilotons C)', fontsize=11)
        plt.title('Cumulative respiration from permafrost soils', fontsize=14, fontweight='bold')
        plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/nh_cumulative_ER_2035-2064.jpg',bbox_inches='tight',dpi=900)
        
        ## ---- cumulative carbon per square meter from permafrost soils ---- ##
        fig = plt.figure(figsize=(10,4.5),dpi=900)
        for ensNum in range(len(ens)):
            plt.plot(ensMembersERCONTROL_ts[ens[ensNum]]/1000.,
                     color='xkcd:pale red',linewidth=0.9)
            plt.plot(ensMembersERFEEDBACK_ts[ens[ensNum]]/1000.,
                     color='xkcd:cerulean',linewidth=0.9)
            plt.plot(ensMembersER_PEAT_CONTROL_ts[ens[ensNum]]/1000.,
                     linestyle='dotted',color='xkcd:pale red',linewidth=0.9)
            plt.plot(ensMembersER_PEAT_FEEDBACK_ts[ens[ensNum]]/1000.,
                     linestyle='dotted',color='xkcd:cerulean',linewidth=0.9)
        plt.plot(ensMeanERCONTROL_ts/1000.,
                     color='xkcd:dark red',linewidth=2,
                     label='CESM2-WACCM-SSP2-4.5 total permafrost')
        plt.plot(ensMeanERFEEDBACK_ts/1000.,
                     color='xkcd:cobalt blue',linewidth=2,
                     label='ARISE-SAI total permafrost')
        plt.plot(ensMeanER_PEAT_CONTROL_ts/1000.,
                     color='xkcd:dark red',linestyle='dashed',linewidth=2,
                     label='CESM2-WACCM-SSP2-4.5 peat permafrost')
        plt.plot(ensMeanER_PEAT_FEEDBACK_ts/1000.,
                      color='xkcd:cobalt blue',linestyle='dashed',linewidth=2,
                      label='ARISE-SAI peat permafrost')
        plt.legend(fancybox=True)
        plt.xticks([0,5,10,15,20,25,29],['2035','2040','2045','2050','2055','2060','2064'])
        plt.xlim([0,29])
        plt.ylim(bottom=0)
        plt.ylabel('Permafrost soil respiration (kgC/m2)', fontsize=11)
        plt.title('Cumulative respiration from permafrost soils', fontsize=14, fontweight='bold')
        plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/nh_cumulative_ER_per_area_2035-2064.jpg',bbox_inches='tight',dpi=900)
        
        
        ## ---- peatland permafrost ---- ##
        fig, ax = plt.subplots(figsize=(10,4.5),dpi=720)
        ensMeanFeedback = 0
        for val in peatlandPfrostFeedbackArea:
            ensMeanFeedback += val
        ensMeanFeedback = ensMeanFeedback/numEns 
        ensMeanControl = 0
        for val in peatlandPfrostControlArea:
            ensMeanControl += val
        ensMeanControl = ensMeanControl/numEns 
        for i in range(numEns):
            plt.plot(
                (100 - (peatlandPfrostFeedbackArea[i,0] - peatlandPfrostFeedbackArea[
                    i,:])/peatlandPfrostFeedbackArea[i,0]*100),
                    color='xkcd:cerulean',linewidth=0.8)
            plt.plot(
                (100 - (peatlandPfrostControlArea[i,0] - peatlandPfrostControlArea
                        [i,:])/peatlandPfrostControlArea[i,0]*100),
                    color='xkcd:pale red',linewidth=0.8)
        plt.plot(100 - ((ensMeanFeedback[0] - ensMeanFeedback[:])/ensMeanFeedback[0]*100),
                 color='xkcd:cobalt blue',linewidth=2,label='ARISE-SAI')
        plt.plot(100 - ((ensMeanControl[0] - ensMeanControl[:])/ensMeanControl[0]*100),
                 color='xkcd:dark red',linewidth=2,label='CESM2-WACCM-SSP2-4.5')
        plt.ylabel('% of 2035 peatland permafrost remaining')
        plt.xticks([0,5,10,15,20,25,29],['2035','2040','2045','2050','2055','2060','2064'])
        plt.xlim([0,29])
        plt.ylim([74,100.25])
        plt.legend(fancybox=True)
        plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/percent_peatland_permafrost_timeseries.jpg', 
                    dpi=720, bbox_inches='tight')
        
    return
