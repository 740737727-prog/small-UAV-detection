import sys
import os

# 首先注册SPD模块
sys.path.insert(0, os.path.dirname(__file__))
import register_spd
register_spd.register_spd_module()

from ultralytics import YOLO

# 测试加载model1
print("\n尝试加载model1...")
model1_path = r"E:\low attitude object dect\ultralytics-main\model\model1\train25\weights\best.pt"
if os.path.exists(model1_path):
    model1 = YOLO(model1_path)
    print("✓ Model1加载成功！")
else:
    print("✗ Model1路径不存在")

# 测试加载model2
print("\n尝试加载model2...")
model2_path = r"E:\low attitude object dect\ultralytics-main\model\model2\train7\weights\best.pt"
if os.path.exists(model2_path):
    model2 = YOLO(model2_path)
    print("✓ Model2加载成功！")
else:
    print("✗ Model2路径不存在")

print("\n测试完成！")