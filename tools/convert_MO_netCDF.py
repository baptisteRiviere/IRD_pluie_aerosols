from osgeo import gdal
import json
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt

import georef as grf

def convert_netCDF(src_path,out_path,proj_path,attribute):
    ds = gdal.Open("NETCDF:{0}:{1}".format(src_path, attribute))

    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()/100

    # TODO : améliorer ça
    driver = gdal.GetDriverByName('GTiff')
    new_ds = driver.Create("temporary.tiff", ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_UInt16)

    new_ds.SetGeoTransform(ds.GetGeoTransform())
    new_ds.SetProjection(ds.GetProjection())
    new_ds.WriteArray(arr)

    grf.georef_ds(new_ds,proj_path,out_path)


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
    out_path = r"../data/test_seg/SSMI.tiff"

    convert_netCDF(netcdf_path,out_path,proj_path,attribute)
    


