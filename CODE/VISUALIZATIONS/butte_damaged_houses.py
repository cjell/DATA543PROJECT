# This is to show the damaged houses in butte county

import geopandas as gpd
import matplotlib.pyplot as plt

fire_path = 'DATA/FIREDATA/POSTFIRE.shp'
fire_data = gpd.read_file(fire_path)

butte_data = fire_data.loc[fire_data['COUNTY'] == 'Butte']

counties_path = 'DATA/COUNTYBOUNDS/CA_Counties.shp'
counties = gpd.read_file(counties_path)

butte_county = counties.loc[counties['NAME'] == 'Butte']

ax = butte_county.plot(figsize = (15,15), color = 'white', edgecolor = 'black')
butte_data.plot(ax = ax, color = 'red', marker = 'o', edgecolor='black', markersize = 5)

ax.set_title("Houses Damaged by Fires in Butte County California")
ax.set_xticks([])
ax.set_yticks([])
plt.show()