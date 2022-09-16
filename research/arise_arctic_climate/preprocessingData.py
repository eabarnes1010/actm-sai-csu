#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 15:59:11 2022

@author: Ariel L. Morrison
"""

def preprocessDataForPrediction(timeFrame,var):
    import os; os.chdir('/Users/arielmor/Projects/actm-sai-csu/research/arise_arctic_climate')
    from readData import readData
    import numpy as np
    import warnings
    
    datadir = '/Users/arielmor/Desktop/SAI/data/ARISE/data'
    ## ------ Read control & feedback active layer depth ------ ##
    if var == 'ALT':
        lat,lon,control,controlGS,controlNGS,controlANN,controlWINTER,controlSPRING,\
            controlSUMMER,controlFALL,controlFEB,controlMARCH,controlAPRIL,controlMAY,\
                controlJUNE,controlJULY,controlAUG,controlSEPT,controlOCT,controlNOV,\
                    controlDEC,ens,timeCONTROL = readData(datadir,str(var),True)
        lat,lon,arise,ariseGS,ariseNGS,ariseANN,ariseWINTER,ariseSPRING,\
            ariseSUMMER,ariseFALL,ariseFEB,ariseMARCH,ariseAPRIL,ariseMAY,\
                ariseJUNE,ariseJULY,ariseAUG,ariseSEPT,ariseOCT,ariseNOV,\
                    ariseDEC,ens,timeARISE = readData(datadir,str(var),False)
    elif var == 'ER':
        lat,lon,control,ens,timeCONTROL = readData(datadir,str(var),True)
        lat,lon,arise,ens,timeARISE = readData(datadir,str(var),False)
    ## ---------------------------------------------------- ##
    
    ## ------ Processing data ------ ##
    ''' 
    lenTime = number of time units in 20 years
    numYears = number of years for training
    numUnits = total number of time units (e.g., total years in data record)
    '''
    numYears = 20
    if timeFrame == 'monthly':
        timeStartControl = 240 # np.where(control[ens[0]].time == np.datetime64(datetime.datetime(2035, 1, 1)))
        timeEndFeedback  = 359 # np.where(arise[ens[0]].time == np.datetime64(datetime.datetime(2064, 12, 1)))
        varCONTROL       = control
        varFEEDBACK      = arise
        lenTime          = 12*numYears
        numUnits         = 360 # number of total months
    elif timeFrame == 'winter' or timeFrame == 'non_growing_season':
        timeStartControl = int(np.abs(2035-controlANN[ens[0]].year).argmin())
        timeEndFeedback  = int(np.abs(2063-ariseANN[ens[0]].year).argmin())
        if timeFrame     == 'winter':
            varCONTROL   = controlWINTER
            varFEEDBACK  = ariseWINTER
        if timeFrame     == 'non_growing_season':
            varCONTROL   = controlNGS
            varFEEDBACK  = ariseNGS
        lenTime          = 1*(numYears-1)
        numUnits         = 29
    elif timeFrame == 'annual':
        if var == 'ALT':
            timeStartControl = int(np.abs(2035-controlANN[ens[0]].year).argmin())
            timeEndFeedback  = int(np.abs(2064-ariseANN[ens[0]].year).argmin())
            varCONTROL   = controlANN
            varFEEDBACK  = ariseANN
        elif var == 'ER':
            timeStartControl = int(np.abs(2035-control[ens[0]].year).argmin())
            timeEndFeedback  = int(np.abs(2064-arise[ens[0]].year).argmin())
            varCONTROL = control
            varFEEDBACK = arise
        lenTime          = 1*numYears
        numUnits         = 30 # number of total years
    else:
        timeStartControl = int(np.abs(2035-controlANN[ens[0]].year).argmin())
        timeEndFeedback  = int(np.abs(2064-ariseANN[ens[0]].year).argmin()) 
        if timeFrame   == 'growing_season':
            varCONTROL   = controlGS
            varFEEDBACK  = ariseGS
        elif timeFrame   == 'spring':
            varCONTROL   = controlSPRING
            varFEEDBACK  = ariseSPRING
        elif timeFrame   == 'summer':
            varCONTROL   = controlSUMMER
            varFEEDBACK  = ariseSUMMER
        elif timeFrame   == 'fall':
            varCONTROL   = controlFALL
            varFEEDBACK  = ariseFALL
        elif timeFrame   == 'feb':
            varCONTROL   = controlFEB
            varFEEDBACK  = ariseFEB
        elif timeFrame   == 'march':
            varCONTROL   = controlMARCH
            varFEEDBACK  = ariseMARCH
        elif timeFrame   == 'april':
            varCONTROL   = controlAPRIL
            varFEEDBACK  = ariseAPRIL
        elif timeFrame   == 'may':
            varCONTROL   = controlMAY
            varFEEDBACK  = ariseMAY
        elif timeFrame   == 'june':
            varCONTROL   = controlJUNE
            varFEEDBACK  = ariseJUNE
        elif timeFrame   == 'july':
            varCONTROL   = controlJULY
            varFEEDBACK  = ariseJULY
        elif timeFrame   == 'august':
            varCONTROL   = controlAUG
            varFEEDBACK  = ariseAUG
        elif timeFrame   == 'september':
            varCONTROL   = controlSEPT
            varFEEDBACK  = ariseSEPT
        elif timeFrame   == 'october':
            varCONTROL   = controlOCT
            varFEEDBACK  = ariseOCT
        elif timeFrame   == 'november':
            varCONTROL   = controlNOV
            varFEEDBACK  = ariseNOV
        elif timeFrame   == 'december':
            varCONTROL   = controlDEC
            varFEEDBACK  = ariseDEC
        lenTime          = 1*numYears
        numUnits         = 30 # number of total years
   
    # CONTROL
    featuresC = []
    for ensNum in range(len(ens)):
        print(varCONTROL[ens[ensNum]]) 
        if timeFrame == 'winter' or timeFrame == 'non_growing_season':
            temp = np.stack(varCONTROL[ens[ensNum]][timeStartControl:,29:-6,:].astype('float'))
        else:
            temp = np.stack(varCONTROL[ens[ensNum]][timeStartControl:,29:-6,:].values.astype('float'))
        featuresC.append(temp)
    del temp
    
    # FEEDBACK
    featuresF = []
    for ensNum in range(len(ens)):
        if timeFrame == 'winter' or timeFrame == 'non_growing_season':
            temp = np.stack(varFEEDBACK[ens[ensNum]][:timeEndFeedback+1,29:-6,:].astype('float'))
        else:
            temp = np.stack(varFEEDBACK[ens[ensNum]][:timeEndFeedback+1,29:-6,:].values.astype('float'))
        featuresF.append(temp)
    del temp
    ## ---------------------------------------------------- ##
    
    ## ------ Split training/test data ------ ##
    from random import sample
    number_list = [4,6,7,8,9,10,1,2,3]
    new_list    = sample(number_list,len(number_list))
    valNum      = 2
    testNum     = 1
    print('training members = ' + str(new_list[:-(valNum+testNum)]))
    print('validate members = ' + str(new_list[-(valNum+testNum):-testNum]))
    print('testing member = ' + str(new_list[-testNum:]))
    featuresF_train = featuresF[:-(valNum+testNum)]
    featuresC_train = featuresC[:-(valNum+testNum)]
    featuresF_val   = featuresF[-(valNum+testNum):-testNum]
    featuresC_val   = featuresC[-(valNum+testNum):-testNum]
    featuresF_test  = featuresF[-testNum:]
    featuresC_test  = featuresC[-testNum:]
    ## ---------------------------------------------------- ##
    
    ## ------ Create labels for each simulation ------ ##
    ''' 
        number of ensemble members, number of time steps
        CONTROL = 0; FEEDBACK = 1
    '''
    labelsC_train = np.ones((len(featuresC_train),numUnits))*0
    labelsF_train = np.ones((len(featuresF_train),numUnits))*1
    labelsC_val   = np.ones((len(featuresC_val),numUnits))*0
    labelsF_val   = np.ones((len(featuresF_val),numUnits))*1
    labelsC_test  = np.ones((len(featuresC_test),numUnits))*0
    labelsF_test  = np.ones((len(featuresF_test),numUnits))*1
    ## ---------------------------------------------------- ##
    
    ## ------ Concatenate control/feedback data for neural net training ------ ##
    '''
        also important for standardizing data
    '''
    features_train = np.append(featuresC_train,featuresF_train,axis=0)
    features_val   = np.append(featuresC_val,featuresF_val,axis=0)
    features_test  = np.append(featuresC_test,featuresF_test,axis=0)
    labels_train   = np.append(labelsC_train,labelsF_train,axis=0)
    labels_val     = np.append(labelsC_val,labelsF_val,axis=0)
    labels_test    = np.append(labelsC_test,labelsF_test,axis=0)
    ## ----------------------------------------------------------------------- ##
    
    ## ------ Standardize data ------ ##
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        featuresMean = np.nanmean(features_train,axis=(0,1))
        featuresStd = np.nanstd(features_train,axis=(0,1))
        
        ''' Standardize training, validation, testing the same way '''
        features_train = (features_train-featuresMean)/featuresStd
        features_val = (features_val-featuresMean)/featuresStd
        features_test = (features_test-featuresMean)/featuresStd        
    ## ------------------------------ ##
    
    ## ------ Replace NaNs with 0 ------ ##
    features_train[np.isnan(features_train)] = 0.
    features_val[np.isnan(features_val)] = 0.
    features_test[np.isnan(features_test)] = 0.
    ## --------------------------------- ##
    
    # ## ------ Map of last time step's active layer depth ------ ##
    from plottingFunctions import make_maps, get_colormap
    brbg_cmap,rdbu_cmap,jet,magma,reds = get_colormap(21)
    if var == 'ALT':
        fig,ax = make_maps(varCONTROL[ens[testNum]][-1,29:-6,:],lat[29:-6],lon,
                            0,20,21,magma,'depth (m)','ALT for control '+str(timeFrame),'LR_active_layer_map_CONTROL_'+str(timeFrame))
        fig,ax = make_maps(varFEEDBACK[ens[testNum]][-1,29:-6,:],lat[29:-6],lon,
                            0,20,21,magma,'depth (m)','ALT for feedback '+str(timeFrame),'LR_active_layer_map_FEEDBACK_'+str(timeFrame))
        fig,ax = make_maps((varCONTROL[ens[testNum]][-1,29:-6,:] - varFEEDBACK[ens[testNum]][-1,29:-6,:]),lat[29:-6],lon,
                           -4,4,17,rdbu_cmap,'depth (m)','ALT difference for '+str(timeFrame)+' SSP - ARISE','LR_active_layer_map_CONTROL_minus_FEEDBACK_'+str(timeFrame))
    elif var == 'ER':
        fig,ax = make_maps(varCONTROL[ens[testNum]][-1,29:-6,:]/1000.,lat[29:-6],lon,
                            0,100,51,reds,'cumulative emissions (kgC/m2)','ER for control '+str(timeFrame),'LR_respiration_map_CONTROL_'+str(timeFrame))
        fig,ax = make_maps(varFEEDBACK[ens[testNum]][-1,29:-6,:]/1000.,lat[29:-6],lon,
                            0,100,51,reds,'cumulative emissions (kgC/m2)','ER for feedback '+str(timeFrame),'LR_respiration_map_FEEDBACK_'+str(timeFrame))
        fig,ax = make_maps((varCONTROL[ens[testNum]][-1,29:-6,:] - varFEEDBACK[ens[testNum]][-1,29:-6,:])/1000.,lat[29:-6],lon,
                           -10,10,21,rdbu_cmap,'rate (kgC/m2)','ER difference for '+str(timeFrame)+' SSP - ARISE','LR_respiration_map_CONTROL_minus_FEEDBACK_'+str(timeFrame))
    # fig,ax = make_maps((features_test[0,-10,:,:] - features_test[1,-10,:,:]),lat[29:-6],lon,
    #                    -5,5,21,rdbu_cmap,'depth (m)','ALT difference for '+str(timeFrame),'LR_active_layer_map_feature_train_diff_'+str(timeFrame))
    # fig,ax = make_maps((features_test[1,-5,:,:] - features_test[1,-10,:,:]),lat[29:-6],lon,
    #                    -5,5,21,rdbu_cmap,'depth (m)','ALT difference for '+str(timeFrame),'LR_active_layer_map_feedback_diff_'+str(timeFrame))
    # fig,ax = make_maps(features_test[0,-10,:,:],lat[29:-6],lon,
    #                    -5,5,21,rdbu_cmap,'depth (m)','feature_test for control '+str(timeFrame),'LR_active_layer_map_feature_test_control_'+str(timeFrame))
    # fig,ax = make_maps(features_test[1,-10,:,:],lat[29:-6],lon,
    #                    -5,5,21,rdbu_cmap,'depth (m)','feature_test for feedback '+str(timeFrame),'LR_active_layer_map_feature_test_feedback_'+str(timeFrame))
    
    del fig, ax
    # ## ----------------------------- ##
    
    return lat,lon,features_train,features_val,features_test,labels_train,labels_val,labels_test,lenTime
