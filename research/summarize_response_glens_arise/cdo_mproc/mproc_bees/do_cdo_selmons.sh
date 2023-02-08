#######################################
# Extract certain months from CESM files. For now, months must be specified
# MANUALLY at CDO call.
# Output files are named automatically as:
# type_ensnumber_variable_YYYYMM-YYYYMM[first]_..._YYYYMM-YYYYMM[last]_[CUSTOM].nc
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
  cdo -selmon,10,11,12 $f $OUT_CARD
done
