from ultralytics import YOLO
if __name__ == '__main__':
    model = YOLO('ultralytics/cfg/models/v8/yolov8-SPD2.yaml')
    model.load('E:/ultralytics-main/yolov8n.pt') # loading pretrain weights
    model.train(data='E:/ultralytics-main/ultralytics/datasets/data-DUT.yaml', epochs=150, batch=6)