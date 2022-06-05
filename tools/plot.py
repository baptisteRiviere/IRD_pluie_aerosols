import matplotlib.pyplot as plt
import cartopy
import numpy as np


features=[cartopy.feature.OCEAN,cartopy.feature.RIVERS,cartopy.feature.BORDERS],


def plot(array2project,filename,type_proj,bounds=[-180,180,-90,90],features=[],coastline=True):
    ax = plt.axes(projection=type_proj) # projection
    for feature in features: # add features like ocean, rivers...
        ax.add_feature(feature)
    if coastline: # add coastline
        ax.coastlines()
    levels = np.linspace(0.0, 1.0) # set limits of the colorbar
    ax.set_extent(bounds, crs=type_proj) # zoom over a specific region and set crs of the given coordinates
    cbar = plt.contourf( # define colorbar and apply array to project to the plot
        lons, 
        lats, 
        array2project, 
        60, 
        levels=levels, 
        cmap = 'gist_rainbow_r', 
        transform=type_proj
        )
    plt.colorbar(cbar, orientation='vertical') # add colorbar to the plot
    plt.plot(Lon, Lat, markersize=3, marker='o', color='red')
    plt.savefig(filename) # save figure
    plt.show() # display the plot