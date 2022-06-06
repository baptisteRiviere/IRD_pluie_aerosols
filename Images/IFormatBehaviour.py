import numpy as np

class IFormat:
    # TODO : documentation
    
    def project(in_path,out_path,projection,attribute):
        return None

    def getResolution(in_path,attribute):
        return (0.0,0.0)

    def getAttributes(in_path):
        return []

    def getArrayLonsLats(in_path,attribute):
        return np.array([]),np.array([]),np.array([])

    



