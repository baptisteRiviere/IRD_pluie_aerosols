import numpy as np
from osgeo import gdal
import pyresample as pr

def define_area(param):
    """
    Permet d'implémenter l'objet AreaDefinition de la librairie pyresample à partir des données demandées

    Args:
        param_fil (string): chemin vers le fichier .json contenant les paramètres de la projection
    
    Return:
        (AreaDefinition): objet AreaDefinition
    """
    # create some information on the reference system
    area_id = param["area_id"]
    description = param["description"]
    proj_id = param["proj_id"]
    proj_dict = {"proj": param["proj"], "ellps": param["ellps"], "datum": param["datum"]}
    llx = param["llx"]                  # lower left x coordinate in degrees
    lly = param["lly"]                  # lower left y coordinate in degrees
    urx = param["urx"]                  # upper right x coordinate in degrees
    ury = param["ury"]                  # upper right y coordinate in degrees
    resolution = param["resolution"]    # target resolution in degrees
    # calculating the number of pixels
    width = int((urx - llx) / resolution)
    height = int((ury - lly) / resolution)
    area_extent = (llx,lly,urx,ury)
    area_def = pr.geometry.AreaDefinition(area_id, proj_id, description, proj_dict, width, height, area_extent)
    return area_def

def georef_ds(ds,projection,out_path):

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

    gdal.Warp(out_path, ds, options=options)

def georef_array(array,srcLons,srcLats,projection,out_path):
    outArea = define_area(projection)
    swath_def = pr.geometry.SwathDefinition(lons=srcLons, lats=srcLats)
    array = pr.kd_tree.resample_nearest(    swath_def, 
                                            array,
                                            outArea,
                                            radius_of_influence=16000, # in meters
                                            epsilon=.5,
                                            fill_value=False
                                            )
    
    cols = array.shape[1]
    rows = array.shape[0]

    pixelWidth = (outArea.area_extent[2] - outArea.area_extent[0]) / cols
    pixelHeight = (outArea.area_extent[1] - outArea.area_extent[3]) / rows
    originX = outArea.area_extent[0]
    originY = outArea.area_extent[3] 
    srs = outArea.proj4_string
    geotransform = (originX, pixelWidth, 0, originY, 0, pixelHeight)
    
    driver = gdal.GetDriverByName('GTiff')
    out_raster = driver.Create(out_path, cols, rows, 1, gdal.GDT_UInt16)
    out_raster.SetGeoTransform(geotransform)

    outband = out_raster.GetRasterBand(1)
    outband.WriteArray(np.array(array)) # writting the values

    out_raster.SetProjection(srs)
    
    # clean up
    outband.FlushCache()
    outband = None
    out_raster = None