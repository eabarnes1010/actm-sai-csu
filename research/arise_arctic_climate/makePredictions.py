#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 14:14:44 2022

@author: arielmor
"""

def makePredictions(timeFrame,var):
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import tensorflow as tf
    from tensorflow import keras
    from preprocessingData import preprocessDataForPrediction
    datadir = '/Users/arielmor/Desktop/SAI/data/ARISE/data/model_output'
        
    model = tf.keras.models.load_model('saved_model/logistic_regression_predict_soil_respiration')
    
    lat,lon,features_train,features_val,features_test,\
        labels_train,labels_val,labels_test,X_train,y_train,\
            X_val,y_val,X_test,y_test,lenTime,testMemNum = preprocessDataForPrediction(str(
                                                    timeFrame),str(var),20)
    
    ## ------ Predictions! ------ ##
    y_pred_test  = model.predict(X_test)
    ## -------------------------- ## 
    
    ## ------ Prediction confidence ------ ##
    '''
        y_pred_test shape is two columns
        1st column = probability that map comes from CONTROL
        2nd column = probability that map comes from FEEDBACK
        Length of array = 2 x lenTime
        20 years of training data = 40 predictions --> 1st 20 = control, 2nd 20 = feedback
    '''
    y_pred_CONTROL= np.round(y_pred_test[:lenTime],decimals=3)
    y_pred_FEEDBACK = np.round(y_pred_test[lenTime:],decimals=3)
    np.save(datadir + '/y_pred_CONTROL_' + str(testMemNum) + '.npy', y_pred_CONTROL)
    np.save(datadir + '/y_pred_FEEDBACK_' + str(testMemNum) + '.npy', y_pred_FEEDBACK)
    
    ens = ['[1.]','[3.]','[4.]','[7.]','[8.]','[9.]','[10.]']
    fig, ax = plt.subplots(figsize=(8,4),dpi=800)
    for ensNum in range(len(ens)):
        y_pred_CONTROL = np.load(datadir + '/y_pred_CONTROL_' + str(ens[ensNum]) + '.npy')
        y_pred_FEEDBACK = np.load(datadir + '/y_pred_FEEDBACK_' + str(ens[ensNum]) + '.npy')
        
        ## - add markers to signify if prediction is right or wrong - ##
        df = pd.DataFrame.from_dict(dict(controlprediction=(1-y_pred_CONTROL[:,0]),
                                         feedbackprediction=y_pred_FEEDBACK[:,0]))
        df.index.name="index"
        df.reset_index(inplace=True)
        df["criteria"] = df.controlprediction > 0.5
        df["criteria2"] = df.feedbackprediction > 0.5
    
        ## - make figure - ##
        ax = df.controlprediction.plot(c='r',linewidth=1)
        df.feedbackprediction.plot(c='xkcd:cobalt blue',ax=ax,linewidth=1)
        df[df.criteria].plot(kind='scatter',x='index',y='controlprediction',
                                     ax=ax,c='r',marker='o')
        df[~df.criteria].plot(kind='scatter',x='index',y='controlprediction',
                                      ax=ax,c='r',marker='x')
        df[df.criteria2].plot(kind='scatter',x='index',y='feedbackprediction',
                                      ax=ax,c='xkcd:cobalt blue',marker='o')
        df[~df.criteria2].plot(kind='scatter',x='index',y='feedbackprediction',
                                       ax=ax,c='xkcd:cobalt blue',marker='x')
    ax.legend(['SSP2-4.5','ARISE'],loc='lower right')
    if timeFrame == 'winter' or timeFrame == 'non_growing_season':
        plt.xlim([-1,lenTime])
        ax.set_xticks([0,2,4,6,8,10,12,14,16,18])
        ax.set_xticklabels(['2035','2037','2039','2041','2043','2045','2047','2049','2051','2053'])
    elif timeFrame == 'monthly':
        plt.xlim([0,lenTime])
    else:
        plt.xlim([0,lenTime-1])
        ax.set_xticks([0,2,4,6,8,10,12,14,16,18])
        ax.set_xticklabels(['2035','2037','2039','2041','2043',
                            '2045','2047','2049','2051','2053',
                            ])
    plt.axhline(0.5,0,lenTime,linestyle='dashed',color='k',linewidth=0.6)
    # plt.legend(loc='lower right')
    ax.set_yticks([])
    ax.set(xlabel=None)
    plt.ylabel('Prediction confidence\n incorrect                        correct',
               fontweight='bold')
    plt.ylim(bottom=0)
    ax.fill_between(range(lenTime),0,0.5,alpha=0.18,color='k')
    plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/prediction_confidence_'\
                +str(timeFrame)+'_'+str(var)+'.jpg',bbox_inches='tight',dpi=800)
    plt.show()
    ## ----------------------------------- ##
    
    ## ------ Accuracy metrics ------ ##    
    ''' Accuracy of each prediction vs label '''
    acc_CONTROL = np.asarray(np.asarray(np.equal(np.round(np.squeeze(y_pred_CONTROL)),
                                                 labels_test[0,:lenTime]),dtype='int32'),dtype='float')
    acc_FEEDBACK = np.asarray(np.asarray(np.equal(np.round(np.squeeze(y_pred_FEEDBACK)),
                                                  labels_test[1,:lenTime]),dtype='int32'),dtype='float')
    # acc_CONTROL[acc_CONTROL == 0] = 2; acc_CONTROL[acc_CONTROL == 1] = 0; acc_CONTROL[acc_CONTROL == 2] = 1
    
    print("-------------------------------------------")
    print("Correct predictions (label = 1; above 50% confidence)")
    print("CONTROL", acc_CONTROL)
    print("FEEDBACK", acc_FEEDBACK)
    print("-------------------------------------------")
    
    fig, (ax1, ax2) = plt.subplots(2, figsize=(8,4), dpi=900)
    ax2.scatter(range(lenTime),acc_FEEDBACK,color='b',label='ARISE-SAI')
    ax2.legend(loc="lower right", fancybox=True, fontsize=11)
    ax1.scatter(range(lenTime),acc_CONTROL,color='r',label='SSP2-4.5')
    ax1.legend(loc="lower right", fancybox=True, fontsize=11)
    if timeFrame == 'winter' or timeFrame == 'non_growing_season':
        ax1.set_xticks([0,2,4,6,8,10,12,14,16,18])
        ax1.set_xticklabels([])
        ax2.set_xticks([0,2,4,6,8,10,12,14,16,18])
        ax2.set_xticklabels(['2035','2037','2039','2041','2043','2045','2047','2049','2051','2053'])
    else:
        ax1.set_xticks([0,2,4,6,8,10,12,14,16,18])
        ax1.set_xticklabels([])
        ax2.set_xticks([0,2,4,6,8,10,12,14,16,18])
        ax2.set_xticklabels(['2035','2037','2039','2041','2043','2045','2047','2049','2051','2053'])
    ax2.set_yticks([0,1]) 
    ax2.set_yticklabels(['False','True'], fontweight='bold')
    ax1.set_yticks([0,1]) 
    ax1.set_yticklabels(['False','True'], fontweight='bold')
    plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/prediction_accuracy_'\
                +str(timeFrame)+'_'+str(var)+'.jpg', bbox_inches='tight',dpi=900); plt.show()
    ## ------------------------------ ##
   
    '''
    First number is likelihood of map coming from first column of testing data,
    second number is likelihood of second column 
    
    First 20 numbers = control, second 20 = arise
    '''
    ## ------ Map of weights ------ ##
    from plottingFunctions import get_colormap, make_maps
    lenLat = 49; lenLon = 288; 
    brbg_cmap,rdbu_cmap,jet,magma,reds = get_colormap(21)
    
    mapWeights = (model.layers[0].get_weights()[0].reshape(lenLat,lenLon))
    
    if var == 'ER':
        vmins = -0.016; vmaxs = 0.016
    else:
        vmins = -0.04; vmaxs = 0.04
    fig,ax = make_maps(mapWeights,lat[30:-6],lon,
                        vmins,vmaxs,21,rdbu_cmap,
                        'weights','weights for '+str(timeFrame),
                        'weights_'+str(timeFrame)+'_'+str(var))
    # mapWeights = model.layers[0].get_weights()[0][:,1].reshape(lenLat,lenLon)
    # fig,ax = make_maps(mapWeights,lat[29:-6],lon,
    #                     -0.02,0.02,21,brbg_cmap,'weights','weights for '+str(timeFrame)+', control','feedback_weights_'+str(timeFrame))
    ## ----------------------------- ##
    return