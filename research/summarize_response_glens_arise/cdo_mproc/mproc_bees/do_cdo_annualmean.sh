#######################################
# Merge CESM monthly netcdf files, shift time, and calculate annual mean.
# Output files are named automatically as:
# type_ensnumber_variable_YYYYMM-YYYYMM[first]_..._YYYYMM-YYYYMM[last].nc
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
echo $PATH_LENGTH

RUN_FNAMES=()
RUN_TIMES=()
RUN_ENSNUMS=()
for f in $IN_CARD; do
  ACTIVE_FNAME=${f:$PATH_LENGTH} #Extract filename from rest of directory structure
  if [[ "$ACTIVE_FNAME" == *"CESM2-WACCM"* ]]; then #CMIP6 processed
    ACTIVE_FNAME=${ACTIVE_FNAME//_/.}
    RUN_FNAMES+=( $ACTIVE_FNAME )
    ACTIVE_TIME=$(echo $ACTIVE_FNAME | cut -d'.' -f7)
    RUN_TIMES+=( $ACTIVE_TIME )
    ACTIVE_ENSNUM=$(echo $ACTIVE_FNAME | cut -d'.' -f5)
    RUN_ENSNUMS+=( $ACTIVE_ENSNUM )
    RUN_TYPE=$(echo $ACTIVE_FNAME | cut -d'.' -f4)
    RUN_VAR=$(echo $ACTIVE_FNAME | cut -d'.' -f1)
  elif [[ "$ACTIVE_FNAME" == *"CMIP6-SSP2-4.5"* ]]; then #ARISE Control (unprocessed)
      ACTIVE_FNAME=${ACTIVE_FNAME//_/.}
      RUN_FNAMES+=( $ACTIVE_FNAME )
      ACTIVE_TIME=$(echo $ACTIVE_FNAME | cut -d'.' -f12)
      RUN_TIMES+=( $ACTIVE_TIME )
      ACTIVE_ENSNUM=$(echo $ACTIVE_FNAME | cut -d'.' -f8)
      RUN_ENSNUMS+=( $ACTIVE_ENSNUM )
      RUN_TYPE=$(echo $ACTIVE_FNAME | cut -d'.' -f3) #Run identifier: "BWSSP245" for ARISE Control
      RUN_VAR=$(echo $ACTIVE_FNAME | cut -d'.' -f11)
  elif [[ "$ACTIVE_FNAME" == *"CMIP6-historical"* ]]; then #CESM Historical (unprocessed)
      ACTIVE_FNAME=${ACTIVE_FNAME//_/.}
      RUN_FNAMES+=( $ACTIVE_FNAME )
      ACTIVE_TIME=$(echo $ACTIVE_FNAME | cut -d'.' -f11)
      RUN_TIMES+=( $ACTIVE_TIME )
      ACTIVE_ENSNUM=$(echo $ACTIVE_FNAME | cut -d'.' -f7)
      RUN_ENSNUMS+=( $ACTIVE_ENSNUM )
      RUN_TYPE=$(echo $ACTIVE_FNAME | cut -d'.' -f3) #Run identifier: "BWHIST" for Historical
      RUN_VAR=$(echo $ACTIVE_FNAME | cut -d'.' -f10)
  else #GLENS or ARISE Feedback
    RUN_FNAMES+=( $ACTIVE_FNAME ) #Append filenames to array
    ACTIVE_TIME=$(echo $ACTIVE_FNAME | cut -d'.' -f10) #Get start/end YYYYMM from file
    RUN_TIMES+=( $ACTIVE_TIME ) #Append start/end YYYYMM to array
    ACTIVE_ENSNUM=$(echo $ACTIVE_FNAME | cut -d'.' -f6) #Get ensemble member number from file (e.g. 001, 002)
    RUN_ENSNUMS+=( $ACTIVE_ENSNUM ) #Append ensemble number to array
    RUN_TYPE=$(echo $ACTIVE_FNAME | cut -d'.' -f5) #Run identifier: "control", "feedback" for GLENS, "SSP245-TSMLT-GAUSS" for ARISE
    RUN_VAR=$(echo $ACTIVE_FNAME | cut -d'.' -f9) #Variable identified in filename, e.g. TEMP, PRECT, hi, FSNO
  fi
done

### Troubleshooting
# echo ${RUN_FNAMES[@]}
# echo ${RUN_TIMES[@]}
# echo $RUN_TYPE
# echo ${RUN_ENSNUMS[@]}
# echo $RUN_VAR

OUT_FNAME="${RUN_TYPE}_${RUN_ENSNUMS[0]}_${RUN_VAR}"
for t in ${RUN_TIMES[@]}; do
  OUT_FNAME="${OUT_FNAME}_${t}" #Append start/end YYYYMM from constituent files to output filename
done
echo $OUT_FNAME

OUT_MERGE="${OUT_PATH}${OUT_FNAME}_merge.nc"
OUT_SHIFT="${OUT_PATH}${OUT_FNAME}_shift.nc"
OUT_ANNUAL="${OUT_PATH}${OUT_FNAME}_annual.nc"

cdo -L -yearmonmean -shifttime,'-1days' -mergetime ${IN_CARD} ${OUT_ANNUAL}
