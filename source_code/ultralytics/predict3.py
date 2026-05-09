import os
import cv2
import torch
from ultralytics import YOLO

# 配置路径
image_folder = 'D:/BaiduNetdiskDownload/DET-FLY/spilt/test/images'  # 替换为你的图片文件夹路径
annotation_folder = 'D:/BaiduNetdiskDownload/DET-FLY/spilt/test/labels'  # 替换为你的标注文件夹路径
output_folder = 'D:/BaiduNetdiskDownload/DET-FLY/spilt/test/wrong2'  # 保存识别错误的图片的文件夹路径

# 加载 YOLO 模型
model = YOLO('E:/ultralytics-main/runs/detect/train15/weights/best.pt')  # 加载预训练的 YOLOv8 模型

# 创建保存错误图片的文件夹
os.makedirs(output_folder, exist_ok=True)

# 获取所有图片文件名
image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg') or f.endswith('.png')]

# 遍历每张图片
for image_file in image_files:
    # 获取图片路径
    image_path = os.path.join(image_folder, image_file)
    image = cv2.imread(image_path)

    # 获取对应的标注文件
    annotation_path = os.path.join(annotation_folder, image_file.replace('.jpg', '.txt').replace('.png', '.txt'))

    # 读取标注文件
    true_labels = []
    if os.path.exists(annotation_path):
        with open(annotation_path, 'r') as f:
            for line in f.readlines():
                class_id, _, _, _, _ = line.strip().split()
                true_labels.append(int(class_id))

    # 运行 YOLO 模型
    results = model(image)

    # 提取预测结果
    pred_labels = results[0].boxes.cls.int().tolist()  # 获取预测的类别标签
    pred_confidences = results[0].boxes.conf.tolist()  # 获取预测的置信度
    pred_bboxes = results[0].boxes.xyxy.tolist()  # 获取预测的边界框 (格式为 [x_min, y_min, x_max, y_max])

    # 判断是否识别错误
    # 条件1：预测的类别与真实标签不一致
    # 条件2：存在置信度低于 0.25 的预测结果
    is_correct = set(true_labels) == set(pred_labels) and all(conf >= 0.25 for conf in pred_confidences)

    # 如果识别错误，绘制边界框并保存图片
    if not is_correct:
        # 绘制边界框
        for label, confidence, bbox in zip(pred_labels, pred_confidences, pred_bboxes):
            x_min, y_min, x_max, y_max = map(int, bbox)  # 将边界框坐标转换为整数
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)  # 绘制绿色边界框
            cv2.putText(image, f'{label} {confidence:.2f}', (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # 添加类别和置信度标签
            output_path = os.path.join(output_folder, image_file)
            cv2.imwrite(output_path, image)


print(f"识别错误的图片已保存到 {output_folder}")