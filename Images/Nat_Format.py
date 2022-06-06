import numpy as np
import pyresample as pr
from satpy import Scene
import numpy.ma as ma
import json 

import georef as grf
from IFormatBehaviour import IFormat

class Nat_Format(IFormat):
    # TODO documentation
    
    def project(in_path,out_path,projection,attribute):
        array,lons,lats = Nat_Format.getArrayLonsLats(in_path, attribute)
        grf.georef_array(array,lons,lats,projection,out_path)
        return array

    def getResolution(in_path,attribute):
        # TODO : alternative reader et calibration
        reader = "seviri_l1b_native" # define reader
        scn = Scene(filenames = {reader:[in_path]})
        scn.load([attribute], calibration = "brightness_temperature")
        return (scn[attribute].resolution,scn[attribute].resolution)
        
    def getAttributes(in_path):
        reader = "seviri_l1b_native" # define reader
        scn = Scene(filenames = {reader:[in_path]})
        return scn.available_dataset_names()

    def getArrayLonsLats(in_path, attribute):
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

            return values_ma,lons_ma,lats_ma

        except KeyError:
            # TODO : trouver meilleure parade
            print(f"ERROR: la température de brillance n'est pas définie pour le attribute {attribute}")
            return None

    
            

if __name__ == '__main__':
    nat_path = r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat"
    out_path = r"../data/teest.tiff"
    attribute = 'IR_087'
    proj_path = r"tools/param_guy.json"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    

    array = Nat_Format.project(nat_path,out_path,projection,attribute)
    
    
    


    
    
    
    
    