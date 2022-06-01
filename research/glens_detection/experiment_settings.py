"""Experimental settings

Functions
---------
get_settings(experiment_name)
"""

__author__ = "Elizabeth A. Barnes"
__date__   = "03 April 2022"


def get_settings(experiment_name):
    experiments = {  
        #---------------------- MAIN SIMULATIONS ---------------------------
        "exp0_tx90p": { 
            "var" : "TX90p",            
            "n_train_val_test" : (16,4,0),
            "ens_seed": (3529,4529,5529,6529,7529),
            "net_seed": (2222,3333,4444,5555,6666),
            "land_only": True,
            "remove_mean": False,

            "network_type": 'logistic',  
            "hiddens": [1],
            "dropout_rate": 0.,
            "ridge_param": .01, 
            "learning_rate": 0.001, 
            "n_epochs": 75,            
            "batch_size": 32,
            "patience": 50,
            "lr_epoch_bound": 150,
        },   
        
        "exp1_r95ptot": { 
            "var" : "R95pTOT",            
            "n_train_val_test" : (16,4,0),
            "ens_seed": (3529,4529,5529,6529,7529),
            "net_seed": (2222,3333,4444,5555,6666),
            "land_only": True,
            "remove_mean": False,

            "network_type": 'logistic', 
            "hiddens": [1],
            "dropout_rate": 0.,
            "ridge_param": .075, 
            "learning_rate": 0.001, 
            "n_epochs": 15,            
            "batch_size": 32,
            "patience": 50,
            "lr_epoch_bound": 150,
        },   
        
        "exp2_t": { 
            "var" : "T",            
            "n_train_val_test" : (16,4,0),
            "ens_seed": (3529,4529,5529,6529,7529),
            "net_seed": (2222,3333,4444,5555,6666),
            "land_only": True,
            "remove_mean": False,

            "network_type": 'logistic',  
            "hiddens": [1],
            "dropout_rate": 0.,
            "ridge_param": .01, 
            "learning_rate": 0.001, 
            "n_epochs": 75,            
            "batch_size": 32,
            "patience": 50,
            "lr_epoch_bound": 150,
        },          
        "exp0a": { 
            "var" : "TX90p",            
            "n_train_val_test" : (16,4,0),
            "ens_seed": (3529,4529,5529,6529,7529),
            "net_seed": (2222,3333,4444,5555,6666),
            "land_only": True,
            "remove_mean": False,

            "network_type": 'logistic',  
            "hiddens": [1],
            "dropout_rate": 0.,
            "ridge_param": .0, 
            "learning_rate": 0.001, 
            "n_epochs": 75,            
            "batch_size": 32,
            "patience": 50,
            "lr_epoch_bound": 150,
        },   
        
        "exp1a": { 
            "var" : "R95pTOT",            
            "n_train_val_test" : (16,4,0),
            "ens_seed": (3529,4529,5529,6529,7529),
            "net_seed": (2222,3333,4444,5555,6666),
            "land_only": True,
            "remove_mean": False,

            "network_type": 'logistic', 
            "hiddens": [1],
            "dropout_rate": 0.,
            "ridge_param": .0, 
            "learning_rate": 0.001, 
            "n_epochs": 15,            
            "batch_size": 32,
            "patience": 50,
            "lr_epoch_bound": 150,
        },   
        
        "exp2a": { 
            "var" : "T",            
            "n_train_val_test" : (16,4,0),
            "ens_seed": (3529,4529,5529,6529,7529),
            "net_seed": (2222,3333,4444,5555,6666),
            "land_only": True,
            "remove_mean": False,

            "network_type": 'logistic',  
            "hiddens": [1],
            "dropout_rate": 0.,
            "ridge_param": .0, 
            "learning_rate": 0.001, 
            "n_epochs": 75,            
            "batch_size": 32,
            "patience": 50,
            "lr_epoch_bound": 150,
        },            
        
        
        
    }
    
    exp_dict = experiments[experiment_name]
    exp_dict['exp_name'] = experiment_name

    return exp_dict

