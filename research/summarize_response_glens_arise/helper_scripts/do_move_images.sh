#######################################
# Move files into proper directories for IPCC regions.
# Written by Daniel Hueholt
# Graduate Research Assistant at Colorado State University
#######################################
UNSORTED_PATH="/Users/dhueholt/Documents/GLENS_fig/Upload/T/"
SORTED_PATH="/Users/dhueholt/Documents/GLENS_fig/Upload/T/992.6mb/"
SLASH="/"
T=".png"

REGIONS=(
"AKNWCan"
"Amazon"
"Antarctica"
"Arctic"
"CAmMex"
"CanGrnIce"
"CenNAm"
"CentralAsia"
"CentralEurope"
"EastAfrica"
"EastAsia"
"EstNAm"
"NorthAsia"
"NorthAustrla"
"NorthEurope"
"NrthestBrazil"
"PacIslReg2"
"PacIslReg3"
"Sahara"
"SAusNewZlnd"
"SEAsia"
"SESAm"
"SEurMed"
"SmIslCarbbn"
"SouthAsia"
"SthrnAfrica"
"STropPac"
"TibetPlat"
"WCstSAm"
"WestAfrica"
"WestAsia"
"WIndOcn"
"WstNAm"
)

for r in ${REGIONS[@]}; do
  mv $UNSORTED_PATH*$r*$T $SORTED_PATH$r/
done
