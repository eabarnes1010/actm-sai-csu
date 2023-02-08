''' fun_regrid_pop
Functions to regrid Parallel Ocean Model (POP) output from the B-grid to a
standard lat/lon using interpolation.

Originally written by Emily Gordon based on code provided by Zachary Labe
Modified by Daniel Hueholt
'''

from icecream import ic
import sys

import numpy as np
import xarray as xr
import scipy.interpolate as interp

def extract_pop_latlons(popFile,latName,lonName):
    ''' Extract lat/lons from the POP grid '''
    popgrid = xr.open_dataset(popFile)
    popLat = np.asarray(popgrid[latName].data)
    popLon = np.asarray(popgrid[lonName].data)

    return popLat, popLon

def regrid(dataIn,latIn,lonIn,latOut,lonOut):
    ''' Takes POP model output on a B-grid (T-cells for scalars,
    U-cells for vectors) (latInxlonIn) and regrids to (latOutxlonOut) '''

    lonOut,latOut = np.meshgrid(lonOut,latOut) # make grid
    dataRg = np.ravel(dataIn) # move inputs to vectors
    lonRg = np.ravel(lonIn)
    latRg = np.ravel(latIn)
    dataInterpRg = interp.griddata((latRg,lonRg),dataRg,(latOut,lonOut), method='linear')

    return dataInterpRg

def operate_regrid(inFile, dataVar, popLat, popLon):
    ''' Carry out regridding and data processing operations from input files '''
    popDataArray = xr.open_dataset(strv,decode_times=False)
    varOfInt = popDataArray[dataVar]
    time = popDataArray.time
    latNew = np.arange(-90,91,0.94240838)
    latNew = latNew[:-1]
    lonNew = np.arange(0,360,1.25)

    dataRegrid = np.empty((varOfInt.shape[0],latNew.shape[0],lonNew.shape[0]))
    for bc in range(varOfInt.shape[0]):
        newDat = regrid(varOfInt[bc,:,:],popLat,popLon,latNew,lonNew)
        dataRegrid[bc,:,:] = newDat

    newDset = xr.Dataset(
        {dataVar: (("time","lat","lon"), dataRegrid)},
        coords={
            "time": time,
            "lat": latNew,
            "lon": lonNew
        }
    )
    newDset.attrs = popDataArray.attrs
    newDset[dataVar].attrs = popDataArray[dataVar].attrs

    originalFilename = strv[0:len(strv)-3]
    strOut =  originalFilename + '_RG' + '.nc' #originalfilename_RG.nc
    newDset.to_netcdf(strOut)
    ic(strOut)

def operate_regrid_direct(popDataArray, popLat, popLon):
    ''' Carry out the regridding and data processing operations from direct
        DataArray input '''
    varOfInt = popDataArray.data
    time = popDataArray.time
    latNew = np.arange(-90,91,0.94240838)
    latNew = latNew[:-1]
    lonNew = np.arange(0,360,1.25)
    # popLat[popLat>90] = np.nan
    # popLon[popLon>360] = np.nan

    dataRegrid = np.empty((varOfInt.shape[0],latNew.shape[0],lonNew.shape[0]))
    for bc in range(varOfInt.shape[0]):
        newDat = regrid(varOfInt[bc,:,:],popLat,popLon,latNew,lonNew)
        dataRegrid[bc,:,:] = newDat

    dataKey = popDataArray.name
    newDset = xr.Dataset(
        {dataKey: (("time","lat","lon"), dataRegrid)},
        coords={
            "time": time,
            "lat": latNew,
            "lon": lonNew
        }
    )
    newDset[dataKey].attrs = popDataArray.attrs

    strOut = popDataArray.attrs['outFile'].replace(".nc","_RG.nc")
    outFile = popDataArray.attrs['outPath'] + strOut
    newDset.to_netcdf(outFile)
    ic(strOut, outFile, newDset)
