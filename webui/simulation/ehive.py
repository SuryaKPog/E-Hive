import math
import random
import pprint
from dataclasses import dataclass
from typing import List, Dict

from road_map import ROAD_GRAPH, ROAD_NODES, nearest_node

# =========================
# GLOBAL PARAMETERS
# =========================
TICK_MINUTES = 5
TICKS_PER_HOUR = 60 // TICK_MINUTES
ANT_COUNT = 40
PHER_DECAY = 0.08
PHER_BOOST = 1.0
ALPHA = 1.0
BETA = 2.0
STATION_SLOTS = 1

# =========================
# DATA CLASSES
# =========================
@dataclass
@dataclass
class EV:
    ev_id: str
    soc: float
    distance: float
    capacity: float
    urgency: float
    x: float
    y: float

    model: str
    battery_kwh: float
    range_km: float
    motor_kw: float


@dataclass
class Station:
    station_id: str
    power_kw: float
    x: float
    y: float
    slots: int = STATION_SLOTS
    queue: List[Dict] = None

    def __post_init__(self):
        if self.queue is None:
            self.queue = []

# =========================
# PHEROMONE INITIALIZATION
# =========================
def init_pheromone(evs: List[EV], stations: List[Station]):
    pher = {}
    for ev in evs:
        pher[ev.ev_id] = {}
        for st in stations:
            pher[ev.ev_id][st.station_id] = 1.0
    return pher

# =========================
# ANT COLONY OPTIMIZATION (ROAD-AWARE)
# =========================
def aco_construct_solution(evs, stations, pher):
    solution = {}

    for ev in evs:
        weights = []
        ev_node = nearest_node((ev.x, ev.y))

        for st in stations:
            st_node = nearest_node((st.x, st.y))
            road_dist = ROAD_GRAPH.shortest_path_distance(ev_node, st_node)

            heuristic = st.power_kw / (1 + road_dist)
            ph = pher[ev.ev_id][st.station_id]

            weight = (ph ** ALPHA) * (heuristic ** BETA)
            weights.append(max(weight, 1e-6))

        chosen_station = random.choices(stations, weights=weights, k=1)[0]
        solution[ev.ev_id] = chosen_station.station_id

    return solution

def aco_run(evs, stations, pher):
    best_solution = None
    best_cost = float("inf")

    for _ in range(ANT_COUNT):
        sol = aco_construct_solution(evs, stations, pher)
        cost = 0.0

        for ev in evs:
            ev_node = nearest_node((ev.x, ev.y))
            st = next(s for s in stations if s.station_id == sol[ev.ev_id])
            st_node = nearest_node((st.x, st.y))
            cost += ROAD_GRAPH.shortest_path_distance(ev_node, st_node)

        if cost < best_cost:
            best_cost = cost
            best_solution = sol

    # Evaporate pheromones
    for ev_id in pher:
        for st_id in pher[ev_id]:
            pher[ev_id][st_id] *= (1 - PHER_DECAY)

    # Reinforce best solution
    for ev_id, st_id in best_solution.items():
        pher[ev_id][st_id] += PHER_BOOST

    return pher, best_solution

# =========================
# BEE URGENCY SCORING
# =========================
def compute_bee_scores(evs):
    scores = {}

    for ev in evs:
        battery_factor = 1 / ev.battery_kwh        # small battery → higher priority
        range_factor = 1 / ev.range_km              # short range → higher priority

        score = (
            0.35 * (1 - ev.soc) +                  # low SoC
            0.20 * battery_factor +
            0.20 * range_factor +
            0.15 * (ev.distance / ev.range_km) +   # distance stress
            0.10 * ev.urgency
        )

        scores[ev.ev_id] = round(score, 4)

    return scores


# =========================
# HYBRID E-HIVE CORE
# =========================
def combine_and_assign(evs, stations, pher):
    bee_scores = compute_bee_scores(evs)

    evs_sorted = sorted(
        evs,
        key=lambda e: bee_scores[e.ev_id],
        reverse=True
    )

    total_slots = sum(st.slots for st in stations)
    charging_evs = evs_sorted[:total_slots]
    waiting_evs = evs_sorted[total_slots:]

    pher, ant_best = aco_run(charging_evs, stations, pher)

    final_assign = {}
    available_stations = {st.station_id: st for st in stations}

    for ev in charging_evs:
        st_id = ant_best[ev.ev_id]

        if st_id not in available_stations:
            st = min(
                available_stations.values(),
                key=lambda s: ROAD_GRAPH.shortest_path_distance(
                    nearest_node((ev.x, ev.y)),
                    nearest_node((s.x, s.y))
                )
            )
            st_id = st.station_id

        final_assign[ev.ev_id] = st_id
        del available_stations[st_id]

    for ev in waiting_evs:
        final_assign[ev.ev_id] = None

    return pher, final_assign, bee_scores, 0.0

# =========================
# TERMINAL SIMULATION (OPTIONAL)
# =========================
def run_simulation(steps=6):
    evs = [
        EV("EV1", 0.20, 120, 60, 1.0, 0, 0),
        EV("EV2", 0.80, 40, 50, 0.0, 2, 0),
        EV("EV3", 0.10, 150, 70, 1.0, 0, 5),
        EV("EV4", 0.50, 80, 45, 0.0, 3, 5),
    ]

    stations = [
        Station("S1", 50, 10, 0),
        Station("S2", 30, 10, 5),
    ]

    pher = init_pheromone(evs, stations)

    print("\nStarting E-Hive Road-Aware Simulation\n")

    for step in range(steps):
        print(f"--- Tick {step+1} ---")
        pher, assignment, priorities, _ = combine_and_assign(
            evs, stations, pher
        )

        print("Assignments:")
        pprint.pprint(assignment)
        print("Bee Priorities:")
        pprint.pprint(priorities)
        print()

    print("Simulation finished.")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    run_simulation()
