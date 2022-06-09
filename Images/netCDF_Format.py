from osgeo import gdal
import netCDF4 as nc
import numpy as np
import json
import matplotlib.pyplot as plt
import datetime
import os

from Image import Image
import georef as grf
from IFormatBehaviour import IFormat


class NetCDF_Format(IFormat):
    """
    Classe héritant de l'interface IFormat permettant de fournir un ensemble de méthodes pour un certain format de données
    Cet outil a été développé pour l'extraction des fichiers netCDF fournis par la NSIDC à l'URL ci-dessous
    afin d'en extraire la température de brillance
    https://nsidc.org/data/NSIDC-0630/versions/1
    
    L'architecture est inspirée du Strategy pattern
    """
    
    def project(in_path,out_path,projection,attribute):
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, attribute))
        f = nc.Dataset(in_path) # ouverture du fichier avec netCDF4 pour obtenir certaines informations
        scale_factor = f.variables[attribute].scale_factor
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()*scale_factor

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
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, attribute)) # ouverture du fichier avec gdal
        f = nc.Dataset(in_path) # ouverture du fichier avec netCDF4 pour obtenir certaines informations
        scale_factor = f.variables[attribute].scale_factor
        #print(f.variables["crs"].proj4text)
        array = ds.ReadAsArray()*scale_factor   # ouverture du fichier
        (x_offset, x_res, rot1, y_offset, rot2, y_res) = ds.GetGeoTransform()        
        lons = np.zeros(array.shape)    ; lats = np.zeros(array.shape)
        # TODO le calcul de lons lats est faux
        for x in range(len(array)):
            for y in range(len(array[0])):
                lons[y][x] = x_res * x + rot1 * y + x_offset
                lats[y][x] = rot2 * x + y_res * y + y_offset
        return Image(array,lons,lats)

        """
        import matplotlib.pyplot as plt
        plt.imshow(src_image.lons)
        plt.show()
        """
    
    def getTime(in_path,projection,attribute="TB_time"):
        img = NetCDF_Format.project(in_path,"temporary.tiff",projection,attribute)
        f = nc.Dataset(in_path)
        minutes = np.mean(img.array)
        days_offset = int(f.variables["time"][0])
        days_since = f.variables["time"].units.split(" ")[2]
        start_date = datetime.datetime.strptime(days_since, "%Y-%m-%d")
        end_date = start_date + datetime.timedelta(days=days_offset,minutes=minutes)
        return end_date

    

if __name__ == '__main__':

    proj_path = r"Images/param.json"
    netcdf_path = r'../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc'
    attribute = "TB"
    out_path = r"../data/test_SSMI.tiff"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    """
    netCDF_image = NetCDF_Format.project(netcdf_path,out_path,projection,attribute)
    plt.imshow(netCDF_image.array)
    plt.show()
    """

    print(NetCDF_Format.getImage(netcdf_path,"TB"))

    

    
    


