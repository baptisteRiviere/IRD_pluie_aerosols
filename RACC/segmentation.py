import numpy as np
import glob
import json
from sklearn.cluster import KMeans
import os
import sys

sys.path.insert(0, r'../Images')
from File import File
from Image import Image

def generate_X(images):
    """
    Génère l'objet X adapté à l'algorithme à partir d'une liste d'images

    Args
        images (list): liste d'instances de la classe Image 

    Return
        X (np.array): attributs des individus de taille (nb_indiv,nb_att)
        (x,y) (tuple): format initial de l'image
    """
    X = []
    for img in images:
        X.append(img.array)
    X = np.array(X)
    (p,x,y) = X.shape
    
    lons, lats = images[0].lons, images[0].lats # on conserve les longitudes et latitudes
    X = X.reshape((p, x*y)).transpose()         # 'applatissement' de l'image en un unique vecteur                   
    return X, (x,y), lons, lats

def standard_scaler(X):
    """
    Transforme les attributs pour qu'ils aient des plages de valeurs comparable

    Args
        X (np.array): attributs des individus de taille (nb_indiv,nb_att)
    
    Return
        X_stand (np.array): X standardisé de taille (nb_indiv,nb_att)
        X_max (np.array) : maximum de chaque colonne de taille (nb_att)
        X_min (np.array) : minimum de chaque colonne de taille (nb_att)
    """
    X_max = np.max(X, axis=0)
    X_min = np.min(X, axis=0)
    return (X-X_min)/(X_max-X_min), X_max, X_min

def classification(main_dir,projection,N=20,epsilon=0.01,T=100,standardisation=False,show=True,save=True):
    """
    classification des images à partir de la méthode des Kmeans

    Args :
        main_dir (string): chemin d'accès au répertoire contenant les images à classifier
        N (int) : nombre de classes
        epsilon (float): seuil à partir duquel on considère que les centres de clusters convergent après 2 itération (norme de Frobenius)
        T (int) : nombre d'itérations maximum
    
    Return
        array_pred (np.array): image de la prédiction finale sur les images
        centers (np.array): centres des classes 
    """
    img_paths = glob.glob(main_dir+r"\*.tiff") # récupération de toutes les images geotiff du dossier
    images = [File(img_path).getImage(1) for img_path in img_paths]
    
    X, (x,y), lons, lats = generate_X(images)
    if standardisation : # la standardisation permet de comparer les données sur les mêmes plages de valeur
        X,X_max,X_min = standard_scaler(X)  
    else : 
        X_max, X_min = 1,0
    
    kmeans = KMeans(n_clusters=N,random_state=0,tol=epsilon,max_iter=T).fit(X)
    pred,centers = kmeans.labels_,kmeans.cluster_centers_

    array_pred = pred.reshape((x,y))
    img_classif = Image(array_pred,lons,lats)
    
    # S'il y a eu standardisation on recalcule les centres de classes dans la bonne unité
    centers = centers*(X_max-X_min)+X_min 

    if save:
        out_dir = main_dir + "/result"
        if not (os.path.exists(out_dir)):
            os.makedirs(out_dir)
        np.save(out_dir+"/centers.npy",centers)
        img_classif.save(projection,out_dir+"/result.tiff")

    if show:
        img_classif.show(simple=True)

    return array_pred,centers
    


if __name__ == '__main__':
    # load projection # TODO : faire en sorte que ce soit exactement la même proj ! important
    projection = json.load(open(r"Images/param_guy.json", "r", encoding="utf-8"))

    directory = r"../data/RACC/train"
    array_pred,centers = classification(directory,projection,N=10,epsilon=0.001,T=100)
    print(centers)
    

    
    


