import numpy as np
from satpy import Scene
import numpy.ma as ma
import json 
from datetime import timezone

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
        src_image = Nat_Format.getImage(in_path,attribute)
        new_array, new_lons, new_lats = grf.georef_image(src_image,projection,out_path)
        return Image(new_array, new_lons, new_lats)

    def getResolution(in_path,attribute):
        """
        renvoie les résolutions spatiales en x et y du fichier

        Args:
            in_path (string) : chemin d'accès au fichier à projeter
            attribute (string, int) : attribut à extraire du fichier
        
        Return:
            (tuple) : résolution x et y
        """
        reader = "seviri_l1b_native"
        scn = Scene(filenames = {reader:[in_path]})
        scn.load([attribute], calibration = "brightness_temperature")
        return (scn[attribute].resolution,scn[attribute].resolution)
        
    def getAttributes(in_path):
        """
        renvoie la liste d'attributs du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            (list) : liste des attributs
        """
        reader = "seviri_l1b_native"
        scn = Scene(filenames = {reader:[in_path]})
        return scn.available_dataset_names()

    def getImage(in_path, attribute):
        """
        Renvoie l'image correspondant à un certain attribut du fichier

        Args:
            in_path (string) : chemin d'accès au fichier
            attribute (string, int) : attribut à extraire du fichier

        Return:
            (Image)
        """
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

    def getAcqDates(in_path):
        """
        Renvoie les dates d'acquisition de l'image contenue dans le fichier 

        Args:
            in_path (string) : chemin d'accès au fichier
        
        Return:
            start_date (datetime) : début de la période d'acquisition
            end_date (datetime) : fin de la période d'acquisition
        """
        reader = "seviri_l1b_native"
        scn = Scene(filenames = {reader:[in_path]})
        start_date = scn.start_time.replace(tzinfo=timezone.utc)
        end_date = scn.end_time.replace(tzinfo=timezone.utc)
        return start_date,end_date
            

if __name__ == '__main__':
    nat_path = r"../data/SEVIRI/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat"
    out_path = r"../data/test.tiff"
    attribute = 'IR_087'
    proj_path = r"../data/param_proj/param_guy.json"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    a = Nat_Format.project(nat_path,projection,attribute)
    print(a)

    """
    import glob
    fns = glob.glob(r"../data/IR/test/*.nat")
    i = 0
    for fn in fns:
        print(i, fn)
        i += 1
        Nat_Format.project(fn,rf"../data/IR/test/{i}.tiff",projection,"IR_087")
    """
    
    
    


    
    
    
    
    
