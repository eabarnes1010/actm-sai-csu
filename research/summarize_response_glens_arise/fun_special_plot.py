''' fun_special_plot
Contains some special plotting functions for specific uses, e.g. plotting
colorbars alone or plotting quantiles vs. members for robustness.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys
import warnings

import cftime
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt

import matplotlib.font_manager as fm
fontPath = '/Users/dhueholt/Library/Fonts/'  #Location of font files
for font in fm.findSystemFonts(fontPath):
    fm.fontManager.addfont(font)

import fun_process_data as fpd
import fun_plot_tools as fpt

def save_colorbar(cbarDict, savePath, saveName, dpiVal=400):
    ''' Plots and saves a colorbar
        cbarDict should have a cmap, range, direction (horizontal vs. vertical),
        and label. Ex:
        cbarDict = {
            "cmap": cmocean.cm.delta,
            "range": [-15,15],
            "direction": 'vertical',
            "label": 'percent'
        }
    '''
    plt.rcParams.update({'font.size': 0})
    plt.rcParams.update({'font.family': 'Lato'})

    cbarRange = np.array([cbarDict["range"]])

    if cbarDict["direction"] == 'horizontal':
        plt.figure(figsize=(9,2.5))
        img = plt.imshow(cbarRange, cmap=cbarDict["cmap"])
        plt.gca().set_visible(False)
        colorAx = plt.axes([0.1,0.2,0.8,0.3])
        cb = plt.colorbar(orientation='horizontal', cax=colorAx)
        for label in cb.ax.get_xticklabels():
            print(label)
            # label.set_fontproperties(FiraSansThin) #Set font
            label.set_fontsize(0) #Set font size
    elif cbarDict["direction"] == 'vertical':
        plt.figure(figsize=(2.5,9))
        img = plt.imshow(cbarRange, cmap=cbarDict["cmap"])
        plt.gca().set_visible(False)
        colorAx = plt.axes([0.1,0.2,0.2,0.6])
        cb = plt.colorbar(orientation='vertical', cax=colorAx)
        for label in cb.ax.get_yticklabels():
            print(label)
            # label.set_fontproperties(FiraSansThin)
            # label.set_fontsize(18)
    else:
        sys.exit('Direction must be either horizontal or vertical.')

    if cbarDict["label"] == '':
        cb.set_ticks([])
    # cb.set_label(cbarDict["label"], size='large')
    # cb.set_label(cbarDict["label"], size='large', fontproperties=FiraSansThin) # Set font
    plt.savefig(savePath + saveName + '.png', dpi=dpiVal)

def quantiles_vs_members(robustness, nRlz, savePath=None):
    ''' Plots quantiles vs number of members '''
    plt.rcParams.update({'font.family': 'Palanquin'})
    plt.rcParams.update({'font.weight': 'light'}) #normal, bold, heavy, light, ultrabold, ultralight

    qList = list()
    quantiles = np.linspace(0,1,500)
    for q in quantiles:
        qList.append(np.nanquantile(robustness,q))

    plt.figure(figsize=(9,6))
    plt.plot(quantiles, qList, color='#ff4d81', linewidth=2.5)

    plt.xlabel('Quantiles', fontsize=18, fontweight='light')
    plt.ylabel('Ensemble members', fontsize=18, fontweight='light')
    plt.xlim(-0.01,1.01)
    plt.xticks([0,0.2,0.4,0.6,0.8,1], fontsize=14)
    plt.ylim(0,nRlz+1)
    plt.yticks(np.arange(0,nRlz,3), fontsize=14)
    plt.title('Quantiles vs members: Annual mean 2m temperature', fontsize=22, fontweight='light')

    if savePath == None:
        plt.show()
    else:
        plt.savefig(savePath + 'QuantileVsMembers_AnnualMean2mTempARISE' + '.png')

def plot_rob_spaghetti_demo(darrList, dataDict, setDict, outDict):
    ''' Timeseries with ensemble members visualized as spaghetti plot. '''
    plotRlzMn = False # Plot ensemble mean in addition to every member
    setYear = [2030, 2045]
    timeSlice = slice(
        cftime.DatetimeNoLeap(setYear[0], 7, 15, 12, 0, 0, 0),
        cftime.DatetimeNoLeap(setYear[1], 7, 15, 12, 0, 0, 0))
    robTime = [2040,2044]
    robSlice = slice(
        cftime.DatetimeNoLeap(robTime[0], 7, 15, 12, 0, 0, 0),
        cftime.DatetimeNoLeap(robTime[1], 7, 15, 12, 0, 0, 0))

    # Plot timeseries
    plt.rcParams.update({'font.size': 14})
    plt.rcParams.update({'font.family': 'Lato'})
    plt.rcParams.update({'font.weight': 'normal'})
    fig,ax = plt.subplots()
    scnToPlot = list() # Make list of all scenarios to be plotted
    for scnDarr in darrList:
        rlzInScn = scnDarr['realization'].data # Number of members in scenario
        scnToPlot.append(scnDarr.scenario) # Add scenario to list
        if setDict["areaAvgBool"] == True: # Ens mean stored as last member
            rlzMn = scnDarr[len(rlzInScn)-1]
            rlzInScn = rlzInScn[:-1] # Don't double-plot ens mean
        elif setDict["areaAvgBool"] == 'sum': # Copy and take ens mean later
            rlzMn = scnDarr.copy()
        for rc in rlzInScn: # For each individual member
            rlzToi = scnDarr.sel(realization=rc, time=timeSlice)
            rlzLoi = fpd.obtain_levels(rlzToi, setDict["levOfInt"])
            rlzToPlot, locStr, locTitleStr = fpd.manage_area(
                rlzLoi, setDict["regOfInt"], areaAvgBool=setDict["areaAvgBool"])
            md = fpd.meta_book(
                setDict, dataDict, rlzToPlot, labelsToPlot=None) # Get metadata
            actCol, actLab = fpt.line_from_scenario(rlzToPlot.scenario, md)
            yrsToPlot = rlzToPlot['time'].dt.year.data
            plt.plot(
                yrsToPlot, rlzToPlot, color=actCol,
                linewidth=0.5, alpha=0.6) # Plot each member TIMESERIES
            rlzRobTm = scnDarr.sel(realization=rc, time=robSlice)
            rlzTmMn = rlzRobTm.mean(dim='time')
            rlzLoiTmMn = fpd.obtain_levels(rlzTmMn, setDict["levOfInt"])
            rlzTmMnToPlot, _, _ = fpd.manage_area(
                rlzLoiTmMn, setDict["regOfInt"],
                areaAvgBool=setDict["areaAvgBool"])
            plt.plot([robTime[0],robTime[1]], [rlzTmMnToPlot,rlzTmMnToPlot], color=actCol)

            if plotRlzMn:
                rlzToiMn = rlzMn.sel(time=timeSlice)
                rlzLoiMn = fpd.obtain_levels(rlzToiMn, setDict["levOfInt"])
                rlzAoiMn = rlzLoiMn.isel()
                if setDict["areaAvgBool"] == 'sum':
                    # Ens mean must be taken AFTER area average
                    rlzAoiMn = rlzAoiMn.mean(dim='realization')
                plt.plot(
                    yrsToPlot, rlzAoiMn, color=actCol, label=actLab,
                    linewidth=2.5) # Plot ensemble mean

    # Plot metadata and settings
    plt.yticks(ticks=setDict["yticks"],labels=None)
    b,t = plt.ylim(setDict["ylim"])
    fpt.plot_metaobjects(scnToPlot, fig, b, t, lw=0.4)
    plt.ylabel('')
    plt.xlim(setYear[0], setYear[1])
    plt.xticks(ticks=[setYear[0],setYear[0]+5,setYear[0]+10,setYear[0]+14],labels=None)

    # Save image
    savePrfx = 'ROB_'
    saveStr = md['varSve'] + '_' + md['levSve'] + '_' + str(setYear[0]) \
        + str(setYear[1]) + '_' + locStr + '_' + md['ensStr'] + '_' \
        + md['ensPid']['spg']
    savename = outDict["savePath"] + savePrfx + saveStr + '.pdf'
    plt.savefig(savename, bbox_inches='tight')
    plt.close()
    ic(savename)
