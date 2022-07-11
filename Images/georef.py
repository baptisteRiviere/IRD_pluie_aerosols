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
    # create some information on the reference system
    area_id = projection["area_id"]
    description = projection["description"]
    proj_id = projection["proj_id"]
    proj_dict = {"proj": projection["proj"], "ellps": projection["ellps"], "datum": projection["datum"]}
    llx = projection["llx"]                  # lower left x coordinate in degrees
    lly = projection["lly"]                  # lower left y coordinate in degrees
    urx = projection["urx"]                  # upper right x coordinate in degrees
    ury = projection["ury"]                  # upper right y coordinate in degrees
    resolution = projection["resolution"]    # target resolution in degrees
    # calculating the number of pixels
    width = int((urx - llx) / resolution)
    height = int((ury - lly) / resolution)
    area_extent = (llx,lly,urx,ury)
    area_def = pr.geometry.AreaDefinition(area_id, proj_id, description, proj_dict, width, height, area_extent)
    return area_def

def georef_ds(ds,projection,out_path=False):
    llx,lly,urx,ury = projection["llx"],projection["lly"],projection["urx"],projection["ury"] 
    resolution = projection["resolution"]
    width = int((urx - llx) / resolution)
    height = int((ury - lly) / resolution)

    options = gdal.WarpOptions(
        outputBounds=[llx,lly,urx,ury],
        format="GTiff",
        width=width,
        height=height,
        dstSRS="+proj=longlat +datum=WGS84 +no_defs"
        ) # TODO : changer srs

    if out_path:
        ds_proj = gdal.Warp(out_path, ds, options=options)
        array,lons,lats = getArrayLonsLats(ds_proj)
    else :
        ds_proj = gdal.Warp(r"C:\Users\Baptiste\Documents\ENSG\stage\data\temporary.tiff", ds, options=options)
        array,lons,lats = getArrayLonsLats(ds_proj)

    return array,lons,lats

def georef_image(src_image,projection,out_path=False):
    warnings.filterwarnings('ignore')
    outArea = define_area(projection)
    swath_def = pr.geometry.SwathDefinition(lons=src_image.lons, lats=src_image.lats)
    new_array = pr.kd_tree.resample_nearest(    swath_def, 
                                                src_image.array,
                                                outArea,
                                                radius_of_influence=16000, # in meters
                                                epsilon=.5,
                                                fill_value=None 
                                                ) 
    
    cols = new_array.shape[1]   ; rows = new_array.shape[0]
    pixelWidth = (outArea.area_extent[2] - outArea.area_extent[0]) / cols
    pixelHeight = (outArea.area_extent[1] - outArea.area_extent[3]) / rows
    originX = outArea.area_extent[0]    ; originY = outArea.area_extent[3] 
    srs = outArea.proj4_string
    geotransform = (originX, pixelWidth, 0, originY, 0, pixelHeight)
    
    driver = gdal.GetDriverByName('GTiff')
    if out_path:
        out_raster = driver.Create(out_path, cols, rows, 1, gdal.GDT_Float32)
    else :
        out_raster = driver.Create(r"C:\Users\Baptiste\Documents\ENSG\stage\data\temporary.tiff", cols, rows, 1, gdal.GDT_Float32)
    out_raster.SetGeoTransform(geotransform)
    
    outband = out_raster.GetRasterBand(1)
    outband.WriteArray(new_array) # writting the values
    out_raster.SetProjection(srs)

    new_lons, new_lats = outArea.get_lonlats()

    return new_array, new_lons, new_lats

def getArrayLonsLats(ds):
    (x_offset, x_res, rot1, y_offset, rot2, y_res) = ds.GetGeoTransform()
    array = ds.ReadAsArray()
    lons = np.zeros(array.shape)    ; lats = np.zeros(array.shape) # 397, 483
    for x in range(array.shape[1]):
        for y in range(array.shape[0]):
            lons[y][x] = x_res * x + rot1 * y + x_offset
            lats[y][x] = rot2 * x + y_res * y + y_offset
    return array,lons,lats