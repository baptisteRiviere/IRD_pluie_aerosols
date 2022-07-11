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

    def project(in_path,projection,attribute=None,out_path=False):
        src_image = Bin_Format.getImage(in_path,attribute)
        new_array, new_lons, new_lats = grf.georef_image(src_image,projection,out_path)
        #aot_edr = ma.masked_where((new_array.any() > 5) or (new_array.any() < -100), new_array) # mask aberrant values
        return Image(new_array, new_lons, new_lats)

    def getResolution(in_path,attribute=None):
        return (0.25,0.25)
        
    def getAttributes(in_path):
        return None

    def getImage(in_path, attribute=None):
        """
        inspiré du code de Laura Orgambide
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

    def getAcqDates(in_path,format=None):
        start_date = datetime.strptime(in_path.split(".high")[0][-8:],'%Y%m%d').replace(tzinfo=timezone.utc)
        end_date = (start_date + timedelta(days=1)).replace(tzinfo=timezone.utc)
        return start_date,end_date
        
    def getValue(in_path, lat, lon):
        img = Bin_Format.getImage(in_path, attribute=None)
        y,x = (np.abs(img.lats.T[0] - lat)).argmin(), (np.abs(img.lons[0] - lon)).argmin()
        return img.array[x][y]

if __name__ == '__main__':
    nat_path = r"../data/AOT/npp_aot550_edr_gridded_0.25_20200503.high.bin"
    out_path = r"../data/test.tiff"
    proj_path = r"../data/param_proj/param_guy.json"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    img = Bin_Format.project(nat_path,projection)
    print(img.array)
    img.show()
    