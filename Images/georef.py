import numpy as np
from osgeo import gdal
import pyresample as pr
import os
import warnings
import numpy.ma as ma

def define_area(projection):
    """
    Permet d'implémenter l'objet AreaDefinition de la librairie pyresample à partir des données demandées

    Args:
        projection (string): chemin vers le fichier .json contenant les paramètres de la projection
    
    Return:
        (AreaDefinition): objet AreaDefinition
    """
    area_id = projection["area_id"]
    description = projection["description"]
    proj_id = projection["proj_id"]
    proj_dict = {"proj": projection["proj"], "ellps": projection["ellps"], "datum": projection["datum"]}
    llx = projection["llx"]                  # coordonnée "lower left x" en degrés
    lly = projection["lly"]                  # coordonnée "lower left y" en degrés
    urx = projection["urx"]                  # coordonnée "upper right x" en degrés
    ury = projection["ury"]                  # coordonnée "upper right y" en degrés
    resolution = projection["resolution"]    # résolution recherchée en degrés
    # calcul du nombre de pixels
    width = int((urx - llx) / resolution)
    height = int((ury - lly) / resolution)
    area_extent = (llx,lly,urx,ury)
    # création de l'objet recherché
    area_def = pr.geometry.AreaDefinition(area_id, proj_id, description, proj_dict, width, height, area_extent)
    return area_def

def georef_ds(ds,projection,out_path=None,temporary_path=r"temporary.tiff"):
    """
    Permet de géoréférencer l'objet dataset de gdal et de renvoyer l'array extrait et géoréférencé

    Args:
        ds (gdal dataset) : objet à géoréférencer
        projection (dict) : paramètres de la projection à effectuer
        out_path (string) : chemin d'enregistrement du fichier, si égal à None crée un fichier et le détruit 
        temporary_path (string) : dans le cas où il n'y a pas d'enregistrement du fichier, permet de choisir le chemin où sera créé le fichier temporaire

    Returns:
        array (np.array) : array contenant l'information extraite
        lons (np.array) : array contenant les longitudes des pixels
        lats (np.array) : array contenant les latitudes des pixels
    """
    # récupération des paramètres de projection
    llx,lly,urx,ury = projection["llx"],projection["lly"],projection["urx"],projection["ury"] 
    resolution = projection["resolution"]
    width = int((urx - llx) / resolution)
    height = int((ury - lly) / resolution)

    # paramétrage de la fonction warp de gdal
    options = gdal.WarpOptions(
        outputBounds=[llx,lly,urx,ury],
        format="GTiff",
        width=width,
        height=height,
        dstSRS="+proj=longlat +datum=WGS84 +no_defs"
        )

    # si aucun nom de fichier n'a été indiqué, out_path prend la valeur du fichier temporaire
    if out_path == None:
        out_path = temporary_path

    # projection du fichier et récupération des valeurs de sortie
    ds_proj = gdal.Warp(out_path, ds, options=options)
    array,lons,lats = getArrayLonsLats(ds_proj)
    
    # nettoyage des fichiers et variables
    ds_proj = None
    if os.path.exists(temporary_path):
        os.remove(temporary_path)

    return array,lons,lats

def georef_image(src_image,projection,out_path=None):
    """
    Permet de géoréférencer l'objet Image et de renvoyer l'array extrait et géoréférencé

    Args:
        src_image (Image) : Image à géoréférencer
        projection (dict) : paramètres de la projection à effectuer
        out_path (string) : chemin d'enregistrement du fichier, si égal à None crée un fichier et le détruit 
        temporary_path (string) : dans le cas où il n'y a pas d'enregistrement du fichier, permet de choisir le chemin où sera créé le fichier temporaire

    Returns:
        array (np.array) : array contenant l'information extraite
        lons (np.array) : array contenant les longitudes des pixels
        lats (np.array) : array contenant les latitudes des pixels
    """
    # permet de ne pas afficher les avertissements
    warnings.filterwarnings('ignore')

    # géoréférencement de l'objet à partir de la fonction resample nearest de pyresample
    outArea = define_area(projection)
    swath_def = pr.geometry.SwathDefinition(lons=src_image.lons, lats=src_image.lats)
    new_array = pr.kd_tree.resample_nearest(    swath_def, 
                                                src_image.array,
                                                outArea,
                                                radius_of_influence=16000, # in meters
                                                epsilon=.5,
                                                fill_value=None 
                                                ) 
    
    # récupération des nouvelles longitudes et latitudes                                       
    new_lons, new_lats = outArea.get_lonlats()

    if out_path != None: # si on enregistre le fichier dans un geotiff

        # calcul des paramètres de projection
        cols = new_array.shape[1]   ; rows = new_array.shape[0]
        pixelWidth = (outArea.area_extent[2] - outArea.area_extent[0]) / cols
        pixelHeight = (outArea.area_extent[1] - outArea.area_extent[3]) / rows
        originX = outArea.area_extent[0]    ; originY = outArea.area_extent[3] 
        srs = outArea.proj4_string
        geotransform = (originX, pixelWidth, 0, originY, 0, pixelHeight)
         
        # écriture sur la fichier
        driver = gdal.GetDriverByName('GTiff')
        out_raster = driver.Create(out_path, cols, rows, 1, gdal.GDT_Float32)
        out_raster.SetGeoTransform(geotransform)
        outband = out_raster.GetRasterBand(1)    
        outband.WriteArray(new_array)
        out_raster.SetProjection(srs)

    return new_array, new_lons, new_lats
    

def getArrayLonsLats(ds):
    """
    permet d'obtenir les matrices contenant l'information et les coordonnées des pixels à partir d'un dataset gdal
    L'image doit être projetée en longitudes latitudes WGS84

    Args:
        ds (gdal dataset) : objet dont on extrait les matrices

    Returns:
        array (np.array) : array contenant l'information extraite
        lons (np.array) : array contenant les longitudes des pixels
        lats (np.array) : array contenant les latitudes des pixels
    """
    (x_offset, x_res, rot1, y_offset, rot2, y_res) = ds.GetGeoTransform()
    array = ds.ReadAsArray()
    lons = np.zeros(array.shape)    ; lats = np.zeros(array.shape) # 397, 483
    for x in range(array.shape[1]):
        for y in range(array.shape[0]):
            lons[y][x] = x_res * x + rot1 * y + x_offset
            lats[y][x] = rot2 * x + y_res * y + y_offset
    return array,lons,lats