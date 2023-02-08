#######################################
# Select field of interest from a CESM file and resave with only that field.
# Output files have the same name as the input, but are placed at the OUT_PATH.
# Variable to be selected must be specified MANUALLY at the cdo call.
# Globals:
#   None
# Arguments:
#   IN_PATH
#   IN_TOKEN
#   OUT_PATH
# Written by Daniel Hueholt
# Graduate Research Assistant at Colorado State University
#######################################

### Input variables
IN_PATH=$1 #Path to data
IN_TOKEN=$2 #Token to match data files, e.g. "*.001.*.nc"
OUT_PATH=$3 #Path to save files

### Script
IN_CARD="$IN_PATH$IN_TOKEN"
PATH_LENGTH=${#IN_PATH}
# echo $PATH_LENGTH

for f in $IN_CARD; do
  ACTIVE_FNAME=${f:$PATH_LENGTH}
  OUT_CARD=$OUT_PATH$ACTIVE_FNAME
  echo $OUT_CARD
  cdo -L -selname,aice $f $OUT_CARD
done
