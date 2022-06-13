# Project Description
* __project-name__: arise_seasonalprediction
* __authors__: Kirsten J. Mayer, Elizabeth A. Barnes, James Hurrell
* __date__: June 13, 2022

The climate is projected to continue warming in the coming decades. To mitgate the impacts of climate change, one proposed method is stratospheric aerosol injection (SAI). By injecting aerosols into the stratopshere, we can enhance Earth's reflectivitly and thus, cool the planet. However, little is known about how SAI may impact the Earth System, including its dynamics and predictability. Previous research suggests that El Nino Southern Oscillation teleconnections may change in a warmer world. These teleconnections provide a large source of seasonal predictability to North America in our current climate. Therefore, this work examines how SAI may impact seasonal predictability over the West Coast of North America compared to a future, warmer world.

# Run the code

## Create empty directories
* You will also need to make additional directories:
    * ```functions/```
    * ```saved_models/```
    * ```figures/```    

## Data Access
* ARISE data can be accessed at this url: 
* Data should be stored in the directory called ```data/```

## Order of code execution
* ENSO Teleconnection Analysis:
   * Step 1: Nino34_t2mteleconnections.py
   * Step 2: plot_t2mteleconnections.py
   * Step 3: plot_t2mteleconnections_freqhist.py
* Neural Network Analysis:
   * Step 1: trainNN.py
   * Step 2: evaluateNN.py
   * Step 3: plot_accvsconf.py

# Extra Information

## License
This project is licensed under an MIT license.

MIT © [Kirsten J. Mayer](https://github.com/kjmayer)
