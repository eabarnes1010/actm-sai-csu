#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 12:42:01 2022

@author: arielmor

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

## ------ Choose time frame ------ ##
timeFrame = 'october'

## ------ Get processed training and test data ------ ##
features_train,features_val,features_test,labels_train,labels_val,labels_test,lenTime = preprocessDataForPrediction(str(timeFrame))
print("Number of time steps: ", lenTime)
## ---------------------------------------------------- ## 

## ------ Categorical labels ------ ##
y_train = tf.keras.utils.to_categorical(labels_train)
y_val = tf.keras.utils.to_categorical(labels_val)
y_test = tf.keras.utils.to_categorical(labels_test)
## ---------------------------------------------------- ##    

## ------ Select training years ------ ##
'''
    Important to keep years in order
    Training years = 2035-2054
'''
X_train = features_train[:,:lenTime,:,:]
X_val = features_val[:,:lenTime,:,:]
X_test = features_test[:,:lenTime,:,:]
y_train = y_train[:,:lenTime,:]
y_val = y_val[:,:lenTime,:]
y_test = y_test[:,:lenTime,:]
## ---------------------------------------------------- ## 

## ------ Flatten data ------ ##
lenLat = 49; lenLon = 288; 
X_train = X_train.reshape(len(X_train)*lenTime,lenLat*lenLon)
X_val = X_val.reshape(len(X_val)*lenTime,lenLat*lenLon)
X_test = X_test.reshape(len(X_test)*lenTime,lenLat*lenLon)
y_train = y_train.reshape((len(y_train)*lenTime,2))
y_val = y_val.reshape((len(y_val)*lenTime,2))
y_test = y_test.reshape((len(y_test)*lenTime,2))
## ---------------------------------------------------- ## 

## ------ Replace NaNs ------ ##  
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

## ------ Predict control vs. feedback simulation ------ ##
y_train = y_train[:,1:]
y_val = y_val[:,1:]
y_test = y_test[:,1:]
## ---------------------------------------------------- ## 

## ------ Train the model ------ ##
tf.keras.backend.clear_session()
tf.keras.utils.set_random_seed(4444)
''' Create model '''
model = Sequential()
model.add(Dense(20, input_shape=(X_train.shape[1],), 
                activation='sigmoid', 
                use_bias=True,
                kernel_regularizer=regularizers.l1_l2(l1=0.00, l2=0.00),
                bias_initializer=tf.keras.initializers.LecunNormal(seed=4444),
                kernel_initializer=tf.keras.initializers.LecunNormal(seed=4444)))
model.add(Dropout(0.2))
model.add(Dense(y_train.shape[1],
                activation='sigmoid', 
                use_bias=False,
                kernel_regularizer=regularizers.l1_l2(l1=0.00, l2=0.00),
                bias_initializer=tf.keras.initializers.LecunNormal(seed=4444),
                kernel_initializer=tf.keras.initializers.LecunNormal(seed=4444)))


''' Training parameters '''
batch_size = 32
epochs = 10
verbose = 0
lr = 0.01

''' Schedule a decreasing learning rate '''
def scheduler(epoch, lr):
    if epoch < 2 or epoch > 16:
        return lr
    else:
        return lr/2.
    
''' Compile the model '''    
model.compile(optimizer=optimizers.SGD(learning_rate=lr, 
                                        momentum=0.9, 
                                        nesterov=True),
              loss = tf.keras.losses.BinaryCrossentropy(from_logits=False),
              metrics=[metrics.binary_accuracy,metrics.categorical_accuracy],)
callback = tf.keras.callbacks.LearningRateScheduler(scheduler)      
print(model.summary())

print('starting training...')
history = model.fit(X_train, y_train, 
                    batch_size=batch_size, 
                    epochs=epochs, 
                    shuffle=True, 
                    verbose=verbose, 
                    callbacks=[callback,], 
                    validation_data=(X_val,y_val))
## ---------------------------------------------------- ## 

## ------ Predictions! ------ ##
y_pred_train = model.predict(X_train)
y_pred_val = model.predict(X_val)
y_pred_test = model.predict(X_test)
print(np.round(y_pred_test[-20:],decimals=3).T)
## -------------------------- ## 

## ------ Prediction confidence ------ ##
y_pred_plot = y_pred_test.reshape((lenTime,int(len(y_pred_test)/lenTime)))
for iline in range(y_pred_plot.shape[1]):
    plt.plot(y_pred_plot[:,iline])
plt.title('prediction confidence')
plt.xlabel('time ' + '(' + str(timeFrame) + ')')
plt.ylim([0,1])
plt.show()
## ----------------------------------- ##

## ------ Accuracy metrics ------ ##
print("categorical accuracy: ", history.history['categorical_accuracy'])
print("binary accuracy: ", history.history['binary_accuracy'])
## ------------------------------ ##

## ------ Summarize history for loss ------ ##
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss ' + '(' + str(timeFrame) + ')', fontsize=11)
plt.ylabel('loss')
plt.xlabel('epoch')
ymax = np.nanmax([np.nanmax(history.history['val_loss']), np.nanmax(history.history['loss'])])
plt.legend(['train', 'val'], loc='upper right')
plt.show()
## ---------------------------------------- ## 

## ------ Map of weights ------ ##
from plottingFunctions import get_colormap, make_maps
brbg_cmap,rdbu_cmap,jet = get_colormap(21)
mapWeights = model.layers[0].get_weights()[0].reshape(lenLat,lenLon,20)
fig,ax = make_maps(mapWeights[:,:,5],lat[30:-6],lon,
                   -0.04,0.04,21,brbg_cmap,'weights','weights','weights')
## ----------------------------- ##
gc.collect()

