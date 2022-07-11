from NetCDF_Format import NetCDF_Format
from Nat_Format import Nat_Format
from Geotiff_Format import Geotiff_Format
from Bin_format import Bin_Format
import json

from Image import Image

class File:
    # TODO : documentation
    
    def __init__(self, path):
        self.path = path
        extensions = {"nat":Nat_Format, "nc":NetCDF_Format, "tiff":Geotiff_Format, "tif":Geotiff_Format, "bin":Bin_Format}
        self.format = extensions[path.split(".")[-1]]

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
        
    def getValue(self,lat,lon):
        return self.format.getValue(self.path,lat,lon)


if __name__ == "__main__":
    
    in_path = r'../data/SSMI/download_dec_2020/NSIDC-0630-EASE2_T3.125km-F17_SSMIS-2020359-91H-D-SIR-CSU-v1.5.nc'
    attribute = "TB"
    out_path = r'../data/test.tiff'
    projection = json.load(open(r"../data/param_proj/param_guy.json", "r", encoding="utf-8"))
    """
    file = File(in_path)
    dates = file.getAcqDates()
    print(dates)
    img = file.project(projection,attribute)
    img.show()
    """


    


