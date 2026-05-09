import sys
import torch
from ultralytics import YOLO
import torch.nn as nn


# 注册SPD模块
class SPD(nn.Module):
    def __init__(self, dimension=1):
        super().__init__()
        self.d = dimension

    def forward(self, x):
        return torch.cat([x[..., ::2, ::2], x[..., 1::2, ::2], x[..., ::2, 1::2], x[..., 1::2, 1::2]], 1)

# 动态注册到 ultralytics.nn.modules.block
import ultralytics.nn.modules.block as block_module
if not hasattr(block_module, 'SPD'):
    setattr(block_module, 'SPD', SPD)
    print("SPD模块已注册到 ultralytics.nn.modules.block")

# 同时注册到 __main__ 以防万一
sys.modules[__name__].SPD = SPD

# Load a model
model = YOLO("best.pt")  # pretrained YOLO11n model

# Run batched inference on a list of images
results = model(source="E:/low attitude object dect/ultralytics-main/00_01_52_to_00_01_58.mp4",
                stream=True,conf=0.5,save_txt=True,save_crop=True,save=True,show_conf=True)  # return a generator of Results objects

# Process results generator
for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs

'''filename = "data2.csv"
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    for result in results:
        csv_result = result.to_csv()
        writer.writerows(csv_result)
    #result.show()  # display to screen
    #result.save(filename="result.jpg")  # save to disk'''