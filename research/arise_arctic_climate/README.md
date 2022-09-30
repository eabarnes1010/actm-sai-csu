# Project Description
* __project-name__: arise_arctic_climate
* __authors__: Ariel L. Morrison, Elizabeth A. Barnes, James Hurrell
* __date__: June 16, 2022

The Arctic is the fastest-warming region on Earth in response to increasing atmospheric greenhouse gas concentrations. As the Arctic warms, its climate is likely to experience dramatic changes such as widespread permafrost thaw. Permafrost thaw could potentially lead to a climate tipping point through the release of stored carbon, where released CO2 and CH4 could accelerate the rate of high latitude warming and cause a positive permafrost carbon feedback. This work examines how climate intervention strategies (i.e., stratospheric aerosol injection) may prevent or slow the onset of this potential tipping point. We focus on the ARISE-SAI-1.5 simluations and compare them with the SSP2-4.5 climate scenario in the CESM2 model.

## Create empty directories
* You will also need to make additional directories:
    * ```functions/```
    * ```data/```
    * ```figures/```    

## Data Access
* ARISE data can be accessed at this url: [ARISE-SAI-1.5](https://www.earthsystemgrid.org/dataset/ucar.cgd.ccsm4.ARISE-SAI-1.5.html)
* CESM2-WACCM data can be accessed at this url: [CESM2-WACCM6-SSP2-4.5](https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2.waccm6.ssp245.html)
* Data should be stored in the directory called ```data/```

## Python environment
* Install requirements.txt to load required python packages 

## Running the code
Scripts should be run in the following order:
1. readData.py
2. preprocessingData.py
3. plottingFunctions.py
4. train_and_predict_year.py

## License
This project is licensed under an MIT license.

MIT © [Ariel L. Morrison](https://github.com/ariel-morrison)
