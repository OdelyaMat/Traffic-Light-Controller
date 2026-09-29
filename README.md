# Smart Traffic Light System

A team project developed as part of a Computer Vision course.

The system combines computer vision, deep learning, and traffic simulation to estimate vehicle density and dynamically control traffic lights at a four-lane intersection.

## My Contribution

I implemented the traffic light control algorithms and system logic, including multiple strategies for selecting the next lane and determining green-light duration based on estimated traffic.

## Technologies

* Python
* Computer Vision
* Deep Learning
* RT-DETR
* Traffic Simulation
* Data Analysis

## Project Overview

The system simulates a four-lane intersection and uses computer vision models to estimate the number of vehicles in each lane. These estimates are then used by different traffic light control strategies to manage traffic flow.

### Simulation Environment

The simulation models a four-lane intersection (N, E, S, W). Each lane starts with a fixed number of vehicles, which enter the intersection at random intervals and rates.

The simulation measures the number of steps required to clear the traffic.

### Components

**Lane**
Each lane contains a reservoir of vehicles. Cars enter the intersection based on probability and a random rate per simulation step.

**Traffic Indicator**
Controls the release of cars from the intersection. Green lights discharge cars at an increasing rate, simulating real traffic flow.

**Photo Picker**
Selects labeled images corresponding to the current estimated vehicle count for each lane.

**Visual Recognition**
Processes intersection images using deep learning models to estimate vehicle counts. The best performing model was the transformer based detector `rtdetr-l.pt`.

**Traffic Light Logic**
Receives estimated vehicle counts and determines which lane receives the green light. Multiple strategies were implemented and compared.

## Traffic Light Logic Functions

1. **Round Robin**: Cycles through lanes in a fixed order.
2. **Most Cars (No Max)**: Prioritizes the lane with the most vehicles.
3. **Most Cars (With Max)**: Adds a maximum green light duration.
4. **Adaptive Timer**: Adjusts green light duration according to traffic share.
5. **Starvation Aware**: Prioritizes lanes that have been waiting for a long time.
6. **Proportional Share**: Allocates green time proportionally while guaranteeing a minimum for each lane.

## Model Comparison & Results

Four computer vision models were evaluated for vehicle detection.

The transformer based model `rtdetr-l.pt` achieved the best overall performance while maintaining reasonable inference speed.

The selected confidence threshold was **0.4**, resulting in an F1 score of **0.57** and a near perfect count ratio.

### Example Results: Strong Model

| Scenario       | Logic                       | Time |
| -------------- | --------------------------- | ---: |
| Low Traffic    | Round Robin                 |  170 |
| Low Traffic    | Most Cars w/ Max Green Time |  161 |
| Low Traffic    | Starvation Aware            |  162 |
| Medium Traffic | Adaptive Timer              |  122 |
| High Traffic   | Adaptive Timer              |  119 |

### Example Results: Weak Model

| Scenario       | Logic                       | Time |
| -------------- | --------------------------- | ---: |
| Low Traffic    | Round Robin                 |  207 |
| Low Traffic    | Most Cars w/ Max Green Time |  600 |
| Medium Traffic | Round Robin                 |  138 |
| High Traffic   | Most Cars w/ Max Green Time |  600 |

## Project Structure

```text
Traffic-Light-Controller/
├── infra/
├── kaggle_data/
│   ├── data.yaml
│   ├── readme.dataset.txt
│   ├── readme.roboflow.txt
│   └── test/
│       ├── images/
│       └── labels/
├── model_research/
├── .gitignore
└── requirements.txt
```

* `infra/`: Core simulation, traffic light logic, visualization, and benchmarking modules.
* `kaggle_data/`: Dataset, configuration, and metadata used for visual recognition.
* `model_research/`: Model comparison, experiments, and tuning.

## Usage

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the main display simulation:

```bash
python -m infra.display
```

Run the benchmark:

```bash
python -m infra.benchmark
```
