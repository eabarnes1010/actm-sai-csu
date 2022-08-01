#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 15:59:11 2022

@author: Ariel L. Morrison
"""

def preprocessDataForPrediction(timeFrame):
    import os; os.chdir('/Users/arielmor/Desktop/SAI/scripts/')
    from readData import readData
    import numpy as np
    import warnings
    
    datadir = '/Users/arielmor/Desktop/SAI/data/ARISE/data'
    
    ## ------ Read control & feedback active layer depth ------ ##
    lat,lon,ALTcontrol,ALTcontrolGS,ALTcontrolANN,ALTcontrolOCT,ens,timeCONTROL = readData(datadir,'ALT',True)
    lat,lon,ALTarise,ALTariseGS,ALTariseANN,ALTariseOCT,ens,timeARISE = readData(datadir,'ALT',False)
    ## ---------------------------------------------------- ##
    
    ## ------ Processing data ------ ##
    ''' 
    lenTime = number of time units in 15 years
    numUnits = total number of time units (e.g., total years in data record)
    '''
    if timeFrame == 'annual':
        timeStartControl = int(np.abs(2035-ALTcontrolANN[ens[0]].year).argmin())
        timeEndFeedback = int(np.abs(2064-ALTariseANN[ens[0]].year).argmin())
        varCONTROL = ALTcontrolANN
        varFEEDBACK = ALTariseANN
        lenTime = 1*20
        numUnits = 30 # number of total years
    elif timeFrame == 'october':
        timeStartControl = int(np.abs(2035-ALTcontrolANN[ens[0]].year).argmin())
        timeEndFeedback = int(np.abs(2064-ALTariseANN[ens[0]].year).argmin())
        varCONTROL = ALTcontrolOCT
        varFEEDBACK = ALTariseOCT
        lenTime = 1*20
        numUnits = 30 # number of total months
    elif timeFrame == 'growing_season':
        timeStartControl = 140 # np.where(ALTcontrolGS[ens[0]].time == np.datetime64(datetime.datetime(2035, 4, 1)))
        timeEndFeedback = 209 # np.where(ALTariseGS[ens[0]].time == np.datetime64(datetime.datetime(2064, 10, 1)))
        varCONTROL = ALTcontrolGS
        varFEEDBACK = ALTariseGS
        lenTime = 7*20
        numUnits = 210 # number of total months
    elif timeFrame == 'monthly':
        timeStartControl = 240 # np.where(ALTcontrol[ens[0]].time == np.datetime64(datetime.datetime(2035, 1, 1)))
        timeEndFeedback = 359 # np.where(ALTarise[ens[0]].time == np.datetime64(datetime.datetime(2064, 12, 1)))
        varCONTROL = ALTcontrol
        varFEEDBACK = ALTarise
        lenTime = 12*20
        numUnits = 360 # number of total months
        
    # CONTROL
    featuresC = []
    for ensNum in range(len(ens)):
        temp = np.stack(varCONTROL[ens[ensNum]][timeStartControl:,30:-6,:].values.astype('float'))
        featuresC.append(temp)
    del temp
    
    # FEEDBACK
    featuresF = []
    for ensNum in range(len(ens)):
        temp = np.stack(varFEEDBACK[ens[ensNum]][:timeEndFeedback+1,30:-6,:].values.astype('float'))
        featuresF.append(temp)
    del temp
    ## ---------------------------------------------------- ##
    
    ## ------ Split training/test data ------ ##
    from random import sample
    number_list = [1,2,3,4,6,7,8,9,10]
    new_list = sample(number_list,len(number_list))
    valNum = 3
    testNum = 2
    print('training members = ' + str(new_list[:-(valNum+testNum)]))
    print('validate members = ' + str(new_list[-(valNum+testNum):-testNum]))
    print('testing members = ' + str(new_list[-testNum:]))
    featuresF_train = featuresF[:-(valNum+testNum)]
    featuresC_train = featuresC[:-(valNum+testNum)]
    featuresF_val = featuresF[-(valNum+testNum):-testNum]
    featuresC_val = featuresC[-(valNum+testNum):-testNum]
    featuresF_test = featuresF[-testNum:]
    featuresC_test = featuresC[-testNum:]
    ## ---------------------------------------------------- ##
    
    ## ------ Create labels for each simulation ------ ##
    ''' 
        number of ensemble members, number of time steps
        CONTROL = 0; FEEDBACK = 1
    '''
    labelsC_train = np.ones((len(featuresC_train),numUnits))*0
    labelsF_train = np.ones((len(featuresF_train),numUnits))*1
    labelsC_val = np.ones((len(featuresC_val),numUnits))*0
    labelsF_val = np.ones((len(featuresF_val),numUnits))*1
    labelsC_test = np.ones((len(featuresC_test),numUnits))*0
    labelsF_test = np.ones((len(featuresF_test),numUnits))*1
    ## ---------------------------------------------------- ##
    
    ## ------ Concatenate control/feedback data for neural net training ------ ##
    '''
        also important for standardizing data
    '''
    features_train = np.append(featuresC_train,featuresF_train,axis=0)
    features_val = np.append(featuresC_val,featuresF_val,axis=0)
    features_test = np.append(featuresC_test,featuresF_test,axis=0)
    labels_train = np.append(labelsC_train,labelsF_train,axis=0)
    labels_val = np.append(labelsC_val,labelsF_val,axis=0)
    labels_test = np.append(labelsC_test,labelsF_test,axis=0)
    ## ----------------------------------------------------------------------- ##
    
    ## ------ Standardize data ------ ##
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        featuresMean = np.nanmean(features_train,axis=(0,1))
        featuresStd = np.nanstd(features_train,axis=(0,1))
        # featuresMean = np.nanmean(np.hstack((features_train.flatten(),features_val.flatten(),features_test.flatten())).flatten())
        # featuresStd = np.nanstd(np.hstack((features_train.flatten(),features_val.flatten(),features_test.flatten())).flatten())
        
        features_train = (features_train-featuresMean)/featuresStd
        features_val = (features_val-featuresMean)/featuresStd
        features_test = (features_test-featuresMean)/featuresStd        
    ## ------------------------------ ##
    
    ## ------ Replace NaNs with 0 ------ ##
    features_train[np.isnan(features_train)] = 0.
    features_val[np.isnan(features_val)] = 0.
    features_test[np.isnan(features_test)] = 0.
    ## --------------------------------- ##
    
    return features_train,features_val,features_test,labels_train,labels_val,labels_test,lenTime
