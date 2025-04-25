import pandas as pd

# Sadly, we do not have the value for every structure in Butte. We looked at the ---
# --- Parcel data but it is not there. I explored imputing all structures with values ---
# --- from the ones that were not damaged but it seemed less accurate than just using ---
# --- the average value of the structures that were damaged. Also, we cross-referenced ---
# --- the values with the ones with Census data and it seems to be a good estimate.
damage_cost = 200_948.39

zones = ["high", "medium", "low"]

total_damages = {}

for zone in zones:
    path = f"CreatedData/ModelOutputs/Predicted_{zone}.csv"
    df = pd.read_csv(path)
    
    # Counting the number of structures predicted to be damaged
    num_damaged = df[df["predicted_damage"] == 1].shape[0]
    
    # getting the total cost of damages and total structures per zone
    total_cost = num_damaged * damage_cost
    total_damages[zone] = {
        "predicted_damaged": num_damaged,
        "total_cost": total_cost
    }

print("Predicted Damages by Zone:\n")
for zone, result in total_damages.items():
    print(f"{zone.capitalize()} Risk:")
    print(f"Structures Predicted Damaged: {result['predicted_damaged']}")
    print(f"Estimated Cost: ${result['total_cost']:,.2f}\n")
