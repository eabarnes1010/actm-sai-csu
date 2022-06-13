#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 11:25:25 2022

@author: kmayer

Functions to create neural network architecture &
plot the accuracy & loss during training

"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import regularizers

import matplotlib as mpl
import matplotlib.pyplot as plt

plt.rc('text',usetex=True)
plt.rcParams['font.family']='sans-serif'
plt.rcParams['font.sans-serif']=['Verdana']
plt.rcParams.update({'font.size': 15})
def adjust_spines(ax, spines):
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', 5))
        else:
            spine.set_color('none')
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        ax.yaxis.set_ticks([])
    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
            ax.xaxis.set_ticks([])
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['figure.dpi'] = 150
dpiFig = 300.

#%% >>>>> NN Architecture >>>>>
def defineNN(hidden, input_shape, output_shape, ridge_penalty=0., lasso_penalty=0., act_fun='relu', network_seed=99):

    input1 = tf.keras.Input(shape = input_shape)
    x = tf.keras.layers.Dense(hidden[0],
                              activation = act_fun,
                              use_bias = True,
                              kernel_regularizer = regularizers.l1_l2(l1=lasso_penalty, l2=ridge_penalty),
                              bias_initializer= tf.keras.initializers.RandomNormal(seed=network_seed),
                              kernel_initializer= tf.keras.initializers.RandomNormal(seed=network_seed)
                              )(input1)
                                   
    #initialize other layers
    for layer in hidden[1:]:
        x = tf.keras.layers.Dense(layer,
                                  activation = act_fun,
                                  use_bias = True, 
                                  kernel_regularizer = regularizers.l1_l2(l1=0.0, l2=0.0),
                                  bias_initializer = tf.keras.initializers.RandomNormal(seed=network_seed),
                                  kernel_initializer = tf.keras.initializers.RandomNormal(seed=network_seed)
                                  )(x)

    #initialize output layer w/ softmax
    output_layer = tf.keras.layers.Dense(output_shape,
                                         activation = tf.keras.activations.softmax,
                                         use_bias = True,
                                         kernel_regularizer = regularizers.l1_l2(l1=0.0, l2=0.0),
                                         bias_initializer = tf.keras.initializers.RandomNormal(seed=network_seed),
                                         kernel_initializer = tf.keras.initializers.RandomNormal(seed=network_seed)
                                         )(x)
    
    #create model
    model = tf.keras.Model(inputs=input1, outputs=output_layer)
    
    return model
# <<<<< NN Architecture <<<<<

#%% >>>>> Plot Accuracy & Loss during Training >>>>>
def plot_results(history, exp_info, showplot=True):
    
    n_epochs, hiddens, lr_init, batch_size, network_seed, patience, ridge = exp_info
    
    trainColor = 'k'
    valColor = (141/255,171/255,127/255,1.)
    FS = 14
    plt.figure(figsize=(15, 7))
    
    #---------- plot loss -------------------
    ax = plt.subplot(2,2,1)
    adjust_spines(ax, ['left', 'bottom'])
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('dimgrey')
    ax.spines['bottom'].set_color('dimgrey')
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    ax.tick_params('both',length=4,width=2,which='major',color='dimgrey')
    ax.yaxis.grid(zorder=1,color='dimgrey',alpha=0.35)

    plt.plot(history.history['loss'], 'o', color=trainColor, label='Training',alpha=0.6)
    plt.plot(history.history['val_loss'], 'o', color=valColor, label='Validation',alpha=0.6)
    plt.vlines(len(history.history['val_sparse_categorical_accuracy'])-(patience+1),-10,np.max(history.history['loss']),'k',linestyle='dashed',alpha=0.4)

    plt.title('LOSS')
    plt.xlabel('EPOCH')
    plt.xticks(np.arange(0,n_epochs+20,20),labels=np.arange(0,n_epochs+20,20))
    plt.yticks(np.arange(0,5.5,.5),labels=[0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0])
    plt.grid(True)
    plt.legend(frameon=True, fontsize=FS)
    plt.xlim(-2, 50)
    plt.ylim(0,5)
    
    # ---------- plot accuracy -------------------
    ax = plt.subplot(2,2,2)
    adjust_spines(ax, ['left', 'bottom'])
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('dimgrey')
    ax.spines['bottom'].set_color('dimgrey')
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    ax.tick_params('both',length=4,width=2,which='major',color='dimgrey')
    ax.yaxis.grid(zorder=1,color='dimgrey',alpha=0.35)
    
    plt.plot(history.history['sparse_categorical_accuracy'], 'o', color=trainColor, label='Training',alpha=0.6)
    plt.plot(history.history['val_sparse_categorical_accuracy'], 'o', color=valColor, label='Validation',alpha=0.6)
    plt.vlines(len(history.history['val_sparse_categorical_accuracy'])-(patience+1),0,1,'k',linestyle='dashed',alpha=0.4)
    plt.title('PREDICTION ACCURACY')
    plt.xlabel('EPOCH')
    plt.legend(frameon=True, fontsize=FS)
    plt.xticks(np.arange(0,n_epochs+20,20),labels=np.arange(0,n_epochs+20,20))
    plt.yticks([0.5,0.6,0.7,0.8,0.9,1.0],labels=[0.5,0.6,0.7,0.8,0.9,1.0])
    plt.ylim(0.48, 1.02)
    plt.grid(True)
    plt.xlim(-2, 50)
    
    # ---------- report parameters -------------------
    plt.subplot(2, 2, 3)
    plt.ylim(0, 1)
    
    text = (
            "\n"
            + f"NETWORK PARAMETERS\n"
            + f"  Number of Epochs     = {n_epochs}\n"
            + f"  Hidden Layers        = {hiddens}\n"
            + f"  Learning Rate        = {lr_init}\n"
            + f"  Network Seed   = {network_seed}\n"
            + f"  Batch Size     = {batch_size}\n"
            + f"  Ridge          = {ridge}\n"
            )

    plt.text(0.01, 0.95, text, fontfamily='monospace', fontsize=FS, va='top')
    
    plt.axis('off')

    # ---------- Make the plot -------------------
    #plt.tight_layout()
    if showplot==False:
        plt.close('all')
    else:
        plt.show()
# <<<<< Plot Training <<<<<
