import geopandas as gpd
import pandas as pd


data = gpd.read_file("CreatedData/StructuresByZone/risk_scoring_structures.shp")

# add a column for the age of the structure since it had high correlation with the risk score
data['age'] = 2025 - data['YEARBUILT']
raw_scores = []

# Here we are going through each row and calculating a score based on the features ---
# that had a high correlation with the risk score in the training data
for _, row in data.iterrows():
    score = 0.0
    if row.get("eaves") == "Unenclosed":
        score += -0.23
    if row.get("eaves") == "Enclosed":
        score += -0.13
    if row.get("eaves") == "Unknown":
        score += 0.33
    if row.get("structure_type") == "Single Family Residence Multi Story":
        score += -0.18
    if row.get("structure_type") == "Mobile Home Double Wide":
        score += 0.08
    if row.get("roof_construction") == "Unknown":
        score += -0.12
    if row.get("roof_construction") == "Tile":
        score += -0.12
    if row.get("roof_construction") == "Metal":
        score += 0.11
    if row.get("vent_screen") == 'Mesh Screen <= 1/8"':
        score += -0.11
    if row.get("window_pane") == "Multi Pane":
        score += -0.14
    if row.get("window_pane") == "Single Pane":
        score += 0.12
    if row.get("deckporch_elevated") == "No Deck/Porch":
        score += 0.13
    if row.get("deckporch_ongrade") == "No Deck/Porch":
        score += 0.13
    if row.get("fence_attached_to_structure") == "Unknown":
        score += -0.14
    if row.get("fence_attached_to_structure") == "Combustible":
        score += -0.12
    if row.get("fence_attached_to_structure") == "No Fence":
        score += 0.20
    score += row.get("age", 0) * -0.08

    raw_scores.append(score)


data["raw_score"] = raw_scores

#Here we want to normalize the raw score before usign the risk zones---
# so we can have more control over the final score and impact of the zones
min_f = data["raw_score"].min()
max_f = data["raw_score"].max()
data["feature_norm"] = (data["raw_score"] - min_f) / (max_f - min_f)

# Using normalized zone scores and then applying them with a weight of .75 to the final score
zone_values = {"None": 0.0, "Low": 0.3, "Medium": 0.5, "High": 1.0}
data["zone_norm"] = data["risk_level"].map(zone_values).fillna(0)
data["final_score"] = 0.75 * data["zone_norm"] + (1 - 0.75) * data["feature_norm"]


data.to_file("CreatedData/ScoredStructures/scored_structures_normalized.shp")
