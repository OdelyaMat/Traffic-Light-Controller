from typing import List, Any
from ultralytics import RTDETR
from ultralytics import YOLO
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = RTDETR('rtdetr-l.pt')
# can switch to 'yolov8n.pt' for a smaller model that runs faster but is less accurate.
# model = RTDETR('rtdetr-l.pt') if device == 'cuda' else YOLO('yolov8n.pt')

target_names = ['car', 'bus']
VALID_CLASSES_LIST = [id for id, name in model.names.items() if name in target_names]

@torch.inference_mode()
def visual_recognition(current_photos: List[Any]) -> List[int]:
    if not current_photos:
        return []

    results = model(current_photos, 
                    verbose=False, 
                    conf=0.4, 
                    classes=VALID_CLASSES_LIST,
                    half=(device == 'cuda'))

    output = []
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy() if hasattr(result.boxes, 'xyxy') else []
        output.append({
            'boxes': boxes,
            'count': len(boxes)
        })
    return output