import cv2
import random
from infra.utils import create_photos_dict

import os 

class PhotoPicker:
    def __init__(self, photos_dict: dict):
        self.photos_dict = photos_dict
        self.current_state = [{"img": None, "count": None, "path": None} for _ in range(4)]

    def update_images(self, cars_in_intersection: list[int]):
        """Syncs the photos with the current car counts in the intersection."""
        for i, cars_in_lane in enumerate(cars_in_intersection):
            # only update if the count changed or we have no image
            if cars_in_lane != self.current_state[i]["count"] or self.current_state[i]["img"] is None:
                available = sorted(self.photos_dict.keys())
                # closest match in the dataset
                best_key = min(available, key=lambda x: abs(x - cars_in_lane))
                path = random.choice(self.photos_dict[best_key])
                new_img = cv2.imread(path)
                if new_img is not None:
                    self.current_state[i] = {
                        "img": cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB),
                        "count": cars_in_lane,
                        "path": path
                    }
        return [state["img"] for state in self.current_state]
    
def photo_picker_factory(data_dir: str):
    images_path = os.path.join(data_dir, "images")
    labels_path = os.path.join(data_dir, "labels")
    my_photos_dict = create_photos_dict(images_path, labels_path)
    return PhotoPicker(my_photos_dict)