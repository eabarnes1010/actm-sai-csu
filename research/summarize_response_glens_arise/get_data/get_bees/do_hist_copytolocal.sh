#######################################
# Copy historical files to local directory.
# Globals:
#   None
# Arguments:
#   IN_PATH
#   MOD_TOKEN
#   TIME_TOKEN
#   OUT_PATH
# Written by Daniel Hueholt
# Graduate Research Assistant at Colorado State University
#######################################

export TMPDIR=/glade/scratch/dhueholt/temp
mkdir -p $TMPDIR

IN_TOKEN=$1
MOD_TOKEN=$2
TIME_TOKEN=$3
OUT_PATH=$4

### Raw historical
CMN_PATHH="/glade/campaign/collections/cmip/CMIP6/timeseries-cmip6/b.e21.BWHIST.f09_g17.CMIP6-historical-WACCM."
EMEMH=(
"001"
"002"
"003"
)
PROC="/proc/tseries/"
S="/"
# CMN_PATHH + EMEMH + /MOD_TOKEN + PROC + TIME_TOKEN = directory structure for each ens member

for emh in ${EMEMH[@]}; do
    FILE_TO_COPYH=$CMN_PATHH$emh$S$MOD_TOKEN$PROC$TIME_TOKEN$IN_TOKEN
    cp $FILE_TO_COPYH $OUT_PATH
done
