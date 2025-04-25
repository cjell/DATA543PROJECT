# This file just creates new files, each with all the structures but now they ---
# --- have a distance to the fire perimieter for each zone.

import geopandas as gpd
import pandas as pd

zones = gpd.read_file("CreatedData/RiskZones/risk_zones.shp")
addresses = gpd.read_file("CreatedData/ImputedAddresses/addresses_imputed.shp")
addresses = addresses.to_crs(zones.crs)

# Only care about high medium and low risk zones since fires have never happened---
#--- in the 'None' zone and it is just all of Butte anyway
zones = zones[zones["risk_level"].isin(["High", "Medium", "Low"])].copy()
zones = zones.explode(index_parts=False).reset_index(drop=True)

# print(addresses.crs)
# print(zones.crs)

for risk_level in ["High", "Medium", "Low"]:
    
    subset = zones[zones["risk_level"] == risk_level].copy()
    union_geom = subset.union_all()
    zone_boundary = union_geom.boundary

    # making the distance and in_zone features
    distance_to_fire_km = addresses.geometry.apply(lambda x: x.distance(zone_boundary) / 1000)
    in_zone = addresses.geometry.within(union_geom)

    result = addresses.copy()
    result["dist_to_fi"] = distance_to_fire_km
    result["in_perimet"] = in_zone.astype(int)

    out_path = f"CreatedData/ModelInputs/ModelInput_{risk_level.lower()}_Risk.csv"
    
    # We make this one a csv bc the model doesnt need the geometry
    result.drop(columns="geometry").to_csv(out_path, index=False)
