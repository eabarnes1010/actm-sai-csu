#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 13:19:32 2022

@author: Ariel L. Morrison
"""

def make_timeseries(numEns,var,lat,lon,latmax,latmin,lonmax,lonmin,dataDict):
    import numpy as np
    import warnings
    
    ens = ['001', '002', '003', '004', '006', '007', '008', '009', '010']
    numEns = len(ens)
    
    latmin_ind = int(np.abs(latmin-lat).argmin())
    latmax_ind = int(np.abs(latmax-lat).argmin())
    lonmin_ind = int(np.abs(lonmin-lon).argmin())
    lonmax_ind = int(np.abs(lonmax-lon).argmin())
    
    # Latitude weighting
    lonmesh,latmesh = np.meshgrid(lon,lat)
    
    # Mask out ocean and non-permafrost land:
    if var == 'ER':
        weights2D = {}
        for i in range(numEns):
            weights2D[ens[i]] = np.zeros((len(dataDict[ens[0]].year),len(lat),len(lon)))
            for iyear in range(len(dataDict[ens[0]].year)):
                weights2D[ens[i]][iyear,:,:] = np.cos(np.deg2rad(latmesh))
                weights2D[ens[i]][iyear,:,:][np.isnan(dataDict[ens[i]][iyear,:,:])] = np.nan
                # weights2D[i,iyear,:,:] = np.ma.array(weights2D[i,iyear,:,:], mask=np.isnan(dataDict[ens[i]][iyear,:,:]))
                # weights2D[i,iyear,:,:] = np.ma.masked_where(np.isnan(dataDict[ens[i]][iyear,:,:]),weights2D[i,iyear,:,:])

    else:
        weights2D = np.cos(np.deg2rad(latmesh))
    
    # Annual time series for each ensemble member
    ensMemberTS = {}
    for ensNum in range(numEns):
        warnings.simplefilter("ignore")
        if var == 'ALT':
            ensMasked = dataDict[ens[ensNum]].where(dataDict[ens[ensNum]] < 40.) # xarray where = keep
            weights2D = np.ma.masked_where(np.nanmean(dataDict[ens[ensNum]],axis=0) > 40., weights2D) # numpy where = discard
            ensMasked_grouped = ensMasked[:,latmin_ind:latmax_ind,lonmin_ind:lonmax_ind].groupby('time.year').mean(dim='time',skipna=True)
            ensMemberTS[ens[ensNum]] = np.array([np.average((np.ma.MaskedArray(ensMasked_grouped,mask=np.isnan(ensMasked_grouped)))[i], weights=weights2D[latmin_ind:latmax_ind,lonmin_ind:lonmax_ind]) for i in range((ensMasked_grouped.shape)[0])])
        elif var == 'ER':
            # weights = np.cos(np.deg2rad(latmesh[latmin_ind:latmax_ind,lonmin_ind:lonmax_ind]))#weights2D[ens[ensNum]][:,latmin_ind:latmax_ind,lonmin_ind:lonmax_ind]
            ensMasked         = dataDict[ens[ensNum]]
            ensMasked_grouped = ensMasked[:,latmin_ind:latmax_ind,lonmin_ind:lonmax_ind]
            ensMasked_grouped = np.ma.MaskedArray(ensMasked_grouped, mask=np.isnan(ensMasked_grouped))
            weights           = weights2D[ens[ensNum]][:,latmin_ind:latmax_ind,lonmin_ind:lonmax_ind]
            weights           = np.ma.asanyarray(weights)
            weights.mask      = ensMasked_grouped.mask
            ensMemberTS[ens[ensNum]] = np.array([np.ma.average(
                                                ensMasked_grouped[i],
                                                weights=weights[i]
                                                ) for i in range((ensMasked_grouped.shape)[0])])
        else:
            ensMasked = dataDict[ens[ensNum]]
            ensMasked_grouped = ensMasked[:,latmin_ind:latmax_ind,lonmin_ind:lonmax_ind].groupby('time.year').mean(dim='time',skipna=True)
            ensMemberTS[ens[ensNum]] = np.array([np.ma.average(ensMasked_grouped[i], weights=weights2D[latmin_ind:latmax_ind,lonmin_ind:lonmax_ind]) for i in range((ensMasked_grouped.shape)[0])])

    # Ensemble mean
    ensMeanTS = 0
    for val in ensMemberTS.values():
        ensMeanTS += val
    ensMeanTS = ensMeanTS/numEns   
    return ensMeanTS, ensMemberTS
