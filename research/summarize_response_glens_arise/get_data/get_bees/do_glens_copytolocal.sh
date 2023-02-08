#######################################
# Copy GLENS control and feedback files to local directory.
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

CNTRL_PATH="/glade/campaign/cesm/collections/GLENS/Control/"
FDBCK_PATH="/glade/campaign/cesm/collections/GLENS/Feedback/"
PROC="/proc/tseries/"
# GLENS data is divided by Feedback/Control, stored with all ensemble members in
# a single directory
NC="/*.nc"

CNTRL_TO_COPY=$CNTRL_PATH$MOD_TOKEN$PROC$TIME_TOKEN$IN_TOKEN$NC
FDBCK_TO_COPY=$FDBCK_PATH$MOD_TOKEN$PROC$TIME_TOKEN$IN_TOKEN$NC
cp $CNTRL_TO_COPY $OUT_PATH
cp $FDBCK_TO_COPY $OUT_PATH
