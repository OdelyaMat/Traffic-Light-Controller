import os
from collections import defaultdict

def create_photos_dict(images_dir, labels_dir):
    photos_dict = defaultdict(list)
    
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    for img_name in image_files:
        label_name = os.path.splitext(img_name)[0] + ".txt"
        label_path = os.path.join(labels_dir, label_name)
        
        car_count = 0
        
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    # YOLO format: <class_id> <x_center> <y_center> <width> <height>
                    parts = line.split()
                    if parts and int(parts[0]) in [1, 2]:  # 1 means bus, 2 means car
                        car_count += 1
        
        full_img_path = os.path.join(images_dir, img_name)
        photos_dict[car_count].append(full_img_path)
            
    return dict(photos_dict)

if __name__ == "__main__":
    images_path = "../kaggle_data/test/images"
    labels_path = "../kaggle_data/test/labels"
    
    results = create_photos_dict(images_path, labels_path)
        
    for car_count in sorted(results.keys()):
        image_list = results[car_count]
        print(f"{car_count:<3} | {len(image_list)}")

