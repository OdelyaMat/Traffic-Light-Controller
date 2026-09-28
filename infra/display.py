from infra.infra import Lane, Intersection
from infra.logic_functions import round_robin_logic, most_cars_logic_with_max_green_time, starvation_aware_logic, most_cars_logic_without_max_green_time
from infra.photo_picker import photo_picker_factory
from infra.visualizer import Visualizer
from infra.visual_recognition import visual_recognition

lanes = [Lane(200, (1, 8), 0.6) for _ in range(4)]
intersection = Intersection(lanes, round_robin_logic)
photo_picker = photo_picker_factory("./kaggle_data/test")
visualizer = Visualizer()

while any(lane.cars > 0 for lane in intersection.lanes) or \
        any(ind.current_cars > 0 for ind in intersection.traffic_indicators):

    current_photos = photo_picker.update_images([ind.current_cars for ind in intersection.traffic_indicators])
    detection_results = visual_recognition(current_photos)
    visualizer.display(
        current_photos, cars_in_intersection = [indicator.current_cars for indicator in intersection.traffic_indicators],
        cars_remaining = [lane.cars for lane in intersection.lanes], green_light_idx = intersection.green_light_index,
        detections = detection_results
    )
    current_counts = [det['count'] for det in detection_results]
    intersection.update(current_counts)
    
    total_waiting = sum(ind.current_cars for ind in intersection.traffic_indicators)
    remaining_in_reservoir = sum(lane.cars for lane in intersection.lanes)    
    # Safety break for testing
    if remaining_in_reservoir == 0 and total_waiting == 0:
        break