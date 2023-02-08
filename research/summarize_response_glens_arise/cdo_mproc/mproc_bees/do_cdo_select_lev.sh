#######################################
# Select surface level from CESM ocean variables.
# Output files have the same name as the original file, but have the level
# appended to the beginning of the variable string.
# Globals:
#   None
# Arguments:
#   IN_PATH
#   IN_TOKEN
#   IN_LEV
#   OUT_PATH
# Written by Daniel Hueholt
# Graduate Research Assistant at Colorado State University
#######################################
IN_PATH=$1
IN_TOKEN=$2
IN_LEV=500
OUT_PATH=$3

for f in $IN_PATH$IN_TOKEN; do
    PATH_LENGTH=${#IN_PATH}
    ACTIVE_FNAME=${f:$PATH_LENGTH}
    ACTIVE_VAR=$( echo $ACTIVE_FNAME | cut -d'_' -f3)
    NEW_VAR=$IN_LEV
    OUT_NAME=${ACTIVE_FNAME//$ACTIVE_VAR/$NEW_VAR$ACTIVE_VAR}
    cdo sellevel,$IN_LEV $f $OUT_PATH$OUT_NAME
done
