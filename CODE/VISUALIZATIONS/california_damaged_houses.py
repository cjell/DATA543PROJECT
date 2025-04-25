#Shows the locations of buildings damaged by fires in California

import geopandas as gpd
import matplotlib.pyplot as plt

fire_path = 'DATA/FIREDATA/POSTFIRE.shp'
fire_data = gpd.read_file(fire_path)


counties_path = 'DATA/COUNTYBOUNDS/CA_Counties.shp'
counties = gpd.read_file(counties_path)

# They already have the same crs so no need to convert

ax = counties.plot(figsize = (15,15), color = 'white', edgecolor = 'black')
fire_data.plot(ax = ax, color = 'red', marker = 'o', edgecolor='black', markersize = 5)
ax.set_title("Buildings Damaged by Fires in California")
ax.set_xticks([])
ax.set_yticks([])
plt.show()
