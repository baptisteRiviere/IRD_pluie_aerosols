from File import File
import json

projection_path = r"tools/param.json"
projection = json.load(open(projection_path, "r", encoding="utf-8"))

IR_file = File(r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat")
MO_file = File(r"../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc")

out_path = r"../data/Results/petit_test.tiff"

canal = IR_file.getCanals()[3]
print(canal)
IR_file.project(out_path,projection,canal)

