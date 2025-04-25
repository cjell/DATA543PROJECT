import geopandas as gpd
import matplotlib.pyplot as plt

# Loading data
addresses = gpd.read_file("DATA/addresses/shape.shp")
counties = gpd.read_file("DATA/COUNTYBOUNDS/CA_Counties.shp")

# Make the crs the same
counties = counties.to_crs(addresses.crs)

# Only want to plot butte county
butte = counties[counties['NAME'] == 'Butte'].copy()

addresses.dropna(subset=['geometry'], inplace=True)

# Some of the coordinates are not NaN but not valid so this is to filter those out
addresses = addresses.cx[-180:180, -90:90]  



fig, ax = plt.subplots(figsize=(15, 15))

butte.plot(ax=ax, color='white', edgecolor='black', linewidth=3)
addresses.plot(ax=ax, color='darkblue', marker='o', edgecolor='darkblue', markersize=1)

ax.set_title("Structures in Butte County")
ax.set_xticks([])
ax.set_yticks([])
ax.set_aspect(1)

plt.show()


