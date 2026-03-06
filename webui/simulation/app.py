import streamlit as st
import heapq
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from ehive import EV, Station, init_pheromone, combine_and_assign
from road_map import ROAD_GRAPH, ROAD_NODES, nearest_node
from vehicle_lookup import VehicleDatabase

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="E-Hive Road Simulation", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0d0d0d; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("🛣 E-Hive Road-Based Swarm Simulation")

STYLE_MULTIPLIERS = {
    "Eco": 0.85,
    "City": 1.00,
    "Highway": 1.10,
    "Aggressive": 1.25
}

CHARGE_RATE = 0.02
DRAIN_BASE = 0.002

# --------------------------------------------------
# DIJKSTRA SHORTEST PATH
# --------------------------------------------------
def shortest_path_nodes(start, end):
    pq = [(0, start, [start])]
    visited = set()

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node == end:
            return path

        if node in visited:
            continue

        visited.add(node)

        for nxt, weight in ROAD_GRAPH.graph[node]:
            if nxt not in visited:
                heapq.heappush(pq, (cost + weight, nxt, path + [nxt]))

    return []

# --------------------------------------------------
# SESSION INIT
# --------------------------------------------------
if "sim" not in st.session_state:
    st.session_state.sim = None

# --------------------------------------------------
# CONTROL PANEL
# --------------------------------------------------
db = VehicleDatabase("Master-EV_vehicle_details.csv")
vehicle_options = db.ev_db["model_name"].unique()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Vehicle Setup")

    vehicles_config = []
    for i in range(4):
        model = st.selectbox(f"EV{i+1} Model", vehicle_options, key=f"m{i}")
        mode = st.radio(
            f"EV{i+1} Mode",
            ["Eco","City","Highway","Aggressive"],
            horizontal=True,
            key=f"mode{i}"
        )
        soc = st.slider(f"EV{i+1} SoC (%)", 20, 100, 80, key=f"soc{i}")
        vehicles_config.append({"model":model,"mode":mode,"soc":soc})
        st.markdown("---")

    trip_distance = st.slider("Trip Distance (km)", 5, 120, 40)

    start = st.button("Initialize Simulation")

# --------------------------------------------------
# INITIALIZE SIMULATION
# --------------------------------------------------
if start:

    evs = []
    for i, cfg in enumerate(vehicles_config):

        specs = db.get_vehicle_specs(cfg["model"])
        start_node = ROAD_NODES[i]

        ev = EV(
            ev_id=f"EV{i+1}",
            soc=cfg["soc"]/100,
            distance=trip_distance,
            capacity=specs["battery_kwh"],
            urgency=1 - (cfg["soc"]/100),
            x=start_node[0],
            y=start_node[1],
            model=cfg["model"],
            battery_kwh=specs["battery_kwh"],
            range_km=specs["range_km"],
            motor_kw=specs["motor_power_kw"]
        )

        ev.state = "moving"
        ev.mode = cfg["mode"]
        ev.path = []
        ev.path_index = 0
        ev.assigned_station = None
        ev.wait_ticks = 0
        ev.charge_ticks = 0
        ev.history = [ev.soc]


        evs.append(ev)

    stations = [
        Station("S1", 50, 10, 4),
        Station("S2", 40, 4, 8)
    ]

    pher = init_pheromone(evs, stations)

    st.session_state.sim = {
        "evs": evs,
        "stations": stations,
        "pher": pher,
        "tick": 0,
        "bee_scores": {},
        "station_occupancy": {s.station_id: None for s in stations}
    }

# --------------------------------------------------
# AUTO REFRESH
# --------------------------------------------------
if st.session_state.sim and not st.session_state.sim.get("all_done", False):
    st_autorefresh(interval=700, key="auto_sim")


# --------------------------------------------------
# SIMULATION STEP
# --------------------------------------------------
if st.session_state.sim:

    sim = st.session_state.sim
    evs = sim["evs"]
    stations = sim["stations"]
    pher = sim["pher"]
    station_occupancy = sim["station_occupancy"]

    # Eligible EVs
    eligible = [
        ev for ev in evs
        if ev.state == "moving" and ev.soc < 0.9
    ]

    available_stations = [
        s for s in stations
        if station_occupancy[s.station_id] is None
    ]

    if eligible and available_stations:
        pher, assignment, bee_scores, _ = combine_and_assign(
            eligible,
            available_stations,
            pher
        )

        sim["bee_scores"] = bee_scores

        for ev in eligible:
            assigned = assignment.get(ev.ev_id)
            if assigned and station_occupancy[assigned] is None:
                ev.assigned_station = assigned
                ev.state = "assigned"
                station_occupancy[assigned] = ev.ev_id

    for ev in evs:

        if ev.state == "moving":
            ev.soc -= DRAIN_BASE * STYLE_MULTIPLIERS[ev.mode]
            ev.soc = max(0, ev.soc)
            ev.urgency = 1 - ev.soc
            ev.wait_ticks += 1
            ev.history.append(ev.soc)


        elif ev.state == "assigned":

            station_obj = next(s for s in stations if s.station_id == ev.assigned_station)

            if not ev.path:
                start_node = nearest_node((ev.x, ev.y))
                end_node = nearest_node((station_obj.x, station_obj.y))
                ev.path = shortest_path_nodes(start_node, end_node)
                ev.path_index = 0

            if ev.path_index < len(ev.path):
                next_node = ev.path[ev.path_index]
                ev.x, ev.y = next_node
                ev.path_index += 1
            else:
                ev.state = "charging"

        elif ev.state == "charging":
            ev.soc += CHARGE_RATE
            ev.charge_ticks += 1
            ev.history.append(ev.soc)


            if ev.soc >= 0.95:
                ev.soc = 0.95
                ev.state = "done"
                station_occupancy[ev.assigned_station] = None

        elif ev.state == "done":
            ev.x += 0.5  # drift off screen
            
    all_done = all(ev.state == "done" for ev in evs)
    sim["all_done"] = all_done

    sim["pher"] = pher
    sim["tick"] += 1

    # --------------------------------------------------
# RENDER ROADMAP
# --------------------------------------------------
with col2:

    if st.session_state.sim:

        sim = st.session_state.sim
        evs = sim["evs"]
        stations = sim["stations"]
        station_occupancy = sim["station_occupancy"]

        SCALE = 40
        OFFSET_X = 100
        OFFSET_Y = 100

        def to_screen(pos):
            return pos[0]*SCALE + OFFSET_X, pos[1]*SCALE + OFFSET_Y

        svg = ""

        # Roads
        for node, neighbors in ROAD_GRAPH.graph.items():
            for nxt, _ in neighbors:
                x1,y1 = to_screen(node)
                x2,y2 = to_screen(nxt)
                svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="white" stroke-width="3"/>'

        # Stations
        for stn in stations:
            sx, sy = to_screen((stn.x, stn.y))
            svg += f'<rect x="{sx-12}" y="{sy-12}" width="24" height="24" fill="yellow"/>'

        # EVs
        for ev in evs:
            ex, ey = to_screen((ev.x, ev.y))

            if ev.state == "charging":
                color = "orange"
            elif ev.soc < 0.2:
                color = "red"
            elif ev.state == "done":
                color = "gray"
            else:
                color = "cyan"

            svg += f'<circle cx="{ex}" cy="{ey}" r="8" fill="{color}"/>'

        html = f'<svg width="900" height="700">{svg}</svg>'
        st.components.v1.html(html, height=700)

        # ------------------------
        # SYSTEM METRICS
        # ------------------------
        st.subheader("📊 System Metrics")

        avg_soc = sum(ev.soc for ev in evs)/len(evs)
        charging_count = sum(1 for ev in evs if ev.state=="charging")
        completed = sum(1 for ev in evs if ev.state=="done")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Average SoC", f"{round(avg_soc*100,2)}%")
        m2.metric("Charging", charging_count)
        m3.metric("Completed", completed)
        m4.metric("Tick", sim["tick"])

        # ------------------------
        # VEHICLE TABLE
        # ------------------------
        st.subheader("🚗 Vehicle Status Overview")

        table_data = []
        for ev in evs:
            bee_score = sim["bee_scores"].get(ev.ev_id, None)
            table_data.append({
                "EV": ev.ev_id,
                "State": ev.state,
                "SoC (%)": round(ev.soc*100, 2),
                "Urgency": round(ev.urgency, 3),
                "Bee Score": round(bee_score, 4) if bee_score else None,
                "Assigned Station": ev.assigned_station,
                "Wait Ticks": ev.wait_ticks,
                "Charge Ticks": ev.charge_ticks
            })

        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

        # ------------------------
        # STATION TABLE
        # ------------------------
        st.subheader("⚡ Station Status")

        station_data = []
        for s in stations:
            station_data.append({
                "Station": s.station_id,
                "Occupied By": station_occupancy[s.station_id],
                "Status": "Occupied" if station_occupancy[s.station_id] else "Available"
            })

        st.dataframe(pd.DataFrame(station_data), use_container_width=True)

        # ------------------------
        # SOC EVOLUTION CHART
        # ------------------------
        import matplotlib.pyplot as plt

        st.subheader("📈 SoC Evolution Over Time")

        fig, ax = plt.subplots()

        for ev in evs:
            ax.plot(ev.history, label=ev.ev_id)

        ax.set_xlabel("Tick")
        ax.set_ylabel("SoC")
        ax.legend()

        st.pyplot(fig)

    else:
        st.info("Initialize simulation.")