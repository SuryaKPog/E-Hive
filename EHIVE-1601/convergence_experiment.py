import matplotlib.pyplot as plt
from ehive import EV, Station, init_pheromone, aco_construct_solution
from sensitivity_ev_generator import generate_evs
from road_map import ROAD_GRAPH, nearest_node
import random

# -----------------------------
# Parameters
# -----------------------------
EV_COUNT = 20
ANT_ITERATIONS = 40

# -----------------------------
# Setup
# -----------------------------
evs = generate_evs(EV_COUNT)

stations = [
    Station("S1", 50, 10, 0),
    Station("S2", 30, 10, 8),
]

pher = init_pheromone(evs, stations)

best_cost_so_far = float("inf")
convergence_curve = []

# -----------------------------
# TRUE ACO CONVERGENCE LOOP
# -----------------------------
for ant_iter in range(ANT_ITERATIONS):

    solution = aco_construct_solution(evs, stations, pher)

    total_cost = 0.0
    for ev in evs:
        ev_node = nearest_node((ev.x, ev.y))
        st = next(s for s in stations if s.station_id == solution[ev.ev_id])
        st_node = nearest_node((st.x, st.y))
        total_cost += ROAD_GRAPH.shortest_path_distance(ev_node, st_node)

    # Update best-so-far
    best_cost_so_far = min(best_cost_so_far, total_cost)
    convergence_curve.append(best_cost_so_far)

    # Pheromone update (manual, incremental)
    for ev_id in pher:
        for st_id in pher[ev_id]:
            pher[ev_id][st_id] *= 0.92  # evaporation

    for ev_id, st_id in solution.items():
        pher[ev_id][st_id] += 1.0     # reinforcement

    print(f"Ant Iter {ant_iter+1}: Best Cost = {best_cost_so_far:.2f}")

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(7,4))
plt.plot(range(1, ANT_ITERATIONS + 1), convergence_curve, marker='o')
plt.xlabel("Ant Iterations")
plt.ylabel("Best Travel Cost")
plt.title("E-Hive Ant Colony Convergence")
plt.grid(True)
plt.tight_layout()
plt.show()
