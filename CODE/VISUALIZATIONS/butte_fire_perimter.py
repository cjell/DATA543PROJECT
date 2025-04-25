# This is to show the fire perimeters and the damaged houses in butte county since 2013
# This has more code than necessary because I originally wanted to show each structure by damage severity but it was too cluttered ---
# --- So I just made them all the same color, but left the code in for future reference
import geopandas as gpd
import matplotlib.pyplot as plt


gdb_path = 'DATA/fire23_1.gdb'

fires = gpd.read_file(gdb_path, layer='firep23_1')

counties_path = 'DATA/COUNTYBOUNDS/CA_Counties.shp'

counties = gpd.read_file(counties_path)
counties = counties.to_crs(fires.crs)

butteCounty = counties.loc[counties['NAME'] == 'Butte']

# Only want fires in butte county
fires_butte_clipped = gpd.clip(fires, butteCounty)

butte_fires_recent = fires_butte_clipped.loc[fires_butte_clipped['YEAR_'] > 2013]


# Creating a clean year column since it is in date, time format/
fire_path = 'DATA/FIREDATA/POSTFIRE.shp'
fire_data = gpd.read_file(fire_path)
fire_data = fire_data.to_crs(fires.crs)
fire_data['YEAR'] = fire_data['INCIDENTST'].astype(str).str.split(',').str[0]
fire_data['YEAR'] = fire_data['INCIDENTST'].astype(str).str.split('-').str[0]
butte_data = fire_data.loc[fire_data['COUNTY'] == 'Butte']
butte_data['Severity'] = butte_data['DAMAGE'].str.split(' ').str[0]

print(butte_data['Severity'].unique())

# # Organizing the data by severity
# affected_damage = butte_data.loc[(butte_data['Severity'] == 'Affected') & (butte_data['YEAR'].astype(int) < 2024)].copy()
# minor_damage = butte_data.loc[(butte_data['Severity'] == 'Minor') & (butte_data['YEAR'].astype(int) < 2024)].copy()
# major_damage = butte_data.loc[(butte_data['Severity'] == 'Major') & (butte_data['YEAR'].astype(int) < 2024)].copy()
# destroyed_damage = butte_data.loc[(butte_data['Severity'] == 'Destroyed') & (butte_data['YEAR'].astype(int) < 2024)].copy()
    
# # Made all severities the same color to avoid cluttering the map
# ax = butteCounty.plot(figsize = (15,15), color = 'white', edgecolor = 'black', linewidth=3)
# butte_fires_recent.plot(ax = ax, color = 'red', edgecolor='black')
# destroyed_damage.plot(ax = ax, color = 'blue', marker = 'o', markersize = 5, edgecolor='black', label = 'Destroyed', alpha = 0.65)
# major_damage.plot(ax = ax, color = 'blue', marker = 'o', markersize = 5, edgecolor='black', label = 'Major', alpha = 0.65)
# minor_damage.plot(ax = ax, color = 'blue', marker = 'o', markersize = 5, edgecolor='black', label = 'Minor', alpha = 0.65)
# affected_damage.plot(ax = ax, color = 'blue', marker = 'o', markersize = 5, edgecolor='black', label = 'Affected', alpha = 0.65)
# ax.set_title("Wildfire Perimeters and Damaged Buildings in Butte Since 2013")
# ax.set_xticks([])
# ax.set_yticks([])
# plt.show()


