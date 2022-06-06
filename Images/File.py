from NetCDF_Format import NetCDF_Format
from Nat_Format import Nat_Format
from Geotiff_Format import Geotiff_Format
import json

from Image import Image

class File:
    # TODO : documentation
    
    def __init__(self, path):
        try :
            self.path = path
            extensions = {"nat":Nat_Format, "nc":NetCDF_Format, "tiff":Geotiff_Format, "tif":Geotiff_Format}
            self.format = extensions[path.split(".")[-1]]
        except KeyError :
            print("Error: cette extension n'est pas reconnue")

    def project(self,out_path,projection,attribute):
        image = self.format.project(self.path,out_path,projection,attribute)
        return image

    def getAttributes(self):
        return self.format.getAttributes(self.path)

    def getResolution(self, attribute):
        return self.format.getResolution(self.path,attribute)

    def getImage(self,attribute):
        return self.format.getImage(self.path,attribute)
         


if __name__ == "__main__":
    
    in_path = r'../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc'
    attribute = "TB"
    """
    in_path = r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat"
    attribute = 'IR_087'
    
    in_path = r'../data/Results/IR_georef_test.tiff'
    attribute = 1
    """
    out_path = r'../data/test.tiff'
    projection = json.load(open(r"tools/param_guy.json", "r", encoding="utf-8"))
    file = File(in_path)

    image_proj = file.project(out_path,projection,attribute)
    image_proj.show()
