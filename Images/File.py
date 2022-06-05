from NetCDF_Format import NetCDF_Format
from Nat_Format import Nat_Format

class File:
    
    def __init__(self, path):
        self.path = path
        extensions = {"nat":Nat_Format, "nc":NetCDF_Format}
        self.format = extensions[path.split(".")[-1]]

    def project(self,out_path,projection,canal):
        self.format.project(self.path,out_path,projection,canal)

    def getCanals(self):
        return self.format.getCanals(self.path)

    def getResolution(self, canal):
        return self.format.getResolution(self.path,canal)


if __name__ == "__main__":
    in_path = r'../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc'
    attribute = "TB"
    
    file = File(in_path)

    print(file.getCanals())
