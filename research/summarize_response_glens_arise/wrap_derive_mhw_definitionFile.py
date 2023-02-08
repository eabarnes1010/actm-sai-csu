'''wrap_derive_mhw_definitionFile
Defines MHW baseline for reference period at a given location. By convention,
MHWs are usually calculated for a POINT, but the code allows for a regional
average to be used if desired.

This code is cumbersome! The workflow established here turned out to be
very inefficient and will be rethought before future work on MHWs. In
particular, this requires the input data to already be restricted to the
intended baseline period (here 2010-2019). Additionally, output files cannot
include lat/lon dimensions, i.e. they must either be calculated for a single
point or an area average. This code is retained because it works adequately to
calculate MHWs at a specific point as used in Hueholt et al. 2023 "Assessing
Outcomes in Stratospheric Aerosol Injection Scenarios Shortly After Deployment".

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''
from icecream import ic
import sys

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import xarray as xr
import numpy as np
from datetime import date
import marineHeatWaves as mhws

import fun_process_data as fpd
import region_library as rlib

# Note data ID keys are slightly different than most wrap_ scripts because
# these have raw-type filenames)!
dataDict = {
    "dataPath": '/Users/dhueholt/Documents/GLENS_data/daily_SST/GLENS_defsPeriod/',
    "idGlensCntrl": '*control*', #'*control*' or None
    "idGlensFdbck": '*feedback*', #'*feedback*' or None
    "idArise": None, #'*SSP245-TSMLT-GAUSS*' or None
    "idS245Cntrl": None, # '*BWSSP245*' or None
    "idS245Hist": None, #'*BWHIST*' or None
    "mask": '/Users/dhueholt/Documents/Summery_Summary/cesm_atm_mask.nc'
}
setDict = {
    "landmaskFlag": None, # None no mask, 'land' to mask ocean, 'ocean' to mask land
    "areaAvgBool": True, # only True for this script
    "convert": None, # TUPLE of converter(s), or None if using default units
    "realization": 'ensplot', # not a plot, but should be 'ensplot' here
    "regOfInt": (rlib.WesternAustraliaMHW_point(),), # rlib.WesternAustraliaMHW_point used for Hueholt et al. 2023
}
outDict = {
    "outKeyMn": "mn_SST",
    "savePath": '/Users/dhueholt/Documents/GLENS_fig/20230207_moreDistill/'
    # "savePath": '/Users/dhueholt/Documents/GLENS_fig/20220401_mhwLastSteps/2_defHistAr/',
}

for reg in setDict["regOfInt"]:
    darrList, cmnDict = fpd.call_to_open(dataDict, setDict) #Long because of I/O overhead on daily data
    for darr in darrList: #for each scenario
        ic(reg)
        darrPoint, locStr, locTitleStr = fpd.manage_area(darr, reg, areaAvgBool=setDict["areaAvgBool"])
        darrPointFullTimes = darrPoint.resample(time='1D').asfreq() #Add missing timesteps with NaN value
        rlzMnInd = len(darrPointFullTimes.realization)-1 #last realization index is mean
        rmn = darrPointFullTimes.isel(realization=rlzMnInd).data.squeeze()

        times = darrPointFullTimes.time.data
        ordArr = fpd.make_ord_array(times)

        rlzMnClimDset = xr.Dataset(
            {outDict["outKeyMn"]: (("time"), rmn)},
            coords={
                "time": (('time'), ordArr),
            }
        )
        rlzMnClimDset[outDict["outKeyMn"]].attrs = darrPointFullTimes.attrs
        rlzMnClimDset[outDict["outKeyMn"]].attrs['long_name'] = 'Ensemble mean SST'
        rlzMnClimDset[outDict["outKeyMn"]].attrs['lat'] = reg["regLats"]
        rlzMnClimDset[outDict["outKeyMn"]].attrs['lon'] = reg["regLons"]

        if 'GLENS:Control' in darrPointFullTimes.scenario:
            scnStr = 'GLENS'
        elif 'ARISE:Control' in darrPointFullTimes.scenario:
            scnStr = 'ARISE'
        else:
            ic('Unknown scenario!')
            scnStr = 'unknown'

        strOutRlzMn = 'mhwDefsFile_' + scnStr + '_' + reg["regSaveStr"]
        outFileRlzMn = outDict["savePath"] + strOutRlzMn + '.nc'
        rlzMnClimDset.to_netcdf(outFileRlzMn) #Save data
        # ic(strOutRlzMn, outFileRlzMn, rlzMnClimDset) #troubleshooting
