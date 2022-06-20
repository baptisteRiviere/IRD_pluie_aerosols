import json
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import cartopy

import georef as grf

class Image:
    # TODO : documentation
    
    def __init__(self, array, lons, lats, proj=None, date=None):
        self.array = array
        self.lons = lons
        self.lats = lats
        self.proj = proj
        self.date = date
    
    def show(self,simple=False):
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

    def computeVar(self):
        im = self.array
        im2 = im**2
        ones = np.ones(im.shape)
        
        kernel = np.ones((3,3))
        s = signal.convolve2d(im, kernel, mode="same")
        s2 = signal.convolve2d(im2, kernel, mode="same")
        ns = signal.convolve2d(ones, kernel, mode="same")
        
        arr_var = np.sqrt(abs((s2 - s**2 / ns) / ns)) # TODO : enlever abs si possible
        
        img_var = Image(arr_var,self.lons,self.lats,self.proj)

        return img_var

    def save(self,projection,out_path):
        grf.georef_image(self,projection,out_path)
        # TODO : il s'agit de la fonction project plutot, renvoie image
        # TODO : mettre en place save avec autre chose que georef_array qui n'existe plus
        












if __name__ == "__main__":
    in_path = r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat"
    out_path = r"../data/test2.tiff"
    projection = json.load(open(r"tools/param.json", "r", encoding="utf-8"))
    canal = "IR_087"

