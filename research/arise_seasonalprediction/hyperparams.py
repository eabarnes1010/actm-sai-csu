#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 10:48:16 2022

@author: kmayer
"""

def get_params(experiment_name):
    
    experiments = {
                    #---------------------------------------------------------------------
                    # FINAL HYPERPARAMETERS
                    #---------------------------------------------------------------------
                    
                    #-------- SW COAST --------
                    'SAI_swcoast': {
                        'hidden_layers':[16],
                        'LR': 0.001,
                        'L2': 0.25,
                        'N_epochs': 1000,
                        'N_batch': 32,
                        'network_seed': 0
                        },
                    'control_swcoast': {
                        'hidden_layers':[8],
                        'LR': 0.01,
                        'L2': 0.5,
                        'N_epochs': 1000,
                        'N_batch': 32,
                        'network_seed': 0
                        },
                    #-------- NW COAST --------
                    'SAI_nwcoast': {
                        'hidden_layers':[8,4],
                        'LR': 0.01,
                        'L2': 1.0,
                        'N_epochs': 1000,
                        'N_batch': 128,
                        'network_seed': 0
                        },
                    'control_nwcoast': {
                        'hidden_layers':[8],
                        'LR': 0.001,
                        'L2': 0.25,
                        'N_epochs': 1000,
                        'N_batch': 128,
                        'network_seed': 0
                        },
                    #-------- ALASKA --------
                    'SAI_alaska': {
                        'hidden_layers':[16,8],
                        'LR': 0.001,
                        'L2': 0.25,
                        'N_epochs': 1000,
                        'N_batch': 32,
                        'network_seed': 0
                        },
                    'control_alaska': {
                        'hidden_layers':[8],
                        'LR': 0.001,
                        'L2': 0.25,
                        'N_epochs': 1000,
                        'N_batch': 32,
                        'network_seed': 0
                        },
                    
                    }
    
    exp_dict = experiments[experiment_name]
    exp_dict['exp_name'] = experiment_name
    
    return exp_dict
