#Code to show wilfire perimeters in California since 1878

import geopandas as gpd
import matplotlib.pyplot as plt

gdb_path = 'WORKFOLDER/DATA/fire23_1.gdb'

fires = gpd.read_file(gdb_path, layer='firep23_1')

counties_path = 'WORKFOLDER/DATA/COUNTYBOUNDS/CA_Counties.shp'
counties = gpd.read_file(counties_path)

counties = counties.to_crs(fires.crs)
ax = counties.plot(figsize = (15,15), color = 'white', edgecolor = 'black', linewidth=2)

fires.plot(ax = ax, color = 'red', edgecolor='black')
ax.set_title("Wildfire Perimeters in California Since 1878")
ax.set_xticks([])
ax.set_yticks([])
plt.show()

