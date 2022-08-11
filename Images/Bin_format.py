import numpy as np
from satpy import Scene
import numpy.ma as ma
import json 
from datetime import datetime, timedelta, timezone, tzinfo

from Image import Image
import georef as grf
from IFormatBehaviour import IFormat

class Bin_Format(IFormat):
    """
    Classe héritant de l'interface IFormat permettant de fournir un ensemble de méthodes pour un certain format de données
    Cet outil a été développé pour l'extraction des fichiers bin donnant accès aux données VIIRS 
    Les méthodes ne fonctionnent que pour ce type de fichier bin 
    Les valeurs dans ce code viennent du readme associé au téléchargement de ces données
    
    L'architecture est inspirée du Strategy pattern
    """

    def project(in_path,projection,attribute=None,out_path=None):
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
        src_image = Bin_Format.getImage(in_path,attribute)
        new_array, new_lons, new_lats = grf.georef_image(src_image,projection,out_path)
        #aot_edr = ma.masked_where((new_array.any() > 5) or (new_array.any() < -100), new_array) # mask aberrant values
        return Image(new_array, new_lons, new_lats)

    def getResolution(in_path,attribute=None):
        """
        renvoie les résolutions spatiales en x et y du fichier

        Args:
            in_path (string) : chemin d'accès au fichier à projeter
            attribute (string, int) : attribut à extraire du fichier
        
        Return:
            (tuple) : résolution x et y
        """
        return (0.25,0.25)
        
    def getAttributes(in_path):
        """
        renvoie la liste d'attributs du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            (list) : liste des attributs
        """
        return None

    def getImage(in_path, attribute=None):
        """
        Renvoie l'image correspondant à un certain attribut du fichier
        inspiré du code de Laura Orgambide

        Args:
            in_path (string) : chemin d'accès au fichier
            attribute (string, int) : attribut à extraire du fichier
                
        Return:
            (Image)
        """
        imnp = np.fromfile(in_path, dtype = np.single)
        aot_edr = np.reshape(imnp, [int(len(imnp)/1440), 1440])[:720, :1440]
        #aot_edr = ma.masked_where(aot_edr > 5, aot_edr) # mask aberrant values
        aot_edr = ma.masked_where(aot_edr < -100, aot_edr) # mask invalid values
        resolution = Bin_Format.getResolution(in_path)[0]
        minLon,maxLon = -179.875,179.875 
        minLat,maxLat = -89.875,89.875
        
        # create an horizontal matrix between -180 to 180 each 0.25
        lon = np.arange(minLon, maxLon+0.25, resolution) 
        lons = np.tile(lon, (720,1)) # clone columns 
        # create an vertical matrix between -90 to 90 each 0.25
        lat = np.arange(minLat, maxLat+0.25, resolution)[:, np.newaxis] 
        lats = np.tile(lat, (1,1440)) # clone lines

        return Image(aot_edr,lons,lats)

    def getAcqDates(in_path):
        """
        Renvoie les dates d'acquisition de l'image contenue dans le fichier 

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            start_date (datetime) : début de la période d'acquisition
            end_date (datetime) : fin de la période d'acquisition
        """
        start_date = datetime.strptime(in_path.split(".high")[0][-8:],'%Y%m%d').replace(tzinfo=timezone.utc)
        end_date = (start_date + timedelta(days=1)).replace(tzinfo=timezone.utc)
        return start_date,end_date

if __name__ == '__main__':
    nat_path = r"../data/AOT/npp_aot550_edr_gridded_0.25_20200503.high.bin"
    out_path = r"../data/test.tiff"
    proj_path = r"../data/param_proj/param_guy.json"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    img = Bin_Format.project(nat_path,projection)
    print(img.array)
    img.show()
    