import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import cartopy

import georef as grf

class Image:
    """
    Image géoréférencée, elle est composée de trois matrices :
        array contient l'information
        lons et lats contiennent les latitudes et longitudes des pixels
    """
    
    def __init__(self, array, lons, lats, projection=None):
        self.array = array
        self.lons = lons
        self.lats = lats
        self.projection = projection
    
    def show(self,simple=False,savefig=False):
        """
        Permet de visualiser l'image avec une certaine projection

        Args :
            simple (Bool) : si vrai, ne montre que l'image sans projection
            savefig (Bool - string) : si non faux, enregistre la figure avec le chemin savefig
        """
        if simple:
            plt.imshow(self.array)
            plt.show()
        else:
            crs = cartopy.crs.PlateCarree()
            ax = plt.axes(projection=crs)
            ax.add_feature(cartopy.feature.BORDERS) # add borders
            ax.coastlines()
            cbar = plt.contourf(self.lons, self.lats, self.array, 60, cmap = 'gist_rainbow_r', transform=crs)
            lon_min,lon_max,lat_min,lat_max = np.min(self.lons),np.max(self.lons),np.min(self.lats),np.max(self.lats)
            ax.set_extent([lon_min,lon_max,lat_min,lat_max], crs=crs) # zoom over a specific region and set crs of the given coordinates
            plt.colorbar(cbar, orientation='vertical') # add colorbar to the plot
            plt.show()
        if savefig:
            plt.savefig(savefig, dpi=500)

    def computeVar(self):
        """
        permet de calculer la variance de l'image
        """
        img_var = Image(compute_var(self.array),self.lons,self.lats,self.proj)
        return img_var

    def save(self,projection,out_path):
        """
        Permet d'enregistrer la figure en format tif 

        Args:
            projection (dict) : paramètres de projection
            out_path (string) : chemin d'enregistrement de l'image
        """
        grf.georef_image(self,projection,out_path)

def compute_var(array):
    """
    mesure la variance de l'image à partir d'une série de convolutions

    Args:
        array (np.array) : matrice dont on calcule la variance

    Returns:
        array_var (np.array) : matrice de variance
    """
    array2 = array**2
    ones = np.ones(array.shape)
    
    kernel = np.ones((3,3))
    s = signal.convolve2d(array, kernel, mode="same")
    s2 = signal.convolve2d(array2, kernel, mode="same")
    ns = signal.convolve2d(ones, kernel, mode="same")
    
    array_var = np.sqrt(abs((s2 - s**2 / ns) / ns)) # TODO : enlever abs si possible
    return array_var
