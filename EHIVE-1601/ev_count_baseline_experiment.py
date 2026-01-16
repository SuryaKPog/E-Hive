import pandas as pd
from ehive import Station, init_pheromone, combine_and_assign
from sensitivity_ev_generator import generate_evs

# -----------------------------
# Helper: Run one algorithm
# -----------------------------
def run_algorithm(ev_count, mode="ehive"):
    evs = generate_evs(ev_count)

    stations = [
        Station("S1", 50, 10, 0),
        Station("S2", 30, 10, 8),
    ]

    pher = init_pheromone(evs, stations)

    low_soc_total = 0
    low_soc_served = 0

    for _ in range(10):  # simulate multiple decision rounds
        pher, assignment, _, _ = combine_and_assign(evs, stations, pher)

        for ev in evs:
            if ev.soc < 0.3:   # critical EV
                low_soc_total += 1
                if assignment[ev.ev_id] is not None:
                    low_soc_served += 1

    return low_soc_served / max(1, low_soc_total)


# -----------------------------
# Main Experiment
# -----------------------------
results = []

for ev_count in [5, 10, 20, 30]:
    ehive_score = run_algorithm(ev_count, "ehive")

    results.append({
        "EV_Count": ev_count,
        "Low_SoC_Served_Rate": ehive_score
    })

df = pd.DataFrame(results)
df.to_csv("ev_count_low_soc_sensitivity.csv", index=False)

print("\nLow-SoC Service Rate Results:\n")
print(df)
