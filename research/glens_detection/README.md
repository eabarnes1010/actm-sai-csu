# Project Description
* __project-name__: glens_detection
* __author__: Elizabeth A. Barnes, James Hurrell and Lantao Sun
* __date__: June 13, 2022

We train a simple machine learning model to predict whether a map of global extremes came from an RCP8.5 or stratospheric aerosol injection simulation. The timing of accurate predictions acts as a quantification of the time to detection of a geoengineered climate. Regional changes in extreme temperatures and extreme precipitation under SAI are robustly detected within 1 and 15 years of injection, respectively.


# Run the code

## Create empty directories
* You will also need to make additional directories:
    * ```saved_models/```
    * ```saved_predictions/```
    * ```figures/```    
    * ```data/```


## Data Access
* Data can be accessed at the group data server [here](https://eabarnes-data.atmos.colostate.edu/projects/actm-sai-csu/glens_detection/). 
* Data should be stored in a directory called ```data/```

## Order of code execution
Step 1: data_preprocessing.ipynb
Step 2: logistic_train.ipynb
Step 3: plot_results.ipynb


# Extra Information

## License
This project is licensed under an MIT license.

MIT © [Elizabeth A. Barnes](https://github.com/eabarnes1010)