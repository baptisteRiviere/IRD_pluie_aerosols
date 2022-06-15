import numpy as np
from satpy import Scene
import numpy.ma as ma
import json 

from Image import Image
import georef as grf
from IFormatBehaviour import IFormat

class Nat_Format(IFormat):
    """
    Classe héritant de l'interface IFormat permettant de fournir un ensemble de méthodes pour un certain format de données
    Cet outil a été développé pour l'extraction des fichiers nat (native Format Archive) fournis par eumetsat à l'URL ci-dessous
    afin d'en extraire la température de brillance, les objets reader et calibration sont ainsi propres à ce cas d'utilisation
    https://data.eumetsat.int/data/map/EO:EUM:DAT:MSG:HRSEVIRI#
    
    L'architecture est inspirée du Strategy pattern
    """
    
    # TODO : moyen pour avoir reader et calibration en paramètre

    def project(in_path,out_path,projection,attribute):
        src_image = Nat_Format.getImage(in_path,attribute)
        new_array, new_lons, new_lats = grf.georef_image(src_image,projection,out_path)
        return Image(new_array, new_lons, new_lats)

    def getResolution(in_path,attribute):
        reader = "seviri_l1b_native"
        scn = Scene(filenames = {reader:[in_path]})
        scn.load([attribute], calibration = "brightness_temperature")
        return (scn[attribute].resolution,scn[attribute].resolution)
        
    def getAttributes(in_path):
        reader = "seviri_l1b_native"
        scn = Scene(filenames = {reader:[in_path]})
        return scn.available_dataset_names()

    def getImage(in_path, attribute):
        try :
            dtype = "float32"
            reader = "seviri_l1b_native" # define reader
            scn = Scene(filenames = {reader:[in_path]})
            
            scn.load([attribute], calibration = "brightness_temperature") # load data
            lons, lats = scn[attribute].area.get_lonlats()
            values = scn[attribute].values # extract data

            lons = lons.astype(dtype) ; lats = lats.astype(dtype) ; values = values.astype(dtype)
            mask = np.where(lons==np.inf,1,0)
            values_ma = ma.array(values, mask=mask)
            lons_ma = ma.array(lons, mask=mask)
            lats_ma = ma.array(lats, mask=mask)

            return Image(values_ma,lons_ma,lats_ma)

        except KeyError:
            # TODO : trouver meilleure parade
            print(f"ERROR: la température de brillance n'est pas définie pour {attribute}")
            return False

    
            

if __name__ == '__main__':
    nat_path = r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat"
    out_path = r"../data/test.tiff"
    attribute = 'IR_087'
    proj_path = r"RACC/param_guy.json"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    import glob
    fns = glob.glob(r"../data/IR/test/*.nat")
    i = 0
    for fn in fns:
        print(i, fn)
        i += 1
        Nat_Format.project(fn,rf"../data/IR/test/{i}.tiff",projection,"IR_087")
    
    
    


    
    
    
    
    
