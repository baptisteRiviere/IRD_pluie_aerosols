import numpy as np
from osgeo import gdal
import georef as grf
import json as json
from Image import Image
import numpy.ma as ma

class Geotiff_Format:
    """
    Classe héritant de l'interface IFormat permettant de fournir un ensemble de méthodes pour un certain format de données
    Cet outil a été développé pour l'extraction des fichiers geotiffs (.tiff)
    
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
        src_image = Geotiff_Format.getImage(in_path,attribute)
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
        ds = gdal.Open(in_path)
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
        ds = gdal.Open(in_path)
        return [i+1 for i in range(ds.RasterCount)]

    def getImage(in_path,attribute):
        """
        Renvoie l'image correspondant à un certain attribut du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
            attribute (string, int) : attribut à extraire du fichier

        Return:
            (Image)
        """
        ds = gdal.Open(in_path)
        (x_offset, x_res, rot1, y_offset, rot2, y_res) = ds.GetGeoTransform()
        array = ds.GetRasterBand(attribute).ReadAsArray()
        masked_array = ma.array(array, mask=np.where(array==0,1,0))
        lons = np.zeros(array.shape)    ; lats = np.zeros(array.shape)
        for y in range(len(array)):
            for x in range(len(array[0])):
                lons[y][x] = x_res * x + rot1 * y + x_offset
                lats[y][x] = rot2 * x + y_res * y + y_offset
        return Image(masked_array,lons,lats)
        


if __name__ == '__main__':

    geotiff_path = r'../data/temporary.tiff'
    attribute = 1
    
    proj_path = r"../data/param_proj/param_guy.json"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    out_path = r"../data/test.tiff"

    print(Geotiff_Format.project(geotiff_path,projection))
