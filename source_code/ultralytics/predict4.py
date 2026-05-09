import os
import cv2
import csv
import torch
from ultralytics import YOLO

# 配置路径
image_folder = 'D:/BaiduNetdiskDownload/DET-FLY/spilt/test/images'  # 替换为你的图片文件夹路径
annotation_folder = 'D:/BaiduNetdiskDownload/DET-FLY/spilt/test/labels'  # 替换为你的标注文件夹路径
output_csv = 'D:/BaiduNetdiskDownload/DET-FLY/spilt/test/result.csv'  # 保存识别错误的图片的文件夹路径

# 加载 YOLO 模型
model = YOLO('E:/ultralytics-main/runs/detect/train15/weights/best.pt')  # 加载预训练的 YOLOv8 模型

# 打开 CSV 文件用于写入
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    # 写入 CSV 文件的表头
    writer.writerow(['Image', 'Class_ID', 'Confidence', 'X_min', 'Y_min', 'X_max', 'Y_max'])

    # 获取所有图片文件名
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg') or f.endswith('.png')]

    # 遍历每张图片
    for image_file in image_files:
        # 获取图片路径
        image_path = os.path.join(image_folder, image_file)
        image = cv2.imread(image_path)

        # 运行 YOLO 模型
        results = model(image)

        # 提取预测结果
        pred_labels = results[0].boxes.cls.int().tolist()  # 获取预测的类别标签
        pred_confidences = results[0].boxes.conf.tolist()  # 获取预测的置信度
        pred_bboxes = results[0].boxes.xywh.tolist()  # 获取预测的边界框 (格式为 [x_min, y_min, x_max, y_max])

        # 遍历每个预测结果并写入 CSV 文件
        for label, confidence, bbox in zip(pred_labels, pred_confidences, pred_bboxes):
            x,y,w,h= bbox
            writer.writerow([image_file, label, confidence, x, y, w, h])

print(f"预测结果已保存到 {output_csv}")