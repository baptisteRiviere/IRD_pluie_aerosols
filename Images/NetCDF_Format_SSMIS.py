from osgeo import gdal
import netCDF4 as nc
import numpy as np
import json
from datetime import datetime

from Image import Image
import georef as grf
from IFormatBehaviour import IFormat


class NetCDF_Format_SSMIS(IFormat):
    """
    Classe héritant de l'interface IFormat permettant de fournir un ensemble de méthodes pour un certain format de données
    Cet outil a été développé pour l'extraction des fichiers netCDF fournis par la NSIDC à l'URL ci-dessous
    afin d'en extraire la température de brillance
    https://nsidc.org/data/NSIDC-0630/versions/1
    
    L'architecture est inspirée du Strategy pattern
    """
    
    def project(in_path,projection,attribute=1,out_path=None):
        """
        effectue le géoréférencement et la projection du fichier à partir des paramètres de projection

        Args:
            in_path (string) : chemin d'accès au fichier à projeter
            projection (dict) : dictionnaire contenant les clés suivantes
                area_id,description,proj_id,proj,ellps,datum,llx,lly,urx,ury,resolution
            attribute (string, int) : attribut à extraire du fichier (Default 1)
            out_path (string, bool) : nom du fichier en sortie (Default False)

        Return:
            img_proj (Image) : image projetée
        """
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, attribute))
        f = nc.Dataset(in_path) # ouverture du fichier avec netCDF4 pour obtenir certaines informations
        try :
            scale_factor = f.variables[attribute].scale_factor
            fill_value = f.variables["TB"]._FillValue
        except AttributeError:
            scale_factor = 1 ; fill_value = None
        arr = ds.GetRasterBand(1).ReadAsArray()*scale_factor
        arr = np.where(arr==fill_value,np.NaN,arr)

        # TODO : améliorer les 8 lignes pro (permettent de prendre en compte le scale factor)
        driver = gdal.GetDriverByName('GTiff')
        new_ds = driver.Create(r"C:\Users\Baptiste\Documents\ENSG\stage\data\temporary.tiff", ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)

        new_ds.SetGeoTransform(ds.GetGeoTransform())
        new_ds.SetProjection(ds.GetProjection())
        new_ds.WriteArray(arr)
        
        new_array,new_lons,new_lats = grf.georef_ds(new_ds,projection,out_path)
        
        return Image(new_array,new_lons,new_lats)
        
    def getResolution(in_path,attribute):
        """
        renvoie les résolutions spatiales en x et y du fichier

        Args:
            in_path (string) : chemin d'accès au fichier à projeter
            attribute (string, int) : attribut à extraire du fichier
        
        Return:
            (tuple) : résolution x et y
        """
        ds = gdal.Open("NETCDF:{0}:{1}".format(in_path, attribute))
        (_, x_res, _, _, _, y_res) = ds.GetGeoTransform()
        return (x_res,-y_res)
    
    def getAttributes(in_path):
        """
        renvoie la liste d'attributs du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            (list) : liste des attributs
        """
        ds = nc.Dataset(in_path,'r')
        return list(ds.variables.keys())

    def getImage(in_path,attribute):
        print("la fonction getImage n'est pas fonctionnelle pour le format netCDF_Format_SSMIS")
        return None
        
    def getAcqDates(in_path):
        """
        Renvoie les dates d'acquisition de l'image contenue dans le fichier 

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            start_date (datetime) : début de la période d'acquisition
            end_date (datetime) : fin de la période d'acquisition
        """
        format='%Y-%m-%dT%H:%M:%S.%f%z'
        ds = nc.Dataset(in_path)
        start_date = datetime.strptime(ds.time_coverage_start, format)
        end_date = datetime.strptime(ds.time_coverage_end, format)
        return start_date,end_date

if __name__ == '__main__':

    proj_path = r"../data/param_proj/param_guy.json"
    netcdf_path = r'../data/SSMIS/NSIDC-0630-EASE2_N3.125km-F17_SSMIS-2020364-91V-E-SIR-CSU-v1.5.nc'
    attribute = "TB"
    out_path = r"../data/test_SSMI.tiff"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    img = NetCDF_Format_SSMIS.project(netcdf_path,projection,attribute)
    img.show()

    print(NetCDF_Format_SSMIS.getAcqDates(netcdf_path))

    