from NetCDF_Format import NetCDF_Format
from Nat_Format import Nat_Format
from Geotiff_Format import Geotiff_Format
from Bin_format import Bin_Format
import json
import numpy as np

class File:
    # TODO : documentation
    
    def __init__(self, path):
        self.path = path
        extensions = {  "nat":Nat_Format, 
                        "nc4":NetCDF_Format, 
                        "nc":NetCDF_Format, 
                        "tiff":Geotiff_Format, 
                        "tif":Geotiff_Format, 
                        "bin":Bin_Format
                        }
        try:
            self.format = extensions[path.split(".")[-1]]
        except KeyError:
            print("erreur : ce fichier n'est pas reconnu")
            
    def project(self,projection,attribute=1,out_path=False):
        image = self.format.project(self.path,projection,attribute,out_path)
        return image

    def getAttributes(self):
        return self.format.getAttributes(self.path)

    def getResolution(self, attribute):
        return self.format.getResolution(self.path,attribute)

    def getImage(self,attribute):
        return self.format.getImage(self.path,attribute)

    def getAcqDates(self):
        return self.format.getAcqDates(self.path)
        
    def getPxlValue(self,lat,lon):
        img = self.format.getImage(in_path, attribute=None)
        y,x = (np.abs(img.lats.T[0] - lat)).argmin(), (np.abs(img.lons[0] - lon)).argmin()
        return img.array[x][y]

if __name__ == "__main__":


    in_path = r'../data/IMERG/3B-DAY.MS.MRG.3IMERG.20200503-S000000-E235959.V06.nc4.nc4'
    attribute = "TB"
    out_path = r'../data/test.tiff'
    projection = json.load(open(r"../data/param_proj/param_guy.json", "r", encoding="utf-8"))
    
    file = File(in_path)
    img = file.project(projection,attribute)
    img.show()
    
   


    


