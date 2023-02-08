''' wrap_paperplots_ensplots_script
Replicates figures from Hueholt et al. 2023 "Assessing Outcomes in Stratospheric Aerosol Injection Scenarios Shortly After Deployment" directly. This makes all of the individual panels of Figure 2, as well as Figure S3 and Figure S4.
Keynote is used to stitch panels together and add annotations.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

import numpy as np

import fun_ens_plot as fep
import fun_convert_unit as fcu
import fun_process_data as fpd
import region_library as rlib

# Call regions
ipccWg1Ar5 = rlib.atlas_ipcc_wg1ar5() #ipccWg1Ar5["allRegions"]
seaIcyRegions = rlib.atlas_seaicy_regions()
planetary = ('global', rlib.Tropics(), rlib.NorthernHemisphere(), rlib.SouthernHemisphere())
insets = rlib.atlas_insets()

# Dictionaries
dataDict = {
    "dataPath": '/Users/dhueholt/Documents/GLENS_data/annual_TREFHT/',
    "idGlensCntrl": 'control_*', #'control_*' or None
    "idGlensFdbck": 'feedback_*', #'feedback_*' or None
    "idArise": '*SSP245-TSMLT-GAUSS*', #'*SSP245-TSMLT-GAUSS*' or None
    "idS245Cntrl": '*BWSSP245*', #'*BWSSP245*' or None
    "idS245Hist": '*BWHIST*', #'*BWHIST*' or None
    "mask": '/Users/dhueholt/Documents/Summery_Summary/cesm_atm_mask.nc' #cesm_component_mask.nc
}
setDict = {
    "landmaskFlag": None, #None or 'land'
    "areaAvgBool": True,
    "convert": (fcu.kel_to_cel,), #TUPLE of converter(s), or None if using default units
    "realization": 'ensplot',
    "styleFlag": 2, #0 all auto, 1 lines only, 2 Hueholt et al. 2023 style, 3 IPCC regions automatic
    "mute": False, #True/False to use image muting on parts of time period
    "ylim": [14, 18.25], #None for automatic, [min,max] for manual
    "ylabel": '',
    "yticks": np.arange(10,25,1),
    "xticks": True
}
outDict = {
    "savePath": '/Users/dhueholt/Documents/GLENS_fig/20230207_moreDistill/1_check/',
    "addToSaveStr": None,
    "dpiVal": 'pdf' #numeric dpi, or 'pdf' for vector as in Hueholt et al. 2023
}

ic(dataDict, setDict, outDict) #Lowers chances of making the wrong plots by mistake

# Make images
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

# Annual mean temperature
setDict["regOfInt"] = 'global'
setDict["xticks"] = False
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2a

setDict["regOfInt"] = rlib.Amazon()
setDict["ylim"] = [25.5,30.5]
setDict["yticks"] = np.arange(20,40,1)
setDict["xticks"] = False
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2e

setDict["regOfInt"] = rlib.NorthEurope()
setDict["ylim"] = [2,10.5]
setDict["yticks"] = np.arange(0,20,2)
setDict["xticks"] = True
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2i

# Annual mean precipitation
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/annual_PRECT/'
setDict["convert"] = (fcu.m_to_cm, fcu.persec_peryr)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["regOfInt"] = 'global'
setDict["ylim"] = [105,120]
setDict["yticks"] = np.arange(105,130,5)
setDict["xticks"] = False
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2b

setDict["regOfInt"] = rlib.AlaskaNorthwestCanada()
setDict["ylim"] = [43,75]
setDict["yticks"] = np.arange(43,80,10)
setDict["xticks"] = False
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2f

# NH monsoon seasonal mean (JJAS) precipitation
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/eimnsn_PRECT/anmn/'
setDict["convert"] = (fcu.m_to_cm, fcu.persec_peryr)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["regOfInt"] = rlib.GeenEtAl20AsianMonsoonRegion()
setDict["ylim"] = [180,345]
setDict["yticks"] = np.arange(180,500,50)
setDict["xticks"] = True
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2j

# Annual mean precipitation (land-only)
setDict["regOfInt"] = 'global'
setDict["landmaskFlag"] = 'land'
setDict["convert"] = (fcu.m_to_cm, fcu.persec_peryr)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}

setDict["ylim"] = [75,105]
setDict["yticks"] = np.arange(80,105,5)
setDict["xticks"] = True
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig S3
setDict["landmaskFlag"] = None

# Annual mean sea surface temperature
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/annual_OCNTEMP500/'
setDict["convert"] = None
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["regOfInt"] = 'global'
setDict["ylim"] = [18,21.25]
setDict["yticks"] = np.arange(10,30,1)
setDict["xticks"] = False
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2c

# September Arctic sea ice extent
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/sept_ICEEXTENT/'
setDict["areaAvgBool"] = 'sum'
setDict["convert"] = (fcu.km2_to_milkm2,)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["regOfInt"] = rlib.Arctic()
setDict["ylim"] = [0,9.5]
setDict["yticks"] = np.arange(0,10,2)
setDict["xticks"] = False
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2g

# February Antarctic sea ice extent
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/feb_ICEEXTENT/'
setDict["areaAvgBool"] = 'sum'
setDict["convert"] = (fcu.km2_to_milkm2,)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["regOfInt"] = rlib.Antarctica()
setDict["ylim"] = [2.5,10]
setDict["yticks"] = np.arange(2.5,40,2)
setDict["xticks"] = True
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2k

# Mid-latitude annual tropical nights
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/extreme_clxTR/'
setDict["areaAvgBool"] = True
setDict["convert"] = None
setDict["landmaskFlag"] = 'land'
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["regOfInt"] = (rlib.NorthernHemisphereMidLat(), rlib.SouthernHemisphereMidLat())
setDict["ylim"] = [28,76]
setDict["yticks"] = np.arange(28,100,15)
setDict["xticks"] = False
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2d

# East African SDII
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/extreme_sdii/'
setDict["areaAvgBool"] = True
setDict["convert"] = None
setDict["landmaskFlag"] = None
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["regOfInt"] = (rlib.EastAfricaAyugiEtAl(),)
setDict["ylim"] = [5.5,9.5]
setDict["yticks"] = np.arange(6,30,1)
setDict["xticks"] = False
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2h

# W Australian MHWs
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/extreme_MHW/roll5_centerFalseShift4/'
setDict["areaAvgBool"] = True
setDict["convert"] = (fcu.roll5_to_percentdays,)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["landmaskFlag"] = None
setDict["regOfInt"] = (rlib.WesternAustraliaMHW_point(),)
setDict["ylim"] = [0,100]
setDict["yticks"] = np.arange(0,101,30)
setDict["xticks"] = True
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig 2l

# September sea ice thickness
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/sept_hi/'
setDict["areaAvgBool"] = True
setDict["convert"] = (fcu.m_to_cm_ice,)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["landmaskFlag"] = None
setDict["regOfInt"] = rlib.Arctic()
setDict["ylim"] = [0,110]
setDict["yticks"] = np.arange(0,110,20)
setDict["xticks"] = True
outDict["addToSaveStr"] = '_sept'
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig S4a

setDict["regOfInt"] = rlib.SouthernOcean()
setDict["ylim"] = [30,75]
setDict["yticks"] = np.arange(0,80,10)
setDict["xticks"] = True
outDict["addToSaveStr"] = '_sept'
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig S4c

# February sea ice thickness
dataDict["dataPath"] = '/Users/dhueholt/Documents/GLENS_data/feb_hi/'
setDict["areaAvgBool"] = True
setDict["convert"] = (fcu.m_to_cm_ice,)
scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
dataDict = {**dataDict, **cmnDict}
setDict["levOfInt"] = None

setDict["landmaskFlag"] = None
setDict["regOfInt"] = rlib.Arctic()
setDict["ylim"] = [0,155]
setDict["yticks"] = np.arange(0,200,25)
setDict["xticks"] = True
outDict["addToSaveStr"] = '_feb'
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig S4b

setDict["regOfInt"] = rlib.SouthernOcean()
setDict["ylim"] = [6,36]
setDict["yticks"] = np.arange(0,50,6)
setDict["xticks"] = True
outDict["addToSaveStr"] = '_feb'
fep.plot_ens_spread_timeseries(scnList, dataDict, setDict, outDict) #Fig S4d
