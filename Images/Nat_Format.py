import numpy as np
import pyresample as pr
from satpy import Scene
import numpy.ma as ma
import matplotlib.pyplot as plt
from scipy import signal

import georef as grf
from IFormatBehaviour import IformatBehaviour


class Nat_Format(IformatBehaviour):
    
    def project(in_path,out_path,projection,canal):
        convert_nat(in_path,out_path,projection,canal)

    def getResolution(self, sound):
        return None

    def getCanals(self, sound):
        return None


def generate_img_var(im):
    im2 = im**2
    ones = np.ones(im.shape)
    
    kernel = np.ones((3,3))
    s = signal.convolve2d(im, kernel, mode="same")
    s2 = signal.convolve2d(im2, kernel, mode="same")
    ns = signal.convolve2d(ones, kernel, mode="same")
    
    return np.sqrt((s2 - s**2 / ns) / ns)

def extract_nat(file,attribute,dtype = "float32"):
    reader = "seviri_l1b_native" # define reader
    scn = Scene(filenames = {reader:[file]})
    
    scn.load([attribute], calibration = "brightness_temperature") # load data
    lons, lats = scn[attribute].area.get_lonlats()

    values = scn[attribute].values # extract the data
    lons = lons.astype(dtype) ; lats = lats.astype(dtype) ; values = values.astype(dtype)
    mask = np.where(lons==np.inf,1,0)
    values_ma = ma.array(values, mask=mask)
    lons_ma = ma.array(lons, mask=mask)
    lats_ma = ma.array(lats, mask=mask)

    return values_ma,lons_ma,lats_ma

def convert_nat(src_path,out_path,projection,attribute,compute_var_path=None,plot=False):
    try :
        values,srcLons,srcLats = extract_nat(src_path,attribute)
        
        outArea = grf.define_area(projection)
        swath_def = pr.geometry.SwathDefinition(lons=srcLons, lats=srcLats)
        values = pr.kd_tree.resample_nearest(   swath_def, 
                                                values,
                                                outArea,
                                                radius_of_influence=16000, # in meters
                                                epsilon=.5,
                                                fill_value=False
                                                )

        grf.georef_array(values,outArea,out_path)

        if plot:
            plt.imshow(values)
            plt.show()
        
        if compute_var_path != None:
                img_var = generate_img_var(values)
                grf.georef_array(img_var,outArea,compute_var_path)

        return values

    except KeyError:
        #print(f"ERROR: la variance n'a pas pu être calculée pour {attribute}")
        print(f"ERROR: la température de brillance n'est pas définie pour le canal {attribute}")
        return None
            


if __name__ == '__main__':
    nat_path = r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat"
    proj_path = r"tools/param.json"

    #attributes = ['HRV', 'IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073'] 
    attributes = ['IR_087']
    for att in attributes:
        out_path = rf"../data/test_seg/Meteosat_{att}.tiff"
        compute_var_path = rf"../data/test_seg/Meteosat_{att}_var.tiff"
        values = convert_nat(nat_path,out_path,proj_path,att,compute_var_path)


    
    


    
    
    
    
    
