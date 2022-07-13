#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 09:31:39 2022

@author: kmayer
"""
import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt
import random
import time
import tensorflow as tf

import sys
sys.path.append('functions/')
from ANN import defineNN, plot_results
from split_data import train_future, balance_classes, val_future
from hyperparams import get_params

#%% DEFINING MACHINE LEARNING FUNCTIONS & PARAMETERS
# ---------------- LEARNING RATE CALLBACK FUNCTION ----------------
def scheduler(epoch, lr):
    # This function keeps the initial learning rate for the first ten epochs
    # and decreases it exponentially after that.
    if epoch < 10:
        return lr
    else:
        return lr * tf.constant(.9,dtype=tf.float32)

# ---------------- SET PARAMETERS ----------------
NLABEL     = 2                 
PATIENCE   = 20         
GLOBAL_SEED = 2147483648
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)
tf.random.set_seed(GLOBAL_SEED)

#%% VARIABLE PARAMETERS
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


#%% 
for RUN in ['SAI','control']:

    for region in ['swcoast','nwcoast','alaska']:
        if region == 'swcoast':
            lower_ilat = 122    # 122 = 25N
            upper_ilat = 139    # 139 = 40N
            left_ilon  = 188    # 188 = 235E
            right_ilon = 201    # 201 = 250E
        elif region == 'nwcoast':
            lower_ilat = 138    # 138 = 40N
            upper_ilat = 155    # 155 = 55N
            left_ilon  = 188    # 188 = 235E
            right_ilon = 201    # 201 = 250E
        elif region == 'alaska':
            lower_ilat = 154    # 154 = 55N
            upper_ilat = 172    # 172 = 70N
            left_ilon  = 152    # 152 = 190E
            right_ilon = 201    # 201 = 250E
            
        for m, mems in enumerate(TRAINmem[:1]):
            # ---------------- GET TRAINING & VALIDATION DATA ----------------
            print('RUN: '+RUN+'\nREGION: '+region)
            print('... LOAD TRAINING DATA ...')
            Xtrain, Ytrain, Xtrain_mean, Xtrain_std, Ytrain_median = train_future(DIR = DIR,
                                                                                    RUN = RUN,
                                                                                    LEAD = LEAD,
                                                                                    TRAINmem = mems,
                                                                                    MEMstr = MEMstr,
                                                                                    lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                                                                                    left_ilon = left_ilon, right_ilon = right_ilon)

            
            print('... LOAD VALIDATION MEMBER '+str(VALmem[m])+' ...')
            Xval, Yval = val_future(DIR = DIR,
                                      RUN = RUN,
                                      LEAD = LEAD,
                                      VALmem = VALmem[m],
                                      MEMstr = MEMstr,
                                      Xtrain_mean = Xtrain_mean,
                                      Xtrain_std = Xtrain_std,
                                      Ytrain_median = Ytrain_median,
                                      lower_ilat = lower_ilat, upper_ilat = upper_ilat,
                                      left_ilon = left_ilon, right_ilon = right_ilon)
            
            
            X_train = np.asarray(Xtrain,dtype='float')
            X_train[np.isnan(X_train)] = 0.
            Y_train = np.asarray(Ytrain)
            
            X_val = np.asarray(Xval,dtype='float')
            X_val[np.isnan(X_val)] = 0.
            Y_val = np.asarray(Yval)
                
            i_new = balance_classes(data = Y_val)     
            Y_val = Y_val[i_new]
            X_val = X_val[i_new]
            
            # -------- GET PARAMETERS --------
            params = get_params(RUN+'_'+region)
            N_EPOCHS   = params['N_epochs']
            HIDDENS    = params['hidden_layers']
            LR_INIT    = params['LR']
            RIDGE      = params['L2']
            BATCH_SIZE = params['N_batch']
            
            #% ------------------------ TRAIN NN ------------------------
            for NETWORK_SEED in np.arange(0,10):  
                # ----- Define NN Architecture -----
                tf.keras.backend.clear_session() 
                model = defineNN(HIDDENS,
                                 input_shape = X_train.shape[1],
                                 output_shape = NLABEL,
                                 ridge_penalty = RIDGE,
                                 act_fun = 'relu',
                                 network_seed = NETWORK_SEED)
                # ----- Compile NN -----
                METRICS = [tf.keras.metrics.SparseCategoricalAccuracy(name="sparse_categorical_accuracy", dtype=None)]
                LOSS_FUNCTION = tf.keras.losses.SparseCategoricalCrossentropy()
                OPTIMIZER = tf.keras.optimizers.Adam(learning_rate=LR_INIT)

                model.compile(optimizer = OPTIMIZER, loss = LOSS_FUNCTION, metrics = METRICS)   
                
                # ----- Callbacks -----
                es_callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                                patience=PATIENCE,
                                                                mode='auto',
                                                                restore_best_weights=True,
                                                                verbose=0)  
                lr_callback = tf.keras.callbacks.LearningRateScheduler(scheduler,verbose=0)
                callbacks = [es_callback,lr_callback]
                
                # ----- TRAINING NETWORK -----
                start_time = time.time()
                history = model.fit(X_train, Y_train,
                                    validation_data=(X_val, Y_val),
                                    batch_size=BATCH_SIZE,
                                    epochs=N_EPOCHS,
                                    shuffle=True,
                                    verbose=0,
                                    callbacks=callbacks,
                                   )
                stop_time = time.time()
                tf.print(f"Elapsed time during fit = {stop_time - start_time:.2f} seconds\n")
                
                if NETWORK_SEED <= 10:
                    #----- PLOT THE RESULTS -----
                    plot_results(
                        history,
                        exp_info=(N_EPOCHS, HIDDENS, LR_INIT, BATCH_SIZE, NETWORK_SEED, PATIENCE, RIDGE),
                        showplot=True
                    )   
                    
                    # ----- PRINT THE RESULTS -----
                predictions = np.argmax(model.predict(X_val),axis=-1)
                confusion = tf.math.confusion_matrix(labels=Y_val, predictions=predictions)

                # PRECISION = correct predictions of a class / total predictions for that class
                zero_precision  = (np.sum(confusion[0,0])/np.sum(confusion[:,0])) * 100
                one_precision   = (np.sum(confusion[1,1])/np.sum(confusion[:,1])) * 100
                    
                # Number of times network predicts a given class
                zero_predictions  = (np.shape(np.where(predictions==0))[1]/predictions.shape[0])* 100
                one_predictions   = (np.shape(np.where(predictions==1))[1]/predictions.shape[0])* 100
                
                print('Zero prediction accuracy: '+str(zero_precision)[:2]+'%')
                print('Zero: '+str(zero_predictions)[:3]+'% of predictions')
                print('One prediction accuracy: '+str(one_precision)[:2]+'%')
                print('One: '+str(one_predictions)[:3]+'% of predictions')
                
                #----- SAVE MODEL -----
                model.save_weights('saved_models/model.h5')
        
                
                
