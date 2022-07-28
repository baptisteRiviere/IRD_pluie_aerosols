from osgeo import gdal
import netCDF4 as nc
import numpy as np
import json
import datetime

from Image import Image
import georef as grf
from IFormatBehaviour import IFormat


class NetCDF_Format_IMERG(IFormat):
    """
    Classe héritant de l'interface IFormat permettant de fournir un ensemble de méthodes pour un certain format de données
    Cet outil a été développé pour l'extraction des fichiers netCDF4 fournis par la NSIDC à l'URL ci-dessous
    
    L'architecture est inspirée du Strategy pattern
    """
    
    def project(in_path,projection,attribute=1,out_path=False):
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
        src_image = NetCDF_Format_IMERG.getImage(in_path,attribute)
        new_array, new_lons, new_lats = grf.georef_image(src_image,projection,out_path)
        return Image(new_array, new_lons, new_lats)
        
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
        f = nc.Dataset(in_path) 
        return list(f.variables.keys())

    def getImage(in_path,attribute):
        """
        Renvoie l'image correspondant à un certain attribut du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
            attribute (string, int) : attribut à extraire du fichier

        Return:
            (Image)
        """
        f = nc.Dataset(in_path)
        array = f.variables[attribute][:][0]
        (nb_rows,nb_cols) = np.shape(array)
        lon = np.array(f.variables["lon"][:]) ; lat = np.array(f.variables["lat"][:])
        lons = np.tile(lon, (nb_cols,1)).T
        lats = np.tile(lat, (nb_rows,1))     
        return Image(array,lons,lats)
        
        
    def getAcqDates(in_path):
        """
        Renvoie les dates d'acquisition de l'image contenue dans le fichier 

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            start_date (datetime) : début de la période d'acquisition
            end_date (datetime) : fin de la période d'acquisition
        """
        f = nc.Dataset(in_path) 
        unit_date = datetime.datetime.strptime(f.variables["time"].units,"days since %Y-%m-%d %H:%M:%SZ")
        acq_date = unit_date + datetime.timedelta(days=f.variables["time"][:][0])
        start_date = acq_date.replace(tzinfo=datetime.timezone.utc)
        end_date = start_date + datetime.timedelta(days=1)
        return start_date,end_date

if __name__ == '__main__':

    proj_path = r"../data/param_proj/param_guy.json"
    netcdf_path = r"..\data\IMERG\3B-DAY.MS.MRG.3IMERG.20200503-S000000-E235959.V06.nc4.nc4"
    attribute = "HQprecipitation"
    out_path = r"../data/test_SSMI.tiff"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

