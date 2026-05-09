import os
import sys
import time

# 首先注册SPD模块
sys.path.insert(0, os.path.dirname(__file__))
import register_spd
register_spd.register_spd_module()

import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import uuid
from collections import deque

class ModelManager:
    def __init__(self):
        self.models = {}
        self.current_model = 'model1'
        self.model_paths = {
            'model1': r"E:/low attitude object dect/ultralytics-main/model/model1/train25/weights/best.pt",
            'model2': r"E:/low attitude object dect/ultralytics-main/model/model2/train7/weights/best.pt"
        }
        self._load_models()

    def _load_models(self):
        for name, path in self.model_paths.items():
            if os.path.exists(path):
                self.models[name] = YOLO(path)
                print(f"Loaded model: {name} from {path}")
            else:
                print(f"Model file not found: {path}")

    def switch_model(self, model_name):
        if model_name in self.models:
            self.current_model = model_name
            return True
        return False

    def get_current_model(self):
        return self.current_model

    def get_available_models(self):
        return list(self.models.keys())

    def predict_image(self, image_path):
        if self.current_model not in self.models:
            return None
        model = self.models[self.current_model]
        results = model(image_path)
        return self._process_results(results)

    def predict_video(self, video_path):
        if self.current_model not in self.models:
            return None
        model = self.models[self.current_model]
        results = model(video_path, stream=True)
        return self._process_video_results(results, video_path)

    def _process_results(self, results):
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': conf,
                        'class_id': cls_id
                    })
        return detections

    def _process_video_results(self, results, video_path):
        all_detections = []
        for frame_idx, result in enumerate(results):
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    all_detections.append({
                        'frame': frame_idx,
                        'bbox': [x1, y1, x2, y2],
                        'confidence': conf,
                        'class_id': cls_id
                    })
        return all_detections

    def crop_detection(self, image_path, bbox, output_dir):
        img = Image.open(image_path)
        x1, y1, x2, y2 = bbox
        crop = img.crop((x1, y1, x2, y2))
        crop = crop.resize((80, 80), Image.Resampling.LANCZOS)
        crop_filename = f"crop_{uuid.uuid4().hex}.jpg"
        crop_path = os.path.join(output_dir, crop_filename)
        crop.save(crop_path)
        return crop_filename

    def crop_detection_from_frame(self, frame, bbox, output_dir):
        """从视频帧裁剪检测目标，先resize到640*640"""
        x1, y1, x2, y2 = bbox

        h, w = frame.shape[:2]
        if h != 640 or w != 640:
            frame_resized = cv2.resize(frame, (640, 640))
            scale_x = 640 / w
            scale_y = 640 / h
            x1, y1, x2, y2 = int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)
        else:
            frame_resized = frame

        crop = frame_resized[y1:y2, x1:x2]
        if crop.size > 0:
            crop_resized = cv2.resize(crop, (640, 640))
        else:
            crop_resized = np.zeros((640, 640, 3), dtype=np.uint8)

        crop_filename = f"crop_{uuid.uuid4().hex}.jpg"
        crop_path = os.path.join(output_dir, crop_filename)
        cv2.imwrite(crop_path, crop_resized)
        return crop_filename

    def draw_detections(self, image_path, detections, output_path):
        img = cv2.imread(image_path)
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Drone {det['confidence']:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imwrite(output_path, img)

    def process_video_stream(self, video_path, detect_interval_ms=100, enable_interpolation=True):
        """
        视频流处理，带跳帧检测和插值
        """
        if self.current_model not in self.models:
            print(f"错误: 模型 {self.current_model} 未加载")
            return

        model = self.models[self.current_model]
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"错误: 无法打开视频 {video_path}")
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"视频信息: 总帧数={total_frames}, 检测间隔={detect_interval_ms}ms")

        last_detect_time = 0
        last_detections = []
        prev_detections = []

        frame_count = 0
        processed_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"视频结束 (已处理 {processed_count}/{total_frames} 帧)")
                break

            frame_count += 1
            current_time = time.time() * 1000

            if current_time - last_detect_time >= detect_interval_ms:
                try:
                    results = model(frame, verbose=False)
                    last_detections = self._process_frame_results(results)
                except Exception as e:
                    print(f"警告: 推理出错: {e}")
                    last_detections = prev_detections.copy() if prev_detections else []

                last_detect_time = current_time
                prev_detections = last_detections.copy()
                processed_count += 1

                if frame_count % 30 == 0:
                    print(f"进度: {processed_count}/{total_frames} 帧, 检测到 {len(last_detections)} 个目标")

            if last_detections:
                frame_detections = last_detections.copy()
            else:
                frame_detections = prev_detections.copy() if prev_detections else []

            processed_frame = self._draw_boxes_on_frame(frame, frame_detections)
            yield processed_frame, frame_detections

        cap.release()
        print("视频流处理完成")

    def _process_frame_results(self, results):
        """处理单帧的推理结果"""
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': conf,
                        'class_id': cls_id
                    })
        return detections

    def _draw_boxes_on_frame(self, frame, detections):
        """在帧上画检测框"""
        img = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Drone {det['confidence']:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return img

    def save_processed_video(self, video_path, output_path, detect_interval_ms=100, enable_interpolation=True):
        """保存处理后的视频"""
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        for frame, _ in self.process_video_stream(video_path, detect_interval_ms, enable_interpolation):
            out.write(frame)

        out.release()
