import time
from simulation_runner import run_simulation, SimulationArgs

def main(scenarios, logic_functions):
    t1 = time.perf_counter()

    tasks = [
        SimulationArgs(s[0], s[1], s[2], l[0], l[1])
        for s in scenarios
        for l in logic_functions
    ]

    results = [run_simulation(task) for task in tasks]

    print_results(results)

    print("GPU duration:", time.perf_counter() - t1)

def print_results(results):
    print("\n" + "="*50)
    print(f"{'Scenario':<20} | {'Logic':<15} | {'Time':<10}")
    print("-" * 50)
    for r in results:
        print(f"{r[0]:<20} | {r[1]:<15} | {r[2]:<10}")
    print("="*50)

if __name__ == "__main__":
    main()