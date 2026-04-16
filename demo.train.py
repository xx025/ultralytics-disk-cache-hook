from ultralytics import YOLO
from ultralytics_disk_cache_hook import enable

enable()
YOLO("yolov8n.pt").train(data="coco128.yaml", epochs=1, imgsz=640, cache="disk")
