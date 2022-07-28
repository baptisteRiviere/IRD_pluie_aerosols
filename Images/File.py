from NetCDF_Format import NetCDF_Format
from Nat_Format import Nat_Format
from Geotiff_Format import Geotiff_Format
from Bin_format import Bin_Format
import json
import numpy as np

class File:
        
    def __init__(self, path):
        self.path = path
        extensions = {  "nat":Nat_Format, 
                        "nc4":NetCDF_Format, 
                        "nc":NetCDF_Format, 
                        "tiff":Geotiff_Format, 
                        "tif":Geotiff_Format, 
                        "bin":Bin_Format
                        }
        try:
            self.format = extensions[path.split(".")[-1]]
        except KeyError:
            print("erreur : ce fichier n'est pas reconnu")
            
    def project(self,projection,attribute=1,out_path=False):
        """
        effectue le géoréférencement et la projection du fichier à partir des paramètres de projection

        Args:
            projection (dict) : dictionnaire contenant les clés suivantes
                area_id,description,proj_id,proj,ellps,datum,llx,lly,urx,ury,resolution
            attribute (string, int) : attribut à extraire du fichier (Default 1)
            out_path (string, bool) : nom du fichier en sortie (Default False)

        Return:
            img_proj (Image) : image projetée
        """
        image = self.format.project(self.path,projection,attribute,out_path)
        return image

    def getAttributes(self):
        """
        renvoie la liste d'attributs du fichier

        Return:
            (list) : liste des attributs
        """
        return self.format.getAttributes(self.path)

    def getResolution(self, attribute):
        """
        renvoie les résolutions spatiales en x et y du fichier

        Args:
            attribute (string, int) : attribut à extraire du fichier
        
        Return:
            (tuple) : résolution x et y
        """
        return self.format.getResolution(self.path,attribute)

    def getImage(self,attribute):
        """
        Renvoie l'image correspondant à un certain attribut du fichier

        Args:
            attribute (string, int) : attribut à extraire du fichier

        Return:
            (Image)
        """
        return self.format.getImage(self.path,attribute)

    def getAcqDates(self):
        """
        Renvoie les dates d'acquisition de l'image contenue dans le fichier 
        
        Return:
            start_date (datetime) : début de la période d'acquisition
            end_date (datetime) : fin de la période d'acquisition
        """
        return self.format.getAcqDates(self.path)
        
    def getPxlValue(self,lat,lon,attribute=1):
        """
        Renvoie la valeur du pixel correspondant à la latitude et longitude en entrée

        Args:
            lat (float) : latitude du pixel dont on demande la valeur
            lon (float) : longitude du pixel dont on demande la valeur
        """
        img = self.format.getImage(self.path, attribute=attribute)
        y,x = (np.abs(img.lats.T[0] - lat)).argmin(), (np.abs(img.lons[0] - lon)).argmin()
        return img.array[x][y]

if __name__ == "__main__":


    in_path = r'../data/IMERG/3B-DAY.MS.MRG.3IMERG.20200503-S000000-E235959.V06.nc4.nc4'
    attribute = "TB"
    out_path = r'../data/test.tiff'
    projection = json.load(open(r"../data/param_proj/param_guy.json", "r", encoding="utf-8"))
    
    file = File(in_path)
    img = file.project(projection,attribute)
    img.show()
    
   


    


