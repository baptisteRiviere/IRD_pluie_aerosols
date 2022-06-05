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
        return None

    def getResolution(self, canal):
        return self.format.getResolution(self.path,canal)

