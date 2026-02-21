import pandas as pd

class VehicleDatabase:
    def __init__(self, file_path="Master-EV_vehicle_details.csv"):
        self.ev_db = pd.read_csv(file_path)

        # Clean column names
        self.ev_db.columns = (
            self.ev_db.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("(", "")
            .str.replace(")", "")
            .str.replace("/", "_")
        )

    def get_vehicle_specs(self, model_name):
        vehicle = self.ev_db[self.ev_db["model_name"] == model_name]

        if vehicle.empty:
            return None

        return vehicle.iloc[0].to_dict()


# Example usage (for testing only)
if __name__ == "__main__":
    db = VehicleDatabase()
    specs = db.get_vehicle_specs("Nexon EV – Medium Range (325 km)")
    print(specs)
