from NetCDF_Format import NetCDF_Format
from Nat_Format import Nat_Format

from Image import Image

class File:
    # TODO : documentation
    
    def __init__(self, path):
        self.path = path
        extensions = {"nat":Nat_Format, "nc":NetCDF_Format}
        self.format = extensions[path.split(".")[-1]]

    def project(self,out_path,projection,attribute):
        image = self.format.project(self.path,out_path,projection,attribute)
        return image

    def getAttributes(self):
        return self.format.getAttributes(self.path)

    def getResolution(self, attribute):
        return self.format.getResolution(self.path,attribute)

    def getImage(self,attribute):
        array,lons,lats = self.format.getArrayLonsLats(self.path,attribute)
        return Image(array,lons,lats)


if __name__ == "__main__":
    in_path = r'../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc'
    attribute = "TB"
    
    file = File(in_path)

    image = file.getImage(attribute)
    image.show()
