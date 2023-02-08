#######################################
# Copy ARISE control files to local directory.
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

### Input variables
IN_TOKEN=$1
MOD_TOKEN=$2
TIME_TOKEN=$3
OUT_PATH=$4

### Raw ARISE control futures
CMN_PATHAF="/glade/campaign/cesm/collections/CESM2-WACCM-SSP245/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM."
EMEMAF=(
"001"
"002"
"003"
"004"
"005"
"006"
"007"
"008"
"009"
"010"
)
# CMN_PATHAF + EMEMAF + MOD_TOKEN + PROC + TIME_TOKEN = directory structure for each ens member
PROC="/proc/tseries/"
S="/"
for emaf in ${EMEMAF[@]}; do
    FILE_TO_COPYAF=$CMN_PATHAF$emaf$S$MOD_TOKEN$PROC$TIME_TOKEN$IN_TOKEN
    cp $FILE_TO_COPYAF $OUT_PATH
done
