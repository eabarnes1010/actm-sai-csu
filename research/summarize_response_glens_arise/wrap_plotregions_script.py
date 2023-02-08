''' wrap_plotregions_script
Make plots of input region(s) on a map.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''

from icecream import ic
import sys

import numpy as np
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import region_library as rlib

# Pre-defined useful sets of regions
boxIPCC = (
    rlib.AlaskaNorthwestCanada(), rlib.CentralAsia(), rlib.CanadaGreenlandIceland(), rlib.CentralNorthAmerica(), rlib.EastAfrica(), rlib.EastAsia(), rlib.EastNorthAmerica(),
    rlib.NorthAsia(), rlib.NorthAustralia(), rlib.NortheastBrazil(), rlib.SouthAustraliaNewZealand(), rlib.SoutheastAsia(), rlib.TibetanPlateau(),
    rlib.WestAsia(), rlib.WestNorthAmerica(), rlib.Antarctica(), rlib.Arctic(),
    rlib.PacificIslandsRegion2(), rlib.PacificIslandsRegion3(), rlib.SouthernTropicalPacific(), rlib.WestIndianOcean()
    ) # IPCC-defined box-shaped regions
boxMerCrossIPCC = (
    rlib.SouthEuropeMediterranean(), rlib.SouthernAfrica(), rlib.Sahara(), rlib.WestAfrica()
    ) # IPCC-defined box-shaped regions that cross the Prime Meridian
polyIPCC = (
    rlib.Amazon(), rlib.CentralAmericaMexico(), rlib.SmallIslandsRegionsCaribbean(),
    rlib.SouthAsia(),rlib.SoutheasternSouthAmerica(), rlib.WestCoastSouthAmerica()
    ) # IPCC-defined non-box polygonal regions
polyMerCrossIPCC = (
    rlib.CentralEurope(),rlib.NorthEurope()
    ) # IPCC-defined non-box polygonal regions that cross the prime meridian
insets = (rlib.Sahara(),rlib.NorthEurope(),rlib.SoutheasternSouthAmerica(),rlib.SouthAsia(),
          rlib.SouthernAfrica(),rlib.WestNorthAmerica(),rlib.EastAsia(),
          rlib.CentralAmericaMexico(),rlib.SoutheastAsia(),rlib.NorthAtlanticWarmingHole(),
          rlib.AustralianContinent())
HueholtEtAl2023Regions = (
    rlib.Amazon(), rlib.AlaskaNorthwestCanada(), rlib.Arctic(), rlib.EastAfricaAyugiEtAl(),
    rlib.NorthEurope(), rlib.GeenEtAl20AsianMonsoonRegion(), rlib.Antarctica(),
    ) # Most regions used in Hueholt et al. 2023

# Set region(s) to be plotted
regionsToPlot = HueholtEtAl2023Regions

# Plot region(s)
# Repeat the same colors a bunch of times to plot each region.
# (There are probably more flexible ways to write this and generate a random
# color each time, but there's not really a reason to get fancy here!)
colors = (
    'viridis', 'magma', 'Purples_r', 'Greens_r', 'Greys_r', 'Oranges_r', 'spring', 'winter', 'cool', 'viridis','magma','Purples_r', 'Greens_r', 'Greys_r', 'Oranges_r', 'spring', 'winter', 'cool', 'viridis', 'magma', 'Purples_r', 'Greens_r', 'Greys_r', 'Oranges_r', 'spring', 'winter', 'cool', 'viridis', 'magma', 'Purples_r', 'Greens_r', 'Greys_r', 'Oranges_r', 'spring', 'winter', 'cool', 'viridis', 'magma', 'Purples_r', 'Greens_r', 'Greys_r', 'Oranges_r', 'spring', 'winter', 'cool'
    )
CL = 0.
mapProj = cartopy.crs.EqualEarth(central_longitude = CL)
fig = plt.figure(figsize=(12, 2.73*2))
ax = plt.subplot(1, 1, 1, projection=mapProj) #nrow ncol index

for rc,reg in enumerate(regionsToPlot):
    ic(reg)
    fig,ax = rlib.plot_region(reg, colors[rc], fig, ax)
# plt.title("WG1-AR5 IPCC regions")
plt.savefig(
    '/Users/dhueholt/Documents/GLENS_fig/20230207_moreDistill/HueholtEtAl2023Reg.png',
    dpi=400)
