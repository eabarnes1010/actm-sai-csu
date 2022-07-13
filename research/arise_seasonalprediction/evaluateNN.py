#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 15:42:59 2022

@author: kmayer
"""
#%% IMPORT FUNCTIONS
import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt
import random
import time
import matplotlib.pyplot as plt
import tensorflow as tf

import sys
sys.path.append('functions/')
from ANN import defineNN, plot_results
from split_data import train_future, balance_classes, test_future
from hyperparams import get_params
#%% DEFINE MACHINE LEARNING FUNCTIONS & PARAMETERS
# ---------------- SET PARAMETERS ----------------
NLABEL     = 2                 
PATIENCE   = 20           
GLOBAL_SEED = 2147483648
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)
tf.random.set_seed(GLOBAL_SEED)


#%% DEFINE VARIABLE PARAMETERS
DIR = 'data/'
LEAD = 2 # 2 = 1 month inbetween (e.g. January --> March)

MEMstr = '1-10'
TRAINmem = [[1,2,3,4,5,6,7,8],
            [2,3,4,5,6,7,8,9],
            [3,4,5,6,7,8,9,10],
            [1,4,5,6,7,8,9,10],
            [1,2,5,6,7,8,9,10],
            [1,2,3,6,7,8,9,10],
            [1,2,3,4,7,8,9,10],
            [1,2,3,4,5,8,9,10],
            [1,2,3,4,5,6,9,10],
            [1,2,3,4,5,6,7,10]]
  
VALmem  = [9,10,1,2,3,4,5,6,7,8]          
TESTmem = [10,1,2,3,4,5,6,7,8,9]


#%%  CALCULATE & SAVE ACCURACY VS CONFIDENCE

for RUN in ['SAI','control']:

    for region in ['swcoast','nwcoast','alaska']:
        if region == 'swcoast':
            lower_ilat = 122    
            upper_ilat = 139    
            left_ilon  = 188    
            right_ilon = 201 
        elif region == 'nwcoast':
            lower_ilat = 138    
            upper_ilat = 155    
            left_ilon  = 188    
            right_ilon = 201
        elif region == 'alaska':
            lower_ilat = 154    
            upper_ilat = 172    
            left_ilon  = 152    
            right_ilon = 201

        for m, mems in enumerate(TRAINmem): 
            # ---------------- GET TESTING DATA ----------------
            print('RUN: '+RUN+'\nREGION: '+region)
            
            _, _, Xtrain_mean, Xtrain_std, Ytrain_median = train_future(DIR = DIR,
                                                                        RUN = RUN,
                                                                        LEAD = LEAD,
                                                                        TRAINmem = mems,
                                                                        MEMstr = MEMstr,
                                                                        lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                                                                        left_ilon = left_ilon, right_ilon = right_ilon)
            
            print('... LOAD TESTING DATA '+str(TESTmem[m])+' ...')
            Xtest, Ytest = test_future(DIR = DIR,
                                         RUN = RUN,
                                         LEAD = LEAD,
                                         TESTmem = TESTmem[m],
                                         MEMstr = MEMstr,
                                         Xtrain_mean = Xtrain_mean,
                                         Xtrain_std = Xtrain_std,
                                         Ytrain_median = Ytrain_median,
                                         lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                                         left_ilon = left_ilon, right_ilon = right_ilon)
            
            
            X_test = np.asarray(Xtest,dtype='float')
            X_test[np.isnan(X_test)] = 0.
            Y_test = np.asarray(Ytest)
            
            i_new = balance_classes(data = Y_test)     
            Y_test = Y_test[i_new]
            X_test = X_test[i_new]
            
            # -------- GET PARAMETERS --------
            params = get_params(RUN+'_'+region)
            N_EPOCHS   = params['N_epochs']
            HIDDENS    = params['hidden_layers']
            LR_INIT    = params['LR']
            RIDGE      = params['L2']
            BATCH_SIZE = params['N_batch']
            
            #% ------------------------ EVALUATE NN ------------------------
            acc = np.zeros(shape=(10,20)) + np.nan
            for NETWORK_SEED in np.arange(0,10):  
                print(NETWORK_SEED)
                # ----- Define NN Architecture -----
                tf.keras.backend.clear_session() 
                model = defineNN(HIDDENS,
                                 input_shape = X_test.shape[1],
                                 output_shape=NLABEL,
                                 ridge_penalty=RIDGE,
                                 act_fun='relu',
                                 network_seed=NETWORK_SEED)
                # ----- Compile NN -----
                METRICS = [tf.keras.metrics.SparseCategoricalAccuracy(name="sparse_categorical_accuracy", dtype=None)]
                LOSS_FUNCTION = tf.keras.losses.SparseCategoricalCrossentropy()
                OPTIMIZER = tf.keras.optimizers.Adam(learning_rate=LR_INIT)
                
                model.compile(optimizer = OPTIMIZER, loss = LOSS_FUNCTION, metrics = METRICS)   
                
                # ----- LOAD MODEL -----               
                model.load_weights('saved_models/model.h5')
               
                # ----- EVALUATE MODEL -----  
                conf_pred = model.predict(X_test)           # softmax output
                
                cat_pred  = np.argmax(conf_pred, axis = -1) # categorical output
                max_conf  = np.max(conf_pred, axis = -1)    # predicted category confidence
                

                for p,per in enumerate(np.arange(0,100,5)):
                    i_cover = np.where(max_conf >= np.percentile(max_conf,per))[0]
                    icorr   = np.where(cat_pred[i_cover] == Y_test[i_cover])[0]
                     
                    if len(i_cover) == 0:
                        acc[NETWORK_SEED,p] = 0.
                    else:
                        acc[NETWORK_SEED,p] = (len(icorr)/len(i_cover)) * 100
                
                
                plt.plot(acc[NETWORK_SEED],'grey',alpha=0.7)
                plt.ylim(50,100)
                plt.xlim(0,19)
                plt.title(RUN+' '+region)
            plt.show()
            
            # ----- SAVE ACC VS CONF -----
            np.save(DIR_SAVE+FI_SAVE, acc, allow_pickle=True)

