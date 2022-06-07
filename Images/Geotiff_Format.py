import numpy as np
from osgeo import gdal
import georef as grf
import json as json
from Image import Image


class Geotiff_Format:
    # TODO : documentation
    
    def project(in_path,out_path,projection,attribute):
        try :
            src_image = Geotiff_Format.getImage(in_path,attribute)
            new_array, new_lons, new_lats = grf.georef_image(src_image,projection,out_path)
            return Image(new_array, new_lons, new_lats)
        except :
            print(f"ERROR: l'image {in_path} n'a pas pu être projetée pour l'attribut {attribute}")
            return False
        

    def getResolution(in_path,attribute):
        ds = gdal.Open(in_path)
        (_, x_res, _, _, _, y_res) = ds.GetGeoTransform()
        return (x_res,-y_res)

    def getAttributes(in_path):
        ds = gdal.Open(in_path)
        return [i+1 for i in range(ds.RasterCount)]

    def getImage(in_path,attribute):
        ds = gdal.Open(in_path)
        (x_offset, x_res, rot1, y_offset, rot2, y_res) = ds.GetGeoTransform()
        rb = ds.GetRasterBand(attribute) # TODO faire en sorte d'avoir toujours un float
        array = rb.ReadAsArray()
        lons = np.zeros(array.shape)    ; lats = np.zeros(array.shape)
        for y in range(len(array)):
            for x in range(len(array[0])):
                lons[y][x] = x_res * x + rot1 * y + x_offset
                lats[y][x] = rot2 * x + y_res * y + y_offset
        return Image(array,lons,lats)
        


if __name__ == '__main__':

    geotiff_path = r'../data/Results/IR_georef_test.tiff'
    attribute = 1
    
    proj_path = r"tools/param_guy.json"
    projection = json.load(open(proj_path, "r", encoding="utf-8"))

    out_path = r"../data/test.tiff"

    print(Geotiff_Format.getArrayLonsLats(geotiff_path,attribute))
