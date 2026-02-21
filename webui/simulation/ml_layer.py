import joblib
import pandas as pd

# Load model once
model = joblib.load("energy_prediction_model.pkl")

def predict_energy(specs, style_multiplier, initial_soc_percent, trip_distance):

    battery = specs["battery_kwh"]
    motor = specs["motor_power_kw"]
    power_ratio = specs["power_ratio"]
    energy_per_km = specs["energy_per_km"]
    efficiency = specs["efficiency_km_per_kwh"]

    input_data = pd.DataFrame([{
        "battery_kWh": battery,
        "motor_power_kW": motor,
        "power_ratio": power_ratio,
        "energy_per_km": energy_per_km,
        "efficiency_km_per_kWh": efficiency,
        "style_multiplier": style_multiplier,
        "initial_soc": initial_soc_percent,
        "trip_distance_km": trip_distance
    }])

    energy = model.predict(input_data)[0]

    final_soc_percent = initial_soc_percent - (energy / battery) * 100

    final_soc_percent = max(0, min(100, final_soc_percent))

    return energy, final_soc_percent
