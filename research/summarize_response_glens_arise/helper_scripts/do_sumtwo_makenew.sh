#######################################
# Use CDO to sum data from two files to make a new variable.
# New variable name and attributes are required as inputs and applied using NCO.
# Globals:
#   None
# Arguments:
#   IN_CARD
#   IN_CARD2
#   IN_VARNAME1
#   IN_VARNAME2
#   OUT_CARD
#   OUT_LONGNAME
# Written by Daniel Hueholt
# Graduate Research Assistant at Colorado State University
#######################################

### Input variables
IN_CARD=$1
IN_CARD2=$2
IN_VARNAME1=$3
OUT_VARNAME=$4
OUT_CARD=$5
OUT_LONGNAME=$6

### Peel the avocado
cdo add $IN_CARD $IN_CARD2 $OUT_CARD
ncrename -O -v $IN_VARNAME1,$OUT_VARNAME $OUT_CARD
ncatted -a long_name,$IN_VARNAME2,o,c,"$OUT_LONGNAME" $OUT_CARD
