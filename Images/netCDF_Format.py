from osgeo import gdal
import netCDF4 as nc
import numpy as np
import json
from Image import Image

import georef as grf
from IFormatBehaviour import IFormat


class NetCDF_Format(IFormat):
    # TODO : documentation
    
    def project(in_path,out_path,projection,attribute):
        """
        # TODO : documentation et voir si on peut utiliser georef_image
        src_image = NetCDF_Format.getImage(in_path,attribute)
        new_array, new_lons, new_lats = grf.georef_image(src_image,projection,out_path)
        return Image(new_array, new_lons, new_lats)
        """
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, attribute))

        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()/100    # TODO : trouver moyen suppr ça

        # TODO : améliorer ça
        driver = gdal.GetDriverByName('GTiff')
        new_ds = driver.Create("temporary.tiff", ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_UInt16)

        new_ds.SetGeoTransform(ds.GetGeoTransform())
        new_ds.SetProjection(ds.GetProjection())
        new_ds.WriteArray(arr)

        new_array,new_lons,new_lats = grf.georef_ds(new_ds,projection,out_path)
        return Image(new_array,new_lons,new_lats)
        
        
    def getResolution(in_path,attribute):
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, attribute))
        (_, x_res, _, _, _, y_res) = ds.GetGeoTransform()
        return (x_res,-y_res)
    
    def getAttributes(in_path):
        ds = nc.Dataset(in_path,'r')
        return ds.variables.keys()

    def getImage(in_path,attribute):
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, attribute))
        (x_offset, x_res, rot1, y_offset, rot2, y_res) = ds.GetGeoTransform()
        array = ds.ReadAsArray()/100 # TODO : passer ça en attribut et utiliser fct georef
        lons = np.zeros(array.shape)    ; lats = np.zeros(array.shape)
        for x in range(len(array)):
            for y in range(len(array[0])):
                lons[y][x] = x_res * x + rot1 * y + x_offset
                lats[y][x] = rot2 * x + y_res * y + y_offset
        return Image(array,lons,lats)
    

if __name__ == '__main__':

    proj_path = r"tools/param.json"
    netcdf_path = r'../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc'
    attribute = "TB"
    out_path = r"../data/test_SSMI.tiff"

    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    array,lons,lats = NetCDF_Format.getArrayLonsLats(netcdf_path,attribute)
    print(array)

    
    


