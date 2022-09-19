#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 12:42:01 2022

@author: Ariel L. Morrison

----------------------------------
Function: train logistic regression neural net
    to predict which simulation a map of active
    layer depth is from (control or ARISE)
"""
import numpy as np
from numpy import inf
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras import regularizers
from tensorflow.keras import metrics
from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential
from preprocessingData import preprocessDataForPrediction
import matplotlib.pyplot as plt
import gc

## ------ random numbers ------ ##
np.random.seed(99)
tf.random.set_seed(99)

## ------ Choose parameters ------ ##
timeFrame   = 'annual'
var = 'NEE'
batch_size  = 28
verbose     = 2
singleLayer = True
denseShape  = 28
dropout     = 0.25
l1, l2      = 0.015,0.8
if var == 'ALT':
    epochs  = 6
    lr      = 0.006
else:
    epochs  = 3
    lr      = 0.006

## ------ Get processed training and test data ------ ##
lat,lon,features_train,features_val,features_test,\
    labels_train,labels_val,labels_test,lenTime = preprocessDataForPrediction(str(timeFrame),str(var))
## ---------------------------------------------------- ## 

## ------ Categorical labels ------ ##
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
lenLat = 50; lenLon = 288; 
X_train = X_train.reshape(len(X_train)*lenTime,lenLat*lenLon)
X_val   = X_val.reshape(len(X_val)*lenTime,lenLat*lenLon)
X_test  = X_test.reshape(len(X_test)*lenTime,lenLat*lenLon)
y_train = y_train.reshape((len(y_train)*lenTime,2))
y_val   = y_val.reshape((len(y_val)*lenTime,2))
y_test  = y_test.reshape((len(y_test)*lenTime,2))
## ---------------------------------------------------- ## 

## ------ Replace NaNs and inf ------ ##  
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

## ------ Create and train the model ------ ##
tf.keras.backend.clear_session()
rseed = 4444
tf.keras.utils.set_random_seed(rseed)
model = Sequential()

if singleLayer:
    model.add(Dense(y_train.shape[1], input_shape=(X_train.shape[1],),
                        activation         = 'sigmoid',
                        use_bias           = True,
                        kernel_regularizer = regularizers.l1_l2(l1=l1, l2=l2),
                        bias_initializer   = tf.keras.initializers.LecunNormal(seed=rseed),
                        kernel_initializer = tf.keras.initializers.LecunNormal(seed=rseed)))
    
else:
    model.add(Dense(denseShape, input_shape=(X_train.shape[1],),
                    activation         = 'relu',
                    use_bias           = True,
                    kernel_regularizer = regularizers.l1_l2(l1=l1, l2=l2),
                    bias_initializer   = tf.keras.initializers.LecunNormal(seed=rseed),
                    kernel_initializer = tf.keras.initializers.LecunNormal(seed=rseed)))
    model.add(Dropout(dropout))
    model.add(Dense(y_train.shape[1],
                    activation         = 'softmax',
                    use_bias           = True,
                    kernel_regularizer = regularizers.l1_l2(l1=l1, l2=l2),
                    bias_initializer   = tf.keras.initializers.LecunNormal(seed=rseed),
                    kernel_initializer = tf.keras.initializers.LecunNormal(seed=rseed)))

''' Schedule a decreasing learning rate '''
# if var == 'ALT':
def scheduler(epoch, lr):
    if epoch < 1 or epoch > 15:
        return lr
    else:
        return lr/2.
# else:
#     def scheduler(epoch, lr):
#         if epoch < 1:
#             return lr
#         else:
#             return lr/4.
    
## ------ Compile the model ------ ##   
model.compile(optimizer = optimizers.SGD(learning_rate=lr, 
                                          momentum=0.8, 
                                          nesterov=True),
              loss      = tf.keras.losses.BinaryCrossentropy(from_logits=False),
              metrics   = [metrics.binary_accuracy,])

lr_scheduler = tf.keras.callbacks.LearningRateScheduler(scheduler) 
stopEarly = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)   
print(model.summary())

print('starting training...')
history = model.fit(X_train, 
                    y_train, 
                    batch_size      = batch_size, 
                    epochs          = epochs, 
                    shuffle         = True, 
                    verbose         = verbose, 
                    callbacks       = [lr_scheduler,stopEarly,],
                    validation_data = (X_val,y_val))
## ---------------------------------------------------- ## 

## ------ Predictions! ------ ##
y_pred_train = model.predict(X_train)
y_pred_val   = model.predict(X_val)
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
# print("CONTROL: ",np.round(y_pred_CONTROL*100.,decimals=1))
# print("FEEDBACK: ",np.round(y_pred_FEEDBACK*100.,decimals=1))
# y_pred_FEEDBACK = y_pred_test[lenTime:]
fig, ax = plt.subplots()
ax.plot(range(lenTime),1-y_pred_CONTROL,color='r',label='SSP2-4.5')
ax.plot(range(lenTime),y_pred_FEEDBACK,color='b',label='ARISE')
fig.suptitle('prediction confidence (' +str(timeFrame)+')', fontsize=11)
if timeFrame == 'winter' or timeFrame == 'non_growing_season':
    plt.xlim([0,lenTime-1])
    ax.set_xticks([0,2,4,6,8,10,12,14,16,18])
    ax.set_xticklabels(['2035','2037','2039','2041','2043','2045','2047','2049','2051','2053'])
elif timeFrame == 'monthly':
    plt.xlim([0,lenTime])
else:
    plt.xlim([0,lenTime])
    ax.set_xticks([0,2,4,6,8,10,12,14,16,18])
    ax.set_xticklabels(['2035','2037','2039','2041','2043','2045','2047','2049','2051','2053'])
plt.axhline(0.5,0,lenTime,linestyle='-.',color='k',linewidth=0.7)
plt.xlabel('time')
plt.legend(loc='lower right')
plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/prediction_confidence_'\
            +str(timeFrame)+'_'+str(var)+'.jpg')
plt.show()
## ----------------------------------- ##

## ------ Accuracy metrics ------ ##
print("binary accuracy: ", np.round(history.history['binary_accuracy'],decimals=3))

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
fig.suptitle("Prediction accuracy for annual mean", fontsize=13, fontweight='bold')
# fig.suptitle("Prediction accuracy for " + str(timeFrame), fontsize=13, fontweight='bold')
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
            +str(timeFrame)+'_'+str(var)+'.jpg', bbox_inches='tight'); plt.show()
## ------------------------------ ##

## ------ Summarize history for loss ------ ##
plt.figure(figsize=(7,5))
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss ' + '(' + str(timeFrame) + ')', fontsize=11)
plt.ylabel('loss'); plt.xlabel('epoch')
ymax = np.nanmax([np.nanmax(history.history['val_loss']), np.nanmax(history.history['loss'])])
plt.legend(['train', 'val'], loc='upper right')
plt.savefig('/Users/arielmor/Desktop/SAI/data/ARISE/figures/train_val_loss_'\
            +str(timeFrame)+'_'+str(var)+'.jpg'); plt.show()
## ---------------------------------------- ## 
'''
First number is likelihood of map coming from first column of testing data,
second number is likelihood of second column 

First 20 numbers = control, second 20 = arise
'''
## ------ Map of weights ------ ##
if singleLayer:
    from plottingFunctions import get_colormap, make_maps
    brbg_cmap,rdbu_cmap,jet,magma,reds = get_colormap(21)
    mapWeights = (model.layers[0].get_weights()[0].reshape(lenLat,lenLon))
    fig,ax = make_maps(mapWeights,lat[29:-6],lon,
                        -0.03,0.03,21,brbg_cmap,
                        'weights','weights for '+str(timeFrame),
                        'weights_'+str(timeFrame)+'_'+str(var))
    # mapWeights = model.layers[0].get_weights()[0][:,1].reshape(lenLat,lenLon)
    # fig,ax = make_maps(mapWeights,lat[29:-6],lon,
    #                     -0.02,0.02,21,brbg_cmap,'weights','weights for '+str(timeFrame)+', control','feedback_weights_'+str(timeFrame))
## ----------------------------- ##

gc.collect()

