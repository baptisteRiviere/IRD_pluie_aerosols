import json

from NetCDF_Format import NetCDF_Format
from Nat_Format import Nat_Format

from File import File

class Image:
    
    def __init__(self, file, canal, projection):
        self.file = file
        self.canal = canal
        self.projection = projection
        self.resolution = file.getResolution(canal)

    def project(self,out_path):
        self.file.project(out_path,self.projection,self.canal)

    def getArray(self, sound):
        return None

    def getLonsLats(self, sound):
        return None
    
    def plot(self):
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
