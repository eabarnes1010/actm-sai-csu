# -*- coding: utf-8 -*-
"""
Created on July 21, 2022

@author: Ariel L. Morrison

Function to read in CESM2-WACCM6 (historical), 
SSP2-4.5 (control) and ARISE-SAI-1.5 (experiment) data
"""
import os; os.chdir('/Users/arielmor/Desktop/SAI/scripts/')
datadir = '/Users/arielmor/Desktop/SAI/data/ARISE/data'

def growing_season(month):
    ## April-October ##
    return (month >=4) & (month <=10)

def readData(datadir, var, CONTROL):
    import xarray as xr
    import pandas as pd
    
    myvar = {}
    myvarAnn = {}
    myvarGS = {}
    myvarOct = {}
    ens = ['001','002','003','004','006','007','008','009','010']
    numEns = len(ens)
    
    ## ---- SSP2-4.5 ---- ##
    if CONTROL:
        print("reading " + str(var) + " (control)")
        for i in range(numEns):
            ds = xr.open_dataset(datadir + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + str(ens[i]) + 
                                 '.clm2.h0.' + str(var) + '.201501-206412_NH.nc',decode_times=False)
            units, reference_date = ds.time.attrs['units'].split('since')
            ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
            lat = ds.lat
            lon = ds.lon
            time = ds.time
            '''
            Soil column only goes to 42m, so CESM2 has no permafrost below
            42m. Active layer > 39 means CESM2 has no pfrost in that cell
            '''
            myvar[ens[i]] = ds[str(var)]
            myvar[ens[i]] = myvar[ens[i]].where(myvar[ens[i]] <= 39.)
            myvarGS[ens[i]] = myvar[ens[i]].sel(time=growing_season(myvar[ens[i]]['time.month']))
            myvarAnn[ens[i]] = myvar[ens[i]].groupby('time.year').mean(dim='time', skipna = True)
            myvarOct[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 10)
            ds.close()
        return lat,lon,myvar,myvarGS,myvarAnn,myvarOct,ens,time
    
    ## ---- ARISE-SAI-1.5 ---- ##
    else:
        print("reading " + str(var) + " (feedback)")
        for i in range(numEns):
            ds = xr.open_dataset(datadir + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + str(ens[i]) + 
                                 '.clm2.h0.' + str(var) + '.203501-206912_NH.nc',decode_times=False)
            units, reference_date = ds.time.attrs['units'].split('since')
            ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
            lat = ds.lat
            lon = ds.lon
            time = ds.time
            myvar[ens[i]] = ds[str(var)]
            myvar[ens[i]] = myvar[ens[i]].where(myvar[ens[i]] <= 39.)
            myvarGS[ens[i]] = myvar[ens[i]].sel(time=growing_season(myvar[ens[i]]['time.month']))
            myvarAnn[ens[i]] = myvar[ens[i]].groupby('time.year').mean(dim='time', skipna = True)
            myvarOct[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 10)
            ds.close()
        return lat,lon,myvar,myvarGS,myvarAnn,myvarOct,ens,time
        

def read_historical(var):
    import xarray as xr
    import pandas as pd
    ds = xr.open_dataset('/Users/arielmor/Desktop/SAI/data/CESM2/b.e21.BWHIST.f09_g17.CMIP6-historical-WACCM.001.clm2.h0.' + str(var) + '.185001-201412_NH.nc', decode_times=False)
    units, reference_date = ds.time.attrs['units'].split('since')
    ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
    myvar = ds[str(var)]
    myvar = myvar.where(myvar <= 39.)
    myvarGS = myvar.sel(time=growing_season(myvar['time.month']))
    myvarAnn = myvar.groupby('time.year').mean(dim='time', skipna = True)
    ds.close()   
    return myvar,myvarGS,myvarAnn
