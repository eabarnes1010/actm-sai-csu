#!/bin/bash -l
### Job Name
#PBS -N selyear_20112014
### Project code
#PBS -A P06010014
#PBS -l walltime=30:00
#PBS -q casper
### Merge output and error files
#PBS -j oe
### Select 1 nodes with 1 CPUs each
#PBS -l select=1:ncpus=1:mem=10GB
### Send email on abort, begin and end
#PBS -m abe
### Specify mail recipient
#PBS -M dhueholt@rams.colostate.edu
# exec &> logfile_ssp245_copy.txt

# export TMPDIR=/glade/scratch/dhueholt/temp
# mkdir -p $TMPDIR

IN_PATH="/Users/dhueholt/Documents/GLENS_data/historical_TREFHT/"
IN_TOKEN="*.TREFHT.*"
STRT_YR=2000
END_YR=2014
OUT_PATH="/Users/dhueholt/Documents/GLENS_data/historical_TREFHT/"

IN_CARD="$IN_PATH$IN_TOKEN"
PATH_LENGTH=${#IN_PATH}
for f in $IN_CARD; do
    ACTIVE_FNAME=${f:$PATH_LENGTH}
    ACTIVE_TIME=$(echo $ACTIVE_FNAME | cut -d'.' -f10)
    STRT_MN=${ACTIVE_TIME:4:2}
    END_MN=${ACTIVE_TIME:11:2}
    OUT_FNAME=${ACTIVE_FNAME//$ACTIVE_TIME/$STRT_YR$STRT_MN"-"$END_YR$END_MN}
    OUT_CARD=$OUT_PATH$OUT_FNAME
    cdo selyear,$STRT_YR/$END_YR $f $OUT_CARD
done
