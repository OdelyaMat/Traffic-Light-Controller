import torch
from infra.logic_functions import round_robin_logic, most_cars_logic_with_max_green_time, starvation_aware_logic, most_cars_logic_without_max_green_time
scenarios = [
    ("Low Traffic", (1, 7), 0.5),
    ("Medium Traffic", (2, 9), 0.6),
    ("High Traffic", (3, 11), 0.7),
]

logic_functions = [
    ("Round Robin", round_robin_logic),
    ("Most Cars With Max Green Time", most_cars_logic_with_max_green_time),
    ("Starvation Aware", starvation_aware_logic),
    ("Most Cars Without Max Green Time", most_cars_logic_without_max_green_time)
]

if torch.cuda.is_available():
    print("CUDA detected → Running GPU benchmark\n")
    from infra.benchmark_gpu import main
else:
    print("No CUDA → Running CPU benchmark\n")
    from infra.benchmark_cpu import main

if __name__ == "__main__":
    main(scenarios, logic_functions)