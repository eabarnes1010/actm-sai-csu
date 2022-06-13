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

def temp_regionalmean(DIR, RUN, MEMstr, LEAD, MEM, lower_ilat, upper_ilat, left_ilon, right_ilon):
    '''
    Load Y (T2M) data for specific 'RUN' and return the T2m spatial mean for the specified region.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    DIR: str
        directory path where SST and T2M data is located
    RUN: str
        the scenario/run to reference the correct file
    MEM: list
        The member(s) being processed (e.g. 3 = member 3)
        --> this/these are the member(s) loaded in this fuction
    MEMstr: str
        The members used for detrending and removing the seasonal cycle
        --> purely an informational str about how each member was preprocessed
    lower_ilat, upper_ilat: int
        the southern and northern most latitudes of the region of T2M being predicted
    left_ilon, right_ilon: int
        the western and eastern most longitudes of the region of T2M being predicted
        
    Returns:
    --------
    Yregion: Xarray
        Mean T2M for specified region
    '''
    
    
    landmask = xr.open_dataset('/Volumes/Elements_External_HD/PhD/data/ARISE/raw/sftlf_fx_CESM2-WACCM_historical_r1i1p1f1_gn.nc')['sftlf']
    landmask = xr.where(landmask>50,x=1,y=np.nan)

    if RUN == 'base':
        yFINAME = 'control_ens'+str(MEM)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        Y = xr.open_dataarray(DIR+yFINAME) * landmask
        Y = Y.where(Y.time.dt.year <= 2034, drop=True)
    else:
        yFINAME = RUN+'_ens'+str(MEM)+'_T2m_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        Y = xr.open_dataarray(DIR+yFINAME) * landmask
        Y = Y.where(Y.time.dt.year >= 2050, drop=True)
        
    Yregion = Y[LEAD:,lower_ilat:upper_ilat,left_ilon:right_ilon].mean(dim = ['lat','lon'], skipna = True)
        
    return Yregion

#-----------------------------------------------------------------------------
def train_future(DIR, RUN, LEAD, TRAINmem, MEMstr, lower_ilat, upper_ilat, left_ilon, right_ilon):
    '''
    Load X (SST) & Y (T2M) data from SAI or SSP run (2050-2069) and return
    training data information.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    DIR: str
        directory path where SST and T2M data is located
    RUN: str
        the scenario/run to reference the correct file
    TRAINmem: list
        The members used for training
        --> these are the members loaded in this function
    MEMstr: str
        The members used for detrending and removing the seasonal cycle
            --> purely an informational str about how each member was preprocessed
    lower_ilat, upper_ilat: int
        the southern and northern most latitudes of the region of T2M being predicted
    left_ilon, right_ilon: int
        the western and eastern most longitudes of the region of T2M being predicted
        
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
        Median of T2M training for the region being predicted
    '''
    for t, trainmem in enumerate(TRAINmem):
        print('Loading X training member '+str(trainmem))
        xFINAME = RUN+'_ens'+str(trainmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        X = xr.open_dataarray(DIR+xFINAME)
        X = X.where(X.time.dt.year >= 2050, drop=True)
        X = X[:-1*LEAD]
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
    X_train = np.asarray(Xtrain,dtype='float')
    X_train[np.isnan(X_train)] = 0.
    
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
    Y_train = np.asarray(Ytrain)
    
    return X_train, Y_train, Xtrain_mean, Xtrain_std, Ytrain_median
 
#-----------------------------------------------------------------------------
def train_base(DIR, LEAD, TRAINmem, MEMstr, lower_ilat, upper_ilat, left_ilon, right_ilon):

    '''
    Load X (SST) & Y (T2M) data from base run (2015-2034) and return
    training data information.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    DIR: str
        directory path where SST and T2M data is located
    TRAINmem: list
        The members used for training
        --> these are the members loaded in this function
    MEMstr: str
        The members used for detrending and removing the seasonal cycle
            --> purely an informational str about how each member was preprocessed
    lower_ilat, upper_ilat: int
        the southern and northern most latitudes of the region of T2M being predicted
    left_ilon, right_ilon: int
        the western and eastern most longitudes of the region of T2M being predicted
        
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
        Median of T2M training for the region being predicted
    '''
    
    
    for t, trainmem in enumerate(TRAINmem):
        print('Loading X training member '+str(trainmem))
        xFINAME = 'control_ens'+str(trainmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'.nc'
        X = xr.open_dataarray(DIR+xFINAME)
        X = X.where(X.time.dt.year <= 2034, drop=True)
        X = X[:-1*LEAD]
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
    X_train = np.asarray(Xtrain,dtype='float')
    X_train[np.isnan(X_train)] = 0.
    
    ##########################################################################
    
    for t, trainmem in enumerate(TRAINmem):
        print('Loading Y training member '+str(trainmem))
        Y = temp_regionalmean(DIR = DIR,
                              RUN = 'base',
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
    Y_train = np.asarray(Ytrain)
    
    return X_train, Y_train, Xtrain_mean, Xtrain_std, Ytrain_median
      
#-----------------------------------------------------------------------------
def val_future(DIR, RUN, LEAD, VALmem, MEMstr, Xtrain_mean, Xtrain_std, Ytrain_median, lower_ilat, upper_ilat, left_ilon, right_ilon):
    
    '''
    Load X (SST) & Y (T2M) data from SSP or SAI run (2050-2069) and return
    validation data.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    DIR: str
        directory path where SST and T2M data is located
    RUN: str
        the scenario/run to reference the correct file
    VALmem: list
        The member(s) used for validation (e.g. 3 = member 3)
        --> this/these are the member(s) loaded in this fuction
    MEMstr: str
        The members used for detrending and removing the seasonal cycle
        --> purely an informational str about how each member was preprocessed
    
    Xtrain_mean: numpy array
        Lat x Lon array of training members' SST means
    Xtrain_std: numpy array
        Lat x Lon array of training members' SST standard deviations
    Ytrain_median: float
        Median of T2M training members for the region being predicted
    lower_ilat, upper_ilat: int
        the southern and northern most latitudes of the region of T2M being predicted
    left_ilon, right_ilon: int
        the western and eastern most longitudes of the region of T2M being predicted
        
    Returns:
    --------
    X_val: numpy array
        SST data used for validation (many members)
    
    Y_val: numpy array
        T2M data used for validation at LEAD = LEAD (many members)
        Converted into 0s and 1s
    '''
    
    xFINAME = RUN+'_ens'+str(VALmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'.nc'
    X = xr.open_dataarray(DIR+xFINAME)
    X = X.where(X.time.dt.year >= 2050, drop=True)
    X = X[:-1*LEAD]
    X = X.where((X.lat <= 20) & (X.lat >= -20),drop=True)
    X = (X - Xtrain_mean) / Xtrain_std
    
    Xval = X.stack(z=('lat','lon'))
    X_val = np.asarray(Xval,dtype='float')
    X_val[np.isnan(X_val)] = 0.
    
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
    Y_val = np.asarray(Yval)
        
    return X_val, Y_val

#-----------------------------------------------------------------------------
def val_base(DIR, LEAD, VALmem, MEMstr, Xtrain_mean, Xtrain_std, Ytrain_median, lower_ilat, upper_ilat, left_ilon, right_ilon):
    
    '''
    Load X (SST) & Y (T2M) data from base run (2015-2034) and return
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
        The members used for detrending and removing the seasonal cycle
        --> purely an informational str about how each member was preprocessed
    
    Xtrain_mean: numpy array
        Lat x Lon array of training members' SST means
    Xtrain_std: numpy array
        Lat x Lon array of training members' SST standard deviations
    Ytrain_median: float
        Median of T2M training members for the region being predicted
    lower_ilat, upper_ilat: int
        the southern and northern most latitudes of the region of T2M being predicted
    left_ilon, right_ilon: int
        the western and eastern most longitudes of the region of T2M being predicted
        
    Returns:
    --------
    X_val: numpy array
        SST data used for validation (many members)
    
    Y_val: numpy array
        T2M data used for validation at LEAD = LEAD (many members)
        Converted into 0s and 1s
    '''
    
    xFINAME = 'control_ens'+str(VALmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'.nc'
    X = xr.open_dataarray(DIR+xFINAME)
    X = X.where(X.time.dt.year <= 2034, drop=True)
    X = X[:-1*LEAD]
    X = X.where((X.lat <= 20) & (X.lat >= -20),drop=True)
    X = (X - Xtrain_mean) / Xtrain_std
    
    Xval = X.stack(z=('lat','lon'))
    X_val = np.asarray(Xval,dtype='float')
    X_val[np.isnan(X_val)] = 0.
    
    ##########################################################################
    Y = temp_regionalmean(DIR = DIR,
                          RUN = 'base',
                          MEMstr = MEMstr,
                          LEAD = LEAD,
                          MEM = VALmem,
                          lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                          left_ilon = left_ilon, right_ilon = right_ilon)
    
    Yval = Y - Ytrain_median
    Yval[np.where(Yval>=0)] = 1
    Yval[np.where(Yval<0)] = 0
    Y_val = np.asarray(Yval)
        
    return X_val, Y_val
    
#-----------------------------------------------------------------------------
def test_future(LEAD, TESTmem, DIR, RUN, MEMstr, Xtrain_mean, Xtrain_std, Ytrain_median, lower_ilat, upper_ilat, left_ilon, right_ilon):

    '''
    Load X (SST) & Y (T2M) data from SSP or SAI run (2050-2069) and return
    testing data.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    DIR: str
        directory path where SST and T2M data is located
    RUN: str
        the scenario/run to reference the correct file
    TESTmem: list
        The member(s) used for testing (e.g. 3 = member 3)
        --> this/these are the member(s) loaded in this fuction
    MEMstr: str
        The members used for detrending and removing the seasonal cycle
        --> purely an informational str about how each member was preprocessed
    
    Xtrain_mean: numpy array
        Lat x Lon array of training members' SST means
    Xtrain_std: numpy array
        Lat x Lon array of training members' SST standard deviations
    Ytrain_median: float
        Median of T2M training members for the region being predicted
    lower_ilat, upper_ilat: int
        the southern and northern most latitudes of the region of T2M being predicted
    left_ilon, right_ilon: int
        the western and eastern most longitudes of the region of T2M being predicted
        
    Returns:
    --------
    X_test: numpy array
        SST data used for validation (many members)
    
    Y_test: numpy array
        T2M data used for validation at LEAD = LEAD (many members)
        Converted into 0s and 1s
    '''
    xFINAME = RUN+'_ens'+str(TESTmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'.nc'
    X = xr.open_dataarray(DIR+xFINAME)
    X = X.where(X.time.dt.year >= 2050, drop=True)
    X = X[:-1*LEAD]
    X = X.where((X.lat <= 20) & (X.lat >= -20),drop=True)
    Xtest = (X - Xtrain_mean) / Xtrain_std
    
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
    Xtest_stacked = Xtest.stack(z=('lat','lon'))
    X_test = np.asarray(Xtest_stacked,dtype='float')
    X_test[np.isnan(X_test)] = 0.
    
    Y_test = np.asarray(Ytest)

    return X_test, Y_test

#-----------------------------------------------------------------------------
def test_base(LEAD, TESTmem, DIR, MEMstr, Xtrain_mean, Xtrain_std, Ytrain_median, lower_ilat, upper_ilat, left_ilon, right_ilon):

    '''
    Load X (SST) & Y (T2M) data from base run (2015-2034) and return
    testing data.
    
    Variables
    ----------
    LEAD: int
        the montly lead time between SST and T2M (e.g. LEAD = 2 --> Jan SST predicts March T2M)
    DIR: str
        directory path where SST and T2M data is located
    TESTmem: list
        The member(s) used for testing (e.g. 3 = member 3)
        --> this/these are the member(s) loaded in this fuction
    MEMstr: str
        The members used for detrending and removing the seasonal cycle
        --> purely an informational str about how each member was preprocessed
    
    Xtrain_mean: numpy array
        Lat x Lon array of training members' SST means
    Xtrain_std: numpy array
        Lat x Lon array of training members' SST standard deviations
    Ytrain_median: float
        Median of T2M training members for the region being predicted
    lower_ilat, upper_ilat: int
        the southern and northern most latitudes of the region of T2M being predicted
    left_ilon, right_ilon: int
        the western and eastern most longitudes of the region of T2M being predicted
        
    Returns:
    --------
    X_test: numpy array
        SST data used for validation (many members)
    
    Y_test: numpy array
        T2M data used for validation at LEAD = LEAD (many members)
        Converted into 0s and 1s
    '''
    
    xFINAME = 'control_ens'+str(TESTmem)+'_SST_2015-2069_detrended_ensmean'+MEMstr+'.nc'
    X = xr.open_dataarray(DIR+xFINAME)
    X = X.where(X.time.dt.year <= 2034, drop=True)
    X = X[:-1*LEAD]
    X = X.where((X.lat <= 20) & (X.lat >= -20),drop=True)
    Xtest = (X - Xtrain_mean) / Xtrain_std
    
    Y = temp_regionalmean(DIR = DIR,
                          RUN = 'base',
                          MEMstr = MEMstr,
                          LEAD = LEAD,
                          MEM = TESTmem,
                          lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                          left_ilon = left_ilon, right_ilon = right_ilon)
    
    Ytest = Y - Ytrain_median
    Ytest[np.where(Ytest>=0)] = 1
    Ytest[np.where(Ytest<0)] = 0
  
    ##########################################################################
    Xtest_stacked = Xtest.stack(z=('lat','lon'))
    X_test = np.asarray(Xtest_stacked,dtype='float')
    X_test[np.isnan(X_test)] = 0.
    
    Y_test = np.asarray(Ytest)

    return X_test, Y_test
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def balance_classes(data):
    # Make validation & testing classes balanced (2 classes)
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
    
    
