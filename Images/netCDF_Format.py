from NetCDF_Format_IMERG import NetCDF_Format_IMERG
from NetCDF_Format_Sentinel5 import NetCDF_Format_S5
from NetCDF_Format_SSMIS import NetCDF_Format_SSMIS
from IFormatBehaviour import IFormat

def get_sub_format(path):
    """
    renvoie la sous classe netCDF correspondant aux images correspondantes
    """
    sub_format = {  "S5P" : NetCDF_Format_S5,
                    "NSIDC" : NetCDF_Format_SSMIS,
                    "IMERG" : NetCDF_Format_IMERG
    }
    for key in sub_format.keys():
        if key in path.split("/")[-1]:
            return sub_format[key]

class NetCDF_Format(IFormat):
    
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
        sub_format = get_sub_format(in_path)
        image = sub_format.project(in_path,projection,attribute,out_path)
        return image

    def getAttributes(in_path):
        """
        renvoie la liste d'attributs du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            (list) : liste des attributs
        """
        sub_format = get_sub_format(in_path)
        return sub_format.getAttributes(in_path)

    def getResolution(in_path, attribute):
        """
        renvoie les résolutions spatiales en x et y du fichier

        Args:
            in_path (string) : chemin d'accès au fichier à projeter
            attribute (string, int) : attribut à extraire du fichier
        
        Return:
            (tuple) : résolution x et y
        """
        sub_format = get_sub_format(in_path)
        return sub_format.getResolution(in_path,attribute)

    def getImage(in_path,attribute):
        """
        renvoie les résolutions spatiales en x et y du fichier

        Args:
            in_path (string) : chemin d'accès au fichier à projeter
            attribute (string, int) : attribut à extraire du fichier
        
        Return:
            (tuple) : résolution x et y
        """
        sub_format = get_sub_format(in_path)
        return sub_format.getImage(in_path,attribute)

    def getAcqDates(in_path):
        """
        Renvoie les dates d'acquisition de l'image contenue dans le fichier 

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            start_date (datetime) : début de la période d'acquisition
            end_date (datetime) : fin de la période d'acquisition
        """
        sub_format = get_sub_format(in_path)
        return sub_format.getAcqDates(in_path)

