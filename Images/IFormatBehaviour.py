import numpy as np
from Image import Image

class IFormat:
    # TODO : documentation
    
    def project(in_path,out_path,projection,attribute):
        return Image(np.array([]),np.array([]),np.array([]))

    def getResolution(in_path,attribute):
        return (0.0,0.0)

    def getAttributes(in_path):
        return []

    def getImage(in_path,attribute):
        return Image(np.array([]),np.array([]),np.array([]))

    



