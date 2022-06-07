import json
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import cartopy

import georef as grf

class Image:
    # TODO : documentation
    
    def __init__(self, array, lons, lats, name="Unkown"):
        self.array = array
        self.name = name
        self.lons = lons
        self.lats = lats
    
    def show(self,save=False):
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
        
        arr_var = np.sqrt((s2 - s**2 / ns) / ns)
        img_var = Image(arr_var,self.lons,self.lats)

        return img_var

    def save(self,projection,out_path):
        grf.georef_image(self,projection,out_path)
        # TODO : il s'agit de la fonction project plutot, renvoie image
        # TODO : mettre en place save avec autre chose que georef_array qui n'existe plus
        












if __name__ == "__main__":
    in_path = r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat"
    #in_path = r"../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc"
    out_path = r"../data/test2.tiff"
    projection = json.load(open(r"tools/param.json", "r", encoding="utf-8"))
    canal = "IR_087"
    #canal = "TB"


    file = File(in_path)
    img = Image(file,canal,projection)
    img.project(out_path)
    #print(img.resolution)
