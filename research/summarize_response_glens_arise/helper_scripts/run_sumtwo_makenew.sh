# !/bin/bash -l
# ## Job Name
# PBS -N make_PRECCPRECL_PRECT
# ## Project code
# PBS -A P06010014
# PBS -l walltime=8:30:00
# PBS -q casper
# ## Merge output and error files
# PBS -j oe
# ## Select 1 nodes with 1 CPUs each
# PBS -l select=1:ncpus=1:mem=50GB
# ## Send email on abort, begin and end
# PBS -m abe
# ## Specify mail recipient
# PBS -M dhueholt@rams.colostate.edu
exec &> logfile.txt

export TMPDIR=/glade/scratch/dhueholt/temp
mkdir -p $TMPDIR

### Load modules
module load cdo
module load nco

EMEM=(
"001_"
"002_"
"003_"
"004_"
"005_"
"006_"
"007_"
"008_"
"009_"
"010_"
"011_"
"012_"
"013_"
"014_"
"015_"
"016_"
"017_"
"018_"
"019_"
"020_"
"021_"
)

SCENARIO=(
"control"
"feedback"
)

IN_PATH="/glade/scratch/dhueholt/annual_PREC/"
IN_VARNAME1=PRECC
IN_VARNAME2=PRECL
OUT_PATH="/glade/scratch/dhueholt/annual_PREC/"
OUT_VARNAME=PRECT
OUT_LONGNAME='Total precipitation (liq+ice)'

for scen in ${SCENARIO[@]}; do
    for em in ${EMEM[@]}; do
        IN_CARD=$IN_PATH*$scen*$em$IN_VARNAME1*
        EXPAND_ICC=`echo $IN_CARD`
        IN_CARD2=$IN_PATH*$scen*$em$IN_VARNAME2*
        OUT_CARD=${EXPAND_ICC//$IN_VARNAME1/$OUT_VARNAME}
        sh do_sumtwo_makenew.sh $IN_CARD $IN_CARD2 $IN_VARNAME1 $OUT_VARNAME $OUT_CARD "$OUT_LONGNAME"
    done
done
