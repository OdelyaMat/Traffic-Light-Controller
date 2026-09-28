import random
from typing import List, Tuple, Callable
from infra.visualizer import Visualizer
from infra.photo_picker import photo_picker_factory
from typing import Callable, List
from infra.logic_functions import round_robin_logic
from infra.visual_recognition import visual_recognition

class TrafficLightState:
    def __init__(self):
        self.timer = 0
        self.current_green = 0

class TrafficIndecator:
    def __init__(self, green_light_release_range: Tuple[int, int]):
        self.current_cars: int = 0
        self.green_light_release_range: Tuple[int, int] = green_light_release_range
        self.green_light_release_rate: int = self.green_light_release_range[0]
        
    def update(self, light_is_green: bool, new_cars: int):
        self.current_cars += new_cars
        if light_is_green:
            # gradually increase release rate while green, up to the max range
            self.green_light_release_rate = min(self.green_light_release_range[1], 
                                               self.green_light_release_rate + random.randint(0, 1))
            
            # remove cars based on release rate, but don't go below zero
            removed_cars = min(self.current_cars, self.green_light_release_rate)
            self.current_cars -= removed_cars
        else:
            # reset release rate when light turns red
            self.green_light_release_rate = self.green_light_release_range[0]

class Lane:
    def __init__(self, cars: int, traffic_rate_range: Tuple[int, int], odds_of_traffic: float):
        self.traffic_rate_range = traffic_rate_range
        self.cars = cars  # Total cars waiting to enter the intersection
        self.odds_of_traffic = odds_of_traffic

    def generate_traffic(self):
        # (odds_of_traffic) chance of cars moving from the 'reservoir' to the intersection
        if random.random() > self.odds_of_traffic or self.cars <= 0:
            return 0
        
        potential_cars = random.randint(self.traffic_rate_range[0], self.traffic_rate_range[1])
        # Can't move more cars than are left in the lane's total count
        cars_generated = min(self.cars, potential_cars)
        
        self.cars -= cars_generated
        return cars_generated
    
class Intersection:
    def __init__(
        self,
        lanes: List[Lane],
        traffic_light_logic: Callable[[List[int], object], int]
    ):
        self.lanes = lanes
        self.traffic_indicators = [TrafficIndecator(green_light_release_range=(8, 12)) for _ in lanes]
        self._logic_func = traffic_light_logic
        self._light_state = TrafficLightState()
        self.green_light_index = 0

    def update(self, current_counts):
        self.green_light_index = self._logic_func(
            current_counts,
            self._light_state
        )

        for i, (lane, indicator) in enumerate(zip(self.lanes, self.traffic_indicators)):
            new_cars = lane.generate_traffic()
            indicator.update(self.green_light_index == i, new_cars)


if __name__ == "__main__":
    lanes = [Lane(200, (1, 8), 0.6) for _ in range(4)]

    intersection = Intersection(lanes, round_robin_logic)
    photo_picker = photo_picker_factory("./kaggle_data/test")
    visualizer = Visualizer()

    while any(lane.cars > 0 for lane in intersection.lanes) or \
          any(ind.current_cars > 0 for ind in intersection.traffic_indicators):

        current_photos = photo_picker.update_images([ind.current_cars for ind in intersection.traffic_indicators])

        visualizer.display(
            current_photos,
            cars_in_intersection = [indicator.current_cars for indicator in intersection.traffic_indicators],
            cars_remaining = [lane.cars for lane in intersection.lanes],
            green_light_idx = intersection.green_light_index
        )

        current_counts = visual_recognition(current_photos)
    
        intersection.update(current_counts)

        total_waiting = sum(ind.current_cars for ind in intersection.traffic_indicators)
        remaining_in_reservoir = sum(lane.cars for lane in intersection.lanes)
        print(f"Waiting at Light: {total_waiting} | Remaining in Lanes: {remaining_in_reservoir}")
        
        if remaining_in_reservoir == 0 and total_waiting == 0:
            break