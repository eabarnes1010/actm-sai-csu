''' wrap_derive_data_script
Runs functions to derive and save data from a base dataset to new files. Used
for derivations that require multiple datasets or time-consuming calculations
where spending the space to save the data is more efficient than spending the
time to do the calculation each time. For non-intensive in-line calculations,
see fun_convert_unit.

Default form uploaded to GitHub demonstrates deriving marine heatwave presence
from daily sea surface temperature output.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

import glob
from multiprocessing import Process
import subprocess

import fun_derive_data as fdd

inPath = '/Users/dhueholt/Documents/GLENS_data/daily_SST/' #LOCAL
# inPath = '/glade/scratch/dhueholt/daily_SST/' #CASPER
inToken = ['*control*','*feedback*']
# inTokens for raw: ['*control*','*feedback*','*SSP245-TSMLT*','*BWSSP245*','*BWHIST*']
# inTokens for cdo merged: ['*control*', '*feedback*', '*SSP245-TSMLT*', '*BWSSP245*', '*BWHIST*']
outPath = '/Users/dhueholt/Documents/GLENS_data/extreme_MHW/' #LOCAL
# outPath = '/glade/scratch/dhueholt/extreme_CLXTR/' #CASPER
nProc = 1

for scen in inToken:
    theGlob = glob.glob(inPath+scen)
    for fc,fn in enumerate(theGlob):
        ic(fn)
        if __name__== '__main__': #If statement required by multiprocessing
            shard = Process(target=fdd.derive_mhw_presence, args=(fn,outPath))
        if fc % nProc == 0 and fc != 0:
            shard.start()
            shard.join() #Forces nProc+1 processes to run to completion before beginning more
            shard.close() #Free up all associated resources
        else:
            shard.start()
        filesRemaining = len(theGlob) - fc - 1
        ic(filesRemaining) #Cheap "progress bar"
