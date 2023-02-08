''' get_all_files
Runs functions to retrieve output from various SAI experiments.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

import subprocess

copyBeesCasper = '/glade/u/home/dhueholt/sai-cesm/SAI-CESM/get_data/get_bees/'
copyBeesLocal = '/Users/dhueholt/Documents/GitHub/SAI-CESM/get_data/get_bees/'
copyBeesPath = copyBeesCasper

def get_glens_all(IN_TOKEN, MOD_TOKEN, TIME_TOKEN, OUT_PATH):
    glensBee = copyBeesPath + 'do_glens_copytolocal.sh'
    subprocess.run(['sh', glensBee, IN_TOKEN, MOD_TOKEN, TIME_TOKEN, OUT_PATH])
    return None

def get_arise_fdbck(IN_TOKEN, MOD_TOKEN, TIME_TOKEN, OUT_PATH):
    aFdbckBee = copyBeesPath + 'do_arise_copytolocal.sh'
    subprocess.run(['sh', aFdbckBee, IN_TOKEN, MOD_TOKEN, TIME_TOKEN, OUT_PATH])
    return None

def get_arise_cntrl(IN_TOKEN, MOD_TOKEN, TIME_TOKEN, OUT_PATH):
    aCntrlBee = copyBeesPath + 'do_acntrl_copytolocal.sh'
    subprocess.run(['sh', aCntrlBee, IN_TOKEN, MOD_TOKEN, TIME_TOKEN, OUT_PATH])
    return None

def get_hist(IN_TOKEN, MOD_TOKEN, TIME_TOKEN, OUT_PATH):
    histBee = copyBeesPath + 'do_hist_copytolocal.sh'
    subprocess.run(['sh', histBee, IN_TOKEN, MOD_TOKEN, TIME_TOKEN, OUT_PATH])
    return None

# Inputs
scnDict = {
    "glens": True,
    "ariseFdbck": True,
    "ariseCntrl": True,
    "hist": False,
}
inTokens = {
    "glens": "PRECT",
    "ariseFdbck": "*.PRECT.*",
    "ariseCntrl": "*.PRECT.*",
    "hist": "*.TREFHT.*",
}
modToken = "lnd" #mod e.g. ocn, atm, lnd
inTimes = { #timecode/
    "glens": "daily/",
    "ariseFdbck": "day_1/",
    "ariseCntrl": "day_1/",
    "hist": "month_1/",
}
outPath = '/glade/scratch/dhueholt/daily_PRECT/'

for scn in scnDict.keys():
    if scnDict[scn] == True:
        if scn == "glens":
            get_glens_all(inTokens["glens"], modToken, inTimes["glens"], outPath)
        elif scn == "ariseFdbck":
            get_arise_fdbck(inTokens["ariseFdbck"], modToken, inTimes["ariseFdbck"], outPath)
        elif scn == "ariseCntrl":
            get_arise_cntrl(inTokens["ariseCntrl"], modToken, inTimes["ariseCntrl"], outPath)
        elif scn == "hist":
            get_hist(inTokens["hist"], modToken, inTimes["hist"], outPath)
        else:
            ic('Unknown scenario!')
            ic(scn)
