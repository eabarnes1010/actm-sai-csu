''' wrap_basicplots_script
Runs map plotting functions in fun_basic_plot. To replicate figures from
Hueholt et al. 2023 "Assessing Outcomes in Stratospheric Aerosol Injection
Scenarios Shortly After Deployment" directly, see
wrap_paperplots_basicplots_script.

dataDict: defines input data
setDict: settings for analysis/visualization
    plotPanel: determines which panel to plot, valid entries given below
        with relevant figure numbers from Hueholt et al. 2023
        'snapR85': snapshot for RCP8.5, Fig. 1a
        'snapS245': snapshot for SSP2-4.5, Fig. 1b
        'snapGLENS': snapshot around deployment for GLENS, Fig. 3a
        'snapARISE15': snapshot around deployment for ARISE-SAI-1.5, Fig. 3b
        'intiGLENS': intervention impact for GLENS, Fig. 6a
        'intiARISE15': intervention impact for ARISE-SAI-1.5, Fig. 6b
        any other value: make a blank map
outDict: output image settings
loopDict: determines which images are made

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

from matplotlib import cm
import cmasher, cmocean, seaborn  # Colormap packages

import fun_basic_plot as fbp
import fun_convert_unit as fcu
import fun_process_data as fpd
import region_library as rlib

# Special color palettes
tropicalPal = seaborn.diverging_palette(133, 324, as_cmap=True)
precipPal = seaborn.diverging_palette(58, 162, s=100, l=45, as_cmap=True)

# Dictionaries to define inputs
dataDict = {
    "dataPath": '/Users/dhueholt/Documents/GLENS_data/annual_TREFHT/',
    "idGlensCntrl": 'control_*',  # 'control_*' or None
    "idGlensFdbck": 'feedback_*',  # 'feedback_*' or None
    "idArise": None,  # '*SSP245-TSMLT-GAUSS*' or None
    "idS245Cntrl": None,  # '*BWSSP245*' or None
    "idS245Hist": None,  # '*BWHIST*' or None
    "mask": '/Users/dhueholt/Documents/Summery_Summary/cesm_atm_mask.nc' # Landmask file location
}
setDict = {
    "landmaskFlag": None,  # None no mask, 'land' to mask ocean, 'ocean' to mask land
    "startIntvl": [2015,2020,2030,2035],  # Window years [glens,glens,arise,arise]
    "endIntvl": [2025,2030,2040,2045],  # Window years [glens,glens,arise,arise]
    "convert": None,  # TUPLE of converter(s), None for default units
    "cmap": None,  # None for default (cmocean balance) or choose colormap
    "cbVals": [-2,2],  # None for automatic or [min,max] to override,
    "addCyclicPoint": False,  # True for ocean data/False for others
    "areaAvgBool": False,  # ALWAYS FALSE: no area averaging for a map!
    "robustnessBool": True,  # True/False to run robustness
    "plotPanel": "intiGLENS" # See docstring for valid inputs
}
outDict = {
    "savePath": '/Users/dhueholt/Documents/GLENS_fig/20230206_distill/',
    "dpiVal": 400
}
loopDict = {
    "rlzs": ('ensplot',),  # number(s) for member(s), 'mean' ens mean all members, 'ensplot' for both member information and mean (i.e. for robustness)
    "levels": (None,),  # None for single-level variable (as for all used in Hueholt et al. 2023)
    "regions": ('global',),  # 'global' only for maps
}
ic(dataDict, setDict, outDict, loopDict)  # Show input settings at command line

# Make images
for rlz in loopDict["rlzs"]:
    setDict["realization"] = rlz
    scnList, cmnDict = fpd.call_to_open(dataDict, setDict)
    dataDict = {**dataDict, **cmnDict}

    for lev in loopDict["levels"]:
        setDict["levOfInt"] = lev
        fbp.plot_single_basic_difference_globe(
            scnList, dataDict, setDict, outDict)
        # fbp.plot_single_robust_globe(
        #    scnList, dataDict, setDict, outDict)
