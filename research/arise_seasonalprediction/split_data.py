#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 14:23:09 2022

@author: kmayer

Script to create training, validation and testing data for
neural network training and model evaluation in trainNN.py & evaluateNN.py

"""
import numpy as np
import xarray as xr
import datetime as dt
import warnings
warnings.simplefilter("ignore") 
#%%
def is_month(data, months):
    i_timedim = np.where(np.asarray(data.dims) == 'time')[0][0]
    if i_timedim == 0:
        data = data[data.time.dt.month.isin(months)]
    elif i_timedim == 1:
        data = data[:,data.time.dt.month.isin(months)]
    return data


def temp_regionalmean(DIR, RUN, MEMstr, LEAD, MEM, lower_ilat, upper_ilat, left_ilon, right_ilon):
    landmask = xr.open_dataset('data/sftlf_fx_CESM2-WACCM_historical_r1i1p1f1_gn.nc')['sftlf']
    landmask = xr.where(landmask>50,x=1,y=np.nan)

    yFINAME = RUN+'_ens'+str(MEM)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
    Y = xr.open_dataarray(DIR+yFINAME) * landmask
    Y = Y.where(Y.time.dt.year >= 2050, drop=True)
        
    Yregion = Y[LEAD:,lower_ilat:upper_ilat,left_ilon:right_ilon].mean(dim = ['lat','lon'], skipna = True)
    Yregion = is_month(Yregion,[11,12,1,2,3])
    
    return Yregion

#-----------------------------------------------------------------------------
def train_future(DIR, RUN, LEAD, TRAINmem, MEMstr, lower_ilat, upper_ilat, left_ilon, right_ilon):
    '''
    Load X (SST) & Y (T2M) data from SAI or SSP2-4.5 and return
    training data information.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    DIR: str
        directory path where SST and T2M data is located
    TRAINstr: list
        The members used for training
        --> these are the members loaded in this function
    MEMstr: str
        The members used for detrending and removing the seasonal cycle (TRAINstr + validation member)
            --> purely an informational str about how each member was preprocessed
    lat,lon: int
        Index of the lat and lon location of T2M being predicted
        
    Returns:
    --------
    X_train: numpy array
        SST data used for training
    
    Y_train: numpy array
        T2M data used for training at LEAD = LEAD
        Converted into 0s and 1s
    
    Xtrain_mean: numpy array
        Lat x Lon array of training members' SST means
    
    Xtrain_std: numpy array
        Lat x Lon array of training members' SST standard deviations
    
    Ytrain_median: float
        Median of T2M training at location lat,lon
    '''
    
    for t, trainmem in enumerate(TRAINmem):
        print('Loading X training member '+str(trainmem))
        xFINAME = RUN+'_ens'+str(trainmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'_2.5x2.5.nc'
        X = xr.open_dataarray(DIR+xFINAME)
        X = X.where(X.time.dt.year >= 2050, drop=True)
        X = X[:-1*LEAD]
        X = is_month(X,[9,10,11,12,1])
        X = X.where((X.lat <= 20) & (X.lat >= -20),drop=True)
        
        if t == 0:
            Xall = xr.DataArray(np.zeros(shape=(len(TRAINmem),np.shape(X)[0],np.shape(X)[1],np.shape(X)[2]),dtype='float')+np.nan,
                                    name='SST',
                                    dims=('ens','time','lat','lon'),
                                    coords=[('ens',TRAINmem),
                                            ('time',X.time),
                                            ('lat',X.lat),('lon',X.lon)])
            
        Xall[t] = X

    Xall_stacked  = Xall.stack(time_all = ('ens','time'))
    Xall_stackedT = Xall_stacked.transpose('time_all','lat','lon')

    Xtrain_std    = np.nanstd(Xall_stackedT,axis=0)
    Xtrain_mean   = np.nanmean(Xall_stackedT, axis=0)
    
    Xtrain  = (Xall_stackedT - Xtrain_mean) / Xtrain_std
    Xtrain  = Xtrain.stack(z=('lat','lon'))
    
    ##########################################################################
    
    for t, trainmem in enumerate(TRAINmem):
        print('Loading Y training member '+str(trainmem))
        Y = temp_regionalmean(DIR = DIR,
                              RUN = RUN,
                              MEMstr = MEMstr,
                              LEAD = LEAD,
                              MEM = trainmem,
                              lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                              left_ilon = left_ilon, right_ilon = right_ilon)
        
        if t == 0:
            Yall = xr.DataArray(np.zeros(shape=(len(TRAINmem),np.shape(Y)[0]),dtype='float')+np.nan,
                                    name='T2m',
                                    dims=('ens','time'),
                                    coords=[('ens',TRAINmem),
                                            ('time',Y.time)])
        
    
        Yall[t] = Y

    Yall_stacked = Yall.stack(time_all=('ens','time'))
    
    Ytrain_median = np.median(Yall_stacked)
    Ytrain = Yall_stacked - Ytrain_median
    Ytrain[np.where(Ytrain>=0)[0]] = 1
    Ytrain[np.where(Ytrain<0)[0]] = 0
    
    return Xtrain, Ytrain, Xtrain_mean, Xtrain_std, Ytrain_median
 

#-----------------------------------------------------------------------------
def val_future(DIR, RUN, LEAD, VALmem, MEMstr, Xtrain_mean, Xtrain_std, Ytrain_median, lower_ilat, upper_ilat, left_ilon, right_ilon):
    
    '''
    Load X (SST) & Y (T2M) data from SAI or SSP2-4.5 and return
    validation data.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    DIR: str
        directory path where SST and T2M data is located
    VALmem: list
        The member(s) used for validation (e.g. 3 = member 3)
        --> this/these are the member(s) loaded in this fuction
    MEMstr: str
        The members used for detrending and removing the seasonal cycle (TRAINstr + validation member)
        --> purely an informational str about how each member was preprocessed
    
    Xtrain_mean: numpy array
        Lat x Lon array of training members' SST means
    Xtrain_std: numpy array
        Lat x Lon array of training members' SST standard deviations
    Ytrain_median: float
        Median of T2M training members at location lat,lon
    lat,lon: int
        Index of the lat and lon location of T2M being predicted
        
    Returns:
    --------
    X_val: numpy array
        SST data used for validation (many members)
    
    Y_val: numpy array
        T2M data used for validation at LEAD = LEAD (many members)
        Converted into 0s and 1s
        
    lattxt,lontxt: str
        lat and lon str for location being predicted
        --> Used in saving model file
    '''
    
    xFINAME = RUN+'_ens'+str(VALmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'_2.5x2.5.nc'
    X = xr.open_dataarray(DIR+xFINAME)
    X = X.where(X.time.dt.year >= 2050, drop=True)
    X = X[:-1*LEAD]
    X = is_month(X,[9,10,11,12,1])
    X = X.where((X.lat <= 20) & (X.lat >= -20),drop=True)
    X = (X - Xtrain_mean) / Xtrain_std
    
    Xval = X.stack(z=('lat','lon'))
    
    ##########################################################################
    Y = temp_regionalmean(DIR = DIR,
                          RUN = RUN,
                          MEMstr = MEMstr,
                          LEAD = LEAD,
                          MEM = VALmem,
                          lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                          left_ilon = left_ilon, right_ilon = right_ilon)
    
    Yval = Y - Ytrain_median
    Yval[np.where(Yval>=0)] = 1
    Yval[np.where(Yval<0)] = 0
        
    return Xval, Yval

#-----------------------------------------------------------------------------
def test_future(LEAD, TESTmem, DIR, RUN, MEMstr, Xtrain_mean, Xtrain_std, Ytrain_median, lower_ilat, upper_ilat, left_ilon, right_ilon):

    '''
    Load X (SST) & Y (T2M) data from control or SAI run (>=2050) and return
    base run testing data. These are the member(s) not used in training and validation.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    NUMMEMS: int
        number of members to loop through and load into a single array
    DIR: str
        directory path where SST and T2M data is located
    RUN: str
        Either 'control' or 'SAI' to denote whether to load in data following SSP2-4.5 or SAI-1.5 scenarios
    MEMstr: std
        The members used for detrending and removing the seasonal cycle (TRAINstr + validation member)
        --> purely an informational str about how each member was preprocessed
    
    Xtrain_mean: numpy array
        Lat x Lon array of training members' SST means
    Xtrain_std: numpy array
        Lat x Lon array of training members' SST standard deviations
    Ytrain_median: float
        Median of T2M training members at location lat,lon
    lat,lon: int
        Index of the lat and lon location of T2M being predicted
        
    Returns:
    --------
    X_test: numpy array
        SST data used for testing (many members)
    
    Y_test: numpy array
        T2M data used for testing at LEAD = LEAD (many members)
        Converted into 0s and 1s
        
    lattxt,lontxt: str
        lat and lon str for location being predicted
        --> Used in saving files
    '''
    xFINAME = RUN+'_ens'+str(TESTmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'_2.5x2.5.nc'
    X = xr.open_dataarray(DIR+xFINAME)
    X = X.where(X.time.dt.year >= 2050, drop=True)
    X = X[:-1*LEAD]
    X = is_month(X,[9,10,11,12,1])
    X = X.where((X.lat <= 20) & (X.lat >= -20),drop=True)
    X = (X - Xtrain_mean) / Xtrain_std
    
    Y = temp_regionalmean(DIR = DIR,
                          RUN = RUN,
                          MEMstr = MEMstr,
                          LEAD = LEAD,
                          MEM = TESTmem,
                          lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                          left_ilon = left_ilon, right_ilon = right_ilon)
    
    Ytest = Y - Ytrain_median
    Ytest[np.where(Ytest>=0)] = 1
    Ytest[np.where(Ytest<0)] = 0
  
    ##########################################################################
    Xtest = X.stack(z=('lat','lon'))

    return Xtest, Ytest

#-----------------------------------------------------------------------------
def balance_classes(data):
    # Make validation classes balanced (2 classes)
    n_zero = np.shape(np.where(data==0)[0])[0]
    n_one  = np.shape(np.where(data==1)[0])[0]
    i_zero = np.where(data==0)[0]
    i_one  = np.where(data==1)[0]
    
    if n_one > n_zero:
        isubset_one = np.random.choice(i_one,size=n_zero,replace=False)
        i_new = np.sort(np.append(i_zero,isubset_one))
    elif n_one < n_zero:
        isubset_zero = np.random.choice(i_zero,size=n_one,replace=False)
        i_new = np.sort(np.append(isubset_zero,i_one))
    else:
        i_new = np.arange(0,len(data))
    
    return i_new
    
    
