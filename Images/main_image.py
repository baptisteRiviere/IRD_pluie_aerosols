from File import File
import json


def download_all(file,out_dir):
    for att in file.getAttributes():
        out_path = out_dir + f"{att}.tiff"
        out_path_var = out_dir + f"{att}_var.tiff"
        image = file.project(out_path,projection,att)
        if image : # if image != False
            image_var = image.computeVar()
            image_var.save(projection,out_path_var)



if __name__ == "__main__":
    projection_path = r"Images/param.json"
    projection = json.load(open(projection_path, "r", encoding="utf-8"))

    
    MO_file = File(r"../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc")
    IR_file = File(r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat")
    out_dir = r"../data/RACC/all_data/"

    download_all(MO_file,out_dir)
    download_all(IR_file,out_dir)
    
    
    
    






"""
    #attributes = ['HRV', 'IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073'] 
    attributes = ['IR_087']
    for att in attributes:
        out_path = rf"../data/test_seg/Meteosat_{att}.tiff"
        compute_var_path = rf"../data/test_seg/Meteosat_{att}_var.tiff"
        values = convert_nat(nat_path,out_path,proj_path,att,compute_var_path)
    """

