#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 15:21:27 2022

@author: kmayer
"""
import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

#%% DEFINING EXTRA FUNCTIONS
def is_month(data, months):
    i_timedim = np.where(np.asarray(data.dims) == 'time')[0][0]
    if i_timedim == 0:
        data = data[data.time.dt.month.isin(months)]
    elif i_timedim == 1:
        data = data[:,data.time.dt.month.isin(months)]
    return data

#%%
DIR = 'data/'
MEMstr = '1-10'
LEAD = 2
MEMS = [10,1,2,3,4,5,6,7,8,9]
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

#%%
landmask = xr.open_dataset(DIR+'sftlf_fx_CESM2-WACCM_historical_r1i1p1f1_gn.nc')['sftlf']
landmask = xr.where(landmask>50,x=1,y=np.nan)

for RUN in ['control','SAI']:

    Yvar = np.zeros(shape=(10,192,288)) + np.nan
    
    for m,mem in enumerate(MEMS):

        # ------ Load 2m temperature from testing member ------
        yFINAME = RUN+'_ens'+str(mem)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        Y = xr.open_dataarray(DIR+yFINAME)
        Y = Y.where(Y.time.dt.year >= 2050, drop=True)
        Y = Y[LEAD:]
        Y = is_month(Y,[11,12,1,2,3])
        
        # ------ Load training members used for testing member to calculate median ------
        for t, trainmem in enumerate(TRAINmem[m]):
            print(trainmem)
            yFINAME = RUN+'_ens'+str(trainmem)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
            Ytemp = xr.open_dataarray(DIR+yFINAME)
            Ytemp = Ytemp.where(Ytemp.time.dt.year >= 2050, drop=True)
            Ytemp = Ytemp[LEAD:]
            Ytemp = is_month(Ytemp,[11,12,1,2,3])
            
            if t == 0:
                Yall = xr.DataArray(np.zeros(shape=(len(TRAINmem[m]),np.shape(Ytemp)[0],np.shape(Ytemp)[1],np.shape(Ytemp)[2]),dtype='float')+np.nan,
                                    name='T2m',
                                    dims=('ens','time','lat','lon'),
                                    coords=[('ens',TRAINmem[m]),
                                            ('time',Ytemp.time),
                                            ('lat',Ytemp.lat),('lon',Ytemp.lon)])
            
            Yall[t] = Ytemp
        Yall_stacked = Yall.stack(time_all=('ens','time')).transpose('time_all','lat','lon')
        Ytrain_median = np.median(Yall_stacked,axis=0)
        # ------ Subtract training median ------
        Y = Y - Ytrain_median
        
        # ------ Calculate variance ------
        Yvar[m] = Y.var(dim='time', skipna=True)
        
    # ------ SAVE ------
    Yvar = xr.DataArray(Yvar,
                        name='T2m_var',
                        dims=('ens','lat','lon'),
                        coords=[('ens',MEMS),
                                ('lat',Y.lat),('lon',Y.lon)])
    Yvar = Yvar*landmask
    Yvar.to_netcdf(DIR+RUN+'_ens1-10_T2mvar_detrended_ensmean'+MEMstr+'.nc')
