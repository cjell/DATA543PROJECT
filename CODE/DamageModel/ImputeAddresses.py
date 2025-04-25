import geopandas as gpd
import pandas as pd

structures = gpd.read_file("DATA/FIREDATA/POSTFIRE.shp")

#only want to work with butte county
structures = structures[structures["COUNTY"] == "Butte"].copy()

# making it easier to work with severity
structures['Severity'] = structures['DAMAGE'].astype(str).str.split(' ').str[0]

# The structures un-harmed for sampling improved value
no_damage = structures[structures['Severity'] == 'No'].copy()   
addresses = gpd.read_file("DATA/addresses/shape.shp")
addresses = addresses.to_crs(structures.crs)

# Rename structure columns to match model features 
column_map = {
    "STRUCTURET": "structure_type",
    "STRUCTUREC": "structure_category",
    "ROOFCONSTR": "roof_construction",
    "EAVES": "eaves",
    "VENTSCREEN": "vent_screen",
    "EXTERIORSI": "exterior_siding",
    "WINDOWPANE": "window_pane",
    "DECKPORCHO": "deckporch_ongrade",
    "DECKPORCHE": "deckporch_elevated",
    "PATIOCOVER": "patio_cover",
    "FENCEATTAC": "fence_attached_to_structure",
    "YEARBUILT": "year_built"
}
structures = structures.rename(columns=column_map)

# List of feature columns to impute
feature_columns = list(column_map.values())

# Sampling features randomly from the structures dataset
sample = structures[feature_columns].sample(n=len(addresses), replace=True, random_state=42).reset_index(drop=True)

# Samppling the assessed value of homes that were not damaged.
improvedValue = no_damage['ASSESSEDIM'].sample(n=len(addresses), replace=True, random_state=42).reset_index(drop=True)
    
sample['ASSESSEDIM'] = improvedValue

addresses_imputed = addresses.copy()
for col in feature_columns + ['ASSESSEDIM']:
    addresses_imputed[col] = sample[col]

# Leave the columns empty as we will have to calculate these later based on the zones
addresses_imputed["dist_to_fire_km"] = None
addresses_imputed["in_perimeter"] = None

# Keep only geometry and essential features
cols_to_keep = ["geometry"] + feature_columns + ["ASSESSEDIM", "dist_to_fire_km", "in_perimeter"]
addresses_imputed = addresses_imputed[cols_to_keep]

# make sure there are no corrupted geometries
valid_addresses = addresses_imputed[
    addresses_imputed.geometry.is_valid & addresses_imputed.geometry.notnull()].copy()

# print(valid_addresses.columns)
valid_addresses.to_file("CreatedData/ImputedAddresses/addresses_imputed.shp")
