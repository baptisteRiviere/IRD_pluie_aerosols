import numpy as np
import tests_correl as tc
from osgeo import gdal
import json
import pyresample as pr
import matplotlib.pyplot as plt

def define_area(param_file):
    """
    Permet d'implémenter l'objet AreaDefinition de la librairie pyresample à partir des données demandées

    Args:
        param_fil (string): chemin vers le fichier .json contenant les paramètres de la projection
    
    Return:
        (AreaDefinition): objet AreaDefinition
    """
    param_json = open(param_file, "r", encoding="utf-8")
    param = json.load(param_json)
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

def georef_array(array,area_def,fname):
    cols = array.shape[1]
    rows = array.shape[0]

    pixelWidth = (area_def.area_extent[2] - area_def.area_extent[0]) / cols
    pixelHeight = (area_def.area_extent[1] - area_def.area_extent[3]) / rows
    originX = area_def.area_extent[0]
    originY = area_def.area_extent[3] 
    srs = area_def.proj4_string
    geotransform = (originX, pixelWidth, 0, originY, 0, pixelHeight)
    
    driver = gdal.GetDriverByName('GTiff')
    out_raster = driver.Create(fname, cols, rows, 1, gdal.GDT_UInt16)
    out_raster.SetGeoTransform(geotransform)

    outband = out_raster.GetRasterBand(1)
    outband.WriteArray(np.array(array)) # writting the values

    out_raster.SetProjection(srs)

    

    # clean up
    outband.FlushCache()
    outband = None
    out_raster = None

def georef_ds(ds,proj_path,out_path):
    proj_param = json.load(open(proj_path, "r", encoding="utf-8"))

    llx,lly,urx,ury = proj_param["llx"],proj_param["lly"],proj_param["urx"],proj_param["ury"] 
    resolution = proj_param["resolution"]
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


if __name__ == '__main__':
    
    aot_edr, n_aot_edr = tc.open_bin(r"..\data\AOT_inf_50_dezip\npp_aot550_edr_gridded_0.25_20120622.high.bin\npp_aot550_edr_gridded_0.25_20120622.high.bin")
    lons, lats = tc.LonLat()
    #georef(n_aot_edr,lons,lats,r"..\data\Results\npp_aot550_georef.tiff")
