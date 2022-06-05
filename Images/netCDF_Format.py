from osgeo import gdal
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import json
import geopy.distance

import georef as grf
from IFormatBehaviour import IFormat



class NetCDF_Format(IFormat):
    
    def project(in_path,out_path,projection,canal):
        convert_netCDF(in_path,out_path,projection,canal)

    def getResolution(in_path,canal,projection):
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, canal))
        (_, x_res, _, _, _, y_res) = ds.GetGeoTransform()
        return (x_res,-y_res)
    
    def getCanals(in_path):
        return None

def convert_netCDF(src_path,out_path,projection,attribute):
    ds = gdal.Open("NETCDF:{0}:{1}".format(src_path, attribute))

    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()/100    # TODO : trouver moyen suppr ça

    # TODO : améliorer ça
    driver = gdal.GetDriverByName('GTiff')
    new_ds = driver.Create("temporary.tiff", ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_UInt16)

    new_ds.SetGeoTransform(ds.GetGeoTransform())
    new_ds.SetProjection(ds.GetProjection())
    new_ds.WriteArray(arr)

    grf.georef_ds(new_ds,projection,out_path)


def get_infos(netcdf_path):
    ds = nc.Dataset(netcdf_path)["TB"][:]
    arr = np.array(ds[:],dtype=int)
    #arr = np.array(ds["TB"][:],dtype=int)
    plt.imshow(arr)
    plt.show()    
    #print(dates)   2021-12-30 00:00:00  1200/60 = 20h

if __name__ == '__main__':

    proj_path = r"tools/param.json"
    netcdf_path = r'../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc'
    attribute = "TB"
    out_path = r"../data/test_SSMI.tiff"

    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    #convert_netCDF(netcdf_path,out_path,projection,attribute)

    print(NetCDF_Format.getResolution(netcdf_path,attribute,projection))
    


