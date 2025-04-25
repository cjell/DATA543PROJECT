import geopandas as gpd

structures = gpd.read_file("DATA/FIREDATA/POSTFIRE.shp")
structures = structures[structures['COUNTY'] == 'Butte'].copy()

structures['YEAR'] = structures['INCIDENTST'].astype(str).str.split('-').str[0]

structures = structures[structures['YEAR'].str.isnumeric()]
structures['YEAR'] = structures['YEAR'].astype(int)
structures = structures[structures['YEAR'] > 2018].copy()

structures = structures.to_crs("EPSG:3310")

zones = gpd.read_file("CreatedData/RiskZones/risk_zones.shp")
zones = zones[zones["risk_level"].isin(["None", "Low", "Medium", "High"])]
zones = zones.to_crs("EPSG:3310")

joined = gpd.sjoin(structures, zones[["risk_level", "geometry"]], how="left", predicate="within")

# print(joined['risk_level'].value_counts(dropna=False))
joined.to_file("CreatedData/StructuresByZone/risk_scoring_structures.shp")

