#Code to show wilfire perimeters in California since 1878

import geopandas as gpd
import matplotlib.pyplot as plt


gdb_path = 'DATA/fire23_1.gdb'


fires = gpd.read_file(gdb_path, layer='firep23_1')
recentFires = fires.loc[fires['YEAR_'] > 2013]




counties_path = 'DATA/COUNTYBOUNDS/CA_Counties.shp'
counties = gpd.read_file(counties_path)

counties = counties.to_crs(recentFires.crs)


ax = counties.plot(figsize = (15,15), color = 'white', edgecolor = 'black', linewidth=2)
recentFires.plot(ax = ax, color = 'red', edgecolor='black')
ax.set_title("Wildfire Perimeters in California Since 2013")
ax.set_xticks([])
ax.set_yticks([])
plt.show()

