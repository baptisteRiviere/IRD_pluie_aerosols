import numpy as np
from Image import Image

class IFormat:
    """
    Interface permettant de définir la structure inspirée du strategy pattern
    toutes les classes héritant de cette interface fournissent un ensemble de méthodes pour un certain format de données
    """
    
    def project(in_path,projection,attribute=1,out_path=False):
        return Image(np.array([]),np.array([]),np.array([]),projection)

    def getResolution(in_path,attribute):
        return (0.0,0.0)

    def getAttributes(in_path):
        return []

    def getImage(in_path,attribute):
        return Image(np.array([]),np.array([]),np.array([]))

    



