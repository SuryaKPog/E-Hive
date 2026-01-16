import random
from ehive import EV

# Sample realistic EV specs (Indian-market inspired)
EV_SPECS = [
    ("MG Comet", 17.3, 230, 42),
    ("Tata Tiago EV", 19.2, 250, 45),
    ("Tata Nexon EV", 40.5, 437, 105),
    ("Mahindra XUV400", 39.4, 456, 110),
    ("BYD Atto 3", 60.5, 521, 150),
]

def generate_evs(n):
    evs = []

    for i in range(n):
        model, battery_kwh, range_km, motor_kw = random.choice(EV_SPECS)

        ev = EV(
            ev_id=f"EV{i}",
            soc=random.uniform(0.1, 0.8),
            distance=random.uniform(2, 25),
            capacity=battery_kwh,              # capacity = battery_kwh
            urgency=random.choice([0, 1]),
            x=random.choice([0, 2, 4, 6, 8]),
            y=random.choice([0, 4, 8]),
            model=model,
            battery_kwh=battery_kwh,
            range_km=range_km,
            motor_kw=motor_kw
        )

        evs.append(ev)

    return evs
