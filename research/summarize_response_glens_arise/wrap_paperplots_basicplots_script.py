''' wrap_paperplots_basicplots_script
Replicates figures from Hueholt et al. 2023 "Assessing Outcomes in Stratospheric Aerosol Injection Scenarios Shortly After Deployment" directly.
Figures are produced in 1-panel format with no annotations. Keynote is used to
stitch panels together, add titles, colorbar, etc.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

import matplotlib.pyplot as plt
from matplotlib import cm
import cmocean
import cmasher
import seaborn
import numpy as np

import fun_basic_plot as fbp
import fun_convert_unit as fcu
import fun_process_data as fpd
import region_library as rlib

# Call regions
ipccWg1Ar5 = rlib.atlas_ipcc_wg1ar5() #ipccWg1Ar5["allRegions"]
testAllTypes = rlib.atlas_all_types() #testAllTypes["allRegions"]
gnsht = ('global', rlib.Arctic(), rlib.HudsonBay(), rlib.NorthernHemisphere(), rlib.SouthernHemisphere(),)

# Specials
tropicalPal = seaborn.diverging_palette(133, 324, as_cmap=True)
indRedPal = seaborn.diverging_palette(16.8, 270.2, s=100, l=40, as_cmap=True)
precipPal = seaborn.diverging_palette(58, 162, s=100, l=45, as_cmap=True)
xtPrecipPal = seaborn.diverging_palette(58, 162, s=100, l=30, as_cmap=True)

# Dictionaries
dataDict = {
    "dataPath": '/Users/dhueholt/Documents/GLENS_data/annual_TREFHT/',
    "idGlensCntrl": 'control_*', #'control_*' or None
    "idGlensFdbck": 'feedback_*', #'feedback_*' or None
    "idArise": '*SSP245-TSMLT-GAUSS*', #'*SSP245-TSMLT-GAUSS*' or None
    "idS245Cntrl": '*BWSSP245*', #'*BWSSP245*' or None
    "idS245Hist": '*BWHIST*', #'*BWHIST*' or None
    "mask": '/Users/dhueholt/Documents/Summery_Summary/cesm_atm_mask.nc'
}
setDict = {
    "landmaskFlag": None,
    "startIntvl": [2015,2020,2030,2035], #dg [2015,2020,2030,2035]
    "endIntvl": [2025,2030,2040,2045], #dg [2025,2030,2040,2045]
    "convert": (fcu.kel_to_cel,), #TUPLE of converter(s), or None if using default units
    "cmap": cmocean.cm.balance, #None for default cmocean "balance" or choose colormap here
    "cbVals": [-2,2], #None for automatic or [min,max] to override #dg
    "addCyclicPoint": False,
    "areaAvgBool": False,
    "robustnessBool": False,
    "plotPanel": 'snapR85'
}
outDict = {
    "savePath": '/Users/dhueholt/Documents/GLENS_fig/20230207_moreDistill/1_check/',
    "dpiVal": 400 #High-res for paper
}
ic(dataDict, setDict, outDict) #Lowers chances of making the wrong plots by mistake

# Make images
setDict["realization"] = 'ensplot'
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

# Annual mean temperature
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 1a
setDict["plotPanel"] = 'snapS245'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 1b
setDict["robustnessBool"] = True #Run robustness for all SAI panels
setDict["plotPanel"] = 'snapGLENS'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 3a
setDict["plotPanel"] = 'snapARISE15'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 3b
setDict["plotPanel"] = 'intiGLENS'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 6a
setDict["plotPanel"] = 'intiARISE15'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 6b
setDict["plotPanel"] = 'GLENS'
fbp.plot_single_robust_globe(scnList, dataDict, setDict, outDict) #Fig S2a
setDict["plotPanel"] = 'ARISE15'
fbp.plot_single_robust_globe(scnList, dataDict, setDict, outDict) #Fig S2b

# Annual mean precipitation
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/annual_PRECT/'
setDict["convert"] = (fcu.m_to_cm, fcu.persec_peryr)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None
setDict["cmap"] = precipPal
setDict["cbVals"] = [-25,25]
setDict["plotPanel"] = 'snapGLENS'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 4a
setDict["plotPanel"] = 'snapARISE15'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 4b
setDict["plotPanel"] = 'intiGLENS'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 7a
setDict["plotPanel"] = 'intiARISE15'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 7b
setDict["plotPanel"] = 'GLENS'
fbp.plot_single_robust_globe(scnList, dataDict, setDict, outDict) #Fig S2c
setDict["plotPanel"] = 'ARISE15'
fbp.plot_single_robust_globe(scnList, dataDict, setDict, outDict) #Fig S2d

# Annual mean SDII
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/extreme_sdii/'
setDict["areaAvgBool"] = True
setDict["convert"] = None
setDict["landmaskFlag"] = 'land'
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None
setDict["cmap"] = precipPal
setDict["cbVals"] = [-1,1]
setDict["plotPanel"] = 'snapGLENS'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 5a
setDict["plotPanel"] = 'snapARISE15'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 5b
setDict["plotPanel"] = 'intiGLENS'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 8a
setDict["plotPanel"] = 'intiARISE15'
fbp.plot_single_basic_difference_globe(scnList, dataDict, setDict, outDict) #Fig 8b
setDict["plotPanel"] = 'GLENS'
fbp.plot_single_robust_globe(scnList, dataDict, setDict, outDict) #Fig S2e
setDict["plotPanel"] = 'ARISE15'
fbp.plot_single_robust_globe(scnList, dataDict, setDict, outDict) #Fig S2f
