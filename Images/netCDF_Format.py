from osgeo import gdal
import netCDF4 as nc
import numpy as np
import json
import matplotlib.pyplot as plt
import datetime

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
        try :
            scale_factor = f.variables[attribute].scale_factor
        except AttributeError:
            scale_factor = 1
        arr = ds.GetRasterBand(1).ReadAsArray()*scale_factor

        # TODO : améliorer les 8 lignes pro (permettent de prendre en compte le scale factor)
        driver = gdal.GetDriverByName('GTiff')
        new_ds = driver.Create("temporary.tiff", ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)

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
        """
        non fonctionnel
        """
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, attribute)) # ouverture du fichier avec gdal
        f = nc.Dataset(in_path) # ouverture du fichier avec netCDF4 pour obtenir certaines informations
        scale_factor = f.variables[attribute].scale_factor
        srcSRS = f.variables["crs"].proj4text
        options = gdal.WarpOptions(
            format="GTiff",
            srcSRS=srcSRS,
            dstSRS="EPSG:4326"
        ) # TODO : changer srs
        ds_proj = gdal.Warp(r"test.tiff", ds, options=options)
        array,lons,lats = grf.getArrayLonsLats(ds_proj)
        return Image(array*scale_factor,lons,lats)
        
        
    def getAcqDates(in_path,format='%Y-%m-%dT%H:%M:%S.%f%z'):
        ds = nc.Dataset(in_path)
        start_date = datetime.datetime.strptime(ds.time_coverage_start, format)
        end_date = datetime.datetime.strptime(ds.time_coverage_end, format)
        return start_date,end_date

if __name__ == '__main__':

    proj_path = r"Images/param_test.json"
    netcdf_path = r'../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2020334-91V-E-GRD-CSU-v1.5.nc'
    attribute = "TB"
    out_path = r"../data/test_SSMI.tiff"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    start_dt, end_dt = NetCDF_Format.getAcqDates(netcdf_path)
    #print(start_dt)

    img = NetCDF_Format.project(netcdf_path,"test.tiff",projection,"TB_num_samples")
    img.show()

    
