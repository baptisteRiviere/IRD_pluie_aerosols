import numpy as np
from Image import Image

class IFormat:
    """
    Interface permettant de définir la structure inspirée du strategy pattern
    toutes les classes héritant de cette interface fournissent un ensemble de méthodes pour un certain format de données
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
        return Image(np.array([]),np.array([]),np.array([]),projection)

    def getResolution(in_path,attribute):
        """
        renvoie les résolutions spatiales en x et y du fichier

        Args:
            in_path (string) : chemin d'accès au fichier à projeter
            attribute (string, int) : attribut correspondant à une image du fichier

        Return:
            (tuple) : résolution x et y
        """
        return (0.0,0.0)

    def getAttributes(in_path):
        """
        renvoie la liste d'attributs du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            (list) : liste des attributs
        """
        return []

    def getImage(in_path,attribute):
        """
        Renvoie l'image correspondant à un certain attribut du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
            attribute (string, int) : attribut à extraire du fichier

        Return:
            (Image)
        """
        return Image(np.array([]),np.array([]),np.array([]))

    



