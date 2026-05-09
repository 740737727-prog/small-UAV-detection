from ultralytics import YOLO
# Load a model

if __name__=='__main__':
    model = YOLO("E:/ultralytics-main/ultralytics/cfg/models/v8/runs/detect/train7/weights/best.pt")
    # Validate with a custom dataset
    validation_results = model.val(data="E:/ultralytics-main/ultralytics/datasets/drone.yaml",
                                   imgsz=640, batch=16,device="0",conf=0.5)