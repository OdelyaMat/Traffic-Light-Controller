

class TrafficLightState:
    def __init__(self):
        self.timer = 0
        self.current_green = 0


def round_robin_logic(counts: list[int], state: TrafficLightState):
    """Cycles through lanes every 6 ticks, ignoring car counts entirely.

    Args:
        counts: Number of cars waiting in each lane, ordered by compass
            direction — North, East, South, West (indices 0–3).
        state: Shared mutable state tracking the current green lane and timer.

    Returns:
        Index of the lane that should have the green light.
    """
    state.timer += 1

    # After 6 ticks, move to the next lane in order
    if state.timer > 5:
        state.current_green = (state.current_green + 1) % len(counts)
        state.timer = 0

    return state.current_green

def most_cars_logic_without_max_green_time(counts: list[int], state: TrafficLightState):
    """Gives green to the lane with the most cars after a fixed interval.

    Switches every 5 ticks to whichever lane is busiest. Has no upper
    bound on how long a lane can stay green if it keeps being the busiest.

    Args:
        counts: Number of cars waiting in each lane, ordered by compass
            direction — North, East, South, West (indices 0–3).
        state: Shared mutable state tracking the current green lane and timer.

    Returns:
        Index of the lane that should have the green light.
    """
    state.timer += 1
    green_time = 5

    # Re-evaluate which lane is busiest every green_time ticks
    if state.timer > green_time:
        state.current_green = counts.index(max(counts))
        state.timer = 0

    return state.current_green

def most_cars_logic_with_max_green_time(counts: list[int], state: TrafficLightState):
    """Always gives green to the lane with the most cars waiting.

    Keeps the current lane green for a minimum of 3 ticks to avoid
    rapid switching.  Forces a round-robin advance after MAX_GREEN
    ticks so no single lane can hog the light forever.

    Args:
        counts: Number of cars waiting in each lane, ordered by compass
            direction — North, East, South, West (indices 0–3).
        state: Shared mutable state tracking the current green lane and timer.

    Returns:
        Index of the lane that should have the green light.
    """
    MIN_GREEN = 3
    MAX_GREEN = 15

    if not hasattr(state, 'round_robin_idx'):
        state.round_robin_idx = 0

    state.timer += 1

    # Force switch via round-robin if we've held green too long
    if state.timer >= MAX_GREEN:
        n = len(counts)
        for _ in range(n):
            state.round_robin_idx = (state.round_robin_idx + 1) % n
            if counts[state.round_robin_idx] > 0:
                break
        state.current_green = state.round_robin_idx
        state.timer = 0
        return state.current_green

    # Skip minimum green time if the current lane is empty
    if state.timer >= MIN_GREEN or counts[state.current_green] == 0:
        busiest = max(range(len(counts)), key=lambda i: counts[i])
        if busiest != state.current_green:
            state.current_green = busiest
            state.timer = 0

    return state.current_green


def adaptive_timer_logic(counts: list[int], state: TrafficLightState):
    """Round-robin but with a green duration proportional to traffic load.

    Each lane gets a green phase whose length scales with the fraction of
    total traffic it holds.  Minimum phase is 3 ticks, maximum is 12.

    Args:
        counts: Number of cars waiting in each lane, ordered by compass
            direction — North, East, South, West (indices 0–3).
        state: Shared mutable state tracking the current green lane and timer.

    Returns:
        Index of the lane that should have the green light.
    """
    MIN_GREEN = 3
    MAX_GREEN = 12

    if not hasattr(state, 'phase_duration'):
        state.phase_duration = MIN_GREEN

    state.timer += 1

    # Skip to next lane immediately if current lane is empty, or when phase expires
    if state.timer >= state.phase_duration or counts[state.current_green] == 0:
        # Advance round-robin, skipping empty lanes (but never loop forever)
        n = len(counts)
        for _ in range(n):
            state.current_green = (state.current_green + 1) % n
            if counts[state.current_green] > 0:
                break
        state.timer = 0

        # Calculate how long the new lane should stay green
        total = sum(counts)
        if total > 0:
            ratio = counts[state.current_green] / total
            state.phase_duration = max(MIN_GREEN, min(MAX_GREEN, round(ratio * MAX_GREEN * n)))
        else:
            state.phase_duration = MIN_GREEN

    return state.current_green


def starvation_aware_logic(counts: list[int], state: TrafficLightState):
    """Greedy approach that picks the busiest lane but prevents starvation.

    Tracks how long each lane has been waiting (red). If any lane has been
    red for more than `MAX_WAIT` ticks, it gets priority regardless of
    its car count. Otherwise the busiest lane wins, with a minimum green
    phase of 3 ticks.  A hard MAX_GREEN cap forces a round-robin advance
    so no lane can hold the light indefinitely.

    Args:
        counts: Number of cars waiting in each lane, ordered by compass
            direction — North, East, South, West (indices 0–3).
        state: Shared mutable state tracking the current green lane and timer.

    Returns:
        Index of the lane that should have the green light.
    """
    MAX_WAIT = 15
    MIN_GREEN = 3
    MAX_GREEN = 18

    if not hasattr(state, 'wait_times'):
        state.wait_times = [0] * len(counts)

    state.timer += 1

    # Update wait times for all red lanes
    for i in range(len(counts)):
        if i == state.current_green:
            state.wait_times[i] = 0
        else:
            state.wait_times[i] += 1

    # Hard cap: force round-robin advance if held green too long
    if state.timer >= MAX_GREEN:
        n = len(counts)
        for _ in range(n):
            state.current_green = (state.current_green + 1) % n
            if counts[state.current_green] > 0:
                break
        state.timer = 0
        return state.current_green

    # Skip minimum green time if the current lane is empty
    if state.timer >= MIN_GREEN or counts[state.current_green] == 0:
        # Check for starving lanes first
        starving = [i for i in range(len(counts))
                    if state.wait_times[i] >= MAX_WAIT and counts[i] > 0]

        if starving:
            # Pick the starving lane that has waited the longest
            chosen = max(starving, key=lambda i: state.wait_times[i])
        else:
            # Pick the busiest lane
            chosen = max(range(len(counts)), key=lambda i: counts[i])

        if chosen != state.current_green:
            state.current_green = chosen
            state.timer = 0

    return state.current_green


def proportional_share_logic(counts: list[int], state: TrafficLightState):
    """Allocates green time in proportion to each lane's share of traffic.

    Works in cycles: at the start of each cycle it looks at current counts
    and assigns each lane a number of ticks proportional to its traffic.
    Every lane is always included in the schedule (even empty ones get
    MIN_GREEN ticks) so no lane is ever completely skipped.

    Args:
        counts: Number of cars waiting in each lane, ordered by compass
            direction — North, East, South, West (indices 0–3).
        state: Shared mutable state tracking the current green lane and timer.

    Returns:
        Index of the lane that should have the green light.
    """
    MIN_GREEN = 2
    CYCLE_BUDGET = 20

    if not hasattr(state, 'schedule'):
        state.schedule = []
        state.schedule_idx = 0

    state.timer += 1

    # If current schedule is exhausted, build a new one
    if not state.schedule or state.timer >= state.schedule[state.schedule_idx][1]:
        if state.schedule and state.schedule_idx < len(state.schedule) - 1:
            # Move to next lane in the current schedule
            state.schedule_idx += 1
            state.timer = 0
            state.current_green = state.schedule[state.schedule_idx][0]
        else:
            # Build a new schedule — include ALL lanes so none get skipped
            total = sum(counts)
            state.schedule = []
            for i in range(len(counts)):
                if total > 0 and counts[i] > 0:
                    ticks = max(MIN_GREEN, round((counts[i] / total) * CYCLE_BUDGET))
                else:
                    ticks = MIN_GREEN
                state.schedule.append((i, ticks))

            state.schedule_idx = 0
            state.timer = 0
            state.current_green = state.schedule[0][0]

    return state.current_green