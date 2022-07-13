#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 11:40:38 2022

@author: kmayer

Plot neural network confidence vs accuracy &
box and whisker plot of the 20% most confident predictions
"""
import numpy as np
import random
import xarray as xr
import pandas as pd

import seaborn as sns
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
def set_box_color(bp, color):
    plt.setp(bp['boxes'],color=color, alpha=0.6)
    plt.setp(bp['whiskers'], color=color,linewidth=0,alpha=0.6)
    plt.setp(bp['caps'], color='w',alpha=0)
    plt.setp(bp['medians'], color='w',linewidth=0)
    plt.setp(bp['means'], linestyle='-', color='w',linewidth=3)
#%%
DIR_LOAD  = 'data/'
LEAD   = 2 
TESTmem = [10,1,2,3,4,5,6,7,8,9]

#%% LOAD data
sai_al = np.zeros(shape=(100,20))
sai_nw = np.zeros(shape=(100,20))
sai_sw = np.zeros(shape=(100,20))
cont_al = np.zeros(shape=(100,20))
cont_nw = np.zeros(shape=(100,20))
cont_sw = np.zeros(shape=(100,20))

for m, mems in enumerate(TESTmem): 
    FI_LOAD = 'accvsconf_SAI_alaska_testmem'+str(TESTmem[m])+'_lead'+str(LEAD)+'_mem1-10.npy'
    sai_al[m*10:(m*10)+10,:] = np.load(DIR_LOAD+FI_LOAD, allow_pickle=True)

    FI_LOAD = 'accvsconf_SAI_nwcoast_testmem'+str(TESTmem[m])+'_lead'+str(LEAD)+'_mem1-10.npy'
    sai_nw[m*10:(m*10)+10,:] = np.load(DIR_LOAD+FI_LOAD, allow_pickle=True)

    FI_LOAD = 'accvsconf_SAI_swcoast_testmem'+str(TESTmem[m])+'_lead'+str(LEAD)+'_mem1-10.npy'
    sai_sw[m*10:(m*10)+10,:] = np.load(DIR_LOAD+FI_LOAD, allow_pickle=True)

    #----------
    FI_LOAD = 'accvsconf_control_alaska_testmem'+str(TESTmem[m])+'_lead'+str(LEAD)+'_mem1-10.npy'
    cont_al[m*10:(m*10)+10,:] = np.load(DIR_LOAD+FI_LOAD, allow_pickle=True)

    FI_LOAD = 'accvsconf_control_nwcoast_testmem'+str(TESTmem[m])+'_lead'+str(LEAD)+'_mem1-10.npy'
    cont_nw[m*10:(m*10)+10,:] = np.load(DIR_LOAD+FI_LOAD, allow_pickle=True)

    FI_LOAD = 'accvsconf_control_swcoast_testmem'+str(TESTmem[m])+'_lead'+str(LEAD)+'_mem1-10.npy'
    cont_sw[m*10:(m*10)+10,:] = np.load(DIR_LOAD+FI_LOAD, allow_pickle=True)


#%% plot shading & median accuracies across all confidence levels for ALL testing members combined
gs_kw = dict(width_ratios=[1.2, 1], height_ratios=[1, 1, 1])

fig = plt.figure(figsize=(20,15),constrained_layout=False)  
ax = fig.subplot_mosaic('''
                        AG
                        BH
                        CI
                        ''', gridspec_kw = gs_kw)  

for loc in ['A','B','C']:                  
    adjust_spines(ax[loc], ['left', 'bottom'])
    ax[loc].spines['top'].set_color('none')
    ax[loc].spines['right'].set_color('none')
    ax[loc].spines['left'].set_color('dimgrey')
    ax[loc].spines['bottom'].set_color('dimgrey')
    ax[loc].spines['left'].set_linewidth(2)
    ax[loc].spines['bottom'].set_linewidth(2)
    ax[loc].tick_params('both',length=4,width=2,which='major',color='dimgrey')
    ax[loc].yaxis.grid(zorder=1,color='dimgrey',alpha=0.35)
    ax[loc].set_xlim(0,18)
    ax[loc].set_xticks(np.arange(0,20,2))
    ax[loc].set_xticklabels(np.arange(10,110,10)[::-1],color='dimgrey',fontsize=30)
    ax[loc].set_ylim(29,100)
    ax[loc].set_yticks(np.arange(40,120,20))
    ax[loc].set_yticklabels(np.arange(40,120,20),color='dimgrey',fontsize=30)
for loc in ['G','H','I']: 
    adjust_spines(ax[loc], ['left', 'bottom'])
    ax[loc].spines['top'].set_color('none')
    ax[loc].spines['right'].set_color('none')
    ax[loc].spines['left'].set_color('dimgrey')
    ax[loc].spines['bottom'].set_color('dimgrey')
    ax[loc].spines['left'].set_linewidth(2)    
    ax[loc].spines['bottom'].set_linewidth(0)
    ax[loc].tick_params('both',length=0,width=2,which='major',color='dimgrey')
    ax[loc].yaxis.grid(zorder=1,color='dimgrey',alpha=0.35)
    ax[loc].get_xaxis().set_visible(False)
    ax[loc].set_ylim(29,100)
    ax[loc].set_yticks(np.arange(40,120,20))
    ax[loc].set_yticklabels(np.arange(40,120,20),color='dimgrey',fontsize=30)    

# ----------- CONFIDENCE VS ACCURACY -----------
ax['A'].plot(np.mean(cont_al,axis=0)[:-1],'xkcd:charcoal',alpha=.75,linewidth=5,label='SSP2-4.5')
ax['A'].plot(np.mean(sai_al,axis=0)[:-1],'xkcd:dark turquoise',alpha=.75,linewidth=5,label='SAI-1.5')

ax['A'].fill_between(x = np.arange(0,19),
                     y1=np.percentile(sai_al[:,:-1],q=0,axis=0),
                     y2=np.percentile(sai_al[:,:-1],q=100,axis=0),color='xkcd:dull teal',alpha=0.5,edgecolor=None,linewidth=2)
ax['A'].fill_between(x = np.arange(0,19),
                     y1=np.percentile(cont_al[:,:-1],q=0,axis=0),
                     y2=np.percentile(cont_al[:,:-1],q=100,axis=0),color='xkcd:charcoal',alpha=0.3,edgecolor=None,linewidth=2)

ax['B'].plot(np.mean(cont_nw,axis=0)[:-1],'xkcd:charcoal',alpha=.75,linewidth=5)
ax['B'].plot(np.mean(sai_nw,axis=0)[:-1],'xkcd:dark turquoise',alpha=.75,linewidth=5)

ax['B'].fill_between(x = np.arange(0,19),
                     y1=np.percentile(sai_nw[:,:-1],q=0,axis=0),
                     y2=np.percentile(sai_nw[:,:-1],q=100,axis=0),color='xkcd:dull teal',alpha=0.5,edgecolor=None,linewidth=2)
ax['B'].fill_between(x = np.arange(0,19),
                     y1=np.percentile(cont_nw[:,:-1],q=0,axis=0),
                     y2=np.percentile(cont_nw[:,:-1],q=100,axis=0),color='xkcd:charcoal',alpha=0.3,edgecolor=None,linewidth=2)
ax['B'].set_ylabel('accuracy',color='dimgrey',fontsize=35)


ax['C'].plot(np.mean(cont_sw,axis=0)[:-1],'xkcd:charcoal',alpha=.75,linewidth=5)
ax['C'].plot(np.mean(sai_sw,axis=0)[:-1],'xkcd:dark turquoise',alpha=.75,linewidth=5)

ax['C'].fill_between(x = np.arange(0,19),
                     y1=np.percentile(sai_sw[:,:-1],q=0,axis=0),
                     y2=np.percentile(sai_sw[:,:-1],q=100,axis=0),color='xkcd:dull teal',alpha=0.5,edgecolor=None,linewidth=2)
ax['C'].fill_between(x = np.arange(0,19), 
                     y1=np.percentile(cont_sw[:,:-1],q=0,axis=0),
                     y2=np.percentile(cont_sw[:,:-1],q=100,axis=0),color='xkcd:charcoal',alpha=0.3,edgecolor=None,linewidth=2)
ax['C'].set_xlabel('percent most confident',color='dimgrey',fontsize=35)


ax['A'].text(x=0.5,y=90,s='ALASKA',fontsize=30,color='dimgrey',rotation=0)
leg1 = ax['A'].legend(loc='lower left',fontsize=28,frameon=False,ncol=2)
leg1._legend_box.align = 'left'
leg1.get_texts()[0].set_color('xkcd:grey')
leg1.get_texts()[1].set_color('xkcd:dull teal')
leg1.get_lines()[0].set_linewidth(10)
leg1.get_lines()[1].set_linewidth(10)
plt.setp(leg1.get_title(),color='dimgrey')

leg2 = ax['B'].legend(loc='upper left',frameon=False,ncol=3,title='NW COAST',title_fontsize=28)
leg2._legend_box.align = 'left'
plt.setp(leg2.get_title(),color='dimgrey')

leg3 = ax['C'].legend(loc='upper left',frameon=False,ncol=3,title='SW COAST',title_fontsize=28)
leg3._legend_box.align = 'left'
plt.setp(leg3.get_title(),color='dimgrey')

ax['A'].set_title('CONFIDENCE vs ACCURACY', fontsize=33, color='dimgrey',loc='left')

# ----------- BOX AND WHISKER -----------
positions_sai = np.array(range(1))*2.0-0.3
positions_cont = np.array(range(1))*2.0+0.3

for loc in ['G','H','I']:
    ax[loc].hlines(y=50,xmin=-.8,xmax=.8,color='k',linestyle='-')

bpmAconf = ax['G'].boxplot(sai_al[:,-4],
                  positions=positions_sai,
                  widths=0.4,
                  patch_artist=True,
                  meanline=True,
                  showmeans=True,
                  sym='')
bprAconf = ax['G'].boxplot(cont_al[:,-4],
                  positions=positions_cont,
                  widths=0.4,
                  patch_artist=True,
                  meanline=True,
                  showmeans=True,
                  sym='')

bpmBconf = ax['H'].boxplot(sai_nw[:,-4],
                  positions=positions_sai,
                  widths=0.4,
                  patch_artist=True,
                  meanline=True,
                  showmeans=True,
                  sym='')
bprBconf = ax['H'].boxplot(cont_nw[:,-4],
                  positions=positions_cont,
                  widths=0.4,
                  patch_artist=True,
                  meanline=True,
                  showmeans=True,
                  sym='')

bpmCconf = ax['I'].boxplot(sai_sw[:,-4],
                  positions=positions_sai,
                  widths=0.4,
                  patch_artist=True,
                  meanline=True,
                  showmeans=True,
                  sym='')
bprCconf = ax['I'].boxplot(cont_sw[:,-4],
                  positions=positions_cont,
                  widths=0.4,
                  patch_artist=True,
                  meanline=True,
                  showmeans=True,
                  sym='')

# Modify boxes
cbase = 'grey'
csai = 'xkcd:dull teal'
ccont = 'xkcd:charcoal'

set_box_color(bpmAconf,csai)
set_box_color(bprAconf,ccont)

set_box_color(bpmBconf,csai)
set_box_color(bprBconf,ccont)

set_box_color(bpmCconf,csai)
set_box_color(bprCconf,ccont)

xs = np.zeros(shape=(len(sai_al))) + positions_sai
xc = np.zeros(shape=(len(cont_al))) + positions_cont

ax['G'].plot(xs, sai_al[:,-4],color=csai, alpha=1,zorder=10,marker='.',linewidth=0,markersize=10,markeredgewidth=.5,markeredgecolor='w')
ax['G'].plot(xc, cont_al[:,-4],color=ccont, alpha=1,zorder=10,marker='.',linewidth=0,markersize=10,markeredgewidth=.5,markeredgecolor='w')

ax['H'].plot(xs, sai_nw[:,-4],color=csai, alpha=1,zorder=10,marker='.',linewidth=0,markersize=10,markeredgewidth=.5,markeredgecolor='w')
ax['H'].plot(xc, cont_nw[:,-4],color=ccont, alpha=1,zorder=10,marker='.',linewidth=0,markersize=10,markeredgewidth=.5,markeredgecolor='w')

ax['I'].plot(xs, sai_sw[:,-4],color=csai, alpha=1,zorder=10,marker='.',linewidth=0,markersize=10,markeredgewidth=.5,markeredgecolor='w')
ax['I'].plot(xc, cont_sw[:,-4],color=ccont, alpha=1,zorder=10,marker='.',linewidth=0,markersize=10,markeredgewidth=.5,markeredgecolor='w')

ax['G'].set_title('CONFIDENT PREDICTIONS', loc='left', fontsize=33,color='dimgrey')
ax['G'].text(x=positions_sai-.17,y=-150,s='SAI-1.5',fontsize=31,color=csai,rotation=0)
ax['G'].text(x=positions_cont-.22,y=-150,s='SSP2-4.5',fontsize=31,color=ccont,rotation=0)


plt.savefig('figures/Figure4.png',bbox_inches='tight',dpi=300)

# plt.show()
