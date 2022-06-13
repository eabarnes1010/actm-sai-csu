"""Analysis functions.

Functions
---------
process_variable(var, da, YEAR_RANGE)
compute_global_mean(da)
fraction_positive(da)
compute_global_mean(da)
fraction_positive(da)
"""

import numpy as np
import xarray as xr
import pandas as pd
import datetime
from tqdm import tqdm

def compute_global_mean(da):
    weights = np.cos(np.deg2rad(da.lat))
    weights.name = "weights"
    temp_weighted = da.weighted(weights)
    global_mean = temp_weighted.mean(("lon", "lat"), skipna=True)
    
    return global_mean

def fraction_positive(da):
    frac = 0.
    return frac

def compute_trends(da, start_year, end_year):
    iy = np.where((da["year"]>=start_year) & (da["year"]<=end_year))[0]
    if(len(da.shape)==3):
        da_years = da[iy,:,:]
    elif(len(da.shape)==4):
        da_years = da[:,iy,:,:]
    else:
        raise NotImplementedError()
        
    da_reg = da_years.polyfit(dim="year",deg=1,)["polyfit_coefficients"]
    
    return da_reg


def process_variable(var, da, YEAR_RANGE):
    da_var = da[var]
    da_var["time"] = da_var["time"] - datetime.timedelta(days=1)

    # annual mean
    da_var = da_var.groupby('time.year').mean('time')
    
    # get years of interest
    iy = np.where((da_var["year"]>=YEAR_RANGE[0]) & (da_var["year"]<=YEAR_RANGE[1]))[0]
    da_var = da_var[iy,:,:]
        
    return da_var

def get_gdp(SHAPE_DIRECTORY, DATA_DIRECTORY):
    regs_shp = pd.read_csv(SHAPE_DIRECTORY + 'ne_10m_admin_0_countries_CSV.csv')  
    country_mask = xr.load_dataarray(SHAPE_DIRECTORY + 'countries_10m_cesm2Grid.nc')

    ## test things worked
    # regs_shp[regs_shp["ADMIN"]=="United States of America"]
    # a = country_mask.where(country_mask==154,np.nan)

    GDP_DIRECTORY = DATA_DIRECTORY + "gdp/"
    gdp_file = GDP_DIRECTORY + "iamc_db.csv"
    gdp_raw = pd.read_csv(gdp_file)
    gdp_raw.head()
    gdp = gdp_raw[["Region", "2040"]]    
    
    return gdp, regs_shp, country_mask


def get_land_mask(filepath, var):
    mask = xr.open_dataset(filepath)[var]
    mask = mask.where(mask >= 50, np.nan, drop=False)*0. + 1
    
    return mask


def get_population(filepath, da_grid):
    da_pop = xr.load_dataarray(filepath)
    da_pop.coords["lon"] = np.mod(da_pop["lon"], 360)
    da_pop = da_pop.sortby(da_pop.lon)
    print(da_pop.sum(("lat","lon"))) 
    
    # da_pop_regrid = np.zeros((len(da_all["lat"].values), len(da_all["lon"].values)))
    da_pop_regrid = xr.zeros_like(da_grid[0,0,:,:].squeeze())

    for ilat,lat in tqdm(enumerate(da_grid["lat"].values[:-1])):
        for ilon,lon in enumerate(da_grid["lon"].values):
            if ilon==len(da_grid["lon"].values)-1:
                eval_lon = 361.
            else:
                eval_lon = da_grid["lon"][ilon+1]
            ilat_pop = np.where((da_pop["lat"]>=da_grid["lat"][ilat]) & (da_pop["lat"]<da_grid["lat"][ilat+1]))[0]
            ilon_pop = np.where((da_pop["lon"]>=da_grid["lon"][ilon]) & (da_pop["lon"]<eval_lon))[0]

            da_pop_regrid[ilat,ilon] = da_pop[ilat_pop,ilon_pop].sum(("lat","lon"))
    
    print(da_pop_regrid.sum(("lat","lon")))     
    
    return da_pop_regrid
    
def get_control_data(DATA_DIRECTORY):
    da_all = None

    for ens in range(0,10):

        member_text = f'{ens+1:03}'
        print('ensemble member = ' + member_text)

        filename_ssp = DATA_DIRECTORY + 'b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + member_text + '.cam.h0.TREFHT.201501-206412.nc'
        das = xr.open_dataset(filename_ssp)
        das = process_variable("TREFHT", das, (2015,2069))

        if da_all is None:
            da_all = das
        else:
            da_all = xr.concat([da_all, das],dim="member")
            
    print(da_all.shape)       
    
    return da_all    
    
def get_data(DATA_DIRECTORY):
    da_all = None

    for ens in range(0,10):

        member_text = f'{ens+1:03}'
        print('ensemble member = ' + member_text)

        filename_ssp = DATA_DIRECTORY + 'b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.' + member_text + '.cam.h0.TREFHT.201501-206412.nc'
        das = xr.open_dataset(filename_ssp)
        das = process_variable("TREFHT", das, (2015,2034))

        if (ens == 7 or ens == 8):
            filename_arise = DATA_DIRECTORY + 'b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + member_text + '.cam.h0.TREFHT.203501-207012.nc'        
        else:
            filename_arise = DATA_DIRECTORY + 'b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.' + member_text + '.cam.h0.TREFHT.203501-206912.nc'
        daa = xr.open_dataset(filename_arise)
        daa = process_variable("TREFHT", daa, (2035,2069))

        da = xr.concat([das, daa], "year")

        if da_all is None:
            da_all = da
        else:
            da_all = xr.concat([da_all, da],dim="member")

    print(da_all.shape)       
    
    return da_all