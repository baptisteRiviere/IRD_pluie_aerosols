from NetCDF_Format_IMERG import NetCDF_Format_IMERG
from NetCDF_Format_Sentinel5 import NetCDF_Format_S5
from NetCDF_Format_SSMIS import NetCDF_Format_SSMIS
from IFormatBehaviour import IFormat
import json

from Image import Image

def get_sub_format(path):
    sub_format = {  "S5P" : NetCDF_Format_S5,
                    "NSIDC" : NetCDF_Format_SSMIS,
                    "IMERG" : NetCDF_Format_IMERG
    }
    for key in sub_format.keys():
        if key in path.split("/")[-1]:
            return sub_format[key]

class NetCDF_Format(IFormat):
    # TODO : documentation
    
    def project(in_path,projection,attribute=1,out_path=False):
        sub_format = get_sub_format(in_path)
        image = sub_format.project(in_path,projection,attribute,out_path)
        return image

    def getAttributes(in_path):
        sub_format = get_sub_format(in_path)
        return sub_format.getAttributes(in_path)

    def getResolution(in_path, attribute):
        sub_format = get_sub_format(in_path)
        return sub_format.getResolution(in_path,attribute)

    def getImage(in_path,attribute):
        sub_format = get_sub_format(in_path)
        return sub_format.getImage(in_path,attribute)

    def getAcqDates(in_path):
        sub_format = get_sub_format(in_path)
        return sub_format.getAcqDates(in_path)
        
    def getValue(in_path,lat,lon):
        sub_format = get_sub_format(in_path)
        return sub_format.getValue(in_path,lat,lon)

