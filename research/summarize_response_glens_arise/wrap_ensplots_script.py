''' wrap_ensplots_script
Runs ensemble plotting functions in fun_ens_plot. To replicate figures from
Hueholt et al. 2023 "Assessing Outcomes in Stratospheric Aerosol Injection
Scenarios Shortly After Deployment" directly, see
wrap_paperplots_basicplots_script.

dataDict: defines input data
setDict: settings for analysis/visualization
    areaAvgBool: sets area averaging behavior, more accurately named areaAvgFlag
        True: plot area average
        'sum': plot area sum (e.g. for ice extent)
    styleFlag: choose preset visual style for ens_spread_timeseries figures
        0: code takes its best guess for all aesthetics
        1: only plot the timeseries curves
        2: aesthetics used in Hueholt et al. 2023
        3: for IPCC-defined region figures in Open Science Foundation archive
outDict: output image settings
loopDict: determines which images are made

Written by Daniel Hueholt | February 2022
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

import matplotlib.pyplot as plt
from matplotlib import cm
import cmocean
import numpy as np

import fun_ens_plot as fep
import fun_convert_unit as fcu
import fun_process_data as fpd
import region_library as rlib

# Dictionaries
dataDict = {
    "dataPath": '/Users/dhueholt/Documents/GLENS_data/extreme_sdii/',
    "idGlensCntrl": 'control_*', #'control_*' or None
    "idGlensFdbck": 'feedback_*', #'feedback_*' or None
    "idArise": '*SSP245-TSMLT-GAUSS*', #'*SSP245-TSMLT-GAUSS*' or None
    "idS245Cntrl": '*BWSSP245*', #'*BWSSP245*' or None
    "idS245Hist": '*BWHIST*', #'*BWHIST*' or None
    "mask": '/Users/dhueholt/Documents/Summery_Summary/cesm_atm_mask.nc' #cesm_component_mask.nc
}
setDict = {
    "landmaskFlag": 'land', # None or 'land'
    "areaAvgBool": True, # see docstring for valid inputs
    "convert": None, #TUPLE of converter(s), or None if using default units
    "realization": 'ensplot',
    "styleFlag": 0, # see docstring for valid inputs
    "mute": False, #True/False to use image muting on parts of time period
    "ylim": None, #None for automatic, [min,max] for manual
    "ylabel": '', #None for automatic
    "yticks": None, #None for automatic, np.arange(mn,mx,step) for manual
    "xticks": True, #True/False to enable/disable x-axis tick labels
}
outDict = {
    "savePath": '/Users/dhueholt/Documents/GLENS_fig/20230206_distill/',
    "addToSaveStr": None,
    "dpiVal": 400
}
loopDict = {
    "levels": (None,), #'stratosphere', 'troposphere', 'total', numeric level(s), or None for surface variable
    "regions": ('global', rlib.Amazon(), rlib.Sahara(), rlib.WestNorthAmerica(), rlib.NorthEurope()) #rlib.region() for single (rlib.region(), rlib.region()) to concatenate)
}

ic(dataDict, setDict, outDict) #Lowers chances of making the wrong plots by mistake

# Make images
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
for lev in loopDict["levels"]:
    setDict["levOfInt"] = lev
    for reg in loopDict["regions"]:
        setDict["regOfInt"] = reg
        # fep.plot_ens_spaghetti_timeseries(scnList, dataDict, setDict, outDict)
        fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict)
