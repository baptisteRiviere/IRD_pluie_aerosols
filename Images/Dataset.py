from Image import Image

class Dataset:
    
    def __init__(self, images):
        self.images = images

if __name__ == "__main__":
    in_path = r'../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc'
    attribute = "TB"
    


    # proj_param = json.load(open(proj_path, "r", encoding="utf-8"))