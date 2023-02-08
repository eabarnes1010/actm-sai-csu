''' fun_convert_unit
Contains functions for unit conversions. Module is sectioned by type of
variable, i.e. temperature, chemistry, etc.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

import xarray as xr
import numpy as np

### Chemistry

def molmol_to_ppm(darrMolmol):
    ''' Convert mol/mol to parts per million
    acmg.seas.harvard.edu/people/faculty/djj/book/bookchap1.html '''
    darrPpm = darrMolmol * 10**6
    darrPpm.attrs = darrMolmol.attrs
    darrPpm.attrs['units'] = 'ppm'

    return darrPpm

def molmol_to_ppb(darrMolmol):
    ''' Convert mol/mol to parts per billion
    acmg.seas.harvard.edu/people/faculty/djj/book/bookchap1.html '''
    darrPpb = darrMolmol * 10**9
    darrPpb.attrs = darrMolmol.attrs
    darrPpb.attrs['units'] = 'ppb'

    return darrPpb

def molmol_to_pptr(darrMolmol):
    ''' Convert mol/mol to parts per trillion
    acmg.seas.harvard.edu/people/faculty/djj/book/bookchap1.html '''
    darrPptr = darrMolmol * 10**12
    darrPptr.attrs = darrMolmol.attrs
    darrPptr.attrs['units'] = 'parts per trillion'

    return darrPptr

def mmolm3_to_micmolkg(darrmmolm3):
    darrMolm3 = (darrmmolm3/1000)
    gSea = 1027 #Assume avg surface seawater density -- NOT sufficient for conclusions
    gmolO2 = 32
    mO2 = darrMolm3*gmolO2
    mSea = gSea - mO2
    darrMolal = darrMolm3 / (gSea/1000)
    darrMicmolKg = darrMolal * 10**6
    darrMicmolKg.attrs = darrmmolm3.attrs
    darrMicmolKg.attrs['units'] = 'micmol/kg'

    return darrMicmolKg


### Moisture
def kgkg_to_gkg(darrKgkg):
    ''' Convert kg/kg to g/kg '''
    darrGkg = darrKgkg * 1000
    darrGkg.attrs = darrKgkg.attrs
    darrGkg.attrs['units'] = 'g/kg'

    return darrGkg

### Precipitation
def m_to_cm(darrM):
    ''' Convert meters to centimeters '''
    darrCm = darrM * 100
    darrCm.attrs = darrM.attrs
    darrCm.attrs['units'] = darrCm.attrs['units'].replace("m/",'cm/')

    return darrCm

def m_to_mm(darrM):
    ''' Convert meters to millimeters '''
    darrMm = darrM * 1000
    darrMm.attrs = darrM.attrs
    darrMm.attrs['units'] = darrMm.attrs['units'].replace("m/",'mm/')

    return darrMm

### Temperature
def kel_to_cel(darrKel):
    ''' Convert K to deg C '''
    darrCel = darrKel - 273.15
    darrCel.attrs = darrKel.attrs
    darrCel.attrs['units'] = 'deg C'

    return darrCel

### Ice
def km2_to_milkm2(darrKm2):
    ''' Convert km2 to millions of km2 '''
    darrMilKm2 = darrKm2 / (10 ** 6)
    darrMilKm2.attrs = darrKm2.attrs
    darrMilKm2.attrs['units'] = 'millions of km2'

    return darrMilKm2

def m_to_cm_ice(darrM):
    ''' Convert meters to centimeters for ice (correct unit string) '''
    darrCm = darrM * 100
    darrCm.attrs = darrM.attrs
    darrCm.attrs['units'] = darrCm.attrs['units'].replace("m",'cm')

    return darrCm

### Marine heatwaves
def bms_to_nannual(darrBms):
    ''' Convert binary MHW start indices to number of annual MHWs '''
    darrNumAnn = darrBms.groupby("time.year").sum()
    darrNumAnn.attrs = darrBms.attrs
    darrNumAnn.attrs['units'] = 'n/yr'
    darrNumAnn.attrs['long_name'] = 'Number of unique MHWs per year'

    return darrNumAnn

def bmp_to_ndays(darrBmp):
    ''' Convert binary MHW presence to number of annual MHW days/yr '''
    darrNumDays = darrBmp.groupby("time.year").sum()
    darrNumDays.attrs = darrBmp.attrs
    darrNumDays.attrs['units'] = 'days/yr'
    darrNumDays.attrs['long_name'] = 'Number of MHW days per year'

    return darrNumDays

### CMIP6 to GLENS/ARISE
def flux_to_prect(darrFlux):
    ''' Convert surface precipitation fluxes to rates '''
    darrPrect = darrFlux / 1000.
    darrPrect.attrs = darrFlux.attrs
    darrPrect.attrs['units'] = 'm/s'

    return darrPrect

def perc_to_frac(darrPerc):
    ''' Convert percent to fraction '''
    darrFrac = darrPerc / 100.
    darrFrac.attrs = darrPerc.attrs
    darrFrac.attrs['units'] = 'fraction'

    return darrFrac

### General
def persec_peryr(darrPerSec):
    ''' Convert per second to per year '''
    darrPerYr = darrPerSec * 3.154*10**7
    darrPerYr.attrs = darrPerSec.attrs
    darrPerYr.attrs['units'] = darrPerSec.attrs['units'].replace("/s",'/yr')
    if "rate" in darrPerYr.attrs['long_name']:
        darrPerYr.attrs['long_name'] = darrPerYr.attrs['long_name'].replace("rate",'')

    return darrPerYr

def persec_perday(darrPerSec):
    ''' Convert per second to per day '''
    darrPerDay = darrPerSec * 86400
    darrPerDay.attrs = darrPerDay.attrs
    darrPerDay.attrs['units'] = darrPerSec.attrs['units'].replace("/s",'/dy')
    if "rate" in darrPerDay.attrs['long_name']:
        darrPerDay.attrs['long_name'] = darrPerDay.attrs['long_name'].replace("rate",'')

    return darrPerDay

def attach_unit(darrIn):
    ''' Use to attach units to data where this field is missing '''
    darrOut = darrIn.copy()
    darrOut.attrs = darrOut.attrs
    darrOut.attrs['units'] = 'd/yr'

    return darrOut

def depth_to_height(darrDepth):
    ''' Flips sign to go from depth coordinates to height coordinates '''
    darrHeight = darrDepth * -1
    darrHeight.attrs = darrDepth.attrs
    # No change to units necessary

    return darrHeight

def fraction_to_percent(darrFrac):
    ''' Converts fraction to percent '''
    darrPercent = darrFrac * 100
    darrPercent.attrs = darrFrac.attrs
    darrPercent.attrs['units'] = 'Percent'

    return darrPercent

def roll5_to_percentdays(darrRoll5):
    ''' Convert rolling 5-year sum to percent days '''
    darrPercDays = darrRoll5 / 1825 * 100
    darrPercDays.attrs = darrRoll5.attrs
    darrPercDays.attrs['units'] = 'Percent of days'

    return darrPercDays
