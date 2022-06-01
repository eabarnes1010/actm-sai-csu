import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy as ct
import cartopy.crs as ccrs
import cmocean as cmocean
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import palettable
import numpy as np
import numpy.ma as ma
import copy as copy
from matplotlib import cm

################################  
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['figure.dpi']= 150
dpiFig = 400.
titleSize = 16

### for white background...
plt.rc('text',usetex=True)
plt.rc('font',**{'family':'sans-serif','sans-serif':['Avant Garde']}) 
plt.rc('savefig',facecolor='white')
plt.rc('axes',facecolor='white')
plt.rc('axes',labelcolor='dimgrey')
plt.rc('axes',labelcolor='dimgrey')
plt.rc('xtick',color='dimgrey')
plt.rc('ytick',color='dimgrey')
################################  



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

def drawOnGlobe(ax, data, lats, lons, cmap='coolwarm', coastline_color='k', vmin=None, vmax=None, inc=None, cbarBool=True, contourMap=[], contourVals = [], fastBool=False, extent='both'):

    data_crs = ct.crs.PlateCarree()
    data_cyc, lons_cyc = add_cyclic_point(data, coord=lons) #fixes white line by adding point#data,lons#ct.util.add_cyclic_point(data, coord=lons) #fixes white line by adding point

    # ax.set_global()
    ax.coastlines(linewidth = 1.2, color=coastline_color)

#     sigma = .5
#     data_cyc = gaussian_filter(data_cyc, sigma)
    
    if(fastBool):
        image = ax.pcolormesh(lons_cyc, lats, data_cyc, transform=data_crs, cmap=cmap,shading='auto')
#         image = ax.contourf(lons_cyc, lats, data_cyc, np.linspace(0,vmax,20),transform=data_crs, cmap=cmap)
    else:
        image = ax.pcolor(lons_cyc, lats, data_cyc, transform=data_crs, cmap=cmap,shading='auto')
    
    if(np.size(contourMap) !=0 ):
        contourMap_cyc, __ = add_cyclic_point(contourMap, coord=lons) #fixes white line by adding point
        ax.contour(lons_cyc,lats,contourMap_cyc,contourVals, transform=data_crs, colors='fuchsia')
    
    if(cbarBool):
        cb = plt.colorbar(image, ax=ax,shrink=.5, orientation="horizontal", pad=.02, extend=extent)
        cb.ax.tick_params(labelsize=6) 
    else:
        cb = None

    image.set_clim(vmin,vmax)
    
    return cb, image   

def add_cyclic_point(data, coord=None, axis=-1):

    # had issues with cartopy finding utils so copied for myself
    
    if coord is not None:
        if coord.ndim != 1:
            raise ValueError('The coordinate must be 1-dimensional.')
        if len(coord) != data.shape[axis]:
            raise ValueError('The length of the coordinate does not match '
                             'the size of the corresponding dimension of '
                             'the data array: len(coord) = {}, '
                             'data.shape[{}] = {}.'.format(
                                 len(coord), axis, data.shape[axis]))
        delta_coord = np.diff(coord)
        if not np.allclose(delta_coord, delta_coord[0]):
            raise ValueError('The coordinate must be equally spaced.')
        new_coord = ma.concatenate((coord, coord[-1:] + delta_coord[0]))
    slicer = [slice(None)] * data.ndim
    try:
        slicer[axis] = slice(0, 1)
    except IndexError:
        raise ValueError('The specified axis does not correspond to an '
                         'array dimension.')
    new_data = ma.concatenate((data, data[tuple(slicer)]), axis=axis)
    if coord is None:
        return_value = new_data
    else:
        return_value = new_data, new_coord
    return return_value
            

def plot_weights(ax, weights, landSeaMask,dsf):
   
    fastBool = False
    cmap = palettable.colorbrewer.diverging.RdBu_11_r.mpl_colormap    
    vmax = .1
    xplot = landSeaMask*weights[:,0]
    
    cb, image = drawOnGlobe(ax, xplot.reshape((len(dsf['lat']),len(dsf['lon']))), dsf['lat'].values, dsf['lon'].values, vmin = -vmax, vmax=vmax, coastline_color='silver',cmap=cmap,  cbarBool=True, fastBool=False, extent='both')
    cb.set_ticks((-vmax,0,vmax))
    cb.set_ticklabels((-vmax,0,vmax))            
    cb.ax.tick_params(labelsize=titleSize/2) 
    cb.set_label('weights', fontsize=titleSize)

def plot_snr(ax,featuresC,featuresF,landSeaMask,time_dsc,dsf,settings):
    cmap = palettable.cubehelix.cubehelix3_16.mpl_colormap
    gaussian_filter_sigma = .5
    fastBool = False    

    #-----------------------------------------------
    maps_C = copy.deepcopy(featuresC)
    maps_F = copy.deepcopy(featuresF)
    if(settings["land_only"]==True):
        maps_C = copy.deepcopy(maps_C*landSeaMask.reshape(featuresC.shape[2],featuresC.shape[3]))
        maps_F = copy.deepcopy(maps_F*landSeaMask.reshape(featuresC.shape[2],featuresC.shape[3]))    
    maps_diff = maps_F - maps_C

    i_nonan = np.count_nonzero(~np.isnan(maps_C[0,0,:,:]))
    mean_vals_C = np.nansum(np.nansum(maps_C,axis=3),axis=2)/i_nonan
    maps_C_nomean = copy.deepcopy(maps_C - mean_vals_C[:,:,np.newaxis,np.newaxis])
    i_nonan = np.count_nonzero(~np.isnan(maps_F[0,0,:,:]))
    mean_vals_F = np.nansum(np.nansum(maps_F,axis=3),axis=2)/i_nonan
    maps_F_nomean = copy.deepcopy(maps_F - mean_vals_F[:,:,np.newaxis,np.newaxis])
    maps_diff_nomean = maps_F_nomean - maps_C_nomean
    #-----------------------------------------------

    for meantype in ('withMean',):
        if(settings["var"]=='T' and meantype=='noMean'):
            continue
        #-----------------------------------------------         
        xplot = []
        #----------------------------------------------- 
        year_signal = 2030
        if(settings["var"]=='R95pTOT'):
            year_signal = 2040
        itime = np.where(time_dsc==year_signal)[0]
        if(meantype=='withMean'):
            xplot = maps_diff[:,itime,:,:]
            iplot = 1
            title_name = settings["var"] + ', ' + str(year_signal) 
            maxVal = 1.0#2.5            
        elif(meantype=='noMean'):
            xplot = maps_diff_nomean[:,itime,:,:]
            iplot = 2
            title_name = settings["var"] + ', ' + str(year_signal) + '\nglobal mean removed'
            maxVal = .5#1.5
        else:
            raise ValueError('no such meantype')
            
        if settings["var"]=='R95pTOT':
            maxVal = 1.0

        x_signal = np.squeeze(np.nanmean(xplot[:,:,:,:],axis=0))
        itime = np.where(time_dsc==year_signal)[0]
        x_noise = np.squeeze(np.nanmax(maps_F[:,itime,:,:],axis=0)-np.nanmin(maps_F[:,itime,:,:],axis=0))    
        xplot = np.abs(x_signal)/x_noise
        # set ocean nans to zeros
        xplot[np.isnan(xplot)==True] = 0.


        cb, image = drawOnGlobe(ax, xplot, dsf['lat'].values, dsf['lon'].values, coastline_color='silver',cmap=cmap, vmin = 0, vmax=maxVal, cbarBool=True, fastBool=fastBool, extent='max')
        cb.set_label('signal-to-noise ratio', fontsize=titleSize)
        cb.set_ticks(np.arange(0,maxVal+.25,.25))
        cb.set_ticklabels(np.arange(0,maxVal+.25,.25))            
        cb.ax.tick_params(labelsize=titleSize/2) 
        
    return title_name

def plot_contributions(ax1,ax2,model,features_train,features_test,X_train,X_test,y_train,y_test,landSeaMask,time_dsc,dsf,settings):
    # cmap = palettable.colorbrewer.diverging.BrBG_11.mpl_colormap
    cmap = palettable.cmocean.diverging.Curl_11_r.mpl_colormap
    fastBool = False
    
    # nan mask
    inanmask_train = np.isnan(features_train).reshape(features_train.shape[0]*features_train.shape[1],features_train.shape[2]*features_train.shape[3])
    inanmask_test = np.isnan(features_test).reshape(features_test.shape[0]*features_test.shape[1],features_test.shape[2]*features_test.shape[3])
    inanmask_all = np.append(inanmask_train,inanmask_test,axis=0)

    # data
    X_all = np.append(X_train,X_test,axis=0)
    y_all = np.append(y_train,y_test,axis=0)

    # X_all[X_all==0] = np.nan                   # nan out oceans too
    y_pred_all = model.predict(X_all)
    X_all[inanmask_all] = np.nan
    y_all[inanmask_all[:,0],:] = np.nan
    y_pred_all[inanmask_all[:,0],:] = np.nan

    # Contributions
    weights = model.get_weights()[0]
    cont = landSeaMask*weights[:,0]
    cont = cont*X_all

    #----------------------------------------------
    # get only a specific year, 2030 or 2040
    time_arr = np.tile(time_dsc,40)
    if(settings["var"]=='R95pTOT'):
        year_signal = 2040
        vmax_c = .1    
        vmax_f = .025
    else:
        year_signal = 2030
        vmax_c = .035
        vmax_f = .035    
    itime = np.where(time_arr==year_signal)[0]
    cont = cont[itime,:]
    y_all = y_all[itime,:]
    y_pred_all = y_pred_all[itime,:]


    #----------------------------------------------
    # grab Feedback only
    iplot = np.where(y_all==1)[0]
    xplot = np.nanmean(cont[iplot,:],axis=0)
    cb1, image1 = drawOnGlobe(ax1, xplot.reshape((len(dsf['lat']),len(dsf['lon']))), dsf['lat'].values, dsf['lon'].values, vmin = -vmax_f, vmax=vmax_f, coastline_color='silver',cmap=cmap,  cbarBool=True, fastBool=fastBool, extent='both')
    cb1.set_ticks((-vmax_f,vmax_f))
    cb1.set_ticklabels(('contributes to\nRCP8.5','contributes to\nGLENS-SAI'))                     
    cb1.ax.tick_params(labelsize=titleSize/2) 
    ax1.set_title('(c) ' + settings["var"] + ', ' + str(year_signal) + '\nGLENS-SAI', fontsize=16)       


    #----------------------------------------------
    # grab Control only
    iplot = np.where(y_all==0)[0]
    xplot = np.nanmean(cont[iplot,:],axis=0)
    cb2, image2 = drawOnGlobe(ax2, xplot.reshape((len(dsf['lat']),len(dsf['lon']))), dsf['lat'].values, dsf['lon'].values, vmin = -vmax_c, vmax=vmax_c, coastline_color='silver',cmap=cmap,  cbarBool=True, fastBool=fastBool, extent='both')
    cb2.set_ticks((-vmax_c,vmax_c))
    cb2.set_ticklabels(('contributes to\nRCP8.5','contributes to\nGLENS-SAI'))                       
    cb2.ax.tick_params(labelsize=titleSize/2) 
    ax2.set_title('(d) ' + settings["var"] + ', ' + str(year_signal) + '\nRCP8.5', fontsize=16)   
    
def plot_dots(ax,corr_F,corr_C,count_F,count_C,time_dsc,marker='s',max_year=2098, bold_year=None):
    
    size = 100
    sai_colors = mpl.colors.ListedColormap(palettable.colorbrewer.sequential.PuBu_5.mpl_colors)
    rcp_colors = mpl.colors.ListedColormap(palettable.colorbrewer.sequential.OrRd_5.mpl_colors)
    for iy,year in enumerate(time_dsc):
        if year > max_year:
            ax.arrow(year,1.5,
                     .5,0,
                     head_width=.025,
                     head_length=.2,
                     color=palettable.colorbrewer.sequential.PuBu_4.hex_colors[-1],
                     linewidth=.5,
                    )
            ax.arrow(year,1.35,
                     .5,0,
                     head_width=.025,
                     head_length=.2,
                     color=palettable.colorbrewer.sequential.OrRd_4.hex_colors[-1],
                     linewidth=.5,
                    )            
            break
        # plot GLENS-SAI
        ax.scatter(year,1.5,
                    s=size,
                    marker=marker,                    
                    c=corr_F[iy]/count_F[iy]-.00001,            
                    cmap=sai_colors,
                    edgecolor='lightgray',
                    linewidth=.5,
                    vmin=-.25,vmax=1,
                   )    
        plt.text(year+.05,1.5-.005,
                 int(corr_F[iy]),
                 color='white',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=5,
                )

        # plot RCP8.5
        ax.scatter(year,1.35,
                    s=size,
                    marker=marker,
                    c=corr_C[iy]/count_C[iy]-.00001,            
                    cmap=rcp_colors,
                    edgecolor='lightgray',
                    linewidth=.5,                    
                    vmin=-.25,vmax=1,                
                   )
        plt.text(year+.05,1.35-.005,
                 int(corr_C[iy]),
                 color='white',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=5,
                 fontweight='heavy',
                )
    plt.text(2020,1.6,
             '(a)',
             fontsize=16,
             verticalalignment='bottom',   
             horizontalalignment='left',         
             color='k',
            )    

    plt.text(2020,1.5-.005,
             'GLENS-SAI',
             fontsize=10,
             verticalalignment='center',   
             horizontalalignment='right',         
             color=palettable.colorbrewer.sequential.PuBu_4.hex_colors[-1],
            )    
    plt.text(2020,1.35-.005,
             'RCP8.5',
             fontsize=10,
             verticalalignment='center',     
             horizontalalignment='right',             
             color=palettable.colorbrewer.sequential.OrRd_4.hex_colors[-1],
            )

    if bold_year==2030:
        ax.set_xticks(np.arange(2020,2100,10),labels=[2020, "\\textbf{2030}", 2040, 2050, 2060, 2070, 2080, 2090])     
    elif bold_year==2040:
        ax.set_xticks(np.arange(2020,2100,10),labels=[2020, 2030, "\\textbf{2040}", 2050, 2060, 2070, 2080, 2090])     
    else:
        ax.set_xticks(np.arange(2020,2100,10),labels=np.arange(2020,2100,10))     
    plt.ylim(1.3,1.55)
    plt.xlim(2020,max_year+1.75)
    adjust_spines(ax, ['bottom'])
      
def plot_dots_seeds(ax,ax1,exp_dict,time_dsc,settings,max_year=2097):
    
    sai_colors = mpl.colors.ListedColormap(palettable.colorbrewer.sequential.PuBu_5.mpl_colors)            
    rcp_colors = mpl.colors.ListedColormap(palettable.colorbrewer.sequential.OrRd_5.mpl_colors)            
    
    X_C = np.zeros((len(exp_dict.keys()),77))
    X_F = np.zeros((len(exp_dict.keys()),77))
    num_C = np.zeros((len(exp_dict.keys()),77))
    num_F = np.zeros((len(exp_dict.keys()),77))

    for f_index,f in enumerate(exp_dict):
        print(f)

        acc_test = []

        y_pred_like_train = exp_dict[f]["y_pred_like_train"]
        y_pred_train = exp_dict[f]["y_pred_train"]
        acc_train = exp_dict[f]["acc_train"]
        y_pred_like_test = exp_dict[f]["y_pred_like_test"]
        y_pred_test = exp_dict[f]["y_pred_test"]
        acc_test = exp_dict[f]["acc_test"]
        valNum = 4

        corr_C = np.nansum(acc_test[:valNum,:], axis=0)    # plot testing only
        corr_F = np.nansum(acc_test[valNum:,:], axis=0)   # plot testing only        
        count_C = np.count_nonzero(~np.isnan(acc_test[:valNum,:]), axis=0)    # plot testing only
        count_F = np.count_nonzero(~np.isnan(acc_test[valNum:,:]), axis=0)   # plot testing only    
        print(count_C)
        # print(count_F)

        for iy,year in enumerate(time_dsc):
            X_F[f_index,iy] = corr_F[iy]/count_F[iy]
            X_C[f_index,iy] = corr_C[iy]/count_C[iy]

            num_F[f_index,iy] = corr_F[iy]
            num_C[f_index,iy] = corr_C[iy]        
            if year > max_year:
                break
    
    ax.pcolor(np.arange(2021,2098),np.arange(0,5),
               X_F-.00001,
               cmap=sai_colors,
               vmin=-.25,
               vmax=1.,
               edgecolors='w',
               # linewidth=.01,
              )
    # Loop over data dimensions and create text annotations.
    for i in np.arange(0,5):
        for j_index,j in enumerate(np.arange(2021,max_year)):
            text = ax.text(j, i, int(num_F[i, j_index]),
                           ha="center", va="center", color="w")

    ax.set_xticks(np.arange(2020,2100,10),labels=np.arange(2020,2100,10))     
    ax.set_yticks(np.arange(0,5,1),labels='')     
    ax.set_xlim(2020+.5,max_year-.5)
    ax.set_title(settings["var"] + ' under GLENS-SAI')

    
    ax1.pcolor(np.arange(2021,2098),np.arange(0,5),
               X_C-.00001,
               cmap=rcp_colors,
               vmin=0.,
               vmax=1.,
               edgecolors='w',
               # linewidth=.01,
              )
    # Loop over data dimensions and create text annotations.
    for i in np.arange(0,5):
        for j_index,j in enumerate(np.arange(2021,max_year)):
            text = ax1.text(j, i, int(num_C[i, j_index]),
                           ha="center", va="center", color="w")
    ax1.set_xticks(np.arange(2020,2100,10),labels=np.arange(2020,2100,10))     
    ax1.set_yticks(np.arange(0,5,1),labels='')     
    ax1.set_xlim(2020+.5,max_year-.5)
    ax1.set_title(settings["var"] + ' under RCP8.5')
    
    adjust_spines(ax,['bottom'])
    adjust_spines(ax1,['bottom'])
    



def plot_noise(ax,featuresC,featuresF,features_noise,landSeaMask,time_dsc,dsf,year_signal,maxVal,settings):
    cmap = palettable.cubehelix.cubehelix3_16.mpl_colormap
    gaussian_filter_sigma = .5
    fastBool = False    

    #-----------------------------------------------
    maps_C = copy.deepcopy(featuresC)
    maps_F = copy.deepcopy(featuresF)
    maps_noise = copy.deepcopy(features_noise)
    
    if(settings["land_only"]==True):
        maps_C = copy.deepcopy(maps_C*landSeaMask.reshape(featuresC.shape[2],featuresC.shape[3]))
        maps_F = copy.deepcopy(maps_F*landSeaMask.reshape(featuresC.shape[2],featuresC.shape[3]))
        maps_noise = copy.deepcopy(maps_noise*landSeaMask.reshape(featuresC.shape[2],featuresC.shape[3]))
    maps_diff = maps_F - maps_C

    #-----------------------------------------------         
    xplot = []
    #----------------------------------------------- 
    itime = np.where(time_dsc==year_signal)[0]
    xplot = maps_diff[:,itime,:,:]         

    x_signal = np.squeeze(np.nanmean(xplot[:,:,:,:],axis=0))
    x_noise = np.squeeze(np.nanmax(maps_noise[:,itime,:,:],axis=0)-np.nanmin(maps_noise[:,itime,:,:],axis=0))    
    xplot = np.abs(x_signal)/x_noise
    # set ocean nans to zeros
    xplot[np.isnan(xplot)==True] = 0.


    cb, image = drawOnGlobe(ax, xplot, dsf['lat'].values, dsf['lon'].values, coastline_color='silver',cmap=cmap, vmin = 0, vmax=maxVal, cbarBool=True, fastBool=fastBool, extent='max')
    cb.set_label('signal-to-noise ratio', fontsize=titleSize)
    cb.set_ticks(np.arange(0,maxVal+.25,.25))
    cb.set_ticklabels(np.arange(0,maxVal+.25,.25))            
    cb.ax.tick_params(labelsize=titleSize/2) 



