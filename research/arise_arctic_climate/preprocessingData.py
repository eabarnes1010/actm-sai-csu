#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 15:59:11 2022

@author: Ariel L. Morrison
"""

def preprocessDataForPrediction(timeFrame,var,numYears):
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
    elif var == 'ER' or var == 'NEE' or var == 'GPP':
        lat,lon,control,ens,timeCONTROL = readData(datadir,str(var),True)
        lat,lon,arise,ens,timeARISE = readData(datadir,str(var),False)
    ## ---------------------------------------------------- ##
    
    ## ------ Processing data ------ ##
    ''' 
    lenTime = number of time units in 20 years
    numYears = number of years for training
    numUnits = total number of time units (e.g., total years in data record)
    '''
    # numYears = numYears
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
        else:
            timeStartControl = 0#int(np.abs(2035-control[ens[0]].year).argmin())
            timeEndFeedback  = 29#int(np.abs(2064-arise[ens[0]].year).argmin())
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
   
    ## ---------------------------------------------------- ##
    from random import sample
    new_list = sample(ens,len(ens))
    print('randomized order of members = ', new_list)
    
    # CONTROL
    featuresC = []
    for ensNum in range(len(new_list)):
        if timeFrame == 'winter' or timeFrame == 'non_growing_season':
            temp = np.stack(varCONTROL[new_list[ensNum]][timeStartControl:,30:-6,:].astype('float'))
        else:
            if var == 'ALT':
                temp = np.stack(varCONTROL[new_list[ensNum]][timeStartControl:,30:-6,:].values.astype('float'))
            else:
                temp = np.stack(varCONTROL[new_list[ensNum]][:,30:-6,:].astype('float'))
        featuresC.append(temp)
    del temp
    
    # FEEDBACK
    featuresF = []
    for ensNum in range(len(new_list)):
        if timeFrame == 'winter' or timeFrame == 'non_growing_season':
            temp = np.stack(varFEEDBACK[new_list[ensNum]][:timeEndFeedback+1,30:-6,:].astype('float'))
        else:
            if var == 'ALT':
                temp = np.stack(varFEEDBACK[new_list[ensNum]][:timeEndFeedback+1,30:-6,:].values.astype('float'))
            else:
                temp = np.stack(varFEEDBACK[new_list[ensNum]][:,30:-6,:].astype('float'))
        featuresF.append(temp)
    del temp
    ## ---------------------------------------------------- ##
    
    ## ------ Split training/test data ------ ##
    valNum      = 2
    testNum     = 1
    print('training members = ' + str(new_list[:-(valNum+testNum)]))
    print('validate members = ' + str(new_list[-(valNum+testNum):-testNum]))
    print('testing member = ' + str(new_list[-testNum:]))
    testMemNum      = np.asarray(new_list[-testNum:]); testMemNum = testMemNum.astype(float)
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
    
    ## ------ Categorical labels ------ ##
    import tensorflow as tf
    y_train = tf.keras.utils.to_categorical(labels_train)
    y_val   = tf.keras.utils.to_categorical(labels_val)
    y_test  = tf.keras.utils.to_categorical(labels_test)
    ## ---------------------------------------------------- ##    
    
    ## ------ Select training years ------ ##
    # Training years = 2035-2054
    X_train = features_train[:,:lenTime,:,:]
    X_val   = features_val[:,:lenTime,:,:]
    X_test  = features_test[:,:lenTime,:,:]
    # y_train = y_train[:,:lenTime,0]
    # y_val   = y_val[:,:lenTime,0]
    # y_test  = y_test[:,:lenTime,0]
    y_train = y_train[:,:lenTime]
    y_val   = y_val[:,:lenTime]
    y_test  = y_test[:,:lenTime]
    ## ---------------------------------------------------- ## 
    
    ## ------ Flatten data ------ ##
    lenLat = 49; lenLon = 288; 
    X_train = X_train.reshape(len(X_train)*lenTime,lenLat*lenLon)
    X_val   = X_val.reshape(len(X_val)*lenTime,lenLat*lenLon)
    X_test  = X_test.reshape(len(X_test)*lenTime,lenLat*lenLon)
    y_train = y_train.reshape((len(y_train)*lenTime,2))
    y_val   = y_val.reshape((len(y_val)*lenTime,2))
    y_test  = y_test.reshape((len(y_test)*lenTime,2))
    ## ---------------------------------------------------- ## 
    
    ## ------ Replace NaNs and inf ------ ##  
    from numpy import inf
    X_train[np.isnan(X_train)] = 0.
    X_train[X_train == inf] = 0.
    X_train[X_train == -inf] = 0.
    X_val[np.isnan(X_val)] = 0.
    X_val[X_val == inf] = 0.
    X_val[X_val == -inf] = 0.
    X_test[np.isnan(X_test)] = 0.
    X_test[X_test == inf] = 0.
    X_test[X_test == -inf] = 0.
    y_train[np.isnan(y_train)] = 0.
    y_val[np.isnan(y_val)] = 0.
    y_test[np.isnan(y_test)] = 0.
    ## ---------------------------------------------------- ## 
    
    ## ------ Predict if map comes from control simulation ------ ##
    y_train = y_train[:,1:]
    y_val   = y_val[:,1:]
    y_test  = y_test[:,1:]
    # y_train = y_train[:lenTime,1]
    # y_val   = y_val[:lenTime,1]
    # y_test  = y_test[:lenTime,1]
    ## ---------------------------------------------------- ## 
    
    ## ------ Map of last time step and difference between SSP & ARISE ------ ##
    from plottingFunctions import make_maps, get_colormap
    brbg_cmap,rdbu_cmap,jet,magma,reds = get_colormap(21)
    
    print("control: ", np.nanmin(varCONTROL[ens[testNum]][numYears-15,30:-6,:]), np.nanmax(varCONTROL[ens[testNum]][numYears,30:-6,:]))
    print("feedback: ",np.nanmin(varFEEDBACK[ens[testNum]][numYears-15,30:-6,:]), np.nanmax(varFEEDBACK[ens[testNum]][numYears,30:-6,:]))
    if var == 'ALT':
        diff = (varCONTROL[ens[testNum]][numYears-15,30:-6,:]) - (varFEEDBACK[ens[testNum]][numYears-15,30:-6,:])
        fig,ax = make_maps(varCONTROL[ens[testNum]][numYears-15,30:-6,:],lat[30:-6],lon,
                            0,20,21,magma,'depth (m)','ALT for control '+str(timeFrame),'LR_active_layer_map_CONTROL_'+str(timeFrame))
        fig,ax = make_maps(varFEEDBACK[ens[testNum]][numYears-15,30:-6,:],lat[30:-6],lon,
                            0,20,21,magma,'depth (m)','ALT for feedback '+str(timeFrame),'LR_active_layer_map_FEEDBACK_'+str(timeFrame))
        fig,ax = make_maps(diff,lat[30:-6],lon,-4,4,17,rdbu_cmap,'depth (m)',
                            '2040 ALT difference for '+str(timeFrame)+' SSP - ARISE','LR_active_layer_map_CONTROL_minus_FEEDBACK_'+str(timeFrame))
    elif var == 'ER':
        diff = (varCONTROL[ens[testNum]][numYears-15,30:-6,:]/1000.) - (varFEEDBACK[ens[testNum]][numYears-15,30:-6,:]/1000.)
        fig,ax = make_maps(varCONTROL[ens[testNum]][numYears-15,30:-6,:]/1000.,lat[30:-6],lon,
                            0,50,11,reds,'cumulative emissions (kgC/m2)','2055 ER for control '+str(timeFrame),'LR_respiration_map_CONTROL_'+str(timeFrame))
        fig,ax = make_maps(varFEEDBACK[ens[testNum]][numYears-15,30:-6,:]/1000.,lat[30:-6],lon,
                            0,50,11,reds,'cumulative emissions (kgC/m2)','2055 ER for feedback '+str(timeFrame),'LR_respiration_map_FEEDBACK_'+str(timeFrame))
        fig,ax = make_maps(diff,lat[30:-6],lon,-5,5,21,rdbu_cmap,'rate (kgC/m2)',
                            '2040 ER difference for '+str(timeFrame)+' SSP - ARISE','LR_respiration_map_CONTROL_minus_FEEDBACK_'+str(timeFrame))
    elif var == 'NEE':
        diff = (varCONTROL[ens[testNum]][numYears-15,30:-6,:]/1000.) - (varFEEDBACK[ens[testNum]][numYears-15,30:-6,:]/1000.)
        fig,ax = make_maps(varCONTROL[ens[testNum]][numYears-15,30:-6,:],lat[30:-6],lon,
                            0,500,21,reds,'cumulative net ecosystem exchange (gC/m2)','2055 NEE for control '+str(timeFrame),'LR_co2_exchange_map_CONTROL_'+str(timeFrame))
        fig,ax = make_maps(varFEEDBACK[ens[testNum]][numYears-15,30:-6,:],lat[30:-6],lon,
                            0,500,21,reds,'cumulative net ecosystem exchange (gC/m2)','2055 NEE for feedback '+str(timeFrame),'LR_co2_exchange_map_FEEDBACK_'+str(timeFrame))
        fig,ax = make_maps(diff,lat[30:-6],lon,-1,1,21,rdbu_cmap,'cumulative exchange (kgC/m2)',
                            '2040 NEE difference for '+str(timeFrame)+' SSP - ARISE','LR_co2_exchange_map_CONTROL_minus_FEEDBACK_'+str(timeFrame))
    elif var == 'GPP':
        diff = (varCONTROL[ens[testNum]][numYears-15,30:-6,:]/1000.) - (varFEEDBACK[ens[testNum]][numYears-15,30:-6,:]/1000.)
        fig,ax = make_maps(varCONTROL[ens[testNum]][numYears-15,30:-6,:]/1000.,lat[30:-6],lon,
                            0,2,21,reds,'cumulative primary productivity (kgC/m2)','2055 GPP for control '+str(timeFrame),'LR_GPP_map_CONTROL_'+str(timeFrame))
        fig,ax = make_maps(varFEEDBACK[ens[testNum]][numYears-15,30:-6,:]/1000.,lat[30:-6],lon,
                            0,2,21,reds,'cumulative primary productivity (kgC/m2)','2055 GPP for feedback '+str(timeFrame),'LR_GPP_map_FEEDBACK_'+str(timeFrame))
        fig,ax = make_maps(diff,lat[30:-6],lon,-1,1,21,rdbu_cmap,'cumulative primary productivity (kgC/m2)',
                            '2040 GPP difference for '+str(timeFrame)+' SSP - ARISE','LR_GPP_map_CONTROL_minus_FEEDBACK_'+str(timeFrame))
    
    del fig, ax
    ## ----------------------------- ##
    
    return lat,lon,features_train,features_val,features_test,\
        labels_train,labels_val,labels_test,X_train,y_train,X_val,\
            y_val,X_test,y_test,lenTime,testMemNum
