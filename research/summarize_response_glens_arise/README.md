# Summarizing regional and global climate responses to GLENS and ARISE
***
We analyze the regional and global climate responses in GLENS and ARISE for a
variety of familiar variables. We identify research questions that allow us to
use GLENS and ARISE together.

This code accompanies the following manuscript:
Hueholt, D.M., E.A. Barnes, J.W. Hurrell, J.H. Richter, & L. Sun. "Assessing Outcomes in Stratospheric Aerosol Injection Scenarios Shortly After Deployment" submitted to *Earth's Future*, [preprint available at ESSOaR](https://www.doi.org/10.22541/essoar.167591089.94758275/v1).

## Table of Contents
* [Project Summary](#project-summary)
* [Key Research Questions](#key-research-questions)
* [Data Access](#data-access)
* [Replicating Hueholt et al. 2023](#replicating-hueholt-et-al-2023)
* [Making Other Plots](#making-other-plots)
    * [Difference globe example](#difference-globe-example)
    * [Timeseries example](#timeseries-example)
* [Requirements](#requirements)
* [Brief Description of Code](#brief-description-of-code)
* [Questions and Answers](#questions-and-answers)
    * [What's with all the variable names referencing "control" and "feedback"?](#whats-with-all-the-variable-names-referencing-control-and-feedback)
    * [What do the "fun_", "run_", and "wrap_" in the filenames mean?](#what-do-the-fun_-run_-and-wrap_-in-the-filenames-mean)
* [Metadata](#metadata)

## Project Summary
The regional and global climate responses to SAI are not well understood. In
particular, it is unknown whether SAI could improve or worsen existing
inequalities in climate risk. **We develop code to visualize the response of
variables in the GLENS and ARISE experiments across global and regional scales.**
While this code is designed for these particular experiments it can be easily
extended, in principle, to any dataset that uses the Community Earth System
Model architecture.

## Key Research Questions
1. "What happens before and after initiation?"
2. “What is the impact of the intervention in each scenario?”

In Hueholt et al. 2023, **we address these questions for a subset of
high-impact, well-constrained variables.** This work is intended to provide a
“one-stop shop” of useful figures, and a point of entry for researchers and
stakeholders new to SAI.

## Data Access
The processed data needed to replicate the results of Hueholt et al. 2023 is hosted in an [Open Science Foundation archive](https://osf.io/5a2zf/). Raw GLENS, ARISE, and CESM2(WACCM6) Historical data is available at NCAR and Amazon Web Services. See the data availability statement in Hueholt et al. 2023, or the Earth science datasheet at our Open Science Foundation archive for details.

## Replicating Hueholt et al. 2023
`wrap_paperplots_basicplots_script` generates all difference globes figures, e.g., Figure 1, 3-8, S2. `wrap_paperplots_ensplots_script` yields all timeseries, e.g., Figure 2, S3, S4.

## Making Other Plots
To make figures that aren't specifically in the paper, use `wrap_basicplots_script` for difference globes and `wrap_ensplots_script` for timeseries.

### Difference globe example
![Difference globe](images/hueholtetal-f03.png)
`wrap_basicplots_script` generates these figures without the title or colorbar; in Hueholt et al. 2023, these are added manually using Keynote. This can easily be modified by the user by editing the functions in `fun_basic_plot`.

### Timeseries example
![Timeseries](images/hueholt-ts-example.png)
The code generates these figures without the title or annotations, which are added manually using Keynote. This behavior can be changed to add titles automatically by modifying the inputs in `wrap_ensplots_script` as stated in the docstring for this file. Similarly, the appearance can also be controlled manually by editing the functions in `fun_ens_plot`.

## Requirements
Required Python packages and versions available on `pip` are listed in the `requirements.txt` file. Additionally, the [marineHeatWaves](https://github.com/ecjoliver/marineHeatWaves) package by [Eric Oliver](https://github.com/ecjoliver) is required to run code related to marine heatwaves.

## Brief description of Code
All code written in Python unless specified otherwise.
* `CustomExceptions`: Custom exceptions, written partly as a coding exercise
* `fun_basic_plot`: Contains the difference globe plotting functions
* `fun_convert_unit`: Functions for simple in-line unit conversions and calculations
* `fun_derive_data`: Functions to derive and save data from a base dataset to a new netCDF file
* `fun_ens_plot`: Functions to plot data as timeseries with ensemble visualizations (spaghetti, spread)
* `fun_plot_tools`: Plotting functions wrapped by `wrap_basicplots_script` and `wrap_paperplots_basicplots_script`
* `fun_process_data`: Functions for operations used across many scripts like extracting metadata from filenames, opening files in, managing area inputs and realizations, etc.
* `fun_regrid_pop`: Functions to remap ocean from POP B-grid to lat/lon using methods from [Emily Gordon](https://sites.google.com/view/emilygordon) and [Zachary Labe](https://zacklabe.com/)
* `fun_robustness`: Functions to calculate robustness of trends in data (see Hueholt et al. 2023 Supplemental for description of robustness)
* `fun_special_plot`: Special plotting functions for specific uses (e.g., plotting colorbars alone)
* `README`: This README file
* `region_library`: Contains regions that can be called from plotting functions
* `requirements.txt`: Required Python packages available on `pip`
* `run_derive_data_script`: Shell script to run wrap_derive_data_script on NCAR Casper
* `run_ocean_script`: Shell script to run wrap_ocean_script on NCAR Casper
* `wrap_basicplots_script`: Wrap difference globe plotting functions
* `wrap_derive_data_script`: Wrap functions to derive data
* `wrap_derive_mhw_definitionFile`: Wrap function to define MHW baseline for reference period at a given location
* `wrap_ensplots_script`: Wrap plotting functions to make timeseries with ensemble visualizations
* `wrap_ocean_script`: Wrap functions to remap ocean data from POP B-grid to lat/lon coordinates
* `wrap_paperplots_basicplots_script`: Script to instantly replicate all difference globe figures (e.g., Figure 1, 3-8, S2) from Hueholt et al. 2023
* `wrap_paperplots_ensplots_script`: Script to instantly replicate all timeseries figures  (e.g., Figure 2, S3, S4) from Hueholt et al. 2023
* `wrap_plotregions_script`: Make plots of input region(s) on a map
* `wrap_stat_robustness`: Calculate statistical metrics for robustness
* `wrap_test_script`: This is just a file I use as "scratch paper" when coding

* `cdo_mproc`: Folder of code that wraps CDO functions in Python to process raw ESM data
    * `run_mproc_cdo_prep`: Shell script to run wrap_mproc_cdo_script on NCAR Casper
    * `wrap_mproc_cdo_prep`: Wraps functions which call CDO to carry out various foundational data processing tasks like making annual mean from monthly data
    * `mproc_bees`: This folder contains the individual CDO functions for each task, these are documented within each file

* `get_data`: Folder of code to obtain data on NCAR Casper

* `helper_scripts`: Contains a few additional shell scripts for one-off tasks that occasionally need to be run.
    * `do_move_images`: Shell script to move images into folders by region (of limited use to anyone but me)
    * `do_sumtwo_makenew`: Shell script to sum data from two files to make a new variable, such as making total precipitation from convective and large-scale precipitation variables in GLENS
    * `run_selyear`: Shell script to select years from data using CDO
    * `run_sumtwo_makenew`: Shell script to run `do_sumtwo_makenew` on NCAR Casper

* `images`: Folder containing images used in the README file.

## Questions and Answers
### What's with all the variable names referencing "control" and "feedback"?
"Control" refers to the runs following a climate change trajectory WITHOUT SAI ("no-SAI" in Hueholt et al. 2023). "Feedback" refers to runs where SAI is also deployed in the model ("SAI" in Hueholt et al. 2023). "Control" and "Feedback" were terms that come out of the development of GLENS and ARISE. I wrote the code in this repository using that standard terminology before settling on the "SAI/no-SAI" terminology we used in the paper.

### What do the "fun_", "run_", and "wrap_" in the filenames mean?
Generally, code in this repository follows the naming schema:
*    "fun_" contains individual functions
*    "wrap_" wraps these functions to be run from the command line
*    "run_" runs scripts from the job scheduler on NCAR's Casper and Cheyenne

***

## Metadata
Funded by DARPA‐PA‐21‐04‐02 with PIs [Prof. James Hurrell](https://sites.google.com/rams.colostate.edu/hurrellgroup/home) and
[Prof. Elizabeth A. Barnes](https://barnes.atmos.colostate.edu) at Colorado
State University. Daniel Hueholt was additionally supported by the National Science Foundation Graduate Research Fellowship Program.

Except where otherwise specified, this code written and maintained by
[Daniel Hueholt](https://www.hueholt.earth/) as a Graduate Research Assistant at
Colorado State University, co-advised by Prof. James Hurrell and Prof. Elizabeth
Barnes.

* Code in this project is licensed under the Open Software License 3.0, included with this repository as `LICENSE.txt`
* Figures and text associated with this project are licensed under [Creative Commons Attribution Share Alike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/)
