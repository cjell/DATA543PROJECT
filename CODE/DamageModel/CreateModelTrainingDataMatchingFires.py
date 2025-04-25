import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry.base import BaseGeometry

post_fire = gpd.read_file("DATA/FIREDATA/POSTFIRE.shp")

# Cleaning up the incident name to match those in the fire perimeter data
post_fire['FIRE_CLEAN'] = (post_fire['INCIDENTNA'].astype(str).str.strip().str.upper())

# Cleaning up the incident start date to match those in the fire perimeter data
post_fire['Date'] = pd.to_datetime(post_fire['INCIDENTST'], errors='coerce')
post_fire['Year'] = post_fire['Date'].dt.year

# Only want fires since 2018
post_fire = post_fire.loc[post_fire['Year'] > 2018].copy()

#Same thing for perimeters dataset
perimeters = gpd.read_file('DATA/fire23_1.gdb', layer='firep23_1')
perimeters['FIRE_CLEAN'] = (perimeters['FIRE_NAME']
                        .astype(str)
                        .str.strip()
                        .str.upper())
perimeters['Date'] = pd.to_datetime(perimeters['ALARM_DATE'], errors='coerce')
perimeters['Year'] = perimeters['Date'].dt.year
perimeters = perimeters.loc[perimeters['Year'] > 2018].copy()

# Since names are reused every few years, we have to match years and names --- 
# --- for each dataset and then use all the ones in both datasets
post_fire_incidents = post_fire[['FIRE_CLEAN', 'Year']].drop_duplicates()
perimeter_incidents = perimeters[['FIRE_CLEAN', 'Year']].drop_duplicates()
in_both = pd.merge(post_fire_incidents, perimeter_incidents, on=['FIRE_CLEAN', 'Year'], how='inner')

# Filtering both datasets by common incidents
postfire = post_fire.merge(in_both, on=['FIRE_CLEAN', 'Year'], how='inner')
perims = perimeters.merge(in_both, on=['FIRE_CLEAN', 'Year'], how='inner')

# Making sure each incident is a distinct polygon
final_perimeter = (
    perims
    .dissolve(by=['FIRE_CLEAN', 'Year'])
    .reset_index()[['FIRE_CLEAN', 'Year', 'geometry']]
    .rename(columns={'geometry': 'geometry_fire'})
)
perim_union = final_perimeter.set_geometry('geometry_fire')

# Setting common CRS
postfire = postfire.to_crs("EPSG:3310")
perim_union = perim_union.to_crs("EPSG:3310")

# We can now merge the datasets to give each structure its correct fire perimeter
merged_data = postfire.merge(
    perim_union,
    on=['FIRE_CLEAN', 'Year'],
    how='left'
)

# We can now calculate the distance to the fire perimeter and if it is inside the perimeter
distances = []
in_perimeters = []
for idx, row in merged_data.iterrows():
    geom = row.geometry
    fire_geom = row.geometry_fire
    if isinstance(geom, BaseGeometry) and isinstance(fire_geom, BaseGeometry): # Double check that the geometries are valid
        inside = geom.within(fire_geom)  
        if inside:
            dist = geom.distance(fire_geom.boundary)
        else:
            dist = geom.distance(fire_geom)
    else:
        inside = False
        dist = np.nan
    distances.append(dist)
    in_perimeters.append(inside)
merged_data['dist_to_fire_m'] = distances
merged_data['in_perimeter'] = in_perimeters
merged_data['dist_to_fire_km'] = merged_data['dist_to_fire_m'] / 1000.0


# Now we can generate the synthetic data for fires with a large distance to the perimeter --- 
# --- by settign its fire to a different one and setting damageto 'No Damage'
# Taking 20,000 of the rows to use as a sample.
merged_small = merged_data.sample(n=20000, random_state=42).copy()

synthetic_rows = []
perim_records = perim_union.to_dict('records')
rng = np.random.default_rng(43)
for _, row in merged_small.sample(n=20000, replace=True, random_state=43).iterrows():
    while True:
        choice = rng.choice(perim_records)
        if (choice['FIRE_CLEAN'], choice['Year']) != (row['FIRE_CLEAN'], row['Year']):
            break
    geom = row.geometry
    fire_geom = choice['geometry_fire']
    dist = geom.distance(fire_geom) if isinstance(geom, BaseGeometry) else np.nan
    new_row = row.copy()
    new_row['FIRE_CLEAN'] = choice['FIRE_CLEAN']
    new_row['Year'] = choice['Year']
    new_row['geometry_fire'] = fire_geom
    new_row['dist_to_fire_m'] = dist
    new_row['dist_to_fire_km'] = dist / 1000.0
    new_row['in_perimeter'] = False
    new_row['DAMAGE'] = 'No Damage (Synthetic)'
    synthetic_rows.append(new_row)
augmented_df = pd.DataFrame(synthetic_rows)

# Concatenating the two datasets and dropping the geometry columns to reduce compute time ---
# --- and saving the final dataset to a csv file.
full_df = pd.concat([merged_small, augmented_df], ignore_index=True)
full_df = full_df.drop(columns=['geometry', 'geometry_fire'], errors='ignore')
full_df.to_csv("CreatedData/TrainingData/ModelTrainingDataMatching.csv", index=False)








