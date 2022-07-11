import json
import os

def get_index(index_path):
    """
    Permet d'avoir accès au dictionnaire index donnant le chemin d'accès aux différentes images

    Args:
        index_path (string) : chemin d'accès au fichier json contenant l'index
    Returns:
        index (dict) : dictionnaire index
    """
    with open(index_path, "r", encoding="utf-8") as json_dict:
        index = json.load(json_dict)
    return index
    
def save_index(index,index_path):
    """
    Permet de sauvegarder le dictionnaire index donnant le chemin d'accès aux différentes images

    Args:
        index (dict) : dictionnaire index
        index_path (string) : chemin d'accès au fichier json contenant l'index        
    """
    with open(index_path, 'w', encoding="utf-8") as json_dict:
        json.dump(index, json_dict, indent=4, default=str)
        
def make_directory(path):
    """
    S'il n'existe pas, crée le dossier dont le chemin d'accès est donné en entrée
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path