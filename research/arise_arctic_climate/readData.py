# -*- coding: utf-8 -*-
"""
Created on July 21, 2022

@author: Ariel L. Morrison

- Function to read in CESM2-WACCM6 (historical), 
SSP2-4.5 (control) and ARISE-SAI-1.5 (experiment) data
- Can read in active layer depth (ALT), soil respiration rate
(ER) or net ecosystem exchange (NEE)
"""
import os

os.chdir('/Users/arielmor/Projects/actm-sai-csu/research/arise_arctic_climate')
datadir = '/Users/arielmor/Desktop/SAI/data/ARISE/data'


def growing_season(month):
    ## April-September ##
    return (month >= 4) & (month <= 9)


def readData(datadir, var, controlSim):
    import xarray as xr
    import pandas as pd
    import numpy as np

    '''
    Can use maps for annual (ANN), growing season (April-September, GS), 
    non-growing season (October-March, NGS),each season, and each
    individual month to predict the simluation. 
    '''
    myvar = {}
    myvarAnn = {}
    myvarGS = {}
    myvarNGS = {}
    myvarWinter = {}
    myvarSpring = {}
    myvarSummer = {}
    myvarFall = {}
    myvarFeb = {}
    myvarMarch = {}
    myvarApril = {}
    myvarMay = {}
    myvarJune = {}
    myvarJuly = {}
    myvarAug = {}
    myvarSept = {}
    myvarOct = {}
    myvarNov = {}
    myvarDec = {}
    ens = ['001', '002', '003', '004', '006', '007', '008', '009', '010']
    numEns = len(ens)

    ## ---- SSP2-4.5 ---- ##
    if controlSim:
        print("reading " + str(var) + " (control)")
        if var == 'ALT':
            for i in range(numEns):
                ds = xr.open_dataset(datadir + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + str(ens[i]) +
                                     '.clm2.h0.' + str(var) + '.201501-206412_NH.nc', decode_times=False)
                units, reference_date = ds.time.attrs['units'].split('since')
                ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
                lat = ds.lat
                lon = ds.lon
                time = ds.time
                myvar[ens[i]] = ds[str(var)]
                '''
                Soil column only goes to 42m, so CESM2 has no permafrost below
                42m. Active layer > 39 means CESM2 has no pfrost in that cell
                '''
                myvar[ens[i]] = myvar[ens[i]].where(myvar[ens[i]] <= 39.)
                ds.close()
                myvarGS[ens[i]] = myvar[ens[i]].sel(time=growing_season(myvar[ens[i]]['time.month'])).groupby(
                    'time.year').mean(dim='time', skipna=True)
                myvarAnn[ens[i]] = myvar[ens[i]].groupby('time.year').mean(dim='time', skipna=True)
                myvarSpring[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.season'] == 'MAM').groupby(
                    'time.year').mean(dim='time', skipna=True)
                myvarSummer[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.season'] == 'JJA').groupby(
                    'time.year').mean(dim='time', skipna=True)
                myvarFall[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.season'] == 'SON').groupby('time.year').mean(
                    dim='time', skipna=True)
                myvarFeb[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 2)
                myvarMarch[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 3)
                myvarApril[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 4)
                myvarMay[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 5)
                myvarJune[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 6)
                myvarJuly[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 7)
                myvarAug[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 8)
                myvarSept[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 9)
                myvarOct[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 10)
                myvarNov[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 11)
                myvarDec[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 12)   
                
                # make winter season
                years = np.linspace(2015, 2064)
                myvarWinter[ens[i]] = np.zeros((49, len(lat), len(lon)))
                for iyear in range(len(years) - 1):
                    myvarWinter[ens[i]][iyear:(iyear + 1), :, :] = myvar[ens[i]].sel(
                        time=slice(str(int(years[iyear])) + '-12-01', str(int(years[iyear + 1])) + '-02-28')).mean(
                        dim='time', skipna=True)
                # make non-growing season
                myvarNGS[ens[i]] = np.zeros((49, len(lat), len(lon)))
                for iyear in range(len(years) - 1):
                    myvarNGS[ens[i]][iyear:(iyear + 1), :, :] = myvar[ens[i]].sel(
                        time=slice(str(int(years[iyear])) + '-10-01', str(int(years[iyear + 1])) + '-03-31')).mean(
                        dim='time', skipna=True)  
            return lat, lon, myvar, myvarGS, myvarNGS, myvarAnn, myvarWinter, myvarSpring, myvarSummer, myvarFall,\
                myvarFeb, myvarMarch, myvarApril, myvarMay, myvarJune, myvarJuly, myvarAug, myvarSept, myvarOct,\
                    myvarNov, myvarDec, ens, time
                
        elif var == 'ER' or var == 'NEE':
            myvarCum = {}
            for i in range(numEns):
                ds = xr.open_dataset(datadir + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + str(ens[i]) +
                                     '.clm2.h0.' + str(var) + '.201501-206412_NH.nc', decode_times=False)
                units, reference_date = ds.time.attrs['units'].split('since')
                ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
                lat = ds.lat
                lon = ds.lon
                time = ds.time[240:]
                myvar[ens[i]] = ds[str(var)][240:,:,:]
                ds.close()
                # active layer depth to mask for permafrost
                ds = xr.open_dataset(datadir + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + str(ens[i]) +
                                     '.clm2.h0.ALTMAX.201501-206412_NH.nc', decode_times=False)
                units, reference_date = ds.time.attrs['units'].split('since')
                ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
                ALTMAX = (ds.ALTMAX[240:,:,:]).where(ds.ALTMAX[240:,:,:] <= 39.).groupby('time.year').mean(dim='time',skipna=True)
                ds.close()
                myvar[ens[i]] = (myvar[ens[i]] * time.dt.daysinmonth * 86400.).groupby('time.year').sum(dim='time',skipna=True)
                myvarCum[ens[i]] = (myvar[ens[i]].cumsum(axis=0)).where(ALTMAX.notnull())
            return lat, lon, myvarCum, ens, time
        
        elif var == 'GPP':
            for i in range(numEns):
                ds = xr.open_dataset(datadir + '/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + str(ens[i]) +
                                      '.clm2.h0.' + str(var) + '.201501-206412_NH.nc', decode_times=False)
                units, reference_date = ds.time.attrs['units'].split('since')
                ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
                lat = ds.lat
                lon = ds.lon
                time = ds.time[240:]
                myvar[ens[i]] = ds[str(var)][240:,:,:]
                myvar[ens[i]] = myvar[ens[i]] * ds.time.dt.daysinmonth * 86400.
                myvar[ens[i]] = myvar[ens[i]].groupby('time.year').sum(dim='time',skipna=True)
                ds.close()
            return lat, lon, myvar, ens, time
            
        
    ## ---- ARISE-SAI-1.5 ---- ##
    else:
        print("reading " + str(var) + " (feedback)")
        if var == 'ALT':
            for i in range(numEns):
                ds = xr.open_dataset(datadir + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + str(ens[i]) +
                                     '.clm2.h0.' + str(var) + '.203501-206912_NH.nc', decode_times=False)
                units, reference_date = ds.time.attrs['units'].split('since')
                ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
                lat = ds.lat
                lon = ds.lon
                time = ds.time
                myvar[ens[i]] = ds[str(var)]
                '''
                Soil column only goes to 42m, so CESM2 has no permafrost below
                42m. Active layer > 39 means CESM2 has no pfrost in that cell
                '''
                myvar[ens[i]] = myvar[ens[i]].where(myvar[ens[i]] <= 39.)
                ds.close()
            
                myvarGS[ens[i]] = myvar[ens[i]].sel(time=growing_season(myvar[ens[i]]['time.month'])).groupby(
                    'time.year').mean(dim='time', skipna=True)
                myvarAnn[ens[i]] = myvar[ens[i]].groupby('time.year').mean(dim='time', skipna=True)
                myvarSpring[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.season'] == 'MAM').groupby(
                    'time.year').mean(dim='time', skipna=True)
                myvarSummer[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.season'] == 'JJA').groupby(
                    'time.year').mean(dim='time', skipna=True)
                myvarFall[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.season'] == 'SON').groupby('time.year').mean(
                    dim='time', skipna=True)
                myvarFeb[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 2)
                myvarMarch[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 3)
                myvarApril[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 4)
                myvarMay[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 5)
                myvarJune[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 6)
                myvarJuly[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 7)
                myvarAug[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 8)
                myvarSept[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 9)
                myvarOct[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 10)
                myvarNov[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 11)
                myvarDec[ens[i]] = myvar[ens[i]].sel(time=myvar[ens[i]]['time.month'] == 12)  
                
                # make winter season
                years = np.linspace(2035, 2069, 35)
                myvarWinter[ens[i]] = np.zeros((34, len(lat), len(lon)))
                for iyear in range(len(years) - 1):
                    myvarWinter[ens[i]][iyear:(iyear + 1), :, :] = myvar[ens[i]].sel(
                        time=slice(str(int(years[iyear])) + '-12-01', str(int(years[iyear + 1])) + '-02-28')).mean(
                        dim='time', skipna=True)
                # make non-growing season
                myvarNGS[ens[i]] = np.zeros((49, len(lat), len(lon)))
                for iyear in range(len(years) - 1):
                    myvarNGS[ens[i]][iyear:(iyear + 1), :, :] = myvar[ens[i]].sel(
                        time=slice(str(int(years[iyear])) + '-10-01', str(int(years[iyear + 1])) + '-03-31')).mean(
                        dim='time', skipna=True)          
            return lat, lon, myvar, myvarGS, myvarNGS, myvarAnn, myvarWinter, myvarSpring, myvarSummer, myvarFall,\
                myvarFeb, myvarMarch, myvarApril, myvarMay, myvarJune, myvarJuly, myvarAug, myvarSept, myvarOct,\
                    myvarNov, myvarDec, ens, time
                    
        elif var == 'ER' or var == 'NEE':
            myvarCum = {}
            for i in range(numEns):
                ds = xr.open_dataset(datadir + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + str(ens[i]) +
                                     '.clm2.h0.' + str(var) + '.203501-206912_NH.nc', decode_times=False)
                units, reference_date = ds.time.attrs['units'].split('since')
                ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
                lat = ds.lat
                lon = ds.lon
                time = ds.time[:-60]
                myvar[ens[i]] = ds[str(var)][:-60,:,:]
                ds.close()
                # active layer depth to mask for permafrost
                ds = xr.open_dataset(datadir + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + str(ens[i]) +
                                     '.clm2.h0.ALTMAX.203501-206912_NH.nc', decode_times=False)
                units, reference_date = ds.time.attrs['units'].split('since')
                ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
                ALTMAX = (ds.ALTMAX[:-60,:,:]).where(ds.ALTMAX[:-60,:,:] <= 39.).groupby('time.year').mean(dim='time',skipna=True)
                ds.close()
                myvar[ens[i]] = (myvar[ens[i]] * time.dt.daysinmonth * 86400.).groupby('time.year').sum(dim='time',skipna=True)
                myvarCum[ens[i]] = (myvar[ens[i]].cumsum(axis=0)).where(ALTMAX.notnull())
            return lat, lon, myvarCum, ens, time
        
        elif var == 'GPP':
            for i in range(numEns):
                ds = xr.open_dataset(datadir + '/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + str(ens[i]) +
                                      '.clm2.h0.' + str(var) + '.203501-206912_NH.nc', decode_times=False)
                units, reference_date = ds.time.attrs['units'].split('since')
                ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
                lat = ds.lat
                lon = ds.lon
                time = ds.time
                myvar[ens[i]] = ds[str(var)][:-60,:,:]
                myvar[ens[i]] = myvar[ens[i]] * myvar[ens[i]].time.dt.daysinmonth * 86400.
                myvar[ens[i]] = myvar[ens[i]].groupby('time.year').sum(dim='time',skipna=True)
                ds.close()
            return lat, lon, myvar, ens, time


def read_historical(var):
    import xarray as xr
    import pandas as pd
    ds = xr.open_dataset(
        '/Users/arielmor/Desktop/SAI/data/CESM2/b.e21.BWHIST.f09_g17.CMIP6-historical-WACCM.001.clm2.h0.' + str(
            var) + '.185001-201412_NH.nc', decode_times=False)
    units, reference_date = ds.time.attrs['units'].split('since')
    ds['time'] = pd.date_range(start=reference_date, periods=ds.sizes['time'], freq='MS')
    myvar = ds[str(var)]
    myvar = myvar.where(myvar <= 39.)
    myvarGS = myvar.sel(time=growing_season(myvar['time.month'])).groupby('time.year').mean(dim='time', skipna=True)
    myvarAnn = myvar.groupby('time.year').mean(dim='time', skipna=True)
    ds.close()
    return myvar, myvarGS, myvarAnn
