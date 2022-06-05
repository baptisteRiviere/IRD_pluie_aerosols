class Image:
    
    def __init__(self, path):
        self.path = path
        self.format = "netCDF"
        self.resolution = format.getResolution(self.path)
        self.canals = format.getCanals(self.path)

    def project(self):
        return None

    def getArray(self, sound):
        return None

    def getLonsLats(self, sound):
        return None

    def getBands(self, sound):
        return None
