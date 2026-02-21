import random

from ehive import EV, Station, init_pheromone, combine_and_assign
from vehicle_lookup import VehicleDatabase
from ml_layer import predict_energy


def run_simulation(selected_vehicles, driving_style, initial_soc_percent, trip_distance):

    # -----------------------
    # STYLE MULTIPLIERS
    # -----------------------
    style_multipliers = {
        "Eco": 0.85,
        "City": 1.00,
        "Highway": 1.10,
        "Aggressive": 1.25
    }

    style_multiplier = style_multipliers[driving_style]

    # -----------------------
    # LOAD DATABASE
    # -----------------------
    db = VehicleDatabase("Master-EV_vehicle_details.csv")

    ev_objects = []

    # -----------------------
    # CREATE EV OBJECTS
    # -----------------------
    for i, model_name in enumerate(selected_vehicles):

        specs = db.get_vehicle_specs(model_name)

        if specs is None:
            continue

        # ML Energy Prediction
        energy, final_soc_percent = predict_energy(
            specs,
            style_multiplier,
            initial_soc_percent,
            trip_distance
        )

        # Convert % to 0-1
        final_soc = final_soc_percent / 100.0

        # Urgency definition (simple)
        urgency = 1 - final_soc

        # Fake circular placement (just random for now)
        angle = random.uniform(0, 6.28)
        x = 5 + 4 * random.random()
        y = 5 + 4 * random.random()

        ev = EV(
            ev_id=f"EV{i+1}",
            soc=final_soc,
            distance=trip_distance,
            capacity=specs["battery_kwh"],
            urgency=urgency,
            x=x,
            y=y,
            model=model_name,
            battery_kwh=specs["battery_kwh"],
            range_km=specs["range_km"],
            motor_kw=specs["motor_power_kw"]
        )

        ev_objects.append(ev)

    # -----------------------
    # CREATE STATIONS
    # -----------------------
    stations = [
        Station("S1", 50, 10, 5),
        Station("S2", 40, 0, 5)
    ]

    # -----------------------
    # INITIALIZE PHEROMONE
    # -----------------------
    pher = init_pheromone(ev_objects, stations)

    # -----------------------
    # RUN E-HIVE
    # -----------------------
    pher, assignment, bee_scores, _ = combine_and_assign(
        ev_objects,
        stations,
        pher
    )

    # -----------------------
    # STRUCTURED RESULT
    # -----------------------
    results = []

    for ev in ev_objects:
        results.append({
            "ev_id": ev.ev_id,
            "model": ev.model,
            "soc_percent": round(ev.soc * 100, 2),
            "assigned_station": assignment.get(ev.ev_id),
            "bee_priority": bee_scores.get(ev.ev_id)
        })

    return results
