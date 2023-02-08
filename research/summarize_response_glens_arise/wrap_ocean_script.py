'''  wrap_ocean_script
Runs functions to process Parallel Ocean Model (POP) output into friendlier
form. Uses multiprocessing when possible for efficiency.
Before running: untar (run_untar_prep) and CDO (run_cdo_prep)
In script:
    If 3D, extracts 2D field like SST or UOHC from 3D output
    Regrids data to standard lat/lon grid using interpolation
    Saves new field of regridded data as netCDF file
After running: regridded data is ready for plotting (wrap_basicplots_script)

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
Regridding code originally written by Emily Gordon based on code provided by
Zachary Labe.
'''

from icecream import ic
import sys

import glob
from multiprocessing import Process
import numpy as np
import xarray as xr

import fun_calc_vars as fcv
import fun_regrid_pop as frp
import fun_process_data as fpd

# Inputs
# dataPath = '/glade/scratch/dhueholt/monthly_OCNO2/' #CASPER
dataPath = '/Users/dhueholt/Documents/GLENS_data/monthly_aice/selname/sept/' #LOCAL
# outPath = '/glade/scratch/dhueholt/monthly_OCNO2/regrid/' #CASPER
outPath = '/Users/dhueholt/Documents/GLENS_data/monthly_aice/selname/sept/regrid/' #LOCAL
dataVar = 'aice' #Manually set data variable
extract2d = False #fun_calc_vars function handle or False
nProc = 1 #Spawn nProc+1 (due to zero indexing) processes for regridding

# Open files
strList = sorted(glob.glob(dataPath + "*.nc"))
dataList = list()
for fc,fv in enumerate(strList):
    glensDset = xr.open_dataset(fv) #Open files separately as times may be mismatched
    if fc == 0:
        dataVar = fpd.discover_data_var(glensDset) #Automatically detect data variable
    glensDarr = glensDset[dataVar]
    glensDarr.attrs['inFile'] = fv.replace(dataPath,"")
    glensDarr.attrs['outPath'] = outPath
    dataList.append(glensDarr) #Place in single list

# Extract 2D field (as written, regridding is a 2D process)
data2dList = list()
if not(extract2d): #If False entry, data is already 2D (ex: SSH data)
    for darr in dataList:
        darr.attrs['outFile'] = darr.attrs['inFile']
        data2dList.append(darr)
else:
    for darr in dataList:
        darr.attrs['outFile'] = darr.attrs['inFile']
        darr2d = extract2d(darr, dataVar) #Use the fcv function input to extract 2D field (ex: UOHC from pot. temp.)
        data2dList.append(darr2d)

# Regrid to standard lat/lon and save
# inPop = '/glade/work/dhueholt/grids/control_IFRAC_useForGrid.nc' #CASPER
inPop = '/Users/dhueholt/Documents/GLENS_data/grids/control_IFRAC_useForGrid.nc' #LOCAL
inNames = ['TLAT','TLONG'] #'TLAT','TLONG' for POP, 'lat', 'lon'
popLat,popLon = frp.extract_pop_latlons(inPop,inNames[0],inNames[1])

for dc, dv in enumerate(data2dList):
    lenDat = len(data2dList)
    if __name__== '__main__': #If statement required by multiprocessing
        shard = Process(target=frp.operate_regrid_direct, args=(dv, popLat, popLon)) #Shard processes regrid files and save data in parallel
        if dc % nProc == 0 and dc != 0:
            shard.start()
            shard.join() #Forces nProc+1 processes to run to completion before starting more
            shard.close() #Free up all associated resources to prevent machine from being overwhelmed
        else:
            shard.start()
        filesRemaining = lenDat - dc - 1
        numleft = ic(filesRemaining) #Cheap "progress bar"
