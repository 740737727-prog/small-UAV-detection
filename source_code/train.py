from ultralytics import YOLO

if __name__=='__main__':
    model = YOLO("yolov8n-SPD2.yaml").load('yolov8n.pt')   # yolov8s.pt build a new model from scratch
    # Use the model
    model.train(data="E:/low attitude object dect/ultralytics-main/ultralytics/datasets/data-DUT.yaml",
                epochs=150, imgsz=640, device=0, workers=8, resume=True, batch=6)  # train the model
    metrics = model.val()  # evaluate model performance on the validation set







