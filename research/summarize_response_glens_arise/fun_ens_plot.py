''' fun_ens_plot
Contains functions to plot data with ensemble visualizations.

plot_ens_spaghetti_timeseries: plots a timeseries with each member visualized
as its own line, this is the classic "spaghetti plot"
plot_ens_spread_timeseries: plots timeseries with ensemble mean shown as line
and spread between max and min member shaded

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

import xarray as xr
xr.set_options(keep_attrs=True)
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import cftime

import matplotlib.font_manager as fm
fontPath = '/Users/dhueholt/Library/Fonts/'  #Location of font files
for font in fm.findSystemFonts(fontPath):
    fm.fontManager.addfont(font)

import fun_process_data as fpd
import fun_plot_tools as fpt
import fun_convert_unit as fcu
import region_library as rlib

def plot_ens_spaghetti_timeseries(darrList, dataDict, setDict, outDict):
    ''' Timeseries with ensemble members visualized as spaghetti plot. '''
    plotRlzMn = True # Plot ensemble mean in addition to every member
    setYear = [2010, 2070]
    timeSlice = slice(
        cftime.DatetimeNoLeap(setYear[0], 7, 15, 12, 0, 0, 0),
        cftime.DatetimeNoLeap(setYear[1], 7, 15, 12, 0, 0, 0))

    # Plot timeseries
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
                setDict, dataDict, rlzToPlot) # Get metadata
            actCol, actLab = fpt.line_from_scenario(rlzToPlot.scenario, md)
            yrsToPlot = rlzToPlot['time'].dt.year.data
            plt.plot(
                yrsToPlot, rlzToPlot, color=actCol,
                linewidth=0.7) # Plot each member
            if plotRlzMn:
                rlzToiMn = rlzMn.sel(time=timeSlice)
                rlzLoiMn = fpd.obtain_levels(rlzToiMn, setDict["levOfInt"])
                rlzAoiMn, _, __ = fpd.manage_area(
                    rlzLoiMn, setDict["regOfInt"],
                    areaAvgBool=setDict["areaAvgBool"])
                if setDict["areaAvgBool"] == 'sum':
                    # Ens mean must be taken AFTER area average
                    rlzAoiMn = rlzAoiMn.mean(dim='realization')
                plt.plot(
                    yrsToPlot, rlzAoiMn, color=actCol, label=actLab,
                    linewidth=2.5) # Plot ensemble mean

    # Plot metadata and settings
    b,t = plt.ylim() if setDict['ylim'] is None else setDict['ylim']
    fpt.plot_metaobjects(scnToPlot, fig, b, t)
    # leg = plt.legend()
    plt.ylabel(md['unit'])
    plt.autoscale(enable=True, axis='x', tight=True)
    plt.autoscale(enable=True, axis='y', tight=True)
    plt.xlim(setYear[0], setYear[1])
    plt.title(md['varStr'] + ' ' + md['levStr'] + ': ' + str(setYear[0]) + '-' \
        + str(setYear[1]) + ' ' + locTitleStr  + ' ' + 'spaghetti')

    # Save image
    savePrfx = ''
    saveStr = md['varSve'] + '_' + md['levSve'] + '_' + str(setYear[0]) \
        + str(setYear[1]) + '_' + locStr + '_' + md['ensStr'] + '_' \
        + md['ensPid']['spg']
    if outDict["dpiVal"] == 'pdf':
        savename = outDict["savePath"] + savePrfx + saveStr + '.pdf'
        plt.savefig(savename, bbox_inches='tight')
    else:
        savename = outDict["savePath"] + savePrfx + saveStr + '.png'
        plt.savefig(savename, dpi=outDict["dpiVal"], bbox_inches='tight')
    plt.close()
    ic(savename)


def plot_ens_spread_timeseries(darrList, dataDict, setDict, outDict):
    ''' Timeseries with ensemble variability visualized as spread between max
    and min at each timestep. '''
    setYear = [2010,2069]
    timeSlice = slice(
        cftime.DatetimeNoLeap(setYear[0], 1, 1, 12, 0, 0, 0),
        cftime.DatetimeNoLeap(setYear[1], 12, 31, 12, 0, 0, 0)) #arbitrary MDHMS

    # General plot settings
    if (setDict["styleFlag"] == 2) | (setDict["styleFlag"] == 3):
        plt.rcParams.update({'font.size': 24})
        plt.rcParams.update({'font.family': 'Lato'})
        plt.rcParams.update({'font.weight': 'normal'})
        # Valid fontweights: normal, bold, heavy, light, ultrabold, ultralight
    plt.rcParams.update({'figure.autolayout': True})
    fig, ax = plt.subplots(figsize=[8,7])
    scnToPlot = list()

    # Plotting
    for darr in darrList:
        darrToi = darr.sel(time=timeSlice)
        darrLoi = fpd.obtain_levels(darrToi, setDict["levOfInt"])
        if isinstance(setDict["regOfInt"],tuple): # Avg over multiple regions
            subregList = list()
            colLocStr = ''
            colLocTitleStr = ''
            for subreg in setDict["regOfInt"]:
                subregData, locStr, locTitleStr = fpd.manage_area(
                        darrLoi, subreg, areaAvgBool=setDict["areaAvgBool"])
                subregList.append(subregData)
                colLocStr += locStr
                colLocTitleStr += locTitleStr
            concatAlongReg = xr.concat(subregList, dim="regions")
            dataToPlot = concatAlongReg.mean(dim="regions", skipna=True)
            locStr = colLocStr
            locTitleStr = colLocTitleStr
        else: # Avg over single region
            dataToPlot, locStr, locTitleStr = fpd.manage_area(
                    darrLoi, setDict["regOfInt"],
                    areaAvgBool=setDict["areaAvgBool"])
        rlzMax = dataToPlot.max(dim='realization', skipna=True)
        rlzMin = dataToPlot.min(dim='realization', skipna=True)
        if setDict["areaAvgBool"] == True:
            ensMnInd = len(dataToPlot['realization'])-1 #Last index is ens mean
            rlzMn = dataToPlot[ensMnInd]
        elif setDict["areaAvgBool"] == 'sum':
            rlzMn = dataToPlot.mean(dim='realization')
        md = fpd.meta_book(setDict, dataDict, rlzMn)
        yrsToPlot = rlzMn['time'].dt.year.data
        scnToPlot.append(darr.scenario)
        activeColor, activeLabel = fpt.line_from_scenario(darr.scenario, md)
        # plt.plot(yrsToPlot,rlzMax.data,color=activeColor,linewidth=0.3) #Border on top of spread
        # plt.plot(yrsToPlot,rlzMin.data,color=activeColor,linewidth=0.3) #Border on bottom of spread
        # plt.plot(yrsToPlot,rlzMax.data,color='#D3D3D3',linewidth=0.3) #Border on top of spread
        # plt.plot(yrsToPlot,rlzMin.data,color='#D3D3D3',linewidth=0.3) #Border on bottom of spread
        # ic(darr.scenario) # For troubleshooting, show plotted scenarios

        # Apply image muting (e.g., gray out and alpha) on part of timeseries
        # i.e. to emphasize a certain time period such as a window for averaging
        # (Not used in Hueholt et al. 2023)
        if setDict["mute"] == True:
            # D3D3D3 is gray for muted objects
            plt.plot(
                yrsToPlot, rlzMn.data, color='#D3D3D3', linewidth=3, alpha=0.5)
            ax.fill_between(
                yrsToPlot, rlzMax.data, rlzMin.data, color='#D3D3D3', alpha=0.2,
                linewidth=0)
            # Plot unmuted sections--hard-coded as indices unique to scenario
            if 'GLENS:Control' in darr.scenario:
                gcw = [5, 11, 55, 60] # [5,11] immediate, [5,11,45,50] impact (+10 for defense), [5,11,15,20] compromise
                ic(yrsToPlot[gcw[0]:gcw[1]], rlzMn.data[gcw[0]:gcw[1]])
                plt.plot(
                    yrsToPlot[gcw[0]:gcw[1]], rlzMn.data[gcw[0]:gcw[1]],
                    color=activeColor, label=activeLabel, linewidth=3.5)
                ax.fill_between(
                    yrsToPlot[gcw[0]:gcw[1]], rlzMax.data[gcw[0]:gcw[1]],
                    rlzMin.data[gcw[0]:gcw[1]], color=activeColor, alpha=0.3,
                    linewidth=0)
                if len(gcw)>2:
                    ic(yrsToPlot[gcw[2]:gcw[3]],rlzMn.data[gcw[2]:gcw[3]])
                    plt.plot(
                        yrsToPlot[gcw[2]:gcw[3]], rlzMn.data[gcw[2]:gcw[3]],
                        color=activeColor, linewidth=3.5)
                    ax.fill_between(
                        yrsToPlot[gcw[2]:gcw[3]], rlzMax.data[gcw[2]:gcw[3]],
                        rlzMin.data[gcw[2]:gcw[3]], color=activeColor,
                        alpha=0.3, linewidth=0)
            elif 'GLENS:Feedback' in darr.scenario:
                gfw = [45,50] # [0,5] immediate, [35,40] impact, [5,10] compromise
                ic(yrsToPlot[gfw[0]:gfw[1]], rlzMn.data[gfw[0]:gfw[1]])
                plt.plot(
                        yrsToPlot[gfw[0]:gfw[1]], rlzMn.data[gfw[0]:gfw[1]],
                        color=activeColor, label=activeLabel, linewidth=3.5)
                ax.fill_between(
                        yrsToPlot[gfw[0]:gfw[1]], rlzMax.data[gfw[0]:gfw[1]],
                        rlzMin.data[gfw[0]:gfw[1]], color=activeColor,
                        alpha=0.3, linewidth=0)
            elif 'ARISE:Feedback' in darr.scenario:
                afw = [30,35] # [0,5] immediate, [20,25] impact, [5,10] compromise
                ic(yrsToPlot[afw[0]:afw[1]], rlzMn.data[afw[0]:afw[1]])
                plt.plot(
                        yrsToPlot[afw[0]:afw[1]], rlzMn.data[afw[0]:afw[1]],
                        color=activeColor,label=activeLabel,linewidth=3.5)
                ax.fill_between(
                        yrsToPlot[afw[0]:afw[1]], rlzMax.data[afw[0]:afw[1]],
                        rlzMin.data[afw[0]:afw[1]], color=activeColor,
                        alpha=0.3, linewidth=0)
            elif 'ARISE:Control' in darr.scenario:
                acw = [20,26,55,60] # [20,26] immediate, [20,26,45,50] impact, [20,26,30,35] compromise
                ic(yrsToPlot[acw[0]:acw[1]], rlzMn.data[acw[0]:acw[1]])
                plt.plot(
                        yrsToPlot[acw[0]:acw[1]], rlzMn.data[acw[0]:acw[1]],
                        color=activeColor, label=activeLabel, linewidth=3.5)
                ax.fill_between(
                        yrsToPlot[acw[0]:acw[1]], rlzMax.data[acw[0]:acw[1]],
                        rlzMin.data[acw[0]:acw[1]], color=activeColor,
                        alpha=0.3, linewidth=0)
                if len(acw)>2:
                    ic(yrsToPlot[acw[2]:acw[3]], rlzMn.data[acw[2]:acw[3]])
                    plt.plot(
                            yrsToPlot[acw[2]:acw[3]], rlzMn.data[acw[2]:acw[3]],
                            color=activeColor, linewidth=3.5)
                    ax.fill_between(
                            yrsToPlot[acw[2]:acw[3]],
                            rlzMax.data[acw[2]:acw[3]],
                            rlzMin.data[acw[2]:acw[3]],
                            color=activeColor, alpha=0.3, linewidth=0)
        else: # No image muting, plot whole timeseries in full color
            plt.plot(
                yrsToPlot, rlzMn.data, color=activeColor, label=activeLabel,
                linewidth=3.5)
            ax.fill_between(
                yrsToPlot, rlzMax.data, rlzMin.data, color=activeColor,
                alpha=0.3, linewidth=0)

    # Plot metadata and settings
    b,t = plt.ylim() if setDict['ylim'] is None else setDict['ylim']
    fpt.plot_metaobjects(scnToPlot, fig, b, t)
    # plt.autoscale(enable=True, axis='x', tight=False)
    # plt.autoscale(enable=True, axis='y', tight=False)
    xlf,xrt = plt.xlim(setYear[0], setYear[1])
    if setDict["styleFlag"] == 0: # All aesthetics automatic
        plt.ylabel(md['unit'])
        leg = plt.legend()
        plt.title(md['varStr'] + ' ' + md['levStr'] + str(setYear[0]) + '-'
                + str(setYear[1]) + ' ' + locTitleStr  + ' ' + 'spread')
        savePrfx = ''
        plt.ylim([b,t])
    elif setDict["styleFlag"] == 1: # Lines only
        savePrfx = 'LINESONLY_'
        ax.axis('off')
    elif setDict["styleFlag"] == 2: # Use setDict inputs, no title or unit
        savePrfx = 'AES_'
        if setDict["xticks"]:
            plt.xticks([2015,2040,2065,])
        else:
            plt.xticks([2015,2040,2065,])
            ax.tick_params(labelbottom=False)
        if setDict['ylim'] is not None:
            plt.yticks(setDict["yticks"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # ax.axes.xaxis.set_ticklabels([])
        # ax.axes.yaxis.set_ticklabels([])
        plt.ylim([b,t])
        if setDict['ylabel'] is not None:
            plt.ylabel(setDict['ylabel'], fontweight='normal')
        # plt.xlabel('years', fontweight='light')
        # ax.axes.xaxis.set_ticklabels([])
    elif setDict["styleFlag"] == 3: # Style for IPCC regions in paper
        savePrfx = 'IPCCregions_'
        plt.xticks([2015, 2040, 2065], size=17)
        plt.yticks(setDict["yticks"], size=17)
        plt.ylabel(md['unit'], size=16)
        titleStr = md['varStr'] + ' ' + str(int(xlf)) + '-' + str(int(xrt)) \
            + ' ' + locTitleStr
        plt.title(titleStr, weight='normal', size=20)
        legProp = {'size': 12,
                   'weight':'normal'}
        leg = ax.legend()
        handles, labels = ax.get_legend_handles_labels()
        handles = [handles[0], handles[1], handles[3], handles[2]]
        labels = [labels[0], labels[1], labels[3], labels[2]]
        ax.legend(
            handles, labels, loc='upper center', prop=legProp,
            bbox_to_anchor=(0.5, -0.07), ncol=2, frameon=True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.ylim([b, t])
        saveStr = md['varSve'] + '_' + str(int(xlf)) + str(int(xrt)) + '_' + \
                locStr + '_' + 'ts'

    # Save image
    savePrfx = savePrfx
    if setDict["styleFlag"] != 3:
        saveStr = md['varSve'] + '_' + md['levSve'] + '_' + str(setYear[0]) + \
                str(setYear[1]) + '_' + locStr + '_' + md['ensStr'] + '_' + \
                md['ensPid']['sprd']
    saveStr = saveStr.replace("/",'-')
    if outDict['addToSaveStr'] is not None:
        saveStr = saveStr + outDict['addToSaveStr']

    # fig.set_size_inches(8, 6)
    if outDict["dpiVal"] == 'pdf':
        savename = outDict["savePath"] + savePrfx + saveStr + '.pdf'
        plt.savefig(savename, bbox_inches='tight')
    else:
        savename = outDict["savePath"] + savePrfx + saveStr + '.png'
        plt.savefig(savename, dpi=outDict["dpiVal"], bbox_inches='tight')
    plt.close()
    ic(savename)
