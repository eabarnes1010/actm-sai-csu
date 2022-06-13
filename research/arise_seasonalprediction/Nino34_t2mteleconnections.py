#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:21:11 2022

@author: kmayer

Calculate the frequency of a positive anomaly following el nino/la nina for each grid point in North America

"""
import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt

#%% Define variables
DIR = 'data/'
MEMstr = '1-10'
RUN = 'control' # 'control', 'SAI', or 'base'
LEAD = 2

# testing members
MEMS = [10,1,2,3,4,5,6,7,8,9]
#training members for each testing member
TRAINmem = [[1,2,3,4,5,6,7,8],
            [2,3,4,5,6,7,8,9],
            [3,4,5,6,7,8,9,10],
            [1,4,5,6,7,8,9,10],
            [1,2,5,6,7,8,9,10],
            [1,2,3,6,7,8,9,10],
            [1,2,3,4,7,8,9,10],
            [1,2,3,4,5,8,9,10],
            [1,2,3,4,5,6,9,10],
            [1,2,3,4,5,6,7,10]]

#%% Calculate frequency of a positive sign T2m anomaly following an el nino/la nina
# arrays to fill with frequency values
Ynino_posfreq = np.zeros(shape=(10,192,288)) + np.nan
Ynina_posfreq = np.zeros(shape=(10,192,288)) + np.nan

# loop through all testing member options
for m,mem in enumerate(MEMS):
    # LOAD data for frequency calculation
    # ------------------------------------------------------------------------- 
    if RUN == 'control' or RUN == 'SAI':
        # ------ Load nino 3.4 index for testing member ------
        FI = RUN+'_ens'+str(mem)+'_nino34std_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        nino34 = xr.open_dataarray(DIR+'Nino34_Index/'+FI)
        nino34 = nino34.where(nino34.time.dt.year >= 2050, drop=True)
        nino34 = nino34[:-1*LEAD]

        # ------ Load 2m temperature from testing member ------
        yFINAME = RUN+'_ens'+str(mem)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        Y = xr.open_dataarray(DIR+yFINAME)
        Y = Y.where(Y.time.dt.year >= 2050, drop=True)
        Y = Y[LEAD:]
        
        # ------ Load training members used for testing member to calculate median ------
        for t, trainmem in enumerate(TRAINmem[m]):
            print(trainmem)
            yFINAME = RUN+'_ens'+str(trainmem)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
            Ytemp = xr.open_dataarray(DIR+yFINAME)
            Ytemp = Ytemp.where(Ytemp.time.dt.year >= 2050, drop=True)
            Ytemp = Ytemp[LEAD:]
            
            if t == 0:
                Yall = xr.DataArray(np.zeros(shape=(len(TRAINmem[m]),np.shape(Ytemp)[0],np.shape(Ytemp)[1],np.shape(Ytemp)[2]),dtype='float')+np.nan,
                                    name='T2m',
                                    dims=('ens','time','lat','lon'),
                                    coords=[('ens',TRAINmem[m]),
                                            ('time',Ytemp.time),
                                            ('lat',Ytemp.lat),('lon',Ytemp.lon)]) 
            
            Yall[t] = Ytemp
        Yall_stacked = Yall.stack(time_all=('ens','time'))
        Ytrain_median = np.median(Yall_stacked)
        
        # ------ Subtract training median ------
        Y = Y - Ytrain_median
        
    # -------------------------------------------------------------------------    
    elif RUN == 'base':
        # ------ Load nino 3.4 index for testing member ------
        FI = 'control_ens'+str(mem)+'_nino34std_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        nino34 = xr.open_dataarray(DIR+'Nino34_Index/'+FI)
        nino34 = nino34.where(nino34.time.dt.year <= 2034, drop=True)
        nino34 = nino34[:-1*LEAD]
        
        # ------ Load 2m temperature from testing member ------
        yFINAME = 'control_ens'+str(mem)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        Y = xr.open_dataarray(DIR+yFINAME)
        Y = Y.where(Y.time.dt.year <= 2034, drop=True)
        Y = Y[LEAD:]
        
        # ------ Load training members used for testing member to calculate median ------
        for t, trainmem in enumerate(TRAINmem[m]):
            print(trainmem)
            yFINAME = 'control_ens'+str(trainmem)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
            Ytemp = xr.open_dataarray(DIR+yFINAME)
            Ytemp = Ytemp.where(Ytemp.time.dt.year <= 2034, drop=True)
            Ytemp = Ytemp[LEAD:]
            
            if t == 0:
                Yall = xr.DataArray(np.zeros(shape=(len(TRAINmem[m]),np.shape(Ytemp)[0],np.shape(Ytemp)[1],np.shape(Ytemp)[2]),dtype='float')+np.nan,
                                    name='T2m',
                                    dims=('ens','time','lat','lon'),
                                    coords=[('ens',TRAINmem[m]),
                                            ('time',Ytemp.time),
                                            ('lat',Ytemp.lat),('lon',Ytemp.lon)]) 
            
            Yall[t] = Ytemp
        Yall_stacked = Yall.stack(time_all=('ens','time'))
        Yall_stackedT = Yall_stacked.transpose('time_all','lat','lon')
        Ytrain_median = np.median(Yall_stackedT,axis=0)
        
        # ------ Subtract training median ------
        Y = Y - Ytrain_median
    
    # -------------------------------------------------------------------------
    # FREQUENCY calculation
    # ------ find location of el nino & la nina ------
    inino = np.where(nino34.values >= 1)[0]
    inina = np.where(nino34.values <= -1)[0]
    
    # ------ count times when T2m following el nino/la nina is positive ------
    Ynino_pos = xr.where(Y[inino] >= 0, x=1, y=0)
    Ynino_poscount = Ynino_pos.sum(dim='time')
    
    Ynina_pos = xr.where(Y[inina] >= 0, x=1, y=0)
    Ynina_poscount = Ynina_pos.sum(dim='time')
    
    # ------ calculate frequency of a positive anomaly following el nino/la nina ------
    Ynino_posfreq[m] = Ynino_poscount/len(inino)
    Ynina_posfreq[m] = Ynina_poscount/len(inina)
    
    
#%% Apply land mask and save
landmask = xr.open_dataset(DIR+'sftlf_fx_CESM2-WACCM_historical_r1i1p1f1_gn.nc')['sftlf']
landmask = xr.where(landmask>50,x=1,y=np.nan)
    
Ynino_posfreqxr = xr.DataArray(Ynino_posfreq,
                               name='T2m_freq',
                               dims=('ens','lat','lon'),
                               coords=[('ens',MEMS),
                                       ('lat',Y.lat),('lon',Y.lon)])  

Ynina_posfreqxr = xr.DataArray(Ynina_posfreq,
                               name='T2m_freq',
                               dims=('ens','lat','lon'),
                               coords=[('ens',MEMS),
                                       ('lat',Y.lat),('lon',Y.lon)])

Ynino_posfreqxr = Ynino_posfreqxr*landmask
Ynina_posfreqxr = Ynina_posfreqxr*landmask

Ynino_posfreqxr.to_netcdf(DIR+RUN+'_ens1-10_freqofposT2m_nino_detrended_ensmean'+MEMstr+'.nc')
Ynina_posfreqxr.to_netcdf(DIR+RUN+'_ens1-10_freqofposT2m_nina_detrended_ensmean'+MEMstr+'.nc')
