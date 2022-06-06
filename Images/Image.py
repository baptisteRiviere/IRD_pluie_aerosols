import json
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

class Image:
    # TODO : documentation
    
    def __init__(self, array, lons, lats, name="Unkown"):
        self.array = array
        self.name = name
        self.lons = lons
        self.lats = lats
    
    def show(self):
        # TODO : test unitaire
        plt.imshow(self.array)
        plt.show()

    def computeVar(self):
        # TODO : test unitaire
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

    def save():
        # TODO : sauvegarder un geotiff, voir quel attribut ajouter
        return None












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
