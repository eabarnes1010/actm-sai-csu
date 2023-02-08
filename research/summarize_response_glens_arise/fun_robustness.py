''' fun_robustness
Contains functions to calculate the robustness of trends in data.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''
from icecream import ic
import sys

import cftime
import numpy as np
import xarray as xr

def handle_robustness(rlzList, rbd):
    ''' Handles robustness calculation '''
    # Select data of interest
    for s in rlzList:
        if rbd["exp"] == 'GLENS':
            if 'GLENS:Control' in s.scenario:
                actCntrlDarr = s
            elif 'GLENS:Feedback' in s.scenario:
                actFdbckDarr = s
        elif rbd["exp"] == 'ARISE15':
            if 'ARISE:Control' in s.scenario:
                actCntrlDarr = s
            elif 'ARISE:Feedback' in s.scenario:
                actFdbckDarr = s

    rbd["nRlz"] = len(actCntrlDarr.realization)-1 #Skip ens mean at last index
    ic(rbd) #Show robustness dictionary for easy troubleshooting
    rbstEcEv, nans = calc_robustness_ecev(
        actCntrlDarr, actFdbckDarr, sprd=rbd['sprd'])

    rbstAbv = beat_rbst(rbstEcEv["above"], beat=rbd["beatNum"])
    rbstBlw = beat_rbst(rbstEcEv["below"], beat=rbd["beatNum"])
    rbst = np.maximum(rbstAbv, rbstBlw) #Composite of above and below
    # ic(rbst, np.max(rbst), np.min(rbst), np.median(rbst), np.mean(rbst)) #troubleshooting
    rbstns = rbst.astype(np.float)
    rbstns[nans] = np.nan #NaNs from e.g. land area in ocean data

    return rbd, rbstns

def calc_robustness_ecev(cntrlDarr, fdbckDarr, sprd=[2025,2029]):
    ''' "Each-Every" robustness. For each Feedback time period, count number of
        Control members the given period time mean is less/greater than. '''
    timeSlice = slice(
        cftime.DatetimeNoLeap(sprd[0], 7, 15, 12, 0, 0, 0),
        cftime.DatetimeNoLeap(sprd[1], 7, 15, 12, 0, 0, 0))

    # Get time means for input periods
    cntrlSprd = cntrlDarr.sel(time=timeSlice)
    cntrlSprdTimeMn = cntrlSprd.mean(dim='time')
    fdbckSprd = fdbckDarr.sel(time=timeSlice)
    fdbckSprdTimeMn = fdbckSprd.mean(dim='time')

    # Loop compares EACH feedback to EVERY control realization
    countFdbckAbvCntrl = np.full(np.shape(fdbckSprdTimeMn), np.nan)
    countFdbckBlwCntrl = np.full(np.shape(fdbckSprdTimeMn), np.nan)
    for rc,rv in enumerate(fdbckSprdTimeMn[:-1]): #Skip final ind, the ens mean
        nans = np.isnan(rv.data) #May have NaNs e.g. land area for ocean data
        fdbckAbvCntrl = rv > cntrlSprdTimeMn
        countFdbckAbvCntrl[rc,:,:] = np.count_nonzero(
            fdbckAbvCntrl.data, axis=2) #axis=2 is realization dimension
        countFdbckAbvCntrl[rc,nans] = np.nan
        fdbckBlwCntrl = rv < cntrlSprdTimeMn
        countFdbckBlwCntrl[rc,:,:] = np.count_nonzero(
            fdbckBlwCntrl.data, axis=2) #axis=2 is realization dimension
        countFdbckBlwCntrl[rc,nans] = np.nan

    robustness = {
        "above": countFdbckAbvCntrl,
        "below": countFdbckBlwCntrl,
    }

    return robustness, nans

def beat_rbst(rbstIn, beat=None):
    ''' Count how many members "beat" a given threshold value. '''
    if beat is None: #Default beat is greater than half of members
        numRlz = np.shape(rbstIn)[0]
        beat = numRlz / 2
        ic(beat)
    rlzAbvBeat = rbstIn > beat
    countGtBeat = np.count_nonzero(rlzAbvBeat, axis=0)
    rbstOut = countGtBeat

    return rbstOut

def mask_rbst(darr, robustness, nRlz, threshold):
    ''' Mask array based on robustness '''
    maskRobustness = robustness < threshold
    robustDarr = darr.copy()
    robustDarr = robustDarr.where(maskRobustness)

    return robustDarr

def get_quantiles(robustness):
    ''' Calculate and print quantiles for robustness array '''
    rbstQuant = {
        "0.99": np.nanquantile(robustness, 0.99),
        "0.9": np.nanquantile(robustness, 0.9),
        "0.7": np.nanquantile(robustness, 0.7),
        "0.5": np.nanquantile(robustness, 0.5),
        "0.3": np.nanquantile(robustness, 0.3),
        "0.2": np.nanquantile(robustness, 0.2),
        "0.1": np.nanquantile(robustness, 0.1),
        "0.05": np.nanquantile(robustness, 0.05),
        "0.01": np.nanquantile(robustness, 0.01)
    }
    ic(rbstQuant)

    return rbstQuant
