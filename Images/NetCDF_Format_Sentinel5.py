from osgeo import gdal
import netCDF4 as nc
import numpy as np
import json
import datetime

from Image import Image
import georef as grf
from IFormatBehaviour import IFormat


class NetCDF_Format_S5(IFormat):
    """
    Classe héritant de l'interface IFormat permettant de fournir un ensemble de méthodes pour un certain format de données
    Cet outil a été développé pour l'extraction des fichiers AOT mesurés par sentinel5
    
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
        src_image = NetCDF_Format_S5.getImage(in_path,attribute)
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
        return list(f.groups["PRODUCT"].variables.keys())

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
        img = f.groups["PRODUCT"].variables[attribute][:][0]
        lons = f.groups["PRODUCT"].variables["longitude"][:][0]
        lats = f.groups["PRODUCT"].variables["latitude"][:][0]
        return Image(img,lons,lats)
        
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
        delta_time = f.groups["PRODUCT"].variables["delta_time"]
        unit_date = datetime.datetime.strptime(delta_time.units,"milliseconds since %Y-%m-%d %H:%M:%S")
        min_time,max_time = int(np.min(delta_time[:])),int(np.max(delta_time[:]))
        start_date = (unit_date + datetime.timedelta(milliseconds=min_time)).replace(tzinfo=datetime.timezone.utc)
        end_date = (unit_date + datetime.timedelta(milliseconds=max_time)).replace(tzinfo=datetime.timezone.utc)
        return start_date,end_date

if __name__ == '__main__':

    proj_path = r"../data/param_proj/param_guy.json"
    netcdf_path = r"../data/Sentinel5_AOT/S5P_OFFL_L2__AER_AI_20201205T150902_20201205T165032_16305_01_010400_20201207T045523.nc"
    attribute = "aerosol_index_354_388"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    img = NetCDF_Format_S5.project(netcdf_path,projection,attribute)
    img.show()
    