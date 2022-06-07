import numpy as np
import matplotlib.pyplot as plt
import random
import glob

from File import File

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
    
    lons, lats = images[0].lons, images[0].lons # on conserve les longitudes et latitudes
    X = X.reshape((p, x*y)).transpose()         # 'applatissement' de l'image en un unique vecteur                   
    return X, (x,y), lons, lats

def standard_scaler(X):
    """
    Transforme les attributs pour qu'ils aient des plages de valeurs comparable

    Args
        X (np.array): attributs des individus de taille (nb_indiv,nb_att)
    
    Return
        X_stand (np.array): X standardisé
    """
    """
    X_mean = np.mean(X, axis=0)
    X_std = np.mean(X, axis=0)
    X_stand = (X-X_mean)/X_std
    """
    X_max = np.max(X, axis=0)
    X_min = np.min(X, axis=0)
    return (X-X_min)/(X_max-X_min)

def first_class_centers(X,N,F):
    """
    Tire aléatoirement F points pour les K centres de cluster et renvoie leurs coordonnées

    Args
        X (np.array): attributs des individus de taille (nb_indiv,nb_att)
        N (int): nombre de cluster
        F (int): nombre de points du noyau par cluster

    Return
        centers (np.array): Array de taille (N,F,nb_att) contenant les coordoonées des N*F centres
    """
    centers = np.zeros((N,F,len(X[0])))
    X_index_list = [i for i in range(len(X))]
    for n in range(N):
        for f in range(F):
            idx = X_index_list.pop(random.randint(0,len(X_index_list)-1))
            centers[n][f]=X[idx]
    return centers

def compute_distance(X,centers):
    """
    Calcule la distance entre chaque individu et les centre des clusters

    Args
        X (np.array): attributs des individus de taille (nb_indiv,nb_att)
        centers (np.array): Array de taille (N,F,nb_att) contenant les coordoonées des N*F centres

    Return
        M_dist (np.array): matrice de taille (nb_indiv,N)
    """
    (N,F,nb_att) = centers.shape    ; nb_indiv = len(X)
    M_dist = np.zeros((nb_indiv,N))
    for idx in range(nb_indiv):
        for centre in range(N):
            dist = 0
            for f in range(F):
                for att in range(nb_att):
                    dist += (X[idx][att] - centers[centre][f][att])**2
            M_dist[idx][centre] = np.sqrt(dist)
    return M_dist

def classif(distance_matrix):
    """
    Calcule le centre de cluster le plus proche de chaque individu

    Args
        distance_matrix (np.array): distances entre les indivuds et l'ensemble des centres de cluster
    
    Return 
        classe (np.array): indique l'identifiant du cluster le plus proche de chaque individu, de taille (nb_individu)
    """
    (nb_indiv,N) = distance_matrix.shape
    classe = np.zeros(nb_indiv)
    for ind in range(nb_indiv):
        classe[ind] = np.argmin(distance_matrix[ind])
    return classe

def del_small_classes(classe,N,seuil=10):
    """
    supprime les clusters dont le nombre d'individus est trop faible, 
    donne une classe null aux individus concernés de l'array classe

    Args
        X (np.array): attributs des individus de taille (nb_indiv,nb_att)
        classe (np.array): indique l'identifiant du cluster le plus proche de chaque individu, de taille (nb_individu)
    
    Return
        centers (np.array): Array de taille (N,F,nb_att) contenant les coordoonées des N*F centres
    """
    for n in range(N):
        nb_indiv = np.sum(np.where(classe==n,1,0))
        if nb_indiv < seuil:
            N -= 1
            classe = np.where(classe==n,None,classe)    # on supprime la classe en question
            classe = np.where(classe>n,classe-1,classe) # on décale toutes les classes supérieures d'un rang
    return classe, N

def compute_new_centroid(X,classe,N,F):
    """
    Calcule le nouveau centre de chaque cluster

    Args
        X (np.array): attributs des individus de taille (nb_indiv,nb_att)
        classe (np.array): indique l'identifiant du cluster le plus proche de chaque individu, de taille (nb_individu)
        N (int): nombre de classes
        F (int): nombre de points du noyau par cluster
    
    Return
        centers (np.array): Array de taille (N,F,nb_att) contenant les coordoonées des N*F centres
    """
    nb_att = X.shape[1]
    centers = np.zeros((N,F,nb_att))
    for n in range(N):
        mask = np.where(classe==n,1,0)
        mask = np.tile(mask, (nb_att, 1))
        masked_X = np.ma.masked_array(X, mask=mask)
        centers[n][0] = masked_X.mean(axis=0)
    return centers

def intraclass_var(X,classe,centers):
    """
    X (np.array): attributs des individus de taille (nb_indiv,nb_att)
    classe (np.array): indique l'identifiant du cluster le plus proche de chaque individu, de taille (nb_individu)
    centers (np.array): Array de taille (N,F,nb_att) contenant les coordoonées des N*F centres
    """
    nb_att = X.shape[1]
    N = centers.shape[0]
    var = 0
    for n in range(N):
        mask = np.where(classe==n,1,0)
        mask = np.tile(mask, (nb_att, 1))
        masked_X = np.ma.masked_array(X, mask=mask)
        var += np.sum(np.sqrt(masked_X-centers[n][0]))
    return var

def classification(X,N,F,epsilon=0.01,T=100,standard_scaling=True,init_size=None):
    """
    Implémente l'entrainement de la classification des clusters dynamiques (Kmeans)

    Args
        X (np.array): attributs des individus de taille (nb_indiv,nb_att)
        N (int): nombre de classes
        F (int): nombre de points du noyau par cluster
        epsilon (float): critère d'arrêt mesurant décalage minimal des centres de classe
        T (int): nombre d'itérations maximum
        standard_scaling (Bool): rééchantillone les données sur des plages de valeurs comparables
    
    Return
        centers (np.array): Array de taille (N,F,nb_att) contenant les coordoonées des N*F centres
    """
    # standardisation pour comparer les données sur les mêmes plages de valeur
    if standard_scaling:
        X = standard_scaler(X)

    #plt.imshow(X[:,2].reshape(init_size))
    #plt.show()
    
    # Un jeu de données de F points est choisi aléatoirement pour chaque classe, il s’agit du noyau de cette classe
    centers = first_class_centers(X,N,F)

    conv=1000  ; t=0  ; var=0  ; nb_indiv=len(X) ; L_conv=[]  # initialisation paramètres critères arrêt
    while abs(conv)>epsilon and t<T:
        
        # Pour chaque noyau, le centre de gravité et de variance est calculé
        distance_matrix = compute_distance(X,centers)
        
        # On attribut à chaque individu le cluster le plus proche
        pred = classif(distance_matrix)

        # Si le nombre d’éléments dans une classe est trop petit, elle est supprimée
        # TODO c'est possible que certaines erreurs viennent du fait qu'il ne reste qu'une classe
        #pred, N = del_small_classes(pred,N,seuil=5)

        # Le centre de gravité des classes sont calculés à nouveau
        # TODO : comprendre le F points
        centers = compute_new_centroid(X,pred,N,F=1)

        # TODO On calcule le centre de variance pour mesurer le 'déplacement' des centres des classes
        new_var = intraclass_var(X,pred,centers)
        
        conv = new_var-var
        var = new_var
        L_conv.append(conv)
        t+=1

        print(f"itération {t}: conv={conv}")
    
    return pred,centers,L_conv
    


if __name__ == '__main__':
    # load images
    img_paths = glob.glob(r"../data/RACC/useful_data/*.tiff")
    images = [File(img_path).getImage(1) for img_path in img_paths]
    
    X, (x,y), lons, lats = generate_X(images)

    print(X.shape)

    #plt.imshow(X[:,3].reshape((x,y)))
    #plt.show()

    pred,centers,L_conv = classification(X,15,5,epsilon=0.001,T=10,standard_scaling=True,init_size=(x,y))

    image_classif = pred.reshape((x,y))
    plt.imshow(image_classif)
    plt.show()
    
    plt.plot(L_conv)
    plt.show()

    print(centers)
    



