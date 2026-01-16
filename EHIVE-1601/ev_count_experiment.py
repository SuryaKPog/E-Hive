from ehive import Station, init_pheromone, combine_and_assign
from sensitivity_ev_generator import generate_evs
import pandas as pd

def run_experiment(ev_count, ticks=30):
    # 1️⃣ Generate EVs
    evs = generate_evs(ev_count)

    # 2️⃣ Create charging stations
    stations = [
        Station("S1", 50, 10, 0),
        Station("S2", 30, 10, 8),
    ]

    # 3️⃣ Initialize pheromones
    pher = init_pheromone(evs, stations)

    # 4️⃣ Track waiting time for each EV
    waiting_time = {ev.ev_id: 0 for ev in evs}
    charging = set()

    # 5️⃣ Simulate time (ticks)
    for _ in range(ticks):
        pher, assignment, _, _ = combine_and_assign(evs, stations, pher)

        for ev in evs:
            ev_id = ev.ev_id

            # If EV is not charging yet
            if ev_id not in charging:
                if assignment[ev_id] is None:
                    waiting_time[ev_id] += 1
                else:
                    charging.add(ev_id)

    # 6️⃣ Compute average waiting time
    avg_wait = sum(waiting_time.values()) / ev_count
    return avg_wait


# =========================
# RUN SENSITIVITY TEST
# =========================
results = []

for ev_count in [5, 10, 20, 30]:
    avg_wait = run_experiment(ev_count)
    results.append({
        "EV_Count": ev_count,
        "Avg_Waiting_Time": round(avg_wait, 2)
    })

df = pd.DataFrame(results)
df.to_csv("ev_count_sensitivity.csv", index=False)

print(df)
